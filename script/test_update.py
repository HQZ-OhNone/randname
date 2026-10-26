"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

"""检查更新版本比较与按钮状态测试。"""

import os
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from lib.UpdateDialog import UpdateDialog, is_newer_version, parse_version, update_timeout_ms


class UpdateVersionTests(unittest.TestCase):
    def test_parse_version(self):
        self.assertEqual(parse_version("v3.9.2"), (3, 9, 2))
        self.assertEqual(parse_version("3.10.0-beta"), (3, 10, 0))
        self.assertEqual(parse_version("release-4"), (4,))
        self.assertEqual(parse_version(""), ())
        self.assertEqual(parse_version(None), ())

    def test_newer_version(self):
        self.assertTrue(is_newer_version("v3.9.2", "3.9.1"))
        self.assertTrue(is_newer_version("3.10.0", "3.9.9"))
        self.assertFalse(is_newer_version("v3.9.1", "3.9.1"))
        self.assertFalse(is_newer_version("v3.9.0", "3.9.1"))
        self.assertFalse(is_newer_version("invalid", "3.9.1"))

    def test_update_timeout_from_config(self):
        self.assertEqual(update_timeout_ms({}), 15000)
        self.assertEqual(update_timeout_ms({"update": {"timeout_ms": 8000}}), 8000)
        self.assertEqual(update_timeout_ms({"update": {"timeout_ms": 1}}), 1000)
        self.assertEqual(update_timeout_ms({"update": {"timeout_ms": 999999}}), 120000)
        self.assertEqual(update_timeout_ms({"update": {"timeout_ms": "bad"}}), 15000)


class UpdateDialogStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_update_button_only_enabled_for_available(self):
        dialog = UpdateDialog(
            None,
            history_path=Path("doc/history.md"),
            translate=lambda key, **values: key,
            config={},
        )
        self.assertFalse(dialog.ui.updateButton.isEnabled())
        dialog._finish("update.latest")
        self.assertFalse(dialog.ui.updateButton.isEnabled())
        dialog._finish("update.failed")
        self.assertFalse(dialog.ui.updateButton.isEnabled())
        dialog._finish("update.available")
        self.assertTrue(dialog.ui.updateButton.isEnabled())
        dialog.close()


if __name__ == "__main__":
    unittest.main()
