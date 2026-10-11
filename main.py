"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

print(r"""
randname Copyright(C) 2026 HQZ-OhNone
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute
it under certain conditions; check GPLv3 for details.

                      _                            
  _ __ __ _ _ __   __| |_ __   __ _ _ __ ___   ___  
 | '__/ _` | '_ \ / _` | '_ \ / _` | '_ ` _ \ / _ \ 
 | | | (_| | | | | (_| | | | | (_| | | | | | |  __/ 
 |_|  \__,_|_| |_|\__,_|_| |_|\__,_|_| |_| |_|\___| 
---HQZ-OhNone <ohnone_hqz@outlook.com>
""", end="\n\n")


import logging
import sys
import tomllib
from pathlib import Path

from PySide6.QtCore import QElapsedTimer, QTimer, QUrl, Qt
from PySide6.QtGui import QAction, QActionGroup, QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QMenu,
    QPlainTextEdit,
    QTextBrowser,
    QSplashScreen,
    QVBoxLayout,
    QWidget,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

ROOT_DIR = Path(__file__).resolve().parent
UI_DIR = ROOT_DIR / "ui"
DEFAULT_REPO_URL = "https://www.github.com/HQZ-OhNone/randname"


def _configured_path(config: dict, section: str, key: str, default: str) -> Path:
    values = config.get(section, {}) if isinstance(config, dict) else {}
    value = values.get(key, default) if isinstance(values, dict) else default
    selected = Path(value) if isinstance(value, str) and value else Path(default)
    return selected if selected.is_absolute() else ROOT_DIR / selected


def _bootstrap_config() -> tuple[dict, list[str]]:
    warnings = []
    for path in (ROOT_DIR / "config" / "config.toml", ROOT_DIR / ".config.default.toml"):
        try:
            with path.open("rb") as config_file:
                config = tomllib.load(config_file)
            if path.name == ".config.default.toml":
                warnings.append("config/config.toml")
            return config, warnings
        except FileNotFoundError:
            warnings.append(str(path.relative_to(ROOT_DIR)))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            warnings.append(f"{path.relative_to(ROOT_DIR)}: {exc}")
    return {}, warnings


def _configured_size(section: dict, screen_width: int, screen_height: int, *, splash=False) -> tuple[int, int]:
    if section.get("size_mode") == "fixed":
        width = section.get("width")
        height = section.get("height")
        if isinstance(width, int) and width > 0 and isinstance(height, int) and height > 0:
            return width, height
    if splash:
        return max(1, int(screen_width * 0.25)), max(1, int(screen_height * 0.25))
    aspect = section.get("aspect_ratio", 1.5)
    if not isinstance(aspect, (int, float)) or isinstance(aspect, bool) or aspect <= 0:
        aspect = 1.5
    width = min(screen_width * 0.75, screen_height * 0.75 * aspect)
    return max(1, int(width)), max(1, int(width / aspect))


def _rate_from_config(config: dict | None, section: str, default: int = 30) -> int:
    """Read a positive ticks-per-second ``rate`` from a config section."""
    values = config.get(section, {}) if isinstance(config, dict) else {}
    rate = values.get("rate", default) if isinstance(values, dict) else default
    try:
        value = int(rate)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def _startup_file_check(config: dict | None = None) -> tuple[list[str], list[str]]:
    help_directory = _configured_path(config or {}, "paths", "help_directory", "doc")
    recoverable = (
        ROOT_DIR / "config" / "config.toml",
        ROOT_DIR / ".config.default.toml",
        ROOT_DIR / "config" / "name.toml",
        ROOT_DIR / ".name.default.toml",
        ROOT_DIR / "config" / "language.toml",
        ROOT_DIR / "config" / "theme.toml",
        _configured_path(config or {}, "assets", "icon", "ui/randname1.png"),
        _configured_path(config or {}, "assets", "splash_image", "ui/randname-start_v3.6.png"),
        _configured_path(config or {}, "paths", "license_file", "doc/gpl-3.0.md"),
        help_directory / "help_en_US.md",
    )
    warnings = [str(path.relative_to(ROOT_DIR)) for path in recoverable if not path.is_file()]
    return warnings, []


"""
主窗口

整个程序只有一个 MainWindow。

MainWindow 负责：

1. 菜单栏
2. 工具栏
3. 状态栏
4. 页面管理（QStackedWidget）
5. 页面切换
6. 打开各种 Dialog
"""


# 注意：UI 不再在运行时从 .ui 动态加载
# 已改为在构建前用 pyside6-uic 编译 .ui 为 Python 模块，放在 lib/ 目录下
# 因此不需要 load_ui 函数（也避免运行时依赖 ui/ 目录）


class MainWindow(QMainWindow):
    def __init__(
        self,
        themes=None,
        selected_theme="",
        languages=None,
        selected_language="en_US",
        rosters=None,
        selected_roster="",
        startup_warnings=None,
    ):
        super().__init__()
        app = QApplication.instance()
        if isinstance(app, QApplication):
            self.setWindowIcon(app.windowIcon())
        self.themes = themes if themes is not None else ThemeManager.discover_themes()
        self.selected_theme = selected_theme
        self.languages = languages if languages is not None else LanguageManager.load_languages()[0]
        self.current_language = LanguageManager.resolve_language(selected_language, self.languages)
        self.rosters = rosters if rosters is not None else importnames.rosters
        self.current_roster = selected_roster or importnames.active_roster
        self.startup_warnings = startup_warnings or []
        self.names = self._load_names()
        self.multi_quantity = 1
        self.lift_quantity = 1
        self.scroll_multi_quantity = 1
        self.lift_current_dict = None  # 保存当前减量抽的字典
        self.multi_result = None
        self.lift_result = None

        self.ui = None
        self.page_multi = None
        self.page_lift = None
        self.page_scrollsingle = None
        self.page_scrollmulti = None
        self.stacked_widget = None

        self.action_multi = None
        self.action_lift = None
        self.action_scrollsingle = None
        self.action_scrollmulti = None
        self.action_exit = None
        self.action_license = None
        self.action_repository = None
        self.action_help = None
        self.action_program_log = None
        self.theme_actions = None
        self.language_actions = None
        self.roster_actions = None
        self.log_level_actions = None

        self.multi_button = None
        self.multi_label = None
        self.multi_quantity_label = None
        self.multi_up_button = None
        self.multi_down_button = None
        self.lift_button = None
        self.lift_label = None
        self.lift_quantity_label = None
        self.lift_up_button = None
        self.lift_down_button = None
        self.lift_renew_button = None

        # ScrollSingle widgets & controller
        self.scroll_button = None
        self.scroll_label = None
        self.scroll_controller = None
        # True once the scroll page shows a real result (rolling stopped or a
        # memory import). Used by _retranslate so switching language never
        # clobbers a produced name with the placeholder.
        self.scroll_has_result = False

        # ScrollMulti widgets & controller
        self.scroll_multi_button = None
        self.scroll_multi_label = None
        self.scroll_multi_quantity_label = None
        self.scroll_multi_up_button = None
        self.scroll_multi_down_button = None
        self.scroll_multi_controller = None

        self._build_ui()
        self._apply_config_window()
        self._retranslate()
        if self.startup_warnings:
            self.statusBar().showMessage(
                self._t("state.startup_warning", files=", ".join(self.startup_warnings)), 0
            )

    def _load_names(self) -> dict:
        names = getattr(importnames, "names", None)
        if isinstance(names, dict) and names:
            return names
        logging.warning("未能从 importnames 中读取姓名数据，使用空列表。")
        return {}

    def _apply_config_window(self):
        """Apply configured or screen-relative startup geometry."""
        config = getattr(importnames, "loaded_config", {})
        window = config.get("window", {}) if isinstance(config, dict) else {}
        screen = QApplication.primaryScreen()
        geometry = screen.availableGeometry() if screen is not None else None
        screen_width = geometry.width() if geometry is not None else 1280
        screen_height = geometry.height() if geometry is not None else 800
        width, height = _configured_size(window, screen_width, screen_height)
        self.resize(width, height)
        self.setMinimumSize(0, 0)
        if geometry is not None:
            self.move(geometry.center().x() - width // 2, geometry.center().y() - height // 2)

    def _build_ui(self):
        # 使用已編譯的 Python UI 模塊（lib/ui_*.py），避免運行時依賴 .ui 文件
        try:
            # Ui_MainWindow.setupUi 會把 menubar, centralwidget, statusbar 等設置到本 QMainWindow 實例上
            self.ui_main = ui_main.Ui_MainWindow()
            self.ui_main.setupUi(self)

            # 獲取 stacked widget（必須由 Ui 定義為屬性 stackedWidget）
            self.stacked_widget = getattr(self.ui_main, "stackedWidget", None)
            if self.stacked_widget is None:
                raise RuntimeError("未找到 stackedWidget")

            # 設置標題（Ui.setupUi 通常已經設置，但保險起見保留回退值）
            self.setWindowTitle(self.windowTitle() or "randname")
        except Exception as exc:  # pragma: no cover - defensive path for runtime errors
            logging.exception("加载主窗口失败: %s", exc)
            self._show_error(
                self._t("menu.about"), self._t("error.window_init", error=str(exc))
            )
            return

        try:
            self._bind_menu_actions()
            self._build_theme_menu()
            self._build_language_menu()
            self._build_roster_menu()
            self._build_log_level_menu()
            self._load_pages()
            self._bind_page_actions()
        except Exception as exc:  # pragma: no cover - defensive path for runtime errors
            logging.exception("初始化界面控件失败: %s", exc)
            self._show_error(
                self._t("menu.about"), self._t("error.controls_init", error=str(exc))
            )

    def _bind_menu_actions(self):
        # 從編譯後的 Ui_MainWindow 模塊獲取 QAction，避免使用 findChild
        self.action_multi = getattr(self.ui_main, "action_Multi", None)
        self.action_lift = getattr(self.ui_main, "action_Lift", None)
        self.action_scrollsingle = getattr(self.ui_main, "action_ScrollSingle", None)
        self.action_scrollmulti = getattr(self.ui_main, "action_ScrollMulti", None)
        self.action_inputconfig = getattr(self.ui_main, "action_inputconfig", None)
        self.action_outputconfig = getattr(self.ui_main, "action_outputconfig", None)
        self.action_reinputconfig = getattr(self.ui_main, "action_reinputconfig", None)
        self.action_exit = getattr(self.ui_main, "action_exit", None)
        self.action_license = getattr(self.ui_main, "action_license", None)
        self.action_repository = getattr(self.ui_main, "action_repository", None)
        self.action_help = getattr(self.ui_main, "action_help", None)
        self.action_program_log = getattr(self.ui_main, "action_program_log", None)

        if self.action_multi:
            self.action_multi.triggered.connect(self._show_multi_page)
        if self.action_lift:
            self.action_lift.triggered.connect(self._show_lift_page)
        if self.action_scrollsingle:
            self.action_scrollsingle.triggered.connect(self._show_scrollsingle_page)
        if self.action_scrollmulti:
            self.action_scrollmulti.triggered.connect(self._show_scrollmulti_page)
        if self.action_inputconfig:
            self.action_inputconfig.triggered.connect(self._on_import_memory)
        if self.action_outputconfig:
            self.action_outputconfig.triggered.connect(self._on_export_memory)
        if self.action_reinputconfig:
            self.action_reinputconfig.triggered.connect(self._on_reload_config)
        if self.action_exit:
            self.action_exit.triggered.connect(self._on_exit)
        if self.action_license:
            self.action_license.triggered.connect(self._open_license)
        if self.action_repository:
            self.action_repository.triggered.connect(self._open_repository)
        if self.action_help:
            self.action_help.triggered.connect(self._open_help)
        if self.action_program_log:
            self.action_program_log.triggered.connect(self._show_program_log)

    def _build_theme_menu(self):
        theme_menu = getattr(self.ui_main, "menu_theme", None)
        if theme_menu is None:
            theme_menu = next(
                (menu for menu in self.menuBar().findChildren(QMenu) if menu.title() == "主题"),
                None,
            )
        if theme_menu is None:
            theme_menu = self.menuBar().addMenu("主题")
        else:
            theme_menu.clear()
        if self.theme_actions is not None:
            self.theme_actions.deleteLater()
        self.theme_actions = QActionGroup(theme_menu)
        self.theme_actions.setExclusive(True)
        for key, theme in self.themes.items():
            display_name = LanguageManager.localized_name(
                theme.get("name", {}), self.current_language, self.languages
            ) or key
            action = QAction(display_name, self)
            action.setCheckable(True)
            action.setChecked(key == self.selected_theme)
            action.triggered.connect(
                lambda _checked=False, theme_key=key: self._select_theme(theme_key)
            )
            action.setData(key)
            self.theme_actions.addAction(action)
            theme_menu.addAction(action)

    def _build_language_menu(self):
        language_menu = self.ui_main.menu_language
        language_menu.clear()
        if self.language_actions is not None:
            self.language_actions.deleteLater()
        self.language_actions = QActionGroup(language_menu)
        self.language_actions.setExclusive(True)
        for code, pack in self.languages.items():
            action = QAction(pack.get("display_name", code), self)
            action.setCheckable(True)
            action.setChecked(code == self.current_language)
            action.setData(code)
            action.triggered.connect(
                lambda _checked=False, language_code=code: self._select_language(language_code)
            )
            self.language_actions.addAction(action)
            language_menu.addAction(action)

    def _build_roster_menu(self):
        roster_menu = self.ui_main.menu_roster
        roster_menu.clear()
        if self.roster_actions is not None:
            self.roster_actions.deleteLater()
        self.roster_actions = QActionGroup(roster_menu)
        self.roster_actions.setExclusive(True)
        for key, roster in self.rosters.items():
            display_name = LanguageManager.localized_name(
                roster.get("name", {}), self.current_language, self.languages
            ) or key
            action = QAction(display_name, self)
            action.setCheckable(True)
            action.setChecked(key == self.current_roster)
            action.setData(key)
            action.triggered.connect(
                lambda _checked=False, roster_key=key: self._select_roster(roster_key)
            )
            self.roster_actions.addAction(action)
            roster_menu.addAction(action)

    def _build_log_level_menu(self):
        log_menu = self.ui_main.menu_log_level
        log_menu.clear()
        if self.log_level_actions is not None:
            self.log_level_actions.deleteLater()
        self.log_level_actions = QActionGroup(log_menu)
        self.log_level_actions.setExclusive(True)
        for level in StateManager.LOG_LEVEL_CHOICES:
            action = QAction(self._t(f"log.{level}"), self)
            action.setCheckable(True)
            action.setChecked(level == StateManager.CURRENT_LOG_LEVEL)
            action.setData(level)
            action.triggered.connect(
                lambda _checked=False, selected_level=level: self._select_log_level(selected_level)
            )
            self.log_level_actions.addAction(action)
            log_menu.addAction(action)

    def _select_log_level(self, level):
        selected = StateManager.configure_logging(level)
        self._build_log_level_menu()
        StateManager.log(selected, "log_level_changed", result=selected)
        self.statusBar().showMessage(self._t("state.log_level_changed", level=self._t(f"log.{selected}")))

    def _t(self, key, **values):
        return LanguageManager.translate(self.languages, self.current_language, key, **values)

    def _select_language(self, code):
        self.current_language = LanguageManager.resolve_language(code, self.languages)
        self._build_language_menu()
        self._build_theme_menu()
        self._build_roster_menu()
        self._build_log_level_menu()
        self._retranslate()
        self.statusBar().showMessage(
            self._t("state.language_changed", name=self.languages[self.current_language]["display_name"])
        )

    def _select_roster(self, key):
        self.names = importnames.select_roster(key)
        self.current_roster = importnames.active_roster
        self.lift_current_dict = None
        self.lift_result = None
        self.multi_quantity = min(max(1, self.multi_quantity), max(1, len(self.names)))
        self.lift_quantity = min(max(1, self.lift_quantity), max(1, len(self.names)))
        self.scroll_multi_quantity = min(max(1, self.scroll_multi_quantity), max(1, len(self.names)))
        self._set_quantity_label(self.multi_quantity_label, self.multi_quantity)
        self._set_quantity_label(self.lift_quantity_label, self.lift_quantity)
        self._set_quantity_label(self.scroll_multi_quantity_label, self.scroll_multi_quantity)
        if self.lift_label is not None:
            self.lift_label.setText(self._t("state.waiting"))
        if self.scroll_controller is not None:
            self.scroll_controller.update_names(self.names)
        if self.scroll_multi_controller is not None:
            self.scroll_multi_controller.set_quantity(self.scroll_multi_quantity)
            self.scroll_multi_controller.update_names(self.names)
        self._build_roster_menu()
        roster = self.rosters.get(key, {})
        display_name = LanguageManager.localized_name(
            roster.get("name", {}), self.current_language, self.languages
        ) or key
        self.statusBar().showMessage(self._t("state.roster_changed", name=display_name))

    def _retranslate(self):
        self.ui_main.menu_file.setTitle(self._t("menu.file"))
        self.ui_main.menu_mode.setTitle(self._t("menu.mode"))
        self.ui_main.menu_theme.setTitle(self._t("menu.theme"))
        self.ui_main.menu_language.setTitle(self._t("menu.language"))
        self.ui_main.menu_roster.setTitle(self._t("menu.roster"))
        self.ui_main.menu_about.setTitle(self._t("menu.about"))
        self.ui_main.menu_log_level.setTitle(self._t("menu.log_level"))
        for action, key in (
            (self.action_multi, "mode.multi"),
            (self.action_lift, "mode.lift"),
            (self.action_scrollsingle, "mode.scroll"),
            (self.action_scrollmulti, "mode.scrollmulti"),
            (self.action_inputconfig, "action.import"),
            (self.action_outputconfig, "action.export"),
            (self.action_reinputconfig, "action.reload"),
            (self.action_exit, "action.exit"),
            (self.action_license, "action.license"),
            (self.action_repository, "action.repository"),
            (self.action_help, "action.help"),
            (self.action_program_log, "action.program_log"),
        ):
            if action is not None:
                action.setText(self._t(key))
        if hasattr(self, "ui_multi"):
            self.ui_multi.pushButton_Multi.setText(self._t("button.draw"))
            self.ui_multi.pushButton_MultiQuantityUp.setText(self._t("button.increase"))
            self.ui_multi.pushButton_MultiQuantityDown.setText(self._t("button.decrease"))
            if self.multi_label is not None:
                self.multi_label.setText(self.multi_result or self._t("state.waiting"))
        if hasattr(self, "ui_lift"):
            self.ui_lift.pushButton_Lift.setText(self._t("button.draw"))
            self.ui_lift.pushButton_LiftQuantityUp.setText(self._t("button.increase"))
            self.ui_lift.pushButton_LiftQuantityDown.setText(self._t("button.decrease"))
            self.ui_lift.pushButton_LiftRenew.setText(self._t("button.reset"))
            if self.lift_label is not None:
                self.lift_label.setText(self.lift_result or self._t("state.waiting"))
        if hasattr(self, "ui_scrollsingle"):
            self.ui_scrollsingle.pushButton_ScrollSingleStart.setText(self._t("button.start"))
            self.ui_scrollsingle.pushButton_ScrollSingleStop.setText(self._t("button.stop"))
            if self.scroll_controller is not None:
                self.scroll_controller.set_button_texts(
                    self._t("button.start"), self._t("button.stop")
                )
            if self.scroll_label is not None and not self.scroll_has_result:
                self.scroll_label.setText(self._t("state.waiting"))
        if hasattr(self, "ui_scrollmulti"):
            self.ui_scrollmulti.pushButton_ScrollMulti.setText(self._t("button.draw"))
            self.ui_scrollmulti.pushButton_ScrollMultiQuantityUp.setText(self._t("button.increase"))
            self.ui_scrollmulti.pushButton_ScrollMultiQuantityDown.setText(self._t("button.decrease"))
            if self.scroll_multi_controller is not None:
                self.scroll_multi_controller.set_button_texts(
                    self._t("button.draw"), self._t("button.stop_scrollmulti"),
                    self._t("state.waiting"),
                )

    def _select_theme(self, name):
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return
        try:
            self.selected_theme = ThemeManager.apply_theme(app, name, self.themes)
            StateManager.log("INFO", "theme", result=self.selected_theme)
            theme = self.themes.get(self.selected_theme, {})
            theme_name = LanguageManager.localized_name(
                theme.get("name", {}), self.current_language, self.languages
            ) or self.selected_theme
            self.statusBar().showMessage(self._t("state.theme_changed", name=theme_name))
        except (OSError, ValueError, KeyError) as exc:
            StateManager.log("ERROR", "theme", error=str(exc))
            self._show_error(self._t("menu.theme"), self._t("error.theme_failed", error=str(exc)))

    def _load_pages(self):
        if self.stacked_widget is None:
            raise RuntimeError("stackedWidget 未初始化")

        # 使用已編譯的 UI 類來建立各頁面（避免依賴 ui/ 目錄）
        # Multi 頁面
        self.page_multi = QWidget()
        self.ui_multi = ui_widgetmulti.Ui_Form()
        self.ui_multi.setupUi(self.page_multi)

        # Lift 頁面
        self.page_lift = QWidget()
        self.ui_lift = ui_widgetlift.Ui_Form()
        self.ui_lift.setupUi(self.page_lift)

        # ScrollSingle page uses the dedicated compiled UI module.
        self.page_scrollsingle = QWidget()
        self.ui_scrollsingle = ui_widgetscrollsingle.Ui_Form()
        self.ui_scrollsingle.setupUi(self.page_scrollsingle)

        # ScrollMulti page reuses the Multi style with a dynamic reel board.
        self.page_scrollmulti = QWidget()
        self.ui_scrollmulti = ui_widgetscrollmulti.Ui_Form()
        self.ui_scrollmulti.setupUi(self.page_scrollmulti)

        self.stacked_widget.addWidget(self.page_multi)
        self.stacked_widget.addWidget(self.page_lift)
        self.stacked_widget.addWidget(self.page_scrollsingle)
        self.stacked_widget.addWidget(self.page_scrollmulti)
        config = getattr(importnames, "loaded_config", {})
        app_config = config.get("app", {}) if isinstance(config, dict) else {}
        default_mode = app_config.get("default_mode", "Multi") if isinstance(app_config, dict) else "Multi"
        if default_mode == "Multi":
            self._show_multi_page()
        elif default_mode == "Lift":
            self._show_lift_page()
        elif default_mode == "ScrollMulti":
            self._show_scrollmulti_page()
        else:
            self._show_scrollsingle_page()

    def _bind_page_actions(self):
        # Multi 頁面綁定
        self.multi_button = getattr(self.ui_multi, "pushButton_Multi", None)
        self.multi_label = getattr(self.ui_multi, "label_MultiOutput", None)
        self.multi_quantity_label = getattr(self.ui_multi, "label_MultiQuantity", None)
        self.multi_up_button = getattr(self.ui_multi, "pushButton_MultiQuantityUp", None)
        self.multi_down_button = getattr(self.ui_multi, "pushButton_MultiQuantityDown", None)
        if self.multi_quantity_label is not None:
            self._set_quantity_label(self.multi_quantity_label, self.multi_quantity)
        if self.multi_up_button is not None:
            self.multi_up_button.clicked.connect(lambda: self._adjust_quantity("multi", 1))
        if self.multi_down_button is not None:
            self.multi_down_button.clicked.connect(lambda: self._adjust_quantity("multi", -1))
        if self.multi_button and self.multi_label:
            self.multi_button.clicked.connect(self._handle_multi)
            self.multi_label.setText(self._t("state.waiting"))

        # ScrollSingle 綁定（使用 WidgetScrollSingle 的專用控件）
        try:
            self.scroll_label = getattr(self.ui_scrollsingle, "label_ScrollSingleOutput", None)
            self.scroll_start_button = getattr(self.ui_scrollsingle, "pushButton_ScrollSingleStart", None)
            self.scroll_stop_button = getattr(self.ui_scrollsingle, "pushButton_ScrollSingleStop", None)
            if self.scroll_label is not None:
                # 默認顯示模式名稱
                try:
                    self.scroll_label.setText(self._t("state.waiting"))
                except Exception:
                    pass
            # 创建控制器，但不自动启动
            if self.scroll_start_button is not None and self.scroll_stop_button is not None and self.scroll_label is not None:
                rate = _rate_from_config(importnames.loaded_config, "scroll_single")
                self.scroll_controller = ScrollSingle.ScrollController(
                    self.scroll_label,
                    self.scroll_start_button,
                    self.scroll_stop_button,
                    self.names,
                    on_result=self._on_scroll_result,
                    rate=rate,
                    start_text=self._t("button.start"),
                    stop_text=self._t("button.stop"),
                    reset_text=self._t("state.waiting"),
                )
        except Exception as exc:
            logging.exception("初始化 ScrollSingle 失败: %s", exc)

        # ScrollMulti 綁定（沿用 Multi 樣式，單一輸出框）
        try:
            self.scroll_multi_button = getattr(self.ui_scrollmulti, "pushButton_ScrollMulti", None)
            self.scroll_multi_quantity_label = getattr(self.ui_scrollmulti, "label_ScrollMultiQuantity", None)
            self.scroll_multi_label = getattr(self.ui_scrollmulti, "label_ScrollMultiOutput", None)
            self.scroll_multi_up_button = getattr(self.ui_scrollmulti, "pushButton_ScrollMultiQuantityUp", None)
            self.scroll_multi_down_button = getattr(self.ui_scrollmulti, "pushButton_ScrollMultiQuantityDown", None)
            if self.scroll_multi_quantity_label is not None:
                self._set_quantity_label(self.scroll_multi_quantity_label, self.scroll_multi_quantity)
            if self.scroll_multi_up_button is not None:
                self.scroll_multi_up_button.clicked.connect(lambda: self._adjust_quantity("scrollmulti", 1))
            if self.scroll_multi_down_button is not None:
                self.scroll_multi_down_button.clicked.connect(lambda: self._adjust_quantity("scrollmulti", -1))
            if self.scroll_multi_button is not None and self.scroll_multi_label is not None:
                self.scroll_multi_controller = ScrollMulti.ScrollMultiController(
                    self.scroll_multi_label,
                    self.scroll_multi_button,
                    self.names,
                    on_result=self._on_scrollmulti_result,
                    rate=_rate_from_config(getattr(importnames, "loaded_config", {}), "scroll_multi"),
                    draw_text=self._t("button.draw"),
                    stop_format=self._t("button.stop_scrollmulti"),
                    reset_text=self._t("state.waiting"),
                    on_warning=self._on_scrollmulti_warning,
                )
                self.scroll_multi_controller.set_quantity(self.scroll_multi_quantity)
        except Exception as exc:
            logging.exception("初始化 ScrollMulti 失败: %s", exc)

        # Lift 頁面綁定
        self.lift_button = getattr(self.ui_lift, "pushButton_Lift", None)
        self.lift_label = getattr(self.ui_lift, "label_LiftOutput", None)
        self.lift_quantity_label = getattr(self.ui_lift, "label_LiftQuantity", None)
        self.lift_up_button = getattr(self.ui_lift, "pushButton_LiftQuantityUp", None)
        self.lift_down_button = getattr(self.ui_lift, "pushButton_LiftQuantityDown", None)
        self.lift_renew_button = getattr(self.ui_lift, "pushButton_LiftRenew", None)
        if self.lift_quantity_label is not None:
            self._set_quantity_label(self.lift_quantity_label, self.lift_quantity)
        if self.lift_up_button is not None:
            self.lift_up_button.clicked.connect(lambda: self._adjust_quantity("lift", 1))
        if self.lift_down_button is not None:
            self.lift_down_button.clicked.connect(lambda: self._adjust_quantity("lift", -1))
        if self.lift_renew_button is not None:
            self.lift_renew_button.clicked.connect(self._reset_lift_page)
        if self.lift_button and self.lift_label:
            self.lift_button.clicked.connect(self._handle_lift)
            self.lift_label.setText(self._t("state.waiting"))

    def _show_multi_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_multi)

    def _show_lift_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_lift)

    def _show_scrollsingle_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_scrollsingle)

    def _show_scrollmulti_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_scrollmulti)

    def _on_import_memory(self):
        # Import JSON memory without changing files under config/.
        try:
            fname, _ = QFileDialog.getOpenFileName(
                self, self._t("dialog.import_title"), "", self._t("dialog.json_filter")
            )
            if not fname:
                return
            from pathlib import Path
            StateManager.import_memory(Path(fname), apply_callback=self._apply_memory_import)
            QMessageBox.information(
                self, self._t("dialog.import_title"), self._t("dialog.import_success", path=fname)
            )
        except Exception as exc:
            logging.exception("导入记忆失败: %s", exc)
            QMessageBox.warning(
                self, self._t("dialog.import_title"), self._t("dialog.operation_failed", error=str(exc))
            )

    def _on_export_memory(self):
        try:
            fname, _ = QFileDialog.getSaveFileName(
                self,
                self._t("dialog.export_title"),
                "memory-export.json",
                self._t("dialog.json_filter"),
            )
            if not fname:
                return
            from pathlib import Path
            StateManager.export_memory(Path(fname))
            QMessageBox.information(
                self, self._t("dialog.export_title"), self._t("dialog.export_success", path=fname)
            )
        except Exception as exc:
            logging.exception("导出记忆失败: %s", exc)
            QMessageBox.warning(
                self, self._t("dialog.export_title"), self._t("dialog.operation_failed", error=str(exc))
            )

    def _on_reload_config(self):
        try:
            previous_theme = self.selected_theme
            previous_language = self.current_language
            previous_roster = self.current_roster
            previous_names = self.names.copy()
            previous_status = self.statusBar().currentMessage()
            importnames.reload_data()
            cfg = importnames.loaded_config
            self.rosters = importnames.rosters
            roster_key = previous_roster if previous_roster in self.rosters else importnames.active_roster
            self.names = importnames.select_roster(roster_key)
            self.current_roster = importnames.active_roster
            roster_changed = previous_names != self.names
            if roster_changed:
                self.lift_current_dict = None
            self.multi_quantity = min(max(1, self.multi_quantity), max(1, len(self.names)))
            self.lift_quantity = min(max(1, self.lift_quantity), max(1, len(self.names)))
            self.scroll_multi_quantity = min(max(1, self.scroll_multi_quantity), max(1, len(self.names)))
            self._set_quantity_label(self.multi_quantity_label, self.multi_quantity)
            self._set_quantity_label(self.lift_quantity_label, self.lift_quantity)
            self._set_quantity_label(self.scroll_multi_quantity_label, self.scroll_multi_quantity)
            self.themes = ThemeManager.discover_themes()
            self.languages, preferred_language, language_warning = LanguageManager.load_languages()
            app_config = cfg.get("app", {}) if isinstance(cfg, dict) else {}
            if not isinstance(app_config, dict):
                app_config = {}
            if previous_theme in self.themes:
                self.selected_theme = previous_theme
            else:
                self.selected_theme = ThemeManager.resolve_startup_theme(
                    self.themes, app_config.get("theme", "")
                )
            if previous_language in self.languages:
                self.current_language = previous_language
            else:
                self.current_language = LanguageManager.resolve_startup_language(
                    self.languages, preferred_language, app_config.get("language", "")
                )
            self._build_theme_menu()
            self._build_language_menu()
            self._build_roster_menu()
            self._build_log_level_menu()
            self._retranslate()
            if self.themes:
                app = QApplication.instance()
                if isinstance(app, QApplication):
                    ThemeManager.apply_theme(app, self.selected_theme, self.themes)
            if self.scroll_controller is not None:
                self.scroll_controller.update_rate(_rate_from_config(cfg, "scroll_single"))
                if roster_changed:
                    self.scroll_controller.update_names(self.names)
            if self.scroll_multi_controller is not None:
                self.scroll_multi_controller.update_rate(
                    _rate_from_config(cfg, "scroll_multi")
                )
                self.scroll_multi_controller.set_quantity(self.scroll_multi_quantity)
                if roster_changed:
                    self.scroll_multi_controller.update_names(self.names)
            warnings = list(StateManager.CONFIG_WARNINGS)
            if importnames.ROSTER_FALLBACK_USED:
                warnings.append("config/name.toml")
            if language_warning:
                warnings.append(language_warning)
            if ThemeManager.THEME_LOAD_WARNING:
                warnings.append(ThemeManager.THEME_LOAD_WARNING)
            self.startup_warnings = list(dict.fromkeys(warnings))
            if warnings:
                StateManager.log("WARN", "reload_fallback", error=", ".join(warnings))
                self.statusBar().showMessage(
                    self._t("state.startup_warning", files=", ".join(warnings)), 0
                )
            else:
                self.statusBar().showMessage(previous_status)
        except Exception as exc:
            logging.exception("重新加载配置失败: %s", exc)
            QMessageBox.warning(
                self,
                self._t("action.reload"),
                self._t("dialog.operation_failed", error=str(exc)),
            )

    @staticmethod
    def _remembered_text(value):
        """Extract a printable result from a memory entry, or None when absent.

        A stored ``null`` means "this mode has no remembered result"; it must not
        be rendered as the literal text ``None``.
        """
        if value is None:
            return None
        return str(value.get("result") if isinstance(value, dict) else value)

    def _apply_memory_import(self, content: dict):
        # content 包含 loaded_config 与 last_results
        try:
            if not isinstance(content, dict):
                return
            # 结果文本可能很长，但导入记忆不能改变用户当前窗口尺寸。
            current_size = self.size()
            self.setMinimumSize(0, 0)
            # 将 last_results 应用到界面显示（若存在）
            last = content.get("last_results", {})
            if isinstance(last, dict):
                if self.multi_label is not None:
                    text = self._remembered_text(last.get("Multi", last.get("multi")))
                    if text is not None:
                        self.multi_result = text
                        self.multi_label.setText(text)
                if self.lift_label is not None:
                    text = self._remembered_text(last.get("Lift", last.get("lift")))
                    if text is not None:
                        self.lift_result = text
                        self.lift_label.setText(text)
                if self.scroll_label is not None:
                    text = self._remembered_text(last.get("ScrollSingle", last.get("scrollsingle")))
                    if text is not None:
                        self.scroll_label.setText(text)
                        self.scroll_has_result = True
                if self.scroll_multi_controller is not None:
                    v = last.get("ScrollMulti", last.get("scrollmulti"))
                    payload = v.get("result") if isinstance(v, dict) and "result" in v else v
                    if payload is not None:
                        self.scroll_multi_controller.show_result(payload)
            self.resize(current_size)
            self.setMinimumSize(0, 0)
        except Exception as exc:
            logging.exception("应用导入记忆失败: %s", exc)

    def _handle_multi(self):
        try:
            logging.info("执行多抽，数量=%s", self.multi_quantity)
            result = multi_module.Multi(self.names, self.multi_quantity)
            self.multi_result = self._format_output_result(result)
            self._set_output_text(self.multi_label, self.multi_result)
            self.statusBar().showMessage(
                self._t("state.multi_result", count=self.multi_quantity)
            )
            # 记录到内存与日志
            try:
                state = StateManager.load_memory()
                state["loaded_config"] = getattr(importnames, 'loaded_config', None)
                state.setdefault("last_results", {})["Multi"] = {"result": result, "time": StateManager._now_iso()}
                StateManager.save_memory(state)
                StateManager.log("INFO", "Multi", result=result)
            except Exception:
                logging.exception("记录 multi 结果失败")
        except Exception as exc:
            logging.exception("多抽执行失败: %s", exc)
            self.multi_result = self._t("dialog.operation_failed", error=str(exc))
            self._set_output_text(self.multi_label, self.multi_result)
            self._show_error(self._t("mode.multi"), str(exc))
            try:
                StateManager.log("ERROR", "Multi", error=str(exc))
            except Exception:
                pass

    def _handle_lift(self):
        try:
            logging.info("执行减量抽，数量=%s", self.lift_quantity)
            # 如果是第一次或者被重置，使用原始names字典
            if self.lift_current_dict is None:
                lift_dict = self.names
            else:
                lift_dict = self.lift_current_dict
            
            result = lift_module.Lift(self.names, lift_dict, self.lift_quantity)
            self.lift_result = self._format_output_result(result)
            self._set_output_text(self.lift_label, self.lift_result)
            
            # 保存本次结果的Liftdict，供下一次使用
            if "Liftdict" in result:
                self.lift_current_dict = result["Liftdict"]
            
            self.statusBar().showMessage(
                self._t("state.lift_result", count=self.lift_quantity)
            )
            # 记录到内存与日志
            try:
                state = StateManager.load_memory()
                state["loaded_config"] = getattr(importnames, 'loaded_config', None)
                state.setdefault("last_results", {})["Lift"] = {"result": result, "time": StateManager._now_iso()}
                StateManager.save_memory(state)
                StateManager.log("INFO", "Lift", result=result)
            except Exception:
                logging.exception("记录 lift 结果失败")
        except Exception as exc:
            logging.exception("减量抽执行失败: %s", exc)
            self.lift_result = self._t("dialog.operation_failed", error=str(exc))
            self._set_output_text(self.lift_label, self.lift_result)
            self._show_error(self._t("mode.lift"), str(exc))
            try:
                StateManager.log("ERROR", "Lift", error=str(exc))
            except Exception:
                pass

    def _on_scroll_result(self, result, meta):
        # Called by ScrollSingle controller when a result is produced
        try:
            logging.info("scrollsingle result: %s", result)
            if self.scroll_label is not None:
                self.scroll_label.setText(str(result))
            self.scroll_has_result = True
            # 保存到记忆与日志
            state = StateManager.load_memory()
            state["loaded_config"] = getattr(importnames, 'loaded_config', None)
            state.setdefault("last_results", {})["ScrollSingle"] = {"result": result, "meta": meta}
            StateManager.save_memory(state)
            StateManager.log("INFO", "ScrollSingle", result={"name": result, "meta": meta})
        except Exception as exc:
            logging.exception("处理 scrollsingle 结果失败: %s", exc)
            try:
                StateManager.log("ERROR", "ScrollSingle", error=str(exc))
            except Exception:
                pass

    def _on_scrollmulti_result(self, result, meta):
        # Called by ScrollMulti controller when a round completes
        try:
            logging.info("scrollmulti result: %s", result)
            selected = 0
            if isinstance(result, dict):
                quantity = result.get("quantity", {})
                if isinstance(quantity, dict):
                    selected = quantity.get("selected", 0)
            self.statusBar().showMessage(
                self._t("state.scrollmulti_result", count=selected)
            )
            state = StateManager.load_memory()
            state["loaded_config"] = getattr(importnames, 'loaded_config', None)
            state.setdefault("last_results", {})["ScrollMulti"] = {"result": result, "meta": meta}
            StateManager.save_memory(state)
            StateManager.log("INFO", "ScrollMulti", result=result)
        except Exception as exc:
            logging.exception("处理 scrollmulti 结果失败: %s", exc)
            try:
                StateManager.log("ERROR", "ScrollMulti", error=str(exc))
            except Exception:
                pass

    def _on_scrollmulti_warning(self, count):
        # Called by ScrollMulti when the requested count exceeds the roster.
        try:
            self.statusBar().showMessage(self._t("state.scrollmulti_invalid", count=count))
            StateManager.log("WARN", "ScrollMulti", error=f"requested more than {count}")
        except Exception:
            pass

    def _adjust_quantity(self, mode, delta):
        max_count = max(1, len(self.names))
        if mode == "multi":
            self.multi_quantity = max(1, min(max_count, self.multi_quantity + delta))
            self._set_quantity_label(self.multi_quantity_label, self.multi_quantity)
            logging.info("更新多抽数量=%s", self.multi_quantity)
        elif mode == "lift":
            self.lift_quantity = max(1, min(max_count, self.lift_quantity + delta))
            self._set_quantity_label(self.lift_quantity_label, self.lift_quantity)
            logging.info("更新减量抽数量=%s", self.lift_quantity)
        elif mode == "scrollmulti":
            self.scroll_multi_quantity = max(1, min(max_count, self.scroll_multi_quantity + delta))
            self._set_quantity_label(self.scroll_multi_quantity_label, self.scroll_multi_quantity)
            if self.scroll_multi_controller is not None:
                self.scroll_multi_controller.set_quantity(self.scroll_multi_quantity)
            logging.info("更新滚动多抽数量=%s", self.scroll_multi_quantity)

    def _reset_lift_page(self):
        # 刷新减量抽页面：不改变 lift_quantity，只重置当前的 Liftdict
        self.lift_current_dict = None  # 重置减量抽字典
        self.lift_result = None
        # 保持数量值不变，仅更新显示
        self._set_quantity_label(self.lift_quantity_label, self.lift_quantity)
        if self.lift_label is not None:
            self.lift_label.setText(self._t("state.waiting"))
        self.statusBar().showMessage(self._t("state.waiting"))

    def _set_quantity_label(self, label, value):
        if label is not None:
            label.setText(str(value))

    def _set_output_text(self, label, text):
        if label is not None:
            label.setText(text)

    def _format_output_result(self, result):
        if not isinstance(result, dict):
            return str(result)

        outdict = result.get("outdict", {})
        if isinstance(outdict, dict) and outdict:
            items = []
            for value in outdict.values():
                if isinstance(value, dict):
                    # Multi模式：{"code": "...", "name": "..."}
                    if "name" in value:
                        item_name = value["name"]
                    # Lift模式：{"code": "name_value"}
                    elif len(value) == 1:
                        item_name = next(iter(value.values()))
                    else:
                        item_name = str(value)
                else:
                    item_name = str(value)
                items.append(str(item_name))
            if items:
                # 改进：名字较多时，一行显示多个名字，之间用空格隔开
                # 每4个名字为一行（可根据需要调整）
                if len(items) <= 4:
                    return "  ".join(items)
                else:
                    lines = []
                    for i in range(0, len(items), 4):
                        lines.append("  ".join(items[i:i+4]))
                    return "\n".join(lines)

        if isinstance(result.get("Liftdict"), dict):
            remaining = list(result["Liftdict"].values())
            if remaining:
                if len(remaining) <= 4:
                    return "  ".join(str(item) for item in remaining)
                else:
                    lines = []
                    for i in range(0, len(remaining), 4):
                        lines.append("  ".join(str(item) for item in remaining[i:i+4]))
                    return "\n".join(lines)
        return self._t("state.no_result")

    def _on_exit(self):
        logging.info("用户请求退出程序")
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _open_help(self):
        language = self.current_language if self.current_language in {"en_US", "zh_CN", "zh_TW"} else "en_US"
        config = getattr(importnames, "loaded_config", {})
        help_directory = _configured_path(config, "paths", "help_directory", "doc")
        help_paths = [help_directory / f"help_{language}.md"]
        if language != "en_US":
            help_paths.append(ROOT_DIR / "doc" / "help_en_US.md")
        for help_path in help_paths:
            if help_path.is_file():
                self._show_document(self._t("action.help"), help_path, markdown=True)
                return
        self._show_error(
            self._t("action.help"), self._t("error.help_missing", path=str(help_paths[-1]))
        )

    def _show_document(self, title: str, path: Path, *, markdown: bool) -> bool:
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            logging.exception("无法读取文档 %s", path)
            StateManager.log("ERROR", "read_document", error=f"{path}: {exc}")
            self._show_error(title, self._t("dialog.operation_failed", error=str(exc)))
            return False

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(900, 680)
        dialog.setMinimumSize(620, 420)
        text_view = QTextBrowser(dialog)
        text_view.setOpenLinks(False)
        text_view.setOpenExternalLinks(False)
        text_view.setReadOnly(True)
        if markdown:
            text_view.setMarkdown(content)
        else:
            text_view.setPlainText(content)
        text_view.setStyleSheet("QTextBrowser { border: none; padding: 16px; }")
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=dialog)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(self._t("action.close"))
        buttons.rejected.connect(dialog.reject)
        buttons.accepted.connect(dialog.accept)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addWidget(text_view)
        layout.addWidget(buttons)
        StateManager.log("INFO", "open_document", result=path.name)
        dialog.exec()
        return True

    def _show_program_log(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self._t("action.program_log"))
        dialog.resize(820, 520)
        text_view = QPlainTextEdit(dialog)
        text_view.setReadOnly(True)
        text_view.setPlainText(StateManager.session_log_text() or self._t("state.no_logs"))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=dialog)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(self._t("action.close"))
        buttons.rejected.connect(dialog.reject)
        buttons.accepted.connect(dialog.accept)
        layout = QVBoxLayout(dialog)
        layout.addWidget(text_view)
        layout.addWidget(buttons)
        dialog.exec()

    def _open_license(self):
        try:
            config = getattr(importnames, "loaded_config", {})
            license_path = _configured_path(config, "paths", "license_file", "doc/gpl-3.0.md")
            if license_path.exists():
                self._show_document(self._t("action.license"), license_path, markdown=True)
            else:
                self._show_error(
                    self._t("action.license"),
                    self._t("error.license_missing", path=str(license_path)),
                )
        except Exception as exc:
            logging.exception("打开许可证文件失败: %s", exc)
            self._show_error(
                self._t("action.license"), self._t("error.open_license", error=str(exc))
            )

    def _open_repository(self):
        try:
            config = getattr(importnames, "loaded_config", {})
            app_settings = config.get("app", {}) if isinstance(config, dict) else {}
            repository_url = (
                app_settings.get("repository_url", DEFAULT_REPO_URL)
                if isinstance(app_settings, dict)
                else DEFAULT_REPO_URL
            )
            logging.info("打开项目仓库: %s", repository_url)
            QDesktopServices.openUrl(QUrl(repository_url))
        except Exception as exc:
            logging.exception("打开仓库链接失败: %s", exc)
            self._show_error(
                self._t("action.repository"), self._t("error.open_repository", error=str(exc))
            )

    def _show_error(self, title, message):
        QMessageBox.critical(self, title, message)


def main():
    global lift_module, multi_module, ScrollSingle, ScrollMulti
    global StateManager, ThemeManager, importnames
    global LanguageManager
    global ui_main, ui_widgetlift, ui_widgetmulti, ui_widgetscrollsingle, ui_widgetscrollmulti

    app = QApplication(sys.argv)
    bootstrap_config, bootstrap_warnings = _bootstrap_config()
    icon_path = _configured_path(bootstrap_config, "assets", "icon", "ui/randname1.png")
    app_icon = QIcon(str(icon_path))
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    else:
        bootstrap_warnings.append(f"Invalid application icon: {icon_path}")
    screen = app.primaryScreen()
    geometry = screen.availableGeometry() if screen is not None else None
    screen_width = geometry.width() if geometry is not None else 1280
    screen_height = geometry.height() if geometry is not None else 800
    splash_config = bootstrap_config.get("splash", {})
    if not isinstance(splash_config, dict):
        splash_config = {}
    splash_enabled = splash_config.get("enabled", True) is True
    splash_mode = splash_config.get("mode", 0)
    splash_duration_ms = splash_config.get("duration_ms", 1000)
    if not isinstance(splash_duration_ms, int) or isinstance(splash_duration_ms, bool):
        splash_duration_ms = 1000
    splash_duration_ms = max(0, splash_duration_ms)
    splash = None
    splash_timer = QElapsedTimer()
    splash_path = _configured_path(
        bootstrap_config, "assets", "splash_image", "ui/randname-start_v3.6.png"
    )
    splash_pixmap = QPixmap(str(splash_path))
    if splash_enabled and not splash_pixmap.isNull():
        splash_width, splash_height = _configured_size(
            splash_config, screen_width, screen_height, splash=True
        )
        splash_pixmap = splash_pixmap.scaled(
            splash_width,
            splash_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        splash = QSplashScreen(splash_pixmap)
        splash.show()
        if geometry is not None:
            splash.move(
                geometry.center().x() - splash.width() // 2,
                geometry.center().y() - splash.height() // 2,
            )
        app.processEvents()
        splash_timer.start()
    elif splash_enabled:
        bootstrap_warnings.append(f"Missing or invalid splash image: {splash_path}")

    missing_recoverable, missing_required = _startup_file_check(bootstrap_config)
    bootstrap_warnings.extend(missing_recoverable)
    if missing_required:
        if splash is not None:
            splash.close()
        QMessageBox.critical(
            None,
            "Startup check failed",
            "Required application files are missing:\n" + "\n".join(missing_required),
        )
        return 1

    app.processEvents()
    try:
        from lib import Lift as lift_module
        from lib import Multi as multi_module
        from lib import importnames
        from lib import StateManager
        from lib import ScrollSingle
        from lib import ScrollMulti
        from lib import ThemeManager
        from lib import LanguageManager
        from lib import ui_main
        from lib import ui_widgetmulti
        from lib import ui_widgetlift
        from lib import ui_widgetscrollsingle
        from lib import ui_widgetscrollmulti
    except Exception as exc:
        if splash is not None:
            splash.close()
        QMessageBox.critical(
            None,
            "Startup failed",
            f"A required application component could not be loaded:\n{type(exc).__name__}: {exc}",
        )
        return 1

    config = getattr(importnames, "loaded_config", {})
    StateManager.configure_paths(config)
    logging_config = config.get("logging", {}) if isinstance(config, dict) else {}
    if not isinstance(logging_config, dict):
        logging_config = {}
    StateManager.configure_logging(logging_config.get("level", "INFO"))
    themes = ThemeManager.discover_themes()
    languages, preferred_language, language_warning = LanguageManager.load_languages()
    app_config = config.get("app", {}) if isinstance(config, dict) else {}
    if not isinstance(app_config, dict):
        app_config = {}
    requested_theme = app_config.get("theme", "")
    selected_theme = ThemeManager.resolve_startup_theme(themes, requested_theme)
    selected_roster = importnames.active_roster
    startup_warnings = list(dict.fromkeys(bootstrap_warnings + StateManager.CONFIG_WARNINGS))
    if importnames.ROSTER_FALLBACK_USED:
        startup_warnings.append("config/name.toml")
    if language_warning:
        startup_warnings.append(language_warning)
    if ThemeManager.THEME_LOAD_WARNING:
        startup_warnings.append(ThemeManager.THEME_LOAD_WARNING)
    if not (ROOT_DIR / "config" / "theme.toml").is_file():
        startup_warnings.append("config/theme.toml")
    startup_warnings = list(dict.fromkeys(startup_warnings))
    for warning in startup_warnings:
        StateManager.log("WARN", "startup_fallback", error=warning)
    selected_language = LanguageManager.resolve_startup_language(
        languages, preferred_language, app_config.get("language", "")
    )
    window = MainWindow(
        themes,
        selected_theme,
        languages,
        selected_language,
        importnames.rosters,
        selected_roster,
        startup_warnings,
    )
    try:
        ThemeManager.apply_theme(app, selected_theme, themes)
    except (OSError, ValueError, KeyError) as exc:
        # A malformed color in theme.toml must never abort startup; keep the
        # built-in palette and keep running.
        logging.exception("应用启动主题失败: %s", exc)
        StateManager.log("ERROR", "startup_theme", error=str(exc))
    window.show()
    if splash is not None:
        if splash_mode in (1, "fixed"):
            remaining_ms = max(0, splash_duration_ms - splash_timer.elapsed())
            if remaining_ms:
                QTimer.singleShot(remaining_ms, lambda: splash.finish(window))
            else:
                splash.finish(window)
        else:
            splash.finish(window)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
