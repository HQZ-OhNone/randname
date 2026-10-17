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

"""记忆与偏好读写测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from lib import StateManager


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.old_memory = StateManager.MEMORY_PATH
        StateManager.MEMORY_PATH = Path(self.tempdir.name) / "memory.json"

    def tearDown(self):
        StateManager.MEMORY_PATH = self.old_memory
        self.tempdir.cleanup()

    def test_default_structure_created(self):
        memory = StateManager.load_memory()
        self.assertIn("preferences", memory)
        self.assertIn("ScrollLift", memory["last_results"])
        self.assertNotIn("ScrollSingle", memory["last_results"])

    def test_preferences_round_trip(self):
        StateManager.save_preferences({
            "theme": "amber-dark",
            "language": "zh_TW",
            "mode": "ScrollLift",
            "quantities": {"scroll_lift": 4},
            "window": {"width": 1200, "height": 760, "maximized": False},
        })
        prefs = StateManager.load_preferences()
        self.assertEqual(prefs["theme"], "amber-dark")
        self.assertEqual(prefs["language"], "zh_TW")
        self.assertEqual(prefs["mode"], "ScrollLift")
        self.assertEqual(prefs["quantities"]["scroll_lift"], 4)
        self.assertEqual(prefs["window"]["width"], 1200)

    def test_legacy_loaded_config_is_used(self):
        StateManager.MEMORY_PATH.write_text(json.dumps({
            "loaded_config": {
                "app": {
                    "theme": "blue-dark",
                    "language": "en_US",
                    "roster": "class_1",
                    "default_mode": "Lift",
                }
            },
            "last_results": {},
        }), encoding="utf-8")
        prefs = StateManager.load_preferences()
        self.assertEqual(prefs["theme"], "blue-dark")
        self.assertEqual(prefs["language"], "en_US")
        self.assertEqual(prefs["mode"], "Lift")

    def test_import_extracts_result_and_keeps_preferences(self):
        source = Path(self.tempdir.name) / "import.json"
        source.write_text(json.dumps({
            "last_results": {
                "Multi": {
                    "result": {
                        "mode": "Multi",
                        "outdict": {"0": {"code": "1", "name": "张三"}},
                    }
                }
            }
        }), encoding="utf-8")
        seen = {}

        def callback(content):
            seen.update(content)

        StateManager.import_memory(
            source,
            apply_callback=callback,
            preferences={"theme": "green-dark"},
        )
        self.assertIn("preferences", seen)
        self.assertEqual(seen["preferences"]["theme"], "green-dark")
        self.assertEqual(
            seen["last_results"]["Multi"]["result"]["outdict"]["0"]["name"],
            "张三",
        )


if __name__ == "__main__":
    unittest.main()
