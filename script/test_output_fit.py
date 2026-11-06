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

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QLabel

from lib.OutputView import OutputView, SlotOutputView, choose_slot_layout, pack_names


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

    def test_output_expands_only_when_min_font_does_not_fit(self):
        from PySide6.QtWidgets import QGridLayout, QLabel as _QLabel, QWidget

        page = QWidget()
        page.resize(480, 220)
        grid = QGridLayout(page)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)
        top = QLabel("top")
        bottom = QLabel("bottom")
        grid.addWidget(top, 0, 0)
        label = QLabel()
        label.setWordWrap(True)
        grid.addWidget(label, 1, 0)
        grid.addWidget(bottom, 2, 0)
        view = OutputView(label, {"ui": {
            "display_font_size": 30,
            "display_min_font_size": 15,
            "display_font_step": 1,
            "display_padding": 8,
            "display_line_spacing": 1.0,
        }}, 30)
        page.show()
        self.app.processEvents()

        view.set_names(["短名字", "短名字"], use_lock=False)
        self.app.processEvents()
        self.assertFalse(view._expansion.expanded)

        many = [f"非常非常非常长的名字{i:02d}" for i in range(40)]
        view.set_names(many, use_lock=False)
        self.app.processEvents()
        self.assertTrue(view._expansion.expanded)
        self.assertEqual(grid.rowStretch(1), 1)
        self.assertGreater(label.height(), 0)

        view.set_names(["短名字", "短名字"], use_lock=False)
        self.app.processEvents()
        self.assertFalse(view._expansion.expanded)
        self.assertEqual(grid.rowStretch(1), 0)
        page.close()

    def test_output_layout_survives_stylesheet_change(self):
        from PySide6.QtWidgets import QGridLayout, QWidget

        page = QWidget()
        page.resize(520, 460)
        grid = QGridLayout(page)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)
        top = QWidget()
        bottom = QWidget()
        label = QLabel()
        label.setWordWrap(True)
        grid.addWidget(top, 0, 0)
        grid.addWidget(label, 1, 0)
        grid.addWidget(bottom, 2, 0)
        page.show()
        self.app.processEvents()
        view = OutputView(label, {"ui": {
            "display_font_size": 30,
            "display_min_font_size": 15,
            "display_font_step": 1,
            "display_padding": 8,
            "display_line_spacing": 1.0,
        }}, 30)
        names = [f"非常非常非常长的名字{i:02d}" for i in range(40)]
        view.set_names(names, use_lock=False)
        for _ in range(4):
            self.app.processEvents()
        self.assertTrue(view._expansion.expanded)
        before = len(label.text().splitlines())
        self.app.setStyleSheet("QLabel { border: 2px solid red; padding: 8px; }")
        for _ in range(8):
            self.app.processEvents()
        self.assertTrue(view._expansion.expanded)
        self.assertEqual(len(label.text().splitlines()), before)
        self.app.setStyleSheet("")
        page.close()

    def test_slot_layout_survives_stylesheet_change(self):
        from PySide6.QtWidgets import QGridLayout, QWidget

        page = QWidget()
        page.resize(520, 460)
        grid = QGridLayout(page)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)
        top = QWidget()
        bottom = QWidget()
        label = QLabel()
        grid.addWidget(top, 0, 0)
        grid.addWidget(label, 1, 0)
        grid.addWidget(bottom, 2, 0)
        page.show()
        self.app.processEvents()
        view = SlotOutputView(label, {"ui": {
            "display_font_size": 30,
            "display_min_font_size": 12,
            "display_font_step": 1,
            "display_padding": 8,
            "display_line_spacing": 1.0,
        }}, 30)
        names = [f"学生{i:02d}号" for i in range(1, 46)]
        view.begin_round(names, 45)
        view.set_names(names)
        for _ in range(6):
            self.app.processEvents()
        self.assertTrue(view._expansion.expanded)
        before = (view._columns, view._rows)
        self.app.setStyleSheet("QLabel { border: 2px solid red; padding: 8px; }")
        for _ in range(10):
            self.app.processEvents()
        self.assertTrue(view._expansion.expanded)
        self.assertEqual((view._columns, view._rows), before)
        self.app.setStyleSheet("")
        page.close()

    def test_refresh_layout_recomputes_slot_grid(self):
        label, view = self.make_slot_view()
        names = [f"学生{i:02d}号" for i in range(1, 13)]
        view.begin_round(names, 12)
        view.set_names(names)
        self.app.processEvents()
        view._columns = 0
        view._rows = 0
        view.refresh_layout()
        for _ in range(3):
            self.app.processEvents()
        self.assertGreater(view._columns, 0)
        self.assertGreater(view._rows, 0)

    def test_output_expansion_is_noop_without_grid_layout(self):
        label, view = self.make_view()
        view.set_names([f"名字{i}" for i in range(60)], use_lock=False)
        self.assertFalse(view._expansion.expanded)

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

    def make_slot_view(self, width=700, height=400):
        label = QLabel()
        label.resize(width, height)
        view = SlotOutputView(label, {"ui": {
            "display_font_size": 30,
            "display_min_font_size": 12,
            "display_font_step": 1,
            "display_padding": 8,
            "display_line_spacing": 1.0,
        }}, 30)
        label.show()
        self.app.processEvents()
        return label, view

    def test_six_names_use_two_rows(self):
        _label, view = self.make_slot_view()
        view.begin_round(["姓名"] * 6, 6)
        view.set_names(["张三", "李四", "王五", "赵六", "周七", "吴八"])
        self.assertEqual((view._columns, view._rows), (3, 2))
        self.assertEqual(len(view.slot_geometries()), 6)

    def test_rolling_text_keeps_slot_positions(self):
        _label, view = self.make_slot_view()
        view.begin_round(["姓名"] * 6, 6)
        view.set_names(["张三", "李四", "王五", "赵六", "周七", "吴八"])
        before = view.slot_geometries()
        view.set_names(["甲", "乙", "丙", "丁", "戊", "己"])
        self.assertEqual(before, view.slot_geometries())

    def test_long_name_relayouts_and_stays_fixed(self):
        _label, view = self.make_slot_view()
        view.begin_round(["姓名"] * 6, 6)
        view.set_names(["张三", "李四", "王五", "赵六", "周七", "吴八"])
        before = (view._columns, view._rows, view._layout_point_size)
        view.set_names(["张三", "李四", "王五", "赵六", "周七", "非常非常非常长的名字"])
        after = (view._columns, view._rows, view._layout_point_size)
        self.assertNotEqual(before, after)
        locked = view.slot_geometries()
        view.set_names(["张三", "李四", "王五", "赵六", "周七", "短"])
        self.assertEqual(locked, view.slot_geometries())

    def test_clear_round_resets_layout(self):
        _label, view = self.make_slot_view()
        view.begin_round(["姓名"] * 6, 6)
        view.set_names(["张三", "李四", "王五", "赵六", "周七", "非常非常非常长的名字"])
        self.assertNotEqual((view._columns, view._rows), (3, 2))
        view.clear_round()
        view.set_names(["张三", "李四", "王五", "赵六", "周七", "吴八"])
        self.assertEqual((view._columns, view._rows), (3, 2))
        self.assertEqual(view._layout_point_size, 30)

    def test_choose_slot_layout_prefers_target_rows_at_same_font(self):
        columns, rows, size = choose_slot_layout(
            ["张三", "李四", "王五", "赵六", "周七", "吴八"],
            700, 400, QFont(), 30, 12, 1, 8, 6,
        )
        self.assertEqual((columns, rows), (3, 2))
        self.assertEqual(size, 30)

    def test_compact_grid_does_not_span_large_screen(self):
        _label, view = self.make_slot_view(1600, 900)
        view.begin_round(["姓名"] * 6, 6)
        view.set_names(["张三", "李四", "王五", "赵六", "周七", "吴八"])
        rects = view.slot_geometries()
        left = min(rect.left() for rect in rects)
        right = max(rect.right() for rect in rects)
        self.assertLess(right - left, 1600 * 0.6)

    def test_choose_slot_layout_handles_missing_size(self):
        columns, rows, size = choose_slot_layout(["张三"], 1, 1, QFont(), 30, 12, 1, 8, 1)
        self.assertEqual((columns, rows, size), (1, 1, 30))


if __name__ == "__main__":
    unittest.main()
