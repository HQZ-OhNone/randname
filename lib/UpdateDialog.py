"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License along
with this program. If not, see <https://www.gnu.org/licenses/>.
"""

"""检查更新窗口。

- 同时尝试 GitHub 直连与镜像站点，首个有效回应即采用；
- 大字显示检测状态；
- 以 Markdown 渲染完整的 doc/releasenote.md，并保留版本号标题；
- 查询成功时用线上最新 Release 正文同步对应版本；
- “更新”用多种方式打开 Releases 页面，失败时保留窗口并显示网址。
"""

import re
from pathlib import Path

from PySide6.QtCore import QJsonDocument, QTimer, QUrl, Qt
from PySide6.QtGui import QPalette, QTextCursor
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import QApplication, QDialog

from lib import StateManager, ui_update
from lib.Scrolling import install_smooth_scrolling
from lib.UrlOpener import open_url
from lib.version import APP_VERSION

API_URL = "https://api.github.com/repos/HQZ-OhNone/randname/releases/latest"
DEFAULT_MIRROR_PREFIXES = (
    "https://gh-proxy.com/",
    "https://ghfast.top/",
)
_VERSION_HEADING = re.compile(r"^##\s+v?([0-9][^\s]*)")


def parse_version(value) -> tuple[int, ...]:
    """把 v3.9.2、3.10.0-beta 等字符串转换为可比较的数字元组。"""
    if not isinstance(value, str):
        return ()
    parts = []
    digits = []
    started = False
    for char in value:
        if char.isdigit():
            digits.append(char)
            started = True
        elif char == "." and digits:
            parts.append(int("".join(digits)))
            digits.clear()
        elif started:
            break
    if digits:
        parts.append(int("".join(digits)))
    return tuple(parts)


def is_newer_version(latest, current) -> bool:
    """latest 是否严格新于 current；无法解析时视为没有新版本。"""
    latest_parts = parse_version(latest)
    current_parts = parse_version(current)
    if not latest_parts or not current_parts:
        return False
    length = max(len(latest_parts), len(current_parts))
    latest_padded = latest_parts + (0,) * (length - len(latest_parts))
    current_padded = current_parts + (0,) * (length - len(current_parts))
    return latest_padded > current_padded


def latest_release_section(text: str) -> str:
    """从 releasenote.md 截取最上方的版本段落，忽略文件头注释。"""
    lines = (text or "").splitlines()
    collected = []
    found = False
    for line in lines:
        if line.startswith("## v"):
            if found:
                break
            found = True
            continue
        if found:
            collected.append(line)
    if not found:
        return (text or "").strip()
    return "\n".join(collected).strip()


def release_notes_document(text: str) -> str:
    """返回可直接渲染的完整发布说明：去掉文件标题与维护注释。"""
    document = (text or "").strip()
    if not document:
        return ""
    document = re.sub(r"^#\s*Release Notes\s*", "", document, count=1).strip()
    while document.startswith("<!--"):
        end = document.find("-->")
        if end < 0:
            break
        document = document[end + 3:].strip()
    return document


def clean_release_body(text: str) -> str:
    """去掉 Release 正文末尾的构建来源页脚。"""
    text = (text or "").strip()
    text = re.sub(r"(?s)\n*-{3,}\s*\nBuilt from commit:.*$", "", text)
    return text.strip()


def merge_release_section(document: str, tag: str, body: str, date: str = "") -> str:
    """把线上最新 Release 正文合并进发布说明，保留全部版本标题。"""
    tag = (tag or "").strip()
    body = clean_release_body(body)
    if not tag or not body:
        return document
    version = tag[1:] if tag.lower().startswith("v") else tag
    heading_tag = f"v{version}"
    lines = (document or "").splitlines()
    start = None
    end = len(lines)
    for index, line in enumerate(lines):
        match = _VERSION_HEADING.match(line.strip())
        if match is None or match.group(1) != version:
            continue
        start = index
        for offset in range(index + 1, len(lines)):
            if _VERSION_HEADING.match(lines[offset].strip()):
                end = offset
                break
        break

    if start is not None:
        heading = lines[start].strip()
        block = [heading, "", body, ""]
        merged = lines[:start] + block + lines[end:]
    else:
        date_part = f" — {date[:10]}" if re.match(r"\d{4}-\d{2}-\d{2}", date or "") else ""
        merged = [f"## {heading_tag}{date_part}", "", body, ""] + lines

    result = "\n".join(merged)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def parse_release_payload(payload) -> dict | None:
    """从 GitHub API 的 JSON 对象中提取版本、正文和发布日期。"""
    if not isinstance(payload, dict):
        return None
    tag = payload.get("tag_name")
    if not isinstance(tag, str) or not tag.strip():
        return None
    body = payload.get("body")
    published = payload.get("published_at")
    return {
        "tag": tag.strip(),
        "body": body.strip() if isinstance(body, str) else "",
        "published": published.strip() if isinstance(published, str) else "",
    }


def _number(value, default, minimum=None, maximum=None):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if minimum is not None and result < minimum:
        result = minimum
    if maximum is not None and result > maximum:
        result = maximum
    return result


def _update_config(config) -> dict:
    update = config.get("update", {}) if isinstance(config, dict) else {}
    return update if isinstance(update, dict) else {}


def update_timeout_ms(config) -> int:
    """读取并限制更新查询超时，非法值回退到 15 秒。"""
    return int(_number(_update_config(config).get("timeout_ms"), 15000, 1000, 120000))


def update_parallel(config) -> bool:
    """是否并发请求直连与镜像；默认开启。"""
    return _update_config(config).get("parallel", True) is not False


def update_mirror_prefixes(config) -> list[str]:
    """读取并过滤镜像前缀，非法值忽略。"""
    raw = _update_config(config).get("mirror_prefixes", DEFAULT_MIRROR_PREFIXES)
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, (list, tuple)):
        raw = DEFAULT_MIRROR_PREFIXES
    prefixes = []
    for value in raw:
        if not isinstance(value, str):
            continue
        value = value.strip()
        if not value.lower().startswith(("http://", "https://")):
            continue
        prefixes.append(value.rstrip("/") + "/")
    return list(dict.fromkeys(prefixes))


def request_urls(api_url: str, config) -> list[str]:
    """返回查询地址：直连在前，镜像在后，去重并过滤非法值。"""
    if not isinstance(api_url, str):
        return []
    api_url = api_url.strip()
    if not api_url.lower().startswith(("http://", "https://")):
        return []
    urls = [api_url]
    for prefix in update_mirror_prefixes(config):
        urls.append(prefix.rstrip("/") + "/" + api_url.lstrip("/"))
    return list(dict.fromkeys(urls))


class UpdateDialog(QDialog):
    def __init__(self, parent, *, notes_path: Path, translate=None, config=None,
                 releases_url: str = "", api_url: str = API_URL):
        super().__init__(parent)
        self.ui = ui_update.Ui_UpdateDialog()
        self.ui.setupUi(self)
        self.translate = translate or (lambda key, **values: key)
        self.notes_path = Path(notes_path)
        self.releases_url = releases_url or "https://github.com/HQZ-OhNone/randname/releases"
        self.api_url = api_url
        self.config = config if isinstance(config, dict) else {}
        self._releases_qurl = QUrl(self.releases_url)
        self.urls = request_urls(self.api_url, self.config)
        self.parallel = update_parallel(self.config)
        self._queue = []
        self._inflight = []
        self._errors = []
        self._check_done = False
        self._finished = False
        self._local_text = ""
        self._remote = None
        self.timeout_ms = update_timeout_ms(self.config)

        viewer = self.config.get("viewer", {})
        if not isinstance(viewer, dict):
            viewer = {}
        font_size = _number(viewer.get("font_size"), 12, 6, 48)
        touch_scroll = viewer.get("touch_scroll", True) is not False

        self.setWindowTitle(self.translate("update.title"))
        self.ui.updateButton.setText(self.translate("update.button_update"))
        self.ui.manualButton.setText(self.translate("update.button_manual"))
        self.ui.okButton.setText(self.translate("update.button_ok"))
        self.ui.updateButton.setEnabled(False)
        self.ui.okButton.clicked.connect(self.reject)
        self.ui.manualButton.clicked.connect(self._manual_query)
        self.ui.updateButton.clicked.connect(self._open_releases_and_close)
        self.ui.statusLabel.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        notes_font = self.ui.notesEdit.font()
        notes_font.setPointSize(int(font_size))
        self.ui.notesEdit.setFont(notes_font)
        self.ui.notesEdit.setOpenExternalLinks(True)
        self.ui.notesEdit.setOpenLinks(True)
        self.ui.notesEdit.document().setDefaultStyleSheet(self._notes_stylesheet())
        install_smooth_scrolling(self.ui.notesEdit, touch_scroll)

        self._load_notes()
        self._set_status("update.checking")
        self._apply_geometry()

        self.manager = QNetworkAccessManager(self)
        QTimer.singleShot(0, self.start_check)

    # ------------------------------------------------------------------ layout
    def _notes_stylesheet(self) -> str:
        try:
            link = self.palette().color(QPalette.ColorRole.Link).name()
        except Exception:
            link = "#4A90E2"
        return (
            "h1 { font-size: 20pt; margin: 14px 0 8px 0; }"
            "h2 { font-size: 17pt; margin: 18px 0 6px 0; }"
            "h3 { font-size: 14pt; margin: 14px 0 4px 0; }"
            "p, li { margin: 3px 0; }"
            f"a {{ color: {link}; }}"
            "code, pre { font-family: monospace; }"
        )

    def _apply_geometry(self):
        screen = QApplication.screenAt(self.pos()) or QApplication.primaryScreen()
        available = screen.availableGeometry() if screen is not None else None
        if available is None:
            return
        width = min(860, max(480, int(available.width() * 0.85)))
        height = min(640, max(360, int(available.height() * 0.85)))
        self.resize(width, height)
        self.move(
            available.center().x() - self.width() // 2,
            available.center().y() - self.height() // 2,
        )

    # ------------------------------------------------------------------ notes
    def _load_notes(self):
        try:
            self._local_text = self.notes_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            self._local_text = ""
        self._render_notes()

    def _render_notes(self):
        document = release_notes_document(self._local_text)
        if self._remote is not None:
            document = merge_release_section(
                document,
                self._remote.get("tag", ""),
                self._remote.get("body", ""),
                self._remote.get("published", ""),
            )
        self.ui.notesEdit.setMarkdown(document)
        self._scroll_top()

    def _scroll_top(self):
        try:
            bar = self.ui.notesEdit.verticalScrollBar()
            bar.setValue(bar.minimum())
            self.ui.notesEdit.moveCursor(QTextCursor.MoveOperation.Start)
        except Exception:
            pass

    def _set_status(self, key, **values):
        self.ui.statusLabel.setText(self.translate(key, **values))

    # ------------------------------------------------------------------ network
    def start_check(self):
        if self._finished or self._check_done:
            return
        self._errors = []
        self._inflight = []
        self._queue = list(self.urls)
        if self.parallel:
            queued, self._queue = list(self._queue), []
            for url in queued:
                self._send(url)
        else:
            self._send_next()

    def _send_next(self):
        if self._finished or self._check_done:
            return
        if not self._queue:
            if not self._inflight:
                self._fail_check()
            return
        self._send(self._queue.pop(0))

    def _send(self, url: str):
        request = QNetworkRequest(QUrl(url))
        request.setTransferTimeout(self.timeout_ms)  # 毫秒
        request.setHeader(
            QNetworkRequest.KnownHeaders.UserAgentHeader,
            f"randname/{APP_VERSION}",
        )
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        reply = self.manager.get(request)
        self._inflight.append(reply)
        reply.finished.connect(lambda current=reply: self._on_reply(current))

    @staticmethod
    def _channel(url: str) -> str:
        host = QUrl(url).host()
        return host or "unknown"

    def _on_reply(self, reply):
        if reply in self._inflight:
            self._inflight.remove(reply)
        url = reply.url().toString()
        try:
            if self._finished or self._check_done:
                return
            if reply.error() != QNetworkReply.NetworkError.NoError:
                self._record_failure(url, reply.errorString())
                return
            document = QJsonDocument.fromJson(reply.readAll())
            payload = None if document.isNull() else document.toVariant()
            release = parse_release_payload(payload)
            if release is None:
                self._record_failure(url, "invalid payload")
                return
            self._accept_release(release, url)
        finally:
            reply.deleteLater()

    def _record_failure(self, url: str, message: str):
        entry = f"{self._channel(url)}: {message}"
        self._errors.append(entry)
        StateManager.log("WARNING", "check_update", error=entry)
        if not self.parallel:
            self._send_next()
        elif not self._inflight and not self._check_done:
            self._fail_check()

    def _accept_release(self, release: dict, url: str):
        self._check_done = True
        for reply in list(self._inflight):
            try:
                reply.abort()
            except Exception:
                pass
        self._inflight.clear()

        tag = release.get("tag", "")
        if release.get("body"):
            self._remote = release
            self._render_notes()
        self._scroll_top()
        channel = self._channel(url)
        if is_newer_version(tag, APP_VERSION):
            StateManager.log(
                "INFO", "check_update", result=f"available:{tag} channel={channel}"
            )
            self._finish("update.available")
            self.ui.statusLabel.setToolTip(tag)
        else:
            StateManager.log("INFO", "check_update", result=f"latest channel={channel}")
            self._finish("update.latest")

    def _fail_check(self):
        if self._finished or self._check_done:
            return
        summary = "; ".join(self._errors[-4:]) or "no channel"
        StateManager.log("WARNING", "check_update", error=summary)
        self._finish("update.failed")

    def _finish(self, status_key):
        self._finished = True
        self._set_status(status_key)
        self.ui.updateButton.setEnabled(status_key == "update.available")

    def _manual_query(self):
        """手动查询：打开 Releases 页面，保持检测窗口开启。"""
        if not open_url(self.releases_url):
            StateManager.log("ERROR", "open_releases", error=self.releases_url)
            self._set_status("update.open_failed", url=self.releases_url)

    def _open_releases_and_close(self):
        """确认更新：打开 Releases 页面并关闭检测窗口。"""
        if open_url(self.releases_url):
            StateManager.log("INFO", "open_releases", result=self.releases_url)
            self.accept()
            return
        StateManager.log("ERROR", "open_releases", error=self.releases_url)
        self._set_status("update.open_failed", url=self.releases_url)
        self.ui.statusLabel.setToolTip(self.releases_url)

    def closeEvent(self, event):
        self._finished = True
        for reply in list(self._inflight):
            try:
                reply.abort()
            except Exception:
                pass
        self._inflight.clear()
        super().closeEvent(event)


__all__ = [
    "UpdateDialog",
    "clean_release_body",
    "is_newer_version",
    "latest_release_section",
    "merge_release_section",
    "parse_release_payload",
    "parse_version",
    "release_notes_document",
    "request_urls",
    "update_mirror_prefixes",
    "update_parallel",
    "update_timeout_ms",
]
