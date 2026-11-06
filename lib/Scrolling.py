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

"""只读文本框的触屏与鼠标平滑滚动配置。"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QInputDevice
from PySide6.QtWidgets import QScroller, QScrollerProperties

SCROLLBAR_STYLE = (
    "QScrollBar:vertical { width: 22px; }"
    "QScrollBar:horizontal { height: 22px; }"
)


def has_touch_screen() -> bool:
    """当前系统是否连接了触摸屏。"""
    try:
        return bool(QInputDevice.devices(QInputDevice.DeviceType.TouchScreen))
    except Exception:
        return False


def install_smooth_scrolling(view, enabled: bool = True) -> bool:
    """为只读文本框启用平滑滚动与触屏拖动。

    有触摸屏时使用 TouchGesture，否则保留鼠标左键拖动。返回是否成功
    注册了拖动手势。
    """
    if view is None:
        return False
    try:
        view.setStyleSheet(SCROLLBAR_STYLE)
        for bar in (view.verticalScrollBar(), view.horizontalScrollBar()):
            if bar is not None:
                bar.setSingleStep(24)
    except Exception:
        pass
    if not enabled:
        return False

    target = view.viewport() if hasattr(view, "viewport") else view
    try:
        target.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
    except Exception:
        pass
    gesture = (
        QScroller.ScrollerGestureType.TouchGesture
        if has_touch_screen()
        else QScroller.ScrollerGestureType.LeftMouseButtonGesture
    )
    try:
        QScroller.grabGesture(target, gesture)
        scroller = QScroller.scroller(target)
        properties = scroller.scrollerProperties()
        properties.setScrollMetric(
            QScrollerProperties.ScrollMetric.DragStartDistance, 0.005
        )
        properties.setScrollMetric(
            QScrollerProperties.ScrollMetric.DecelerationFactor, 0.125
        )
        properties.setScrollMetric(
            QScrollerProperties.ScrollMetric.MousePressEventDelay, 0.08
        )
        properties.setScrollMetric(
            QScrollerProperties.ScrollMetric.FrameRate,
            QScrollerProperties.FrameRates.Fps60,
        )
        scroller.setScrollerProperties(properties)
        return True
    except Exception:
        return False


__all__ = ["SCROLLBAR_STYLE", "has_touch_screen", "install_smooth_scrolling"]
