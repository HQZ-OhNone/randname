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
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication

import main
from lib import LanguageManager, ScrollLift, ScrollMulti, StateManager, ThemeManager, importnames
from lib import Lift as lift_module
from lib import Multi as multi_module
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
    main.multi_module = multi_module
    main.lift_module = lift_module
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

    def test_initialize_does_not_show_confirmation(self):
        from unittest import mock
        from PySide6.QtWidgets import QMessageBox

        window = self.window
        window.multi_quantity = 3
        with mock.patch.object(
            main.StateManager, "reset_memory", return_value={"last_results": {}}
        ):
            with mock.patch.object(
                QMessageBox, "question", side_effect=AssertionError("confirm dialog")
            ):
                window._on_initialize()
        self.assertEqual(window.multi_quantity, 1)
        self.assertEqual(
            window.status_message_label.text(), window._t("state.initialized")
        )

    def test_mode_switch_resets_display_keeps_lift_pool_and_quantity(self):
        window = self.window
        window.multi_result_names = ["甲"]
        window.lift_quantity = 3
        window._set_quantity_label(window.lift_quantity_label, 3)
        window.lift_current_dict = {"a": "甲"}
        window._show_multi_page()
        self.assertEqual(window.multi_result_names, [])
        self.assertEqual(window.current_mode, "Multi")
        window._show_lift_page()
        self.assertEqual(window.current_mode, "Lift")
        self.assertEqual(window.lift_current_dict, {"a": "甲"})
        self.assertEqual(window.lift_quantity, 3)
        self.assertEqual(window.lift_quantity_label.text(), "3")

    def test_mode_switch_keeps_scroll_lift_pool(self):
        window = self.window
        controller = window.scroll_lift_controller
        self.assertIsNotNone(controller)
        controller.lift_pool = {"x": "X"}
        window._show_scroll_lift_page()
        self.assertEqual(controller.lift_pool, {"x": "X"})

    def test_buttons_still_work(self):
        self.window.multi_quantity_slider.setValue(1)
        self.window.multi_up_button.click()
        self.app.processEvents()
        self.assertEqual(self.window.multi_quantity, 2)
        self.window.multi_down_button.click()
        self.app.processEvents()
        self.assertEqual(self.window.multi_quantity, 1)

    @staticmethod
    def _wheel_button(button, delta):
        event = QWheelEvent(
            QPointF(1, 1), QPointF(1, 1), QPoint(0, 0), QPoint(0, int(delta)),
            Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase, False,
        )
        QApplication.sendEvent(button, event)

    def test_multi_button_wheel_up_draws_and_down_does_nothing(self):
        window = self.window
        window._set_quantity(main.MODE_MULTI, 1, log=False)
        window.multi_result_names = []
        self._wheel_button(window.multi_button, 120)
        self.app.processEvents()
        self.assertTrue(window.multi_result_names)

        window.multi_result_names = []
        self._wheel_button(window.multi_button, -120)
        self.app.processEvents()
        self.assertEqual(window.multi_result_names, [])

    def test_multi_button_wheel_accumulates_notches(self):
        window = self.window
        window.multi_result_names = []
        self._wheel_button(window.multi_button, 60)
        self.app.processEvents()
        self.assertEqual(window.multi_result_names, [])
        self._wheel_button(window.multi_button, 60)
        self.app.processEvents()
        self.assertTrue(window.multi_result_names)

    def test_quantity_adjustment_log_is_coalesced(self):
        window = self.window
        window._set_quantity(main.MODE_MULTI, 1, log=False)
        window._pending_quantity_log.clear()
        with mock.patch.object(main.StateManager, "log") as log_mock:
            for _ in range(5):
                window._adjust_quantity(main.MODE_MULTI, 1)
            log_mock.assert_not_called()
            window._flush_quantity_log()
            log_mock.assert_called_once()
            args = log_mock.call_args.args
            self.assertEqual(args[1], "quantity")
            self.assertIn("Multi=", log_mock.call_args.kwargs["result"])

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
