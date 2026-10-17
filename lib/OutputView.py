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

"""在固定窗口内自适应显示姓名。

显示策略（所有抽取模式共用）：
1. 先尝试用基准字号单行显示；
2. 单行放不下、但结果框高度足够时，改为多行显示；
3. 多行仍放不下时，在本次抽取内逐步缩小字号；
4. 滚动抽取在每轮开始时锁定字号，避免滚动过程中字号抖动。
"""

from PySide6.QtCore import QEvent, QObject
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QLabel, QSizePolicy


def _number(value, default, minimum=None):
    """读取配置中的数值；非法值回退默认值。"""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if result != result or result in (float("inf"), float("-inf")):
        return default
    if minimum is not None and result < minimum:
        return minimum
    return result


def pack_names(names, metrics, max_width):
    """把姓名按显示宽度贪婪地排成若干行，保证不会从姓名中间断开。"""
    lines = []
    current = []
    for raw_name in names:
        name = str(raw_name)
        candidate = current + [name]
        if current and metrics.horizontalAdvance("  ".join(candidate)) > max_width:
            lines.append("  ".join(current))
            current = [name]
        else:
            current = candidate
    if current:
        lines.append("  ".join(current))
    return lines or [""]


class OutputView(QObject):
    """包装一个 QLabel，负责单行/多行/缩字号显示。"""

    def __init__(self, label, config=None, fallback_point_size=None, parent=None):
        super().__init__(parent)
        self.label = label
        self.padding = 8.0
        self.line_spacing = 1.0
        self.base_point_size = float(fallback_point_size or label.font().pointSizeF() or 30.0)
        self.min_point_size = 12.0
        self.font_step = 1.0
        self._names = []
        self._text = ""
        self._locked_point_size = None
        self._font_family = ""
        self._message_mode = True

        # 输出框必须保留 .ui 中 160 的水平 stretch，否则 QGridLayout 会把
        # 大部分宽度分给左右 spacer，输出框只剩几十像素。
        # Expanding + wordWrap=True 让 minimumSizeHint 保持较小，长名字
        # 由 OutputView 手动分行/缩字号处理，同时窗口不会被内容撑大。
        self.label.setWordWrap(True)
        policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        policy.setHorizontalStretch(160)
        policy.setVerticalStretch(0)
        self.label.setSizePolicy(policy)
        self.label.setMinimumSize(0, 0)
        self.configure(config, fallback_point_size)
        self.label.installEventFilter(self)
        self.set_message("")

    # ------------------------------------------------------------------ config
    def configure(self, config, fallback_point_size=None):
        """应用 [ui] 配置；窗口尺寸变化或刷新配置后调用。"""
        ui = config.get("ui", {}) if isinstance(config, dict) else {}
        if not isinstance(ui, dict):
            ui = {}
        fallback = float(fallback_point_size or self.label.font().pointSizeF() or 30.0)
        self.base_point_size = _number(ui.get("display_font_size"), fallback, 1.0)
        self.min_point_size = _number(ui.get("display_min_font_size"), 12.0, 1.0)
        if self.min_point_size > self.base_point_size:
            self.min_point_size = self.base_point_size
        self.font_step = _number(ui.get("display_font_step"), 1.0, 0.5)
        self.padding = _number(ui.get("display_padding"), 8.0, 0.0)
        self.line_spacing = _number(ui.get("display_line_spacing"), 1.0, 0.5)
        family = ui.get("font_family", "")
        self._font_family = family.strip() if isinstance(family, str) else ""
        self._base_font = QFont(self.label.font())
        if self._font_family:
            self._base_font.setFamily(self._font_family)
        self._relayout()

    # ------------------------------------------------------------------ public
    def set_message(self, text):
        """显示等待/占位文案，使用基准字号。"""
        self._message_mode = True
        self._names = []
        self._locked_point_size = None
        self._text = str(text)
        font = QFont(self._base_font)
        font.setPointSizeF(self.base_point_size)
        self.label.setWordWrap(True)
        self.label.setFont(font)
        self.label.setText(self._text)

    def set_names(self, names, use_lock=True):
        """显示一组姓名；use_lock=True 时沿用 begin_round 锁定的字号。"""
        self._message_mode = False
        self._names = [str(name) for name in names if name is not None]
        if not use_lock:
            self._locked_point_size = None
        if not self._names:
            self.set_message("")
            return
        self._relayout()

    def begin_round(self, pool_names, quantity):
        """按最坏情况为本轮锁定一个能容纳所有可能姓名的字号。"""
        names = [str(name) for name in pool_names if name is not None]
        try:
            count = max(1, int(quantity))
        except (TypeError, ValueError):
            count = 1
        if self.label.width() <= 1 or self.label.height() <= 1:
            # 页面尚未完成布局时先不锁定，等 resizeEvent 自动排版。
            self._locked_point_size = None
            return
        metrics = QFontMetrics(self._font_with_size(self.base_point_size))
        widest = sorted(names, key=lambda name: metrics.horizontalAdvance(name), reverse=True)
        self._locked_point_size = self._font_size_for(widest[:count])

    def clear_round(self):
        """结束本轮锁定，后续消息/结果恢复自动字号。"""
        self._locked_point_size = None

    @property
    def current_text(self):
        return self._text

    # ------------------------------------------------------------------ internals
    def eventFilter(self, watched, event):
        if watched is self.label and event.type() == QEvent.Type.Resize:
            self._relayout()
        return False

    def _font_with_size(self, point_size):
        font = QFont(self._base_font)
        font.setPointSizeF(max(1.0, float(point_size)))
        return font

    def _available(self):
        width = max(1, self.label.width() - int(self.padding * 2) - 4)
        height = max(1, self.label.height() - int(self.padding * 2) - 4)
        return width, height

    def _layout_for(self, names, point_size):
        font = self._font_with_size(point_size)
        metrics = QFontMetrics(font)
        width, height = self._available()
        lines = pack_names(names, metrics, width)
        line_height = max(1, int(metrics.lineSpacing() * self.line_spacing))
        return font, lines, max(metrics.horizontalAdvance(line) for line in lines), line_height * len(lines)

    def _fits(self, names, point_size):
        _, _, width, height = self._layout_for(names, point_size)
        available_width, available_height = self._available()
        return width <= available_width and height <= available_height

    def _font_size_for(self, names):
        if not names:
            return self.base_point_size
        if self.label.width() <= 1 or self.label.height() <= 1:
            return self.base_point_size
        size = self.base_point_size
        while size >= self.min_point_size:
            if self._fits(names, size):
                return size
            size -= self.font_step
        return self.min_point_size

    def _apply(self, names, point_size):
        font, lines, _width, _height = self._layout_for(names, point_size)
        self.label.setFont(font)
        # 始终保持 wordWrap，避免 QLabel 重新产生巨大的 minimumSizeHint。
        self.label.setWordWrap(True)
        text = "\n".join(lines)
        if text != self._text:
            self._text = text
            self.label.setText(text)

    def _relayout(self):
        if self._message_mode or not self._names:
            return
        point_size = self._locked_point_size
        if point_size is None:
            point_size = self._font_size_for(self._names)
        self._apply(self._names, point_size)


__all__ = ["OutputView", "pack_names"]
