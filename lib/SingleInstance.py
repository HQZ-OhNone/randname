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

"""单实例控制。

同一版本只允许运行一个窗口：第二个进程连接到已有窗口后立即退出。
不同版本使用不同名称，因此不同版本的可移植副本可以同时运行。
"""

import getpass
import hashlib
import re

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from lib.version import APP_VERSION

WAKE_MESSAGE = b"show\n"
_SAFE_VERSION = re.compile(r"[^0-9A-Za-z._-]")


def server_name(version: str = APP_VERSION, user: str | None = None) -> str:
    """返回同一版本、同一用户共用的本地服务名。"""
    name = user or getpass.getuser() or "user"
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]
    safe_version = _SAFE_VERSION.sub("_", str(version or "0"))
    return f"randname-{safe_version}-{digest}"


def notify_running(name: str | None = None, timeout_ms: int = 400) -> bool:
    """通知已运行的窗口显示自己；没有正在运行的实例时返回 False。"""
    socket = QLocalSocket()
    socket.connectToServer(name or server_name())
    if not socket.waitForConnected(timeout_ms):
        return False
    written = socket.write(WAKE_MESSAGE) >= 0
    socket.flush()
    socket.waitForBytesWritten(timeout_ms)
    socket.disconnectFromServer()
    return written


class SingleInstanceServer(QObject):
    """监听第二个实例的唤醒请求。"""

    activated = Signal()

    def __init__(self, parent=None, name: str | None = None):
        super().__init__(parent)
        self.name = name or server_name()
        self.server = QLocalServer(self)
        self.server.newConnection.connect(self._on_new_connection)
        self.listening = self._listen()

    def _listen(self) -> bool:
        if self.server.listen(self.name):
            return True
        # 上次异常退出可能留下同名套接字/命名管道，清理后重试一次。
        QLocalServer.removeServer(self.name)
        return self.server.listen(self.name)

    def _on_new_connection(self) -> None:
        while self.server.hasPendingConnections():
            connection = self.server.nextPendingConnection()
            if connection is None:
                continue
            connection.readyRead.connect(
                lambda conn=connection: self._read(conn)
            )
            connection.disconnected.connect(connection.deleteLater)
            if connection.bytesAvailable():
                self._read(connection)

    def _read(self, connection) -> None:
        try:
            data = bytes(connection.readAll()).strip()
        except RuntimeError:
            return
        if not data:
            return
        try:
            connection.disconnectFromServer()
        except RuntimeError:
            pass
        self.activated.emit()

    def close(self) -> None:
        """停止监听并清理名称，供退出或测试使用。"""
        try:
            self.server.close()
        except RuntimeError:
            pass
        QLocalServer.removeServer(self.name)
        self.listening = False


__all__ = ["SingleInstanceServer", "notify_running", "server_name"]
