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

"""输出框自适应测试（离屏 Qt）。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel

from lib.OutputView import OutputView, pack_names


class OutputFitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def make_view(self, width=700, height=400):
        label = QLabel()
        label.resize(width, height)
        view = OutputView(label, {"ui": {
            "display_font_size": 30,
            "display_min_font_size": 12,
            "display_font_step": 1,
            "display_padding": 8,
            "display_line_spacing": 1.0,
        }}, 30)
        return label, view

    def test_short_names_stay_on_one_line(self):
        label, view = self.make_view()
        view.set_names(["张三", "李四"], use_lock=False)
        self.assertNotIn("\n", label.text())
        self.assertGreaterEqual(label.font().pointSizeF(), 30)

    def test_size_policy_keeps_output_wide(self):
        from PySide6.QtWidgets import QSizePolicy
        label, _view = self.make_view()
        policy = label.sizePolicy()
        self.assertEqual(policy.horizontalPolicy(), QSizePolicy.Policy.Expanding)
        self.assertEqual(policy.verticalPolicy(), QSizePolicy.Policy.Expanding)
        self.assertEqual(policy.horizontalStretch(), 160)
        self.assertTrue(label.wordWrap())

    def test_long_names_are_wrapped_or_shrunk(self):
        label, view = self.make_view()
        view.set_names(["非常非常非常长的名字"] * 20, use_lock=False)
        self.assertTrue("\n" in label.text() or label.font().pointSizeF() < 30)
        self.assertGreaterEqual(label.font().pointSizeF(), 12)

    def test_round_lock_keeps_font_stable(self):
        label, view = self.make_view()
        pool = ["短", "很长很长很长的名字"]
        view.begin_round(pool, 2)
        view.set_names(pool)
        first = label.font().pointSizeF()
        view.set_names(["短", "短"])
        second = label.font().pointSizeF()
        self.assertEqual(first, second)

    def test_pack_names_never_returns_empty(self):
        from PySide6.QtGui import QFontMetrics, QFont
        metrics = QFontMetrics(QFont())
        self.assertEqual(pack_names([], metrics, 100), [""])


if __name__ == "__main__":
    unittest.main()
