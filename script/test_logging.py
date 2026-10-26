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

"""日志等级与查看器高亮测试。"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import StateManager
from lib.TextViewer import highlight_log_text


class LoggingTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = Path(self.temp_dir.name) / "log.log"
        self.original_records = list(StateManager.SESSION_LOG_RECORDS)
        self.original_level = StateManager.CURRENT_LOG_LEVEL
        StateManager.SESSION_LOG_RECORDS.clear()

    def tearDown(self):
        StateManager.SESSION_LOG_RECORDS[:] = self.original_records
        StateManager.CURRENT_LOG_LEVEL = self.original_level
        self.temp_dir.cleanup()

    def test_level_filters_file_but_not_session(self):
        with mock.patch.object(StateManager, "LOG_PATH", self.log_path):
            StateManager.configure_logging("WARNING")
            StateManager.log("DEBUG", "unit_debug", result="hidden")
            StateManager.log("ERROR", "unit_error", result="visible")
        text = StateManager.session_log_text()
        self.assertIn("action=unit_debug", text)
        self.assertIn("action=unit_error", text)
        content = self.log_path.read_text(encoding="utf-8")
        self.assertNotIn("unit_debug", content)
        self.assertIn("unit_error", content)

    def test_log_text_highlights_level_and_escapes_html(self):
        html = highlight_log_text(
            "2026-10-25 12:00:00 [INFO] action=test <script>alert(1)</script>"
        )
        self.assertIn('color:', html)
        self.assertIn("[INFO]", html)
        self.assertNotIn("<script>", html)


if __name__ == "__main__":
    unittest.main()
