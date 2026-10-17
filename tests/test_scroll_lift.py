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

"""滚动减量抽控制器测试（离屏 Qt）。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton

from lib.ScrollLift import ScrollLiftController
from lib.ScrollMulti import ScrollMultiController


class FakeView:
    def __init__(self):
        self.names = []
        self.message = ""
        self.locked = None

    def begin_round(self, pool_names, quantity):
        self.locked = (tuple(pool_names), quantity)

    def clear_round(self):
        self.locked = None

    def set_names(self, names, use_lock=True):
        self.names = [str(name) for name in names]

    def set_message(self, text):
        self.message = str(text)


class ScrollLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def make_controller(self):
        self.view = FakeView()
        self.button = QPushButton()
        self.results = []
        controller = ScrollLiftController(
            self.view,
            self.button,
            {"0": "甲", "1": "乙", "2": "丙", "3": "丁"},
            on_result=lambda result, meta: self.results.append(result),
            rate=1000,
        )
        controller.set_quantity(2)
        return controller

    def test_draw_removes_selected_from_pool(self):
        controller = self.make_controller()
        controller.start()
        controller.timer.stop()
        controller.stop_next()
        controller.stop_next()
        self.assertEqual(len(self.view.names), 2)
        self.assertEqual(len(controller.lift_pool), 2)
        self.assertEqual(self.results[-1]["mode"], "ScrollLift")
        self.assertEqual(len(self.results[-1]["outdict"]), 2)
        self.assertEqual(len(self.results[-1]["Liftdict"]), 2)
        self.assertEqual(self.results[-1]["quantity"]["selected"], 2)

    def test_reset_restores_full_pool(self):
        controller = self.make_controller()
        controller.start()
        controller.timer.stop()
        controller.stop_next()
        controller.stop_next()
        self.assertEqual(len(controller.lift_pool), 2)
        controller.reset()
        self.assertEqual(len(controller.lift_pool), 4)

    def test_quantity_exceeding_pool_is_clamped(self):
        controller = self.make_controller()
        controller.set_quantity(99)
        warnings = []
        controller.on_warning = warnings.append
        controller.start()
        controller.timer.stop()
        self.assertEqual(controller.total, 4)
        self.assertEqual(warnings, [4])

    def test_scroll_multi_still_uses_full_roster_after_round(self):
        view = FakeView()
        button = QPushButton()
        controller = ScrollMultiController(
            view, button, {"0": "甲", "1": "乙"}, on_result=lambda result, meta: None, rate=1000
        )
        controller.set_quantity(2)
        controller.start()
        controller.timer.stop()
        controller.stop_next()
        controller.stop_next()
        self.assertEqual(controller.total, 2)


if __name__ == "__main__":
    unittest.main()
