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

"""Windows 标题栏颜色适配；非 Windows 平台直接跳过。"""

import sys

from PySide6.QtGui import QColor


def colorref(color: QColor) -> int:
    """Qt 颜色转 Windows COLORREF（0x00BBGGRR）。"""
    color = QColor(color)
    return (color.blue() << 16) | (color.green() << 8) | color.red()


def is_dark(color: QColor) -> bool:
    """按感知亮度判断是否应使用深色标题栏。"""
    return QColor(color).lightnessF() < 0.5


def _set_attribute(dwmapi, hwnd: int, attribute: int, value: int) -> bool:
    import ctypes

    raw = ctypes.c_int(int(value))
    result = dwmapi.DwmSetWindowAttribute(
        ctypes.c_void_p(hwnd),
        ctypes.c_int(attribute),
        ctypes.byref(raw),
        ctypes.sizeof(raw),
    )
    return result == 0


def _redraw_frame(hwnd: int) -> None:
    """强制重画非客户区，避免标题栏颜色延迟生效。"""
    import ctypes

    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOZORDER = 0x0004
    SWP_NOACTIVATE = 0x0010
    SWP_FRAMECHANGED = 0x0020
    flags = SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED
    try:
        ctypes.windll.user32.SetWindowPos(ctypes.c_void_p(hwnd), None, 0, 0, 0, 0, flags)
    except Exception:
        pass
    try:
        ctypes.windll.dwmapi.DwmFlush()
    except Exception:
        pass


def apply_titlebar(hwnd: int, color: QColor, dark: bool | None = None) -> bool:
    """尝试把窗口标题栏设置为指定颜色，失败时静默返回 False。"""
    if sys.platform != "win32" or not hwnd:
        return False
    color = QColor(color)
    if not color.isValid():
        return False
    dark = is_dark(color) if dark is None else bool(dark)
    text = 0xFFFFFF if dark else 0x000000
    try:
        import ctypes

        dwmapi = ctypes.windll.dwmapi
    except Exception:
        return False

    # Windows 11 22000+：精确设置标题栏、文字与边框颜色。
    applied = False
    try:
        results = (
            _set_attribute(dwmapi, hwnd, 35, colorref(color)),
            _set_attribute(dwmapi, hwnd, 36, text),
            _set_attribute(dwmapi, hwnd, 34, colorref(color)),
        )
        applied = any(results)
    except Exception:
        applied = False
    if applied:
        _redraw_frame(hwnd)
        return True

    # Windows 10/11 回退：只切换深色/浅色标题栏。
    try:
        if _set_attribute(dwmapi, hwnd, 20, 1 if dark else 0):
            _redraw_frame(hwnd)
            return True
        if _set_attribute(dwmapi, hwnd, 19, 1 if dark else 0):
            _redraw_frame(hwnd)
            return True
        return False
    except Exception:
        return False


__all__ = ["apply_titlebar", "colorref", "is_dark"]
