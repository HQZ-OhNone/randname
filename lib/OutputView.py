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

非滚动模式（OutputView）：
1. 先尝试用基准字号单行显示；
2. 单行放不下、但结果框高度足够时，改为多行显示；
3. 多行仍放不下时，在本次抽取内逐步缩小字号。

滚动模式（SlotOutputView）：
4. 每个姓名放在固定的格子中，已抽出的位置不随其他名字滚动；
5. 第一次抽取时计算并锁定布局；名字放不下时才重新调整并锁定。
"""

import math

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget


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


def _largest_font_for_grid(names, cell_width, cell_height, base_font,
                           max_size, min_size, step):
    """返回能让所有姓名单行放进格子的最大字号。"""
    size = float(max_size)
    minimum = float(min_size)
    step = max(0.1, float(step))
    while size >= minimum:
        metrics = QFontMetrics(_font_at_size(base_font, size))
        if (
            all(metrics.horizontalAdvance(name) <= max(1.0, cell_width - 4.0) for name in names)
            and metrics.lineSpacing() <= max(1.0, cell_height - 2.0)
        ):
            return size
        size -= step
    return minimum


def _font_at_size(base_font, point_size):
    font = QFont(base_font)
    font.setPointSizeF(max(1.0, float(point_size)))
    return font


def choose_slot_layout(names, width, height, base_font, max_size, min_size,
                       step, gap=8, count=None):
    """选择固定格子布局，返回 (columns, rows, point_size)。

    优先保证字号最大；字号相同时选择最接近目标行数的配置。目标行数按
    输出框宽高比与人数估算，例如 6 人、宽输出框会得到 2 行（3×2）。
    """
    values = [str(name) for name in names if name is not None]
    try:
        total = max(1, int(count if count is not None else len(values)))
    except (TypeError, ValueError):
        total = max(1, len(values))
    if width <= 1 or height <= 1:
        return 1, total, float(max_size)
    gap = max(0, int(gap))
    target_rows = max(
        1, min(total, int(round(math.sqrt(total * max(1, height) / max(1, width)))))
    )
    best = None
    for columns in range(1, total + 1):
        rows = math.ceil(total / columns)
        cell_width = (width - (columns - 1) * gap) / columns
        cell_height = (height - (rows - 1) * gap) / rows
        if cell_width <= 1 or cell_height <= 1:
            continue
        size = _largest_font_for_grid(
            values, cell_width, cell_height, base_font, max_size, min_size, step
        )
        score = (size, -abs(rows - target_rows), -rows, -columns)
        if best is None or score > best[0]:
            best = (score, columns, rows, size)
    if best is None:
        return 1, total, float(max_size)
    return best[1], best[2], best[3]


class _SlotGrid(QWidget):
    """按固定格子摆放多个 QLabel；只更新文字，不改变已锁定位置。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 子标签不参与主题的 QLabel 背景绘制，输出框背景由外层 QLabel 负责。
        self.setStyleSheet("background-color: transparent; border: none; padding: 0px;")
        self.slots = []
        self.message_label = QLabel(self)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet(
            "background-color: transparent; border: none; padding: 0px;"
        )
        self._message_mode = True
        self._columns = 1
        self._rows = 1
        self._gap = 8
        self._font = QFont()

    def set_slot_count(self, count):
        count = max(0, int(count))
        while len(self.slots) < count:
            label = QLabel(self)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            label.setStyleSheet(
                "background-color: transparent; border: none; padding: 0px;"
            )
            label.setFont(self._font)
            self.slots.append(label)
        while len(self.slots) > count:
            label = self.slots.pop()
            label.hide()
            label.deleteLater()
        self._message_mode = count == 0
        self.message_label.setVisible(self._message_mode)
        for label in self.slots:
            label.setVisible(not self._message_mode)
        self._layout_children()

    def set_message(self, text):
        self._message_mode = True
        self.message_label.setText(str(text))
        self.message_label.setVisible(True)
        for label in self.slots:
            label.setVisible(False)
        self._layout_children()

    def show_slots(self):
        self._message_mode = False
        self.message_label.setVisible(False)
        for label in self.slots:
            label.setVisible(True)

    def set_names(self, names):
        names = [str(name) for name in names]
        self.show_slots()
        for index, label in enumerate(self.slots):
            label.setText(names[index] if index < len(names) else "")

    def set_font(self, font):
        self._font = QFont(font)
        self.message_label.setFont(self._font)
        for label in self.slots:
            label.setFont(self._font)

    def set_grid(self, columns, rows):
        self._columns = max(1, int(columns))
        self._rows = max(1, int(rows))
        self._layout_children()

    def set_gap(self, gap):
        self._gap = max(0, int(gap))
        self._layout_children()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_children()

    def _layout_children(self):
        rect = self.rect()
        width = max(1, rect.width())
        height = max(1, rect.height())
        gap = self._gap
        cell_width = max(1.0, (width - (self._columns - 1) * gap) / self._columns)
        cell_height = max(1.0, (height - (self._rows - 1) * gap) / self._rows)
        self.message_label.setGeometry(rect)
        for index, label in enumerate(self.slots):
            row = index // self._columns
            column = index % self._columns
            row_count = min(self._columns, len(self.slots) - row * self._columns)
            row_width = row_count * cell_width + max(0, row_count - 1) * gap
            start_x = (width - row_width) / 2.0
            x = start_x + column * (cell_width + gap)
            y = row * (cell_height + gap)
            label.setGeometry(
                int(round(x)), int(round(y)),
                int(round(cell_width)), int(round(cell_height)),
            )


class SlotOutputView(QObject):
    """滚动模式输出框：每个姓名固定在独立格子中，只有文字更新。"""

    def __init__(self, label, config=None, fallback_point_size=None, parent=None):
        super().__init__(parent)
        self.label = label
        self.padding = 8.0
        self.line_spacing = 1.0
        self.base_point_size = float(fallback_point_size or label.font().pointSizeF() or 30.0)
        self.min_point_size = 12.0
        self.font_step = 1.0
        self._names = []
        self._message_mode = True
        self._quantity = 0
        self._columns = 0
        self._rows = 0
        self._layout_point_size = None
        self._font_family = ""
        self._base_font = QFont(label.font())

        # 沿用原输出 QLabel 作为背景容器，子控件负责固定格子排版。
        label.setText("")
        label.setWordWrap(False)
        policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        policy.setHorizontalStretch(160)
        policy.setVerticalStretch(0)
        label.setSizePolicy(policy)
        label.setMinimumSize(0, 0)
        self.grid = _SlotGrid(label)
        self.grid.setGeometry(label.contentsRect())
        label.installEventFilter(self)
        self.configure(config, fallback_point_size)
        self.set_message("")

    # ------------------------------------------------------------------ config
    def configure(self, config, fallback_point_size=None):
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
        self._layout_point_size = None
        self._columns = 0
        self._rows = 0
        if self._message_mode:
            self._grid_font(self.base_point_size)
            self.grid.set_message(self.grid.message_label.text())
        else:
            self._relayout()

    # ------------------------------------------------------------------ public
    def set_message(self, text):
        self._message_mode = True
        self._names = []
        self._quantity = 0
        self._layout_point_size = None
        self._columns = 0
        self._rows = 0
        self.grid.set_slot_count(0)
        self.grid.set_message(str(text))
        self._grid_font(self.base_point_size)
        self.grid.setGeometry(self.label.contentsRect())

    def set_names(self, names, use_lock=True):
        self._message_mode = False
        self._names = [str(name) for name in names if name is not None]
        if not self._names:
            self.set_message("")
            return
        if not use_lock:
            self.clear_round()
        required = len(self._names)
        if required != len(self.grid.slots):
            self._quantity = required
            self.grid.set_slot_count(required)
        self.grid.set_names(self._names)
        self._ensure_layout()

    def begin_round(self, pool_names, quantity):
        """建立本轮固定数量的格子；第一次 set_names 时锁定布局。"""
        try:
            count = max(1, int(quantity))
        except (TypeError, ValueError):
            count = 1
        self._message_mode = False
        self._names = []
        self._quantity = count
        self._layout_point_size = None
        self._columns = 0
        self._rows = 0
        self.grid.set_slot_count(count)
        self.grid.set_names([""] * count)
        self._grid_font(self.base_point_size)
        self.grid.setGeometry(self.label.contentsRect())

    def clear_round(self):
        """下一轮、数量变化或导入结果时清除布局锁定。"""
        self._layout_point_size = None
        self._columns = 0
        self._rows = 0
        self._quantity = 0

    @property
    def current_text(self):
        return " ".join(self._names)

    def slot_geometries(self):
        """测试与调试用：返回每个已显示格子的几何信息。"""
        return [label.geometry() for label in self.grid.slots]

    # ------------------------------------------------------------------ internals
    def eventFilter(self, watched, event):
        if watched is self.label and event.type() == QEvent.Type.Resize:
            self.grid.setGeometry(self.label.contentsRect())
            if not self._message_mode and self._names:
                self._ensure_layout()
        return False

    def _available(self):
        rect = self.label.contentsRect()
        return max(1, rect.width()), max(1, rect.height())

    def _gap(self):
        width, height = self._available()
        return max(4, int(min(width, height) * 0.02))

    def _grid_font(self, point_size):
        font = _font_at_size(self._base_font, point_size)
        self.grid.set_font(font)

    def _layout_fits(self, names, columns, rows, point_size):
        if point_size <= self.min_point_size:
            return True
        width, height = self._available()
        gap = self._gap()
        cell_width = (width - (columns - 1) * gap) / max(1, columns)
        cell_height = (height - (rows - 1) * gap) / max(1, rows)
        if cell_width <= 1 or cell_height <= 1:
            return False
        metrics = QFontMetrics(_font_at_size(self._base_font, point_size))
        if metrics.lineSpacing() > max(1.0, cell_height - 2.0):
            return False
        return all(
            metrics.horizontalAdvance(name) <= max(1.0, cell_width - 4.0)
            for name in names
        )

    def _ensure_layout(self):
        if not self._names:
            return
        if (
            self._columns
            and self._rows
            and self._layout_point_size is not None
            and self._layout_fits(
                self._names, self._columns, self._rows, self._layout_point_size
            )
        ):
            return
        width, height = self._available()
        gap = self._gap()
        count = len(self.grid.slots)
        columns, rows, size = choose_slot_layout(
            self._names,
            width,
            height,
            self._base_font,
            self.base_point_size,
            self.min_point_size,
            self.font_step,
            gap,
            count,
        )
        self._columns = columns
        self._rows = rows
        self._layout_point_size = size
        self.grid.set_gap(gap)
        self.grid.set_grid(columns, rows)
        self._grid_font(size)

    def _relayout(self):
        if self._message_mode or not self._names:
            return
        self._ensure_layout()


__all__ = ["OutputView", "SlotOutputView", "choose_slot_layout", "pack_names"]
