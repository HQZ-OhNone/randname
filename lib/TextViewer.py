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

"""只读、实时刷新的内部文本查看器。

用于帮助、许可证和程序日志：
- 始终以只读方式打开文件；
- 文件被修改、追加或替换后自动刷新；
- 非模态显示，可一边运行程序一边查看；
- 窗口尺寸限制在桌面可用区域内，为任务栏留出空间；
- 支持触屏拖动滚动和更宽的滚动条。
"""

from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, QTimer, Qt
from PySide6.QtGui import QDesktopServices, QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QPlainTextEdit,
    QTextBrowser,
    QVBoxLayout,
)
from PySide6.QtWidgets import QScroller


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


class TextViewerDialog(QDialog):
    def __init__(self, parent, title, path: Path, *, markdown=False, config=None,
                 translate=None, empty_text="", close_text="Close"):
        super().__init__(parent)
        self.path = Path(path)
        self.markdown = bool(markdown)
        self.translate = translate or (lambda key, **values: key)
        self.empty_text = empty_text or self.translate("state.no_logs")
        self._last_signature = None
        self._closing = False
        viewer = config.get("viewer", {}) if isinstance(config, dict) else {}
        if not isinstance(viewer, dict):
            viewer = {}
        self.refresh_ms = int(_number(viewer.get("refresh_ms"), 500, 100, 60000))
        self.font_size = _number(viewer.get("font_size"), 12, 6, 48)
        self.max_screen_ratio = _number(viewer.get("max_screen_ratio"), 0.85, 0.3, 1.0)
        self.touch_scroll = viewer.get("touch_scroll", True) is not False

        self.setWindowTitle(title)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setSizeGripEnabled(True)
        self._apply_geometry()

        if self.markdown:
            self.text_view = QTextBrowser(self)
            self.text_view.setOpenExternalLinks(False)
            self.text_view.setOpenLinks(False)
            self.text_view.anchorClicked.connect(lambda url: QDesktopServices.openUrl(url))
        else:
            self.text_view = QPlainTextEdit(self)
        self.text_view.setReadOnly(True)
        self.text_view.setUndoRedoEnabled(False)
        flags = (
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        if self.markdown:
            flags |= Qt.TextInteractionFlag.LinksAccessibleByMouse
        self.text_view.setTextInteractionFlags(flags)
        self.text_view.setFont(QFont(self.text_view.font().family(), int(self.font_size)))
        self.text_view.setStyleSheet(
            "QScrollBar:vertical { width: 22px; }"
            "QScrollBar:horizontal { height: 22px; }"
        )
        if self.touch_scroll:
            try:
                QScroller.grabGesture(
                    self.text_view.viewport(),
                    QScroller.ScrollerGestureType.LeftMouseButtonGesture,
                )
            except Exception:
                pass

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=self)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(close_text)
        buttons.button(QDialogButtonBox.StandardButton.Close).setMinimumHeight(40)
        buttons.rejected.connect(self.close)
        buttons.accepted.connect(self.close)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addWidget(self.text_view)
        layout.addWidget(buttons)

        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self._on_file_changed)
        self.watcher.directoryChanged.connect(self._on_file_changed)
        self.timer = QTimer(self)
        self.timer.setInterval(self.refresh_ms)
        self.timer.timeout.connect(self._refresh)
        self._watch()
        self.timer.start()
        self._refresh(force=True)

    # ------------------------------------------------------------------ geometry
    def _apply_geometry(self):
        screen = self.parent().screen() if self.parent() is not None else QApplication.primaryScreen()
        available = screen.availableGeometry() if screen is not None else None
        if available is None:
            self.resize(820, 560)
            return
        # 留出窗口边框和任务栏空间，绝不超过可用桌面。
        margin = 24
        max_width = max(280, int(available.width() * self.max_screen_ratio) - margin * 2)
        max_height = max(240, int(available.height() * self.max_screen_ratio) - margin * 2)
        width = min(900, max_width)
        height = min(680, max_height)
        width = min(width, available.width() - margin)
        height = min(height, available.height() - margin)
        self.setMinimumSize(min(420, width), min(300, height))
        self.resize(max(280, width), max(240, height))
        self.move(
            available.center().x() - self.width() // 2,
            available.center().y() - self.height() // 2,
        )

    # ------------------------------------------------------------------ watching
    def _watch(self):
        paths = []
        if self.path.exists():
            paths.append(str(self.path))
        parent = self.path.parent
        if parent.exists():
            paths.append(str(parent))
        for path in paths:
            if path not in self.watcher.files() and path not in self.watcher.directories():
                self.watcher.addPath(path)

    def _on_file_changed(self, _path):
        # 文件被替换或删除后，watcher 会丢失目标，重新挂载后再刷新。
        self._watch()
        self._refresh()

    def _signature(self):
        try:
            stat = self.path.stat()
        except OSError:
            return None
        return (stat.st_mtime_ns, stat.st_size)

    def _read_text(self):
        try:
            return self.path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    def _refresh(self, force=False):
        if self._closing:
            return
        signature = self._signature()
        if not force and signature == self._last_signature:
            return
        text = self._read_text()
        if text is None:
            text = self.empty_text
        self._last_signature = signature
        bar = self.text_view.verticalScrollBar()
        at_bottom = bar.value() >= bar.maximum() - 4
        if self.markdown:
            self.text_view.setMarkdown(text)
        else:
            self.text_view.setPlainText(text)
        if at_bottom:
            self.text_view.moveCursor(QTextCursor.MoveOperation.End)
            bar.setValue(bar.maximum())

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh(force=True)

    def closeEvent(self, event):
        self._closing = True
        self.timer.stop()
        super().closeEvent(event)


__all__ = ["TextViewerDialog"]
