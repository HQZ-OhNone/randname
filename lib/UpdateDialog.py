"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

"""检查更新窗口。

- 异步请求 GitHub Releases，避免阻塞界面；
- 大字显示检测状态；
- 下方文本框展示 history.md 正文；
- “更新”打开 Releases 页面并关闭，“确定”只关闭窗口。
"""

import json
import re
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import QApplication, QDialog, QScroller

from lib import StateManager, ui_update
from lib.version import APP_VERSION

API_URL = "https://api.github.com/repos/HQZ-OhNone/randname/releases/latest"


def parse_version(value) -> tuple[int, ...]:
    """把 v3.9.2、3.10.0-beta 等字符串转换为可比较的数字元组。"""
    if not isinstance(value, str):
        return ()
    match = re.search(r"\d+(?:\.\d+)*", value)
    if match is None:
        return ()
    return tuple(int(part) for part in match.group(0).split("."))


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


def update_timeout_ms(config) -> int:
    """读取并限制更新查询超时，非法值回退到 15 秒。"""
    update_config = config.get("update", {}) if isinstance(config, dict) else {}
    if not isinstance(update_config, dict):
        update_config = {}
    return int(_number(update_config.get("timeout_ms"), 15000, 1000, 120000))


class UpdateDialog(QDialog):
    def __init__(self, parent, *, history_path: Path, translate=None, config=None,
                 releases_url: str = "", api_url: str = API_URL):
        super().__init__(parent)
        self.ui = ui_update.Ui_UpdateDialog()
        self.ui.setupUi(self)
        self.translate = translate or (lambda key, **values: key)
        self.history_path = Path(history_path)
        self.releases_url = releases_url or "https://github.com/HQZ-OhNone/randname/releases"
        self.api_url = api_url
        self.reply = None
        self._finished = False
        self.timeout_ms = update_timeout_ms(config)

        viewer = config.get("viewer", {}) if isinstance(config, dict) else {}
        if not isinstance(viewer, dict):
            viewer = {}
        font_size = _number(viewer.get("font_size"), 12, 6, 48)
        touch_scroll = viewer.get("touch_scroll", True) is not False

        update_config = config.get("update", {}) if isinstance(config, dict) else {}
        if not isinstance(update_config, dict):
            update_config = {}
        self.timeout_ms = int(_number(update_config.get("timeout_ms"), 15000, 1000, 120000))

        self.setWindowTitle(self.translate("update.title"))
        self.ui.updateButton.setText(self.translate("update.button_update"))
        self.ui.manualButton.setText(self.translate("update.button_manual"))
        self.ui.okButton.setText(self.translate("update.button_ok"))
        self.ui.updateButton.setEnabled(False)
        self.ui.okButton.clicked.connect(self.reject)
        self.ui.manualButton.clicked.connect(self._manual_query)
        self.ui.updateButton.clicked.connect(self._open_releases_and_close)
        self.ui.historyEdit.setFont(QFont(self.ui.historyEdit.font().family(), int(font_size)))
        if touch_scroll:
            try:
                QScroller.grabGesture(
                    self.ui.historyEdit.viewport(),
                    QScroller.ScrollerGestureType.LeftMouseButtonGesture,
                )
            except Exception:
                pass

        self._load_history()
        self._set_status("update.checking")
        self._apply_geometry()

        self.manager = QNetworkAccessManager(self)
        QTimer.singleShot(0, self.start_check)

    # ------------------------------------------------------------------ layout
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

    def _load_history(self):
        try:
            text = self.history_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        self.ui.historyEdit.setPlainText(text)

    def _set_status(self, key):
        self.ui.statusLabel.setText(self.translate(key))

    # ------------------------------------------------------------------ network
    def start_check(self):
        if self._finished:
            return
        request = QNetworkRequest(QUrl(self.api_url))
        request.setTransferTimeout(self.timeout_ms)  # 毫秒
        request.setHeader(
            QNetworkRequest.KnownHeaders.UserAgentHeader,
            f"randname/{APP_VERSION}",
        )
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        self.reply = self.manager.get(request)
        self.reply.finished.connect(self._on_finished)

    def _on_finished(self):
        reply = self.reply
        self.reply = None
        if reply is None:
            return
        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                StateManager.log("WARNING", "check_update", error=reply.errorString())
                self._finish("update.failed")
                return
            try:
                raw = reply.readAll().data().decode("utf-8", errors="replace")
                payload = json.loads(raw)
            except (ValueError, UnicodeDecodeError) as exc:
                StateManager.log("ERROR", "check_update", error=str(exc))
                self._finish("update.failed")
                return
            latest = payload.get("tag_name") if isinstance(payload, dict) else None
            if not isinstance(latest, str) or not latest.strip():
                StateManager.log("ERROR", "check_update", error="missing tag_name")
                self._finish("update.failed")
                return
            if is_newer_version(latest, APP_VERSION):
                StateManager.log("INFO", "check_update", result=f"available:{latest}")
                self._finish("update.available")
                self.ui.statusLabel.setToolTip(latest)
            else:
                StateManager.log("INFO", "check_update", result="latest")
                self._finish("update.latest")
        finally:
            reply.deleteLater()

    def _finish(self, status_key):
        self._finished = True
        self._set_status(status_key)
        self.ui.updateButton.setEnabled(status_key == "update.available")

    def _manual_query(self):
        """手动查询：打开 Releases 页面，保持检测窗口开启。"""
        QDesktopServices.openUrl(QUrl(self.releases_url))

    def _open_releases_and_close(self):
        """确认更新：打开 Releases 页面并关闭检测窗口。"""
        QDesktopServices.openUrl(QUrl(self.releases_url))
        self.accept()

    def closeEvent(self, event):
        self._finished = True
        if self.reply is not None:
            self.reply.abort()
            self.reply = None
        super().closeEvent(event)


__all__ = ["UpdateDialog", "is_newer_version", "parse_version", "update_timeout_ms"]
