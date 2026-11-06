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

"""用默认浏览器打开外部链接。

部分 Windows 精简系统（例如希沃白板）没有正确注册默认浏览器，
QDesktopServices 会静默失败；这里依次尝试系统接口与命令行回退。
"""

import os
import subprocess
import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


def browser_commands(url: str, platform: str | None = None) -> list[list[str]]:
    """返回当前平台可用的浏览器启动命令列表。"""
    platform = platform or sys.platform
    if platform == "win32":
        return [["cmd", "/c", "start", "", url]]
    if platform == "darwin":
        return [["open", url]]
    return [["xdg-open", url]]


def open_url(url, *, platform=None, desktop=None, opener=None, spawn=None) -> bool:
    """打开链接；成功返回 True，全部失败返回 False。"""
    if not isinstance(url, str) or not url.strip():
        return False
    platform = platform or sys.platform
    desktop = desktop or (lambda value: QDesktopServices.openUrl(QUrl(value)))
    spawn = spawn or subprocess.Popen

    try:
        if desktop(url):
            return True
    except Exception:
        pass

    opener = opener if opener is not None else getattr(os, "startfile", None)
    if platform == "win32" and opener is not None:
        try:
            opener(url)
            return True
        except Exception:
            pass

    for command in browser_commands(url, platform):
        try:
            spawn(command)
            return True
        except Exception:
            continue
    return False


__all__ = ["browser_commands", "open_url"]
