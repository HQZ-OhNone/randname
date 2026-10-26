"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; see the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
"""

"""记忆结果读写与导入导出测试。"""

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

    def test_default_structure_only_contains_results(self):
        memory = StateManager.load_memory()
        self.assertNotIn("preferences", memory)
        self.assertNotIn("loaded_config", memory)
        self.assertIn("ScrollLift", memory["last_results"])
        self.assertNotIn("ScrollSingle", memory["last_results"])

    def test_reset_memory_clears_results(self):
        StateManager.save_memory({
            "last_results": {
                "Multi": {"result": {"outdict": {"0": {"name": "张三"}}}},
                "Lift": {"result": {}},
                "ScrollMulti": {"result": {}},
                "ScrollLift": {"result": {}},
            }
        })
        memory = StateManager.reset_memory()
        self.assertTrue(all(value is None for value in memory["last_results"].values()))

    def test_old_preferences_are_dropped(self):
        StateManager.MEMORY_PATH.write_text(json.dumps({
            "preferences": {
                "theme": "amber-dark",
                "language": "zh_TW",
                "mode": "ScrollLift",
                "window": {"width": 1200, "height": 760, "maximized": False},
            },
            "loaded_config": {"app": {"theme": "blue-dark"}},
            "last_results": {
                "Multi": {"result": {"outdict": {"0": {"name": "张三"}}}},
            },
        }), encoding="utf-8")
        memory = StateManager.load_memory()
        self.assertNotIn("preferences", memory)
        self.assertNotIn("loaded_config", memory)
        self.assertEqual(
            memory["last_results"]["Multi"]["result"]["outdict"]["0"]["name"],
            "张三",
        )

    def test_import_keeps_only_results(self):
        source = Path(self.tempdir.name) / "import.json"
        source.write_text(json.dumps({
            "preferences": {"theme": "amber-dark"},
            "last_results": {
                "Multi": {
                    "result": {
                        "mode": "Multi",
                        "outdict": {"0": {"code": "1", "name": "张三"}},
                    }
                }
            },
        }), encoding="utf-8")
        seen = {}

        def callback(content):
            seen.update(content)

        StateManager.import_memory(source, apply_callback=callback)
        self.assertNotIn("preferences", seen)
        self.assertEqual(
            seen["last_results"]["Multi"]["result"]["outdict"]["0"]["name"],
            "张三",
        )

    def test_export_writes_memory_results(self):
        StateManager.load_memory()
        destination = Path(self.tempdir.name) / "export.json"
        StateManager.export_memory(destination)
        exported = json.loads(destination.read_text(encoding="utf-8"))
        self.assertIn("last_results", exported)
        self.assertNotIn("preferences", exported)


if __name__ == "__main__":
    unittest.main()
