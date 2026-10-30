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

"""数量滑杆回归测试（离屏 Qt）。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

import main
from lib import LanguageManager, ScrollLift, ScrollMulti, StateManager, ThemeManager, importnames
from lib import WindowTheme
from lib import ui_main, ui_widgetlift, ui_widgetmulti, ui_widgetscrolllift, ui_widgetscrollmulti
from lib.BackgroundWidget import BackgroundWidget
from lib.OutputView import OutputView, SlotOutputView
from lib.TextViewer import TextViewerDialog


def _install_main_globals():
    """MainWindow 依赖 main() 内延迟导入的模块，测试时手动注入。"""
    main.ThemeManager = ThemeManager
    main.LanguageManager = LanguageManager
    main.importnames = importnames
    main.StateManager = StateManager
    main.OutputView = OutputView
    main.SlotOutputView = SlotOutputView
    main.TextViewerDialog = TextViewerDialog
    main.BackgroundWidget = BackgroundWidget
    main.WindowTheme = WindowTheme
    main.ScrollMulti = ScrollMulti
    main.ScrollLift = ScrollLift
    main.ui_main = ui_main
    main.ui_widgetmulti = ui_widgetmulti
    main.ui_widgetlift = ui_widgetlift
    main.ui_widgetscrollmulti = ui_widgetscrollmulti
    main.ui_widgetscrolllift = ui_widgetscrolllift


class QuantitySliderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _install_main_globals()
        cls.app = QApplication.instance() or QApplication([])
        cls.themes = ThemeManager.discover_themes()
        cls.languages, _, _ = LanguageManager.load_languages()

    def setUp(self):
        self.window = main.MainWindow(
            self.themes,
            "randname-dark",
            self.languages,
            "zh_TW",
            importnames.rosters,
            importnames.active_roster,
        )

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_multi_slider_updates_quantity(self):
        target = min(3, len(self.window.names))
        self.window.multi_quantity_slider.setValue(target)
        self.app.processEvents()
        self.assertEqual(self.window.multi_quantity, target)
        self.assertEqual(self.window.multi_quantity_label.text(), str(target))

    def test_lift_slider_updates_quantity(self):
        target = min(2, len(self.window.names))
        self.window.lift_quantity_slider.setValue(target)
        self.app.processEvents()
        self.assertEqual(self.window.lift_quantity, target)
        self.assertEqual(self.window.lift_quantity_label.text(), str(target))

    def test_buttons_still_work(self):
        self.window.multi_quantity_slider.setValue(1)
        self.window.multi_up_button.click()
        self.app.processEvents()
        self.assertEqual(self.window.multi_quantity, 2)
        self.window.multi_down_button.click()
        self.app.processEvents()
        self.assertEqual(self.window.multi_quantity, 1)

    def test_theme_menu_has_dark_and_light_columns(self):
        from PySide6.QtWidgets import QLabel, QToolButton

        actions = self.window.ui_main.menu_theme.actions()
        self.assertEqual(len(actions), 1)
        container = actions[0].defaultWidget()
        self.assertIsNotNone(container)
        headers = [label.text() for label in container.findChildren(QLabel)]
        self.assertEqual(headers, ["深色", "淺色"])
        buttons = container.findChildren(QToolButton)
        self.assertEqual(len(buttons), len(self.themes))
        checked = [button.text() for button in buttons if button.isChecked()]
        self.assertEqual(len(checked), 1)


if __name__ == "__main__":
    unittest.main()
