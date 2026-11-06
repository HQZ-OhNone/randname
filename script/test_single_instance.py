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

"""单实例唤醒测试（离屏 Qt）。"""

import os
import unittest
import uuid

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from lib.SingleInstance import SingleInstanceServer, notify_running, server_name
from lib.version import APP_VERSION


class SingleInstanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_name_depends_on_version_not_directory(self):
        self.assertIn(APP_VERSION, server_name())
        self.assertEqual(server_name(), server_name())
        self.assertEqual(
            server_name("3.11.2", "user"), server_name("3.11.2", "user")
        )
        self.assertNotEqual(
            server_name("3.11.1", "user"), server_name("3.11.2", "user")
        )

    def test_notify_without_server_returns_false(self):
        self.assertFalse(notify_running(f"randname-missing-{uuid.uuid4().hex}", 100))

    def test_notify_activates_listening_server(self):
        name = f"randname-test-{uuid.uuid4().hex}"
        server = SingleInstanceServer(name=name)
        self.assertTrue(server.listening)
        received = []
        server.activated.connect(lambda: received.append(True))
        self.assertTrue(notify_running(name))
        for _ in range(10):
            self.app.processEvents()
        self.assertEqual(received, [True])
        server.close()
        self.assertFalse(notify_running(name, 100))


if __name__ == "__main__":
    unittest.main()
