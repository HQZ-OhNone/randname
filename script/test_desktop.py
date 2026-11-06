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

"""外部链接打开与平滑滚动辅助测试。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QTextBrowser

from lib.Scrolling import SCROLLBAR_STYLE, has_touch_screen, install_smooth_scrolling
from lib.UrlOpener import browser_commands, open_url


class UrlOpenerTests(unittest.TestCase):
    def test_browser_commands_per_platform(self):
        self.assertEqual(browser_commands("u", "win32")[0][0], "cmd")
        self.assertEqual(browser_commands("u", "darwin")[0][0], "open")
        self.assertEqual(browser_commands("u", "linux")[0][0], "xdg-open")

    def test_desktop_opener_wins(self):
        calls = []
        result = open_url(
            "https://example.test",
            platform="linux",
            desktop=lambda url: calls.append(url) or True,
            spawn=lambda command: calls.append(command),
        )
        self.assertTrue(result)
        self.assertEqual(calls, ["https://example.test"])

    def test_command_fallback(self):
        calls = []
        result = open_url(
            "https://example.test",
            platform="linux",
            desktop=lambda url: False,
            spawn=lambda command: calls.append(command),
        )
        self.assertTrue(result)
        self.assertEqual(calls, [["xdg-open", "https://example.test"]])

    def test_failure_returns_false(self):
        def fail(_command):
            raise OSError("missing")

        def fail_opener(_url):
            raise OSError("missing")

        self.assertFalse(
            open_url(
                "https://example.test",
                platform="win32",
                desktop=lambda url: False,
                opener=fail_opener,
                spawn=fail,
            )
        )

    def test_invalid_url(self):
        self.assertFalse(open_url(""))
        self.assertFalse(open_url(None))


class ScrollingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_touch_detection_is_boolean(self):
        self.assertIsInstance(has_touch_screen(), bool)

    def test_install_sets_scrollbar_style_and_gesture(self):
        view = QTextBrowser()
        self.assertTrue(install_smooth_scrolling(view, True))
        self.assertEqual(view.styleSheet(), SCROLLBAR_STYLE)
        self.assertEqual(view.verticalScrollBar().singleStep(), 24)

    def test_disabled_skips_gesture_but_keeps_style(self):
        view = QTextBrowser()
        self.assertFalse(install_smooth_scrolling(view, False))
        self.assertEqual(view.styleSheet(), SCROLLBAR_STYLE)


if __name__ == "__main__":
    unittest.main()
