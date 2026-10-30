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

from lib.UpdateDialog import (
    UpdateDialog,
    clean_release_body,
    is_newer_version,
    latest_release_section,
    parse_version,
    update_timeout_ms,
)


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


class ReleaseNoteTests(unittest.TestCase):
    def test_latest_section_uses_first_version(self):
        text = """# Release Notes

<!-- 注释 -->
## v3.11.1 — 2026-10-30

- 最新

## v3.11.0 — 2026-10-27

- 旧版
"""
        section = latest_release_section(text)
        self.assertTrue(section.startswith("- 最新"))
        self.assertNotIn("v3.11.0", section)
        self.assertNotIn("注释", section)

    def test_latest_section_without_heading_returns_text(self):
        self.assertEqual(latest_release_section("纯文本"), "纯文本")

    def test_clean_release_body_removes_footer(self):
        body = "### 中文\n\n- 内容\n\n---\nBuilt from commit: abc123\n"
        self.assertEqual(clean_release_body(body), "### 中文\n\n- 内容")


class UpdateDialogStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_update_button_only_enabled_for_available(self):
        dialog = UpdateDialog(
            None,
            notes_path=Path("doc/releasenote.md"),
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

    def test_dialog_shows_local_release_note(self):
        dialog = UpdateDialog(
            None,
            notes_path=Path("doc/releasenote.md"),
            translate=lambda key, **values: key,
            config={},
        )
        text = dialog.ui.notesEdit.toPlainText()
        self.assertTrue(text.strip())
        self.assertNotIn("Built from commit", text)
        self.assertNotIn("## v", text)
        dialog.close()


if __name__ == "__main__":
    unittest.main()
