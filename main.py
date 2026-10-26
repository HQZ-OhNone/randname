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


import gc
import logging
import sys
import tomllib
from pathlib import Path

from PySide6.QtCore import QElapsedTimer, QEvent, QObject, QPointF, QTimer, QUrl, Qt
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QColor,
    QDesktopServices,
    QFont,
    QFontMetricsF,
    QIcon,
    QPainter,
    QPixmap,
    QPixmapCache,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QMenu,
    QSplashScreen,
    QSlider,
    QWidget,
)

from lib.version import APP_VERSION

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")

ROOT_DIR = Path(__file__).resolve().parent
UI_DIR = ROOT_DIR / "ui"
DOC_DIR = ROOT_DIR / "doc"
ICON_PATH = UI_DIR / "randname1.png"
SPLASH_IMAGE_PATH = UI_DIR / "randname-start.png"
LICENSE_PATH = DOC_DIR / "gpl-3.0.md"
HISTORY_PATH = DOC_DIR / "history.md"
# 模式名称与配置、记忆和界面文案共用同一套标准写法。
MODE_MULTI = "Multi"
MODE_LIFT = "Lift"
MODE_SCROLL_MULTI = "ScrollMulti"
MODE_SCROLL_LIFT = "ScrollLift"
MODE_SINGLE = "Single"
MODE_SCROLL_SINGLE = "ScrollSingle"
# 这些模块在 main() 中导入；提前声明便于无 GUI 的测试导入 main。
BackgroundWidget = None
WindowTheme = None
# 仓库与反馈地址固定不变，直接写在程序中，不放进配置文件。
REPOSITORY_URL = "https://www.github.com/HQZ-OhNone/randname"
RELEASES_URL = "https://github.com/HQZ-OhNone/randname/releases"
FEEDBACK_URL = "https://github.com/HQZ-OhNone/randname/issues"
EMAIL_ADDRESS = "ohnone_hqz@outlook.com"


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


def _as_float(value, default, minimum=None, maximum=None):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if result != result or result in (float("inf"), float("-inf")):
        return default
    if minimum is not None and result < minimum:
        result = minimum
    if maximum is not None and result > maximum:
        result = maximum
    return result


def _configured_size(section: dict, screen_width: int, screen_height: int, *, splash=False) -> tuple[int, int]:
    if not isinstance(section, dict):
        section = {}
    if section.get("size_mode") == "fixed":
        width = section.get("width")
        height = section.get("height")
        if isinstance(width, int) and width > 0 and isinstance(height, int) and height > 0:
            return width, height
    ratio = _as_float(section.get("screen_ratio"), 0.25 if splash else 0.75, 0.05, 1.0)
    aspect = _as_float(section.get("aspect_ratio"), 2.0 if splash else 1.5, 0.1)
    width = screen_width * ratio
    height = width / aspect
    if height > screen_height * ratio:
        height = screen_height * ratio
        width = height * aspect
    return max(1, int(width)), max(1, int(height))


def _window_is_maximized(section: dict) -> bool:
    """判断窗口配置是否要求启动时最大化。"""
    return isinstance(section, dict) and section.get("size_mode") == "maximum"


def _fixed_size_exceeds_screen(section: dict, screen_width: int, screen_height: int) -> bool:
    """固定尺寸超出可用屏幕时返回 True，用于临时切换到最大化。"""
    if not isinstance(section, dict) or section.get("size_mode") != "fixed":
        return False
    width = section.get("width")
    height = section.get("height")
    if isinstance(width, bool) or isinstance(height, bool):
        return False
    if not isinstance(width, int) or not isinstance(height, int):
        return False
    return width > screen_width or height > screen_height


def _clamp_quantity(value, maximum) -> int:
    """把抽取数量夹紧到 1..maximum，非法输入回退为 1。"""
    try:
        maximum = int(maximum)
    except (TypeError, ValueError):
        maximum = 1
    maximum = max(1, maximum)
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = 1
    return max(1, min(maximum, value))


def _splash_wait_ms(mode, duration_ms, elapsed_ms) -> int:
    """返回 mode=1 时启动画面还需显示的毫秒数；其他模式立即关闭。"""
    if mode not in (1, "fixed"):
        return 0
    try:
        duration = max(0, int(duration_ms))
    except (TypeError, ValueError):
        duration = 0
    try:
        elapsed = max(0, int(elapsed_ms))
    except (TypeError, ValueError):
        elapsed = 0
    return max(0, duration - elapsed)


def _rate_from_config(config: dict | None, default: int = 30) -> int:
    """Read a positive ticks-per-second rate, accepting old section names."""
    if not isinstance(config, dict):
        return default
    for section in ("scroll", "scroll_multi", "scroll_lift", "scroll_single"):
        values = config.get(section, {})
        if not isinstance(values, dict):
            continue
        raw = values.get("rate")
        if raw is None:
            continue
        try:
            value = int(raw)
        except (TypeError, ValueError):
            continue
        if value > 0:
            return value
    return default


def _startup_file_check(config: dict | None = None) -> tuple[list[str], list[str]]:
    def relative(path: Path) -> str:
        try:
            return str(path.relative_to(ROOT_DIR))
        except ValueError:
            return str(path)

    recoverable = (
        ROOT_DIR / "config" / "config.toml",
        ROOT_DIR / ".config.default.toml",
        ROOT_DIR / "config" / "name.toml",
        ROOT_DIR / ".name.default.toml",
        ROOT_DIR / "config" / "language.toml",
        ROOT_DIR / "config" / "theme.toml",
        ICON_PATH,
        SPLASH_IMAGE_PATH,
        LICENSE_PATH,
        DOC_DIR / "help_en_US.md",
    )
    warnings = [relative(path) for path in recoverable if not path.is_file()]
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


class _QuantitySliderTouchFilter(QObject):
    """把触点纵向位置直接映射为纵向滑动条数值，保证触屏可以稳定拖动。"""

    def eventFilter(self, watched, event):
        if not isinstance(watched, QSlider):
            return False
        event_type = event.type()
        if event_type == QEvent.Type.TouchEnd:
            event.accept()
            return True
        if event_type not in (QEvent.Type.TouchBegin, QEvent.Type.TouchUpdate):
            return False
        points = event.points()
        if not points:
            return False
        position = points[0].position()
        span = max(1, watched.height())
        ratio = min(1.0, max(0.0, 1.0 - position.y() / span))
        value = watched.minimum() + round(ratio * (watched.maximum() - watched.minimum()))
        watched.setValue(int(value))
        event.accept()
        return True


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
        startup_mode=None,
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
        self.scroll_lift_quantity = 1
        self.startup_mode = startup_mode
        self.current_mode = MODE_MULTI
        self.lift_current_dict = None  # 保存当前减量抽的字典
        self.multi_result = None
        self.multi_result_names = []
        self.lift_result = None
        self.lift_result_names = []

        self.ui = None
        self.page_multi = None
        self.page_lift = None
        self.page_scroll_multi = None
        self.page_scroll_lift = None
        self.stacked_widget = None

        self.action_multi = None
        self.action_single = None
        self.action_lift = None
        self.action_scroll_single = None
        self.action_scroll_multi = None
        self.action_scroll_lift = None
        self.action_exit = None
        self.action_license = None
        self.action_repository = None
        self.action_feedback_github = None
        self.action_feedback_email = None
        self.action_help = None
        self.action_program_log = None
        self.action_check_update = None
        self.action_init = None
        self.theme_actions = None
        self.language_actions = None
        self.roster_actions = None
        self.log_level_actions = None

        self.multi_button = None
        self.multi_view = None
        self.multi_quantity_label = None
        self.multi_up_button = None
        self.multi_down_button = None
        self.multi_quantity_slider = None
        self.lift_button = None
        self.lift_view = None
        self.lift_quantity_label = None
        self.lift_up_button = None
        self.lift_down_button = None
        self.lift_quantity_slider = None
        self.lift_renew_button = None

        self.scroll_multi_button = None
        self.scroll_multi_view = None
        self.scroll_multi_quantity_label = None
        self.scroll_multi_up_button = None
        self.scroll_multi_down_button = None
        self.scroll_multi_quantity_slider = None
        self.scroll_multi_controller = None

        self.scroll_lift_button = None
        self.scroll_lift_view = None
        self.scroll_lift_quantity_label = None
        self.scroll_lift_up_button = None
        self.scroll_lift_down_button = None
        self.scroll_lift_quantity_slider = None
        self.scroll_lift_renew_button = None
        self.scroll_lift_controller = None
        self._syncing_quantity = False
        self._quantity_touch_filters = []

        self.status_widgets = {}
        self.status_separators = []
        self.status_container = None
        self.status_message_label = None
        self.viewer_dialogs = {}
        self.background_layer = None
        self._background_enabled = False
        self._titlebar_applied = False
        self._resizable = True
        self._start_maximized = False
        self._temporary_maximized = False

        self._build_ui()
        self._apply_config_window()
        self._retranslate()
        self._update_status_info()
        if self.startup_warnings:
            self._show_status_message(
                self._t("state.startup_warning", files=", ".join(self.startup_warnings)), 0
            )

    # ------------------------------------------------------------------ helpers
    def _t(self, key, **values):
        return LanguageManager.translate(self.languages, self.current_language, key, **values)

    def _load_names(self) -> dict:
        names = getattr(importnames, "names", None)
        if isinstance(names, dict) and names:
            return names
        logging.warning("未能从 importnames 中读取姓名数据，使用空列表。")
        return {}

    def _app_config(self):
        config = getattr(importnames, "loaded_config", {})
        return config if isinstance(config, dict) else {}

    def _ui_config(self):
        config = self._app_config()
        ui = config.get("ui", {})
        return ui if isinstance(ui, dict) else {}

    def _status_config(self):
        config = self._app_config()
        status = config.get("statusbar", {})
        return status if isinstance(status, dict) else {}

    # ------------------------------------------------------------------ window
    def _apply_config_window(self):
        """每次启动都使用配置文件中的初始窗口尺寸。"""
        window = self._app_config().get("window", {})
        if not isinstance(window, dict):
            window = {}
        screen = self.screen() or QApplication.primaryScreen()
        geometry = screen.availableGeometry() if screen is not None else None
        screen_width = geometry.width() if geometry is not None else 1280
        screen_height = geometry.height() if geometry is not None else 800
        oversized_fixed = _fixed_size_exceeds_screen(window, screen_width, screen_height)
        self._temporary_maximized = oversized_fixed
        self._start_maximized = _window_is_maximized(window) or oversized_fixed
        self._resizable = window.get("resizable", True) is not False
        if oversized_fixed:
            # 固定尺寸大于可用屏幕时临时允许最大化与还原；不改写配置文件。
            self._resizable = True
        if self._start_maximized:
            # 最大化模式只约束最小尺寸，实际显示时由 showMaximized() 完成。
            self.setMinimumSize(640, 480)
            self.setMaximumSize(16777215, 16777215)
            if oversized_fixed:
                width, height = _configured_size(window, screen_width, screen_height)
                self.resize(min(width, screen_width), min(height, screen_height))
            if self.isVisible():
                self.showMaximized()
            return
        if self.isMaximized():
            self.showNormal()
        width, height = _configured_size(window, screen_width, screen_height)
        self.resize(width, height)
        if self._resizable:
            self.setMinimumSize(640, 480)
            self.setMaximumSize(16777215, 16777215)
        else:
            self.setFixedSize(width, height)
        if geometry is not None:
            self.move(
                geometry.center().x() - self.width() // 2,
                geometry.center().y() - self.height() // 2,
            )

    def closeEvent(self, event):
        for dialog in list(self.viewer_dialogs.values()):
            try:
                dialog.close()
            except Exception:
                pass
        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        # Windows 标题栏需要在窗口句柄有效后才能设置。
        QTimer.singleShot(0, self._apply_window_frame)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.background_layer is not None:
            central = self.centralWidget()
            if central is not None:
                self.background_layer.setGeometry(central.rect())
                self.background_layer.lower()

    # ------------------------------------------------------------------ UI build
    def _build_ui(self):
        try:
            self.ui_main = ui_main.Ui_MainWindow()
            self.ui_main.setupUi(self)
            self.stacked_widget = getattr(self.ui_main, "stackedWidget", None)
            if self.stacked_widget is None:
                raise RuntimeError("未找到 stackedWidget")
            self.setWindowTitle(self.windowTitle() or "randname")
        except Exception as exc:  # pragma: no cover - defensive path
            logging.exception("加载主窗口失败: %s", exc)
            self._show_error(self._t("menu.about"), self._t("error.window_init", error=str(exc)))
            return

        try:
            self._bind_menu_actions()
            self._build_theme_menu()
            self._build_language_menu()
            self._build_roster_menu()
            self._build_log_level_menu()
            self._load_pages()
            self._setup_background_layer()
            self._bind_page_actions()
            self._build_status_widgets()
            self._apply_ui_config()
            self._apply_theme_background(self.selected_theme)
        except Exception as exc:  # pragma: no cover - defensive path
            logging.exception("初始化界面控件失败: %s", exc)
            self._show_error(self._t("menu.about"), self._t("error.controls_init", error=str(exc)))

    def _bind_menu_actions(self):
        self.action_multi = getattr(self.ui_main, "action_Multi", None)
        self.action_single = getattr(self.ui_main, "action_Single", None)
        self.action_lift = getattr(self.ui_main, "action_Lift", None)
        self.action_scroll_single = getattr(self.ui_main, "action_ScrollSingle", None)
        self.action_scroll_multi = getattr(self.ui_main, "action_ScrollMulti", None)
        self.action_scroll_lift = getattr(self.ui_main, "action_ScrollLift", None)
        self.action_inputconfig = getattr(self.ui_main, "action_inputconfig", None)
        self.action_outputconfig = getattr(self.ui_main, "action_outputconfig", None)
        self.action_init = getattr(self.ui_main, "action_init", None)
        self.action_reinputconfig = getattr(self.ui_main, "action_reinputconfig", None)
        self.action_exit = getattr(self.ui_main, "action_exit", None)
        self.action_license = getattr(self.ui_main, "action_license", None)
        self.action_repository = getattr(self.ui_main, "action_repository", None)
        self.action_feedback_github = getattr(self.ui_main, "action_feedback_github", None)
        self.action_feedback_email = getattr(self.ui_main, "action_feedback_email", None)
        self.action_help = getattr(self.ui_main, "action_help", None)
        self.action_program_log = getattr(self.ui_main, "action_program_log", None)
        self.action_check_update = getattr(self.ui_main, "action_check_update", None)

        if self.action_multi:
            self.action_multi.triggered.connect(lambda: self._show_multi_page())
        if self.action_single:
            self.action_single.triggered.connect(self._show_single_page)
        if self.action_lift:
            self.action_lift.triggered.connect(lambda: self._show_lift_page())
        if self.action_scroll_single:
            self.action_scroll_single.triggered.connect(self._show_scroll_single_page)
        if self.action_scroll_multi:
            self.action_scroll_multi.triggered.connect(lambda: self._show_scroll_multi_page())
        if self.action_scroll_lift:
            self.action_scroll_lift.triggered.connect(lambda: self._show_scroll_lift_page())
        if self.action_inputconfig:
            self.action_inputconfig.triggered.connect(self._on_import_memory)
        if self.action_outputconfig:
            self.action_outputconfig.triggered.connect(self._on_export_memory)
        if self.action_init:
            self.action_init.triggered.connect(self._on_initialize)
        if self.action_reinputconfig:
            self.action_reinputconfig.triggered.connect(self._on_reload_config)
        if self.action_exit:
            self.action_exit.triggered.connect(self._on_exit)
        if self.action_license:
            self.action_license.triggered.connect(self._open_license)
        if self.action_repository:
            self.action_repository.triggered.connect(self._open_repository)
        if self.action_feedback_github:
            self.action_feedback_github.triggered.connect(self._open_feedback_github)
        if self.action_feedback_email:
            self.action_feedback_email.triggered.connect(self._open_feedback_email)
        if self.action_help:
            self.action_help.triggered.connect(self._open_help)
        if self.action_program_log:
            self.action_program_log.triggered.connect(self._show_program_log)
        if self.action_check_update:
            self.action_check_update.triggered.connect(self._open_update_check)

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

    def _build_status_widgets(self):
        status = self._status_config()
        # QStatusBar 的 addPermanentWidget 默认从右往左排列。这里放一个占满
        # 状态栏的容器，在容器内部用 QHBoxLayout 左对齐所有信息。
        container = QWidget(self)
        container.setObjectName("status_container")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(4)
        self.status_container = container
        self.status_message_label = QLabel("", container)
        self.status_message_label.setObjectName("status_message")
        layout.addWidget(self.status_message_label)

        keys = (
            ("mode", "show_mode"),
            ("roster", "show_roster"),
            ("quantity", "show_quantity"),
            ("theme", "show_theme"),
            ("language", "show_language"),
            ("log_level", "show_log_level"),
            ("version", "show_version"),
        )
        for key, option in keys:
            separator = QLabel("|", container)
            separator.setObjectName("status_separator")
            layout.addWidget(separator)
            label = QLabel("", container)
            label.setObjectName(f"status_{key}")
            label.setMargin(2)
            layout.addWidget(label)
            self.status_widgets[key] = label
            self.status_separators.append((separator, key))
            visible = status.get(option, True) is not False
            label.setVisible(visible)
            separator.setVisible(visible)
        layout.addStretch(1)
        self.statusBar().addPermanentWidget(container, 1)

    # ------------------------------------------------------------------ background / frame
    def _setup_background_layer(self):
        """把背景图层放到中央区域最底层，菜单栏和状态栏不覆盖图片。"""
        if BackgroundWidget is None:
            return
        central = self.centralWidget()
        if central is None:
            return
        self.background_layer = BackgroundWidget(central)
        self.background_layer.setObjectName("background_layer")
        self.background_layer.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground, False
        )
        self.background_layer.setAutoFillBackground(False)
        self.background_layer.setGeometry(central.rect())
        self.background_layer.show()
        self.background_layer.lower()
        if self.stacked_widget is not None:
            self.stacked_widget.raise_()

    def _set_background_style(self, enabled: bool):
        """切换背景时刷新 QSS 的透明规则。"""
        self._background_enabled = bool(enabled)
        self.setProperty("hasBackgroundImage", self._background_enabled)
        for widget in (self, self.centralWidget(), self.stacked_widget,
                       self.page_multi, self.page_lift,
                       self.page_scroll_multi, self.page_scroll_lift):
            if widget is None:
                continue
            try:
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.update()
            except Exception:
                pass
        # 祖先属性变化后，Qt 不会自动重算所有后代的选择器；重设一次样式表。
        app = QApplication.instance()
        if isinstance(app, QApplication) and app.styleSheet():
            app.setStyleSheet(app.styleSheet())

    def _apply_theme_background(self, theme_name: str):
        """主题切换时读取 [themes.<name>.background] 并应用。"""
        if self.background_layer is None:
            return
        theme = self.themes.get(theme_name, {})
        config = ThemeManager.background_config(theme)
        if config is None:
            self.background_layer.set_background(None)
            self._set_background_style(False)
            return
        path = ThemeManager.resolve_background_image(config.get("image", ""))
        settings = dict(config)
        settings["path"] = str(path)
        self.background_layer.set_background(settings)
        if not self.background_layer.has_image():
            StateManager.log("WARN", "background", error=f"missing {path}")
            self._set_background_style(False)
            return
        self._set_background_style(True)

    def _apply_window_frame(self):
        """在 Windows 上让标题栏跟随当前主题色。"""
        if WindowTheme is None:
            return
        try:
            theme = self.themes.get(self.selected_theme, {})
            colors = theme.get("colors", {}) if isinstance(theme, dict) else {}
            color_format = theme.get("color_format", "Hex") if isinstance(theme, dict) else "Hex"
            raw = theme.get("titlebar") if isinstance(theme, dict) else None
            if not isinstance(raw, str) or not raw.strip():
                raw = colors.get("titlebar")
            if not isinstance(raw, str) or not raw.strip():
                raw = colors.get("panel") or colors.get("background") or "#202124"
            color = ThemeManager.parse_color(raw, color_format, allow_alpha=False)
            if WindowTheme.apply_titlebar(int(self.winId()), color):
                self._titlebar_applied = True
        except Exception as exc:
            logging.debug("应用窗口标题栏颜色失败: %s", exc)

    def _show_status_message(self, text, _timeout=0):
        """在状态栏最左侧显示临时消息；信息区保持左对齐。"""
        if self.status_message_label is not None:
            self.status_message_label.setText(str(text))

    def _refresh_status_visibility(self):
        status = self._status_config()
        options = {
            "mode": "show_mode",
            "roster": "show_roster",
            "quantity": "show_quantity",
            "theme": "show_theme",
            "language": "show_language",
            "log_level": "show_log_level",
            "version": "show_version",
        }
        for key, label in self.status_widgets.items():
            visible = status.get(options.get(key, ""), True) is not False
            label.setVisible(visible)
        for separator, key in self.status_separators:
            separator.setVisible(status.get(options.get(key, ""), True) is not False)

    def _apply_ui_config(self):
        ui = self._ui_config()
        family = ui.get("font_family", "")
        family = family.strip() if isinstance(family, str) else ""
        button_size = ui.get("button_font_size")
        quantity_size = ui.get("quantity_font_size")

        def apply(widget, size):
            if widget is None:
                return
            font = widget.font()
            if family:
                font.setFamily(family)
            if isinstance(size, (int, float)) and size > 0:
                font.setPointSize(int(size))
            widget.setFont(font)

        for widget in (
            self.multi_button, self.multi_up_button, self.multi_down_button,
            self.lift_button, self.lift_up_button, self.lift_down_button, self.lift_renew_button,
            self.scroll_multi_button, self.scroll_multi_up_button,
            self.scroll_multi_down_button, self.scroll_lift_button,
            self.scroll_lift_up_button, self.scroll_lift_down_button,
            self.scroll_lift_renew_button,
        ):
            apply(widget, button_size)
        for widget in (
            self.multi_quantity_label, self.lift_quantity_label,
            self.scroll_multi_quantity_label, self.scroll_lift_quantity_label,
        ):
            apply(widget, quantity_size)

    # ------------------------------------------------------------------ menus / state
    def _select_log_level(self, level):
        selected = StateManager.configure_logging(level)
        self._build_log_level_menu()
        StateManager.log(selected, "log_level_changed", result=selected)
        self._show_status_message(self._t("state.log_level_changed", level=self._t(f"log.{selected}")))
        self._update_status_info()

    def _select_language(self, code):
        self.current_language = LanguageManager.resolve_language(code, self.languages)
        self._build_language_menu()
        self._build_theme_menu()
        self._build_roster_menu()
        self._build_log_level_menu()
        self._retranslate()
        self._show_status_message(
            self._t("state.language_changed", name=self.languages[self.current_language]["display_name"])
        )
        self._update_status_info()

    def _select_roster(self, key):
        self.names = importnames.select_roster(key)
        self.current_roster = importnames.active_roster
        self.lift_current_dict = None
        self.lift_result = None
        self.lift_result_names = []
        self._refresh_quantity_ranges()
        if self.lift_view is not None:
            self.lift_view.set_message(self._t("state.waiting"))
        if self.scroll_multi_controller is not None:
            self.scroll_multi_controller.set_quantity(self.scroll_multi_quantity)
            self.scroll_multi_controller.update_names(self.names)
        if self.scroll_lift_controller is not None:
            self.scroll_lift_controller.set_quantity(self.scroll_lift_quantity)
            self.scroll_lift_controller.update_names(self.names)
        self._build_roster_menu()
        roster = self.rosters.get(key, {})
        display_name = LanguageManager.localized_name(
            roster.get("name", {}), self.current_language, self.languages
        ) or key
        self._show_status_message(self._t("state.roster_changed", name=display_name))
        self._update_status_info()

    def _retranslate(self):
        self.ui_main.menu_file.setTitle(self._t("menu.file"))
        self.ui_main.menu_mode.setTitle(self._t("menu.mode"))
        self.ui_main.menu_theme.setTitle(self._t("menu.theme"))
        self.ui_main.menu_language.setTitle(self._t("menu.language"))
        self.ui_main.menu_roster.setTitle(self._t("menu.roster"))
        self.ui_main.menu_about.setTitle(self._t("menu.about"))
        self.ui_main.menu_log_level.setTitle(self._t("menu.log_level"))
        self.ui_main.menu_feedback.setTitle(self._t("menu.feedback"))
        for action, key in (
            (self.action_multi, "mode.Multi"),
            (self.action_single, "mode.Single"),
            (self.action_lift, "mode.Lift"),
            (self.action_scroll_single, "mode.ScrollSingle"),
            (self.action_scroll_multi, "mode.ScrollMulti"),
            (self.action_scroll_lift, "mode.ScrollLift"),
            (self.action_inputconfig, "action.import"),
            (self.action_outputconfig, "action.export"),
            (self.action_init, "action.init"),
            (self.action_reinputconfig, "action.reload"),
            (self.action_exit, "action.exit"),
            (self.action_license, "action.license"),
            (self.action_repository, "action.repository"),
            (self.action_feedback_github, "action.feedback.github"),
            (self.action_feedback_email, "action.feedback.email"),
            (self.action_help, "action.help"),
            (self.action_program_log, "action.program_log"),
            (self.action_check_update, "action.check_update"),
        ):
            if action is not None:
                action.setText(self._t(key))
        if hasattr(self, "ui_multi"):
            self.ui_multi.pushButton_Multi.setText(self._t("button.draw"))
            self.ui_multi.pushButton_MultiQuantityUp.setText(self._t("button.increase"))
            self.ui_multi.pushButton_MultiQuantityDown.setText(self._t("button.decrease"))
            if self.multi_view is not None:
                if self.multi_result_names:
                    self.multi_view.set_names(self.multi_result_names, use_lock=False)
                else:
                    self.multi_view.set_message(self._t("state.waiting"))
        if hasattr(self, "ui_lift"):
            self.ui_lift.pushButton_Lift.setText(self._t("button.draw"))
            self.ui_lift.pushButton_LiftQuantityUp.setText(self._t("button.increase"))
            self.ui_lift.pushButton_LiftQuantityDown.setText(self._t("button.decrease"))
            self.ui_lift.pushButton_LiftRenew.setText(self._t("button.reset"))
            if self.lift_view is not None:
                if self.lift_result_names:
                    self.lift_view.set_names(self.lift_result_names, use_lock=False)
                else:
                    self.lift_view.set_message(self._t("state.waiting"))
        if hasattr(self, "ui_scroll_multi"):
            self.ui_scroll_multi.pushButton_ScrollMulti.setText(self._t("button.draw"))
            self.ui_scroll_multi.pushButton_ScrollMultiQuantityUp.setText(self._t("button.increase"))
            self.ui_scroll_multi.pushButton_ScrollMultiQuantityDown.setText(self._t("button.decrease"))
            if self.scroll_multi_controller is not None:
                self.scroll_multi_controller.set_button_texts(
                    self._t("button.draw"), self._t("button.stop_scroll_multi"),
                    self._t("state.waiting"),
                )
        if hasattr(self, "ui_scroll_lift"):
            self.ui_scroll_lift.pushButton_ScrollLift.setText(self._t("button.draw"))
            self.ui_scroll_lift.pushButton_ScrollLiftQuantityUp.setText(self._t("button.increase"))
            self.ui_scroll_lift.pushButton_ScrollLiftQuantityDown.setText(self._t("button.decrease"))
            self.ui_scroll_lift.pushButton_ScrollLiftRenew.setText(self._t("button.reset"))
            if self.scroll_lift_controller is not None:
                self.scroll_lift_controller.set_button_texts(
                    self._t("button.draw"), self._t("button.stop_scroll_multi"),
                    self._t("state.waiting"),
                )

    def _select_theme(self, name):
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return
        try:
            self.selected_theme = ThemeManager.apply_theme(app, name, self.themes)
            StateManager.log("INFO", "theme", result=self.selected_theme)
            self._apply_theme_background(self.selected_theme)
            self._apply_window_frame()
            theme = self.themes.get(self.selected_theme, {})
            theme_name = LanguageManager.localized_name(
                theme.get("name", {}), self.current_language, self.languages
            ) or self.selected_theme
            self._show_status_message(self._t("state.theme_changed", name=theme_name))
            self._update_status_info()
        except (OSError, ValueError, KeyError) as exc:
            StateManager.log("ERROR", "theme", error=str(exc))
            self._show_error(self._t("menu.theme"), self._t("error.theme_failed", error=str(exc)))

    # ------------------------------------------------------------------ pages
    @staticmethod
    def _normalize_mode(mode):
        if isinstance(mode, str):
            lowered = mode.lower().replace("_", "")
            if lowered == "single":
                return MODE_MULTI, 1
            if lowered == "scrollsingle":
                return MODE_SCROLL_MULTI, 1
            if lowered in ("multi", "lift", "scrollmulti", "scrolllift"):
                return {
                    "multi": MODE_MULTI,
                    "lift": MODE_LIFT,
                    "scrollmulti": MODE_SCROLL_MULTI,
                    "scrolllift": MODE_SCROLL_LIFT,
                }[lowered], None
        return MODE_MULTI, None

    def _load_pages(self):
        if self.stacked_widget is None:
            raise RuntimeError("stackedWidget 未初始化")
        self.page_multi = QWidget()
        self.ui_multi = ui_widgetmulti.Ui_Form()
        self.ui_multi.setupUi(self.page_multi)
        self.page_lift = QWidget()
        self.ui_lift = ui_widgetlift.Ui_Form()
        self.ui_lift.setupUi(self.page_lift)
        self.page_scroll_multi = QWidget()
        self.ui_scroll_multi = ui_widgetscrollmulti.Ui_Form()
        self.ui_scroll_multi.setupUi(self.page_scroll_multi)
        self.page_scroll_lift = QWidget()
        self.ui_scroll_lift = ui_widgetscrolllift.Ui_Form()
        self.ui_scroll_lift.setupUi(self.page_scroll_lift)

        for page in (
            self.page_multi, self.page_lift, self.page_scroll_multi, self.page_scroll_lift
        ):
            self.stacked_widget.addWidget(page)

        app_config = self._app_config().get("app", {})
        configured_mode = app_config.get("default_mode", MODE_MULTI) if isinstance(app_config, dict) else MODE_MULTI
        mode = self.startup_mode or configured_mode
        normalized, quantity = self._normalize_mode(mode)
        if quantity is not None:
            if normalized == MODE_MULTI:
                self.multi_quantity = quantity
            elif normalized == MODE_SCROLL_MULTI:
                self.scroll_multi_quantity = quantity
        if normalized == MODE_LIFT:
            self._show_lift_page()
        elif normalized == MODE_SCROLL_MULTI:
            self._show_scroll_multi_page()
        elif normalized == MODE_SCROLL_LIFT:
            self._show_scroll_lift_page()
        else:
            self._show_multi_page()

    def _bind_page_actions(self):
        config = self._app_config()
        rate = _rate_from_config(config)

        # Multi
        self.multi_button = getattr(self.ui_multi, "pushButton_Multi", None)
        output = getattr(self.ui_multi, "label_MultiOutput", None)
        if output is not None:
            self.multi_view = OutputView(output, config, 33)
        self.multi_quantity_label = getattr(self.ui_multi, "label_MultiQuantity", None)
        self.multi_up_button = getattr(self.ui_multi, "pushButton_MultiQuantityUp", None)
        self.multi_down_button = getattr(self.ui_multi, "pushButton_MultiQuantityDown", None)
        self.multi_quantity_slider = getattr(self.ui_multi, "verticalSlider_MultiQuantity", None)
        self._prepare_quantity_slider(self.multi_quantity_slider, MODE_MULTI)
        self._set_quantity_label(self.multi_quantity_label, self.multi_quantity)
        if self.multi_up_button is not None:
            self.multi_up_button.clicked.connect(lambda: self._adjust_quantity(MODE_MULTI, 1))
        if self.multi_down_button is not None:
            self.multi_down_button.clicked.connect(lambda: self._adjust_quantity(MODE_MULTI, -1))
        if self.multi_button is not None:
            self.multi_button.clicked.connect(self._handle_multi)
        if self.multi_view is not None:
            self.multi_view.set_message(self._t("state.waiting"))

        # Lift
        self.lift_button = getattr(self.ui_lift, "pushButton_Lift", None)
        output = getattr(self.ui_lift, "label_LiftOutput", None)
        if output is not None:
            self.lift_view = OutputView(output, config, 33)
        self.lift_quantity_label = getattr(self.ui_lift, "label_LiftQuantity", None)
        self.lift_up_button = getattr(self.ui_lift, "pushButton_LiftQuantityUp", None)
        self.lift_down_button = getattr(self.ui_lift, "pushButton_LiftQuantityDown", None)
        self.lift_quantity_slider = getattr(self.ui_lift, "verticalSlider_LiftQuantity", None)
        self._prepare_quantity_slider(self.lift_quantity_slider, MODE_LIFT)
        self.lift_renew_button = getattr(self.ui_lift, "pushButton_LiftRenew", None)
        self._set_quantity_label(self.lift_quantity_label, self.lift_quantity)
        if self.lift_up_button is not None:
            self.lift_up_button.clicked.connect(lambda: self._adjust_quantity(MODE_LIFT, 1))
        if self.lift_down_button is not None:
            self.lift_down_button.clicked.connect(lambda: self._adjust_quantity(MODE_LIFT, -1))
        if self.lift_renew_button is not None:
            self.lift_renew_button.clicked.connect(self._reset_lift_page)
        if self.lift_button is not None:
            self.lift_button.clicked.connect(self._handle_lift)
        if self.lift_view is not None:
            self.lift_view.set_message(self._t("state.waiting"))

        # ScrollMulti
        try:
            self.scroll_multi_button = getattr(self.ui_scroll_multi, "pushButton_ScrollMulti", None)
            self.scroll_multi_quantity_label = getattr(self.ui_scroll_multi, "label_ScrollMultiQuantity", None)
            output = getattr(self.ui_scroll_multi, "label_ScrollMultiOutput", None)
            if output is not None:
                self.scroll_multi_view = SlotOutputView(output, config, 33)
            self.scroll_multi_up_button = getattr(self.ui_scroll_multi, "pushButton_ScrollMultiQuantityUp", None)
            self.scroll_multi_down_button = getattr(self.ui_scroll_multi, "pushButton_ScrollMultiQuantityDown", None)
            self.scroll_multi_quantity_slider = getattr(
                self.ui_scroll_multi, "verticalSlider_ScrollMultiQuantity", None
            )
            self._prepare_quantity_slider(self.scroll_multi_quantity_slider, MODE_SCROLL_MULTI)
            self._set_quantity_label(self.scroll_multi_quantity_label, self.scroll_multi_quantity)
            if self.scroll_multi_up_button is not None:
                self.scroll_multi_up_button.clicked.connect(lambda: self._adjust_quantity(MODE_SCROLL_MULTI, 1))
            if self.scroll_multi_down_button is not None:
                self.scroll_multi_down_button.clicked.connect(lambda: self._adjust_quantity(MODE_SCROLL_MULTI, -1))
            if self.scroll_multi_button is not None and self.scroll_multi_view is not None:
                self.scroll_multi_controller = ScrollMulti.ScrollMultiController(
                    self.scroll_multi_view,
                    self.scroll_multi_button,
                    self.names,
                    on_result=self._on_scroll_multi_result,
                    rate=rate,
                    draw_text=self._t("button.draw"),
                    stop_format=self._t("button.stop_scroll_multi"),
                    reset_text=self._t("state.waiting"),
                    on_warning=lambda count: self._on_scroll_warning(MODE_SCROLL_MULTI, count),
                )
                self.scroll_multi_controller.set_quantity(self.scroll_multi_quantity)
        except Exception as exc:
            logging.exception("初始化 ScrollMulti 失败: %s", exc)

        # ScrollLift
        try:
            self.scroll_lift_button = getattr(self.ui_scroll_lift, "pushButton_ScrollLift", None)
            self.scroll_lift_quantity_label = getattr(self.ui_scroll_lift, "label_ScrollLiftQuantity", None)
            output = getattr(self.ui_scroll_lift, "label_ScrollLiftOutput", None)
            if output is not None:
                self.scroll_lift_view = SlotOutputView(output, config, 33)
            self.scroll_lift_up_button = getattr(self.ui_scroll_lift, "pushButton_ScrollLiftQuantityUp", None)
            self.scroll_lift_down_button = getattr(self.ui_scroll_lift, "pushButton_ScrollLiftQuantityDown", None)
            self.scroll_lift_quantity_slider = getattr(
                self.ui_scroll_lift, "verticalSlider_ScrollLiftQuantity", None
            )
            self._prepare_quantity_slider(self.scroll_lift_quantity_slider, MODE_SCROLL_LIFT)
            self.scroll_lift_renew_button = getattr(self.ui_scroll_lift, "pushButton_ScrollLiftRenew", None)
            self._set_quantity_label(self.scroll_lift_quantity_label, self.scroll_lift_quantity)
            if self.scroll_lift_up_button is not None:
                self.scroll_lift_up_button.clicked.connect(lambda: self._adjust_quantity(MODE_SCROLL_LIFT, 1))
            if self.scroll_lift_down_button is not None:
                self.scroll_lift_down_button.clicked.connect(lambda: self._adjust_quantity(MODE_SCROLL_LIFT, -1))
            if self.scroll_lift_renew_button is not None:
                self.scroll_lift_renew_button.clicked.connect(self._reset_scroll_lift_page)
            if self.scroll_lift_button is not None and self.scroll_lift_view is not None:
                self.scroll_lift_controller = ScrollLift.ScrollLiftController(
                    self.scroll_lift_view,
                    self.scroll_lift_button,
                    self.names,
                    on_result=self._on_scroll_lift_result,
                    rate=rate,
                    draw_text=self._t("button.draw"),
                    stop_format=self._t("button.stop_scroll_multi"),
                    reset_text=self._t("state.waiting"),
                    on_warning=lambda count: self._on_scroll_warning(MODE_SCROLL_LIFT, count),
                )
                self.scroll_lift_controller.set_quantity(self.scroll_lift_quantity)
        except Exception as exc:
            logging.exception("初始化 ScrollLift 失败: %s", exc)

        self._refresh_quantity_ranges()

    def _show_multi_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_multi)
        self.current_mode = MODE_MULTI
        self._update_status_info()

    def _show_single_page(self):
        self._set_quantity(MODE_MULTI, 1, log=False)
        self._show_multi_page()

    def _show_lift_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_lift)
        self.current_mode = MODE_LIFT
        self._update_status_info()

    def _show_scroll_single_page(self):
        self._set_quantity(MODE_SCROLL_MULTI, 1, log=False)
        self._show_scroll_multi_page()

    def _show_scroll_multi_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_scroll_multi)
        self.current_mode = MODE_SCROLL_MULTI
        self._update_status_info()

    def _show_scroll_lift_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_scroll_lift)
        self.current_mode = MODE_SCROLL_LIFT
        self._update_status_info()

    # ------------------------------------------------------------------ status bar
    def _current_quantity(self):
        return {
            MODE_MULTI: self.multi_quantity,
            MODE_LIFT: self.lift_quantity,
            MODE_SCROLL_MULTI: self.scroll_multi_quantity,
            MODE_SCROLL_LIFT: self.scroll_lift_quantity,
        }.get(self.current_mode, self.multi_quantity)

    def _localized_roster_name(self, key):
        roster = self.rosters.get(key, {})
        return LanguageManager.localized_name(
            roster.get("name", {}), self.current_language, self.languages
        ) or key

    def _update_status_info(self):
        if not self.status_widgets:
            return
        mode_key = {
            MODE_MULTI: "mode.Multi",
            MODE_LIFT: "mode.Lift",
            MODE_SCROLL_MULTI: "mode.ScrollMulti",
            MODE_SCROLL_LIFT: "mode.ScrollLift",
        }.get(self.current_mode, "mode.Multi")
        theme = self.themes.get(self.selected_theme, {})
        theme_name = LanguageManager.localized_name(
            theme.get("name", {}), self.current_language, self.languages
        ) or self.selected_theme
        language_name = self.languages.get(self.current_language, {}).get("display_name", self.current_language)
        values = {
            "mode": self._t("status.mode", name=self._t(mode_key)),
            "roster": self._t("status.roster", name=self._localized_roster_name(self.current_roster)),
            "quantity": self._t("status.quantity", count=self._current_quantity()),
            "theme": self._t("status.theme", name=theme_name),
            "language": self._t("status.language", name=language_name),
            "log_level": self._t("status.log_level", name=self._t(f"log.{StateManager.CURRENT_LOG_LEVEL}")),
            "version": self._t("status.version", version=APP_VERSION),
        }
        for key, label in self.status_widgets.items():
            label.setText(values.get(key, ""))

    # ------------------------------------------------------------------ memory
    @staticmethod
    def _remembered_result(entry):
        if entry is None:
            return None
        if isinstance(entry, dict) and "result" in entry:
            return entry.get("result")
        return entry

    @staticmethod
    def _names_from_result(result):
        if not isinstance(result, dict):
            return [str(result)] if result is not None else []
        outdict = result.get("outdict", {})
        names = []
        if isinstance(outdict, dict):
            for value in outdict.values():
                if isinstance(value, dict):
                    if "name" in value:
                        names.append(str(value["name"]))
                    elif len(value) == 1:
                        names.append(str(next(iter(value.values()))))
                    else:
                        names.append(str(value))
                else:
                    names.append(str(value))
        return names

    def _apply_memory_import(self, content: dict):
        try:
            if not isinstance(content, dict):
                return
            last = content.get("last_results", {})
            if not isinstance(last, dict):
                return
            if self.multi_view is not None:
                result = self._remembered_result(last.get("Multi", last.get("multi")))
                if result is not None:
                    names = self._names_from_result(result)
                    self.multi_result_names = names
                    self.multi_result = self._format_output_result(result)
                    if names:
                        self.multi_view.set_names(names, use_lock=False)
            if self.lift_view is not None:
                result = self._remembered_result(last.get("Lift", last.get("lift")))
                if result is not None:
                    names = self._names_from_result(result)
                    self.lift_result_names = names
                    self.lift_result = self._format_output_result(result)
                    if names:
                        self.lift_view.set_names(names, use_lock=False)
            if self.scroll_multi_controller is not None:
                result = self._remembered_result(
                    last.get("ScrollMulti", last.get("scrollmulti"))
                )
                if result is not None:
                    self.scroll_multi_controller.show_result(result)
            if self.scroll_lift_controller is not None:
                result = self._remembered_result(
                    last.get("ScrollLift", last.get("scrolllift"))
                )
                if result is not None:
                    self.scroll_lift_controller.show_result(result)
        except Exception as exc:
            logging.exception("应用导入记忆失败: %s", exc)

    # ------------------------------------------------------------------ draws
    def _handle_multi(self):
        try:
            logging.info("执行多抽，数量=%s", self.multi_quantity)
            result = multi_module.Multi(self.names, self.multi_quantity)
            names = self._names_from_result(result)
            self.multi_result_names = names
            self.multi_result = self._format_output_result(result)
            if self.multi_view is not None:
                if names:
                    self.multi_view.set_names(names, use_lock=False)
                else:
                    self.multi_view.set_message(self._t("state.no_result"))
            self._show_status_message(
                self._t("state.multi_result", count=self.multi_quantity)
            )
            self._update_status_info()
            try:
                state = StateManager.load_memory()
                state.setdefault("last_results", {})["Multi"] = {
                    "result": result, "time": StateManager._now_iso()
                }
                StateManager.save_memory(state)
                StateManager.log("INFO", "Multi", result=result)
            except Exception:
                logging.exception("记录 multi 结果失败")
        except Exception as exc:
            logging.exception("多抽执行失败: %s", exc)
            self.multi_result_names = []
            self.multi_result = self._t("dialog.operation_failed", error=str(exc))
            if self.multi_view is not None:
                self.multi_view.set_message(self.multi_result)
            self._show_error(self._t("mode.Multi"), str(exc))
            try:
                StateManager.log("ERROR", "Multi", error=str(exc))
            except Exception:
                pass

    def _handle_lift(self):
        try:
            logging.info("执行减量抽，数量=%s", self.lift_quantity)
            lift_dict = self.names if self.lift_current_dict is None else self.lift_current_dict
            result = lift_module.Lift(self.names, lift_dict, self.lift_quantity)
            names = self._names_from_result(result)
            self.lift_result_names = names
            self.lift_result = self._format_output_result(result)
            if self.lift_view is not None:
                if names:
                    self.lift_view.set_names(names, use_lock=False)
                else:
                    self.lift_view.set_message(self._t("state.no_result"))
            if "Liftdict" in result:
                self.lift_current_dict = result["Liftdict"]
            self._show_status_message(
                self._t("state.lift_result", count=self.lift_quantity)
            )
            self._update_status_info()
            try:
                state = StateManager.load_memory()
                state.setdefault("last_results", {})["Lift"] = {
                    "result": result, "time": StateManager._now_iso()
                }
                StateManager.save_memory(state)
                StateManager.log("INFO", "Lift", result=result)
            except Exception:
                logging.exception("记录 lift 结果失败")
        except Exception as exc:
            logging.exception("减量抽执行失败: %s", exc)
            self.lift_result_names = []
            self.lift_result = self._t("dialog.operation_failed", error=str(exc))
            if self.lift_view is not None:
                self.lift_view.set_message(self.lift_result)
            self._show_error(self._t("mode.Lift"), str(exc))
            try:
                StateManager.log("ERROR", "Lift", error=str(exc))
            except Exception:
                pass

    def _on_scroll_multi_result(self, result, meta):
        try:
            logging.info("ScrollMulti result: %s", result)
            selected = 0
            if isinstance(result, dict):
                quantity = result.get("quantity", {})
                if isinstance(quantity, dict):
                    selected = quantity.get("selected", 0)
            self._show_status_message(
                self._t("state.scroll_multi_result", count=selected)
            )
            self._update_status_info()
            state = StateManager.load_memory()
            state.setdefault("last_results", {})["ScrollMulti"] = {"result": result, "meta": meta}
            StateManager.save_memory(state)
            StateManager.log("INFO", "ScrollMulti", result=result)
        except Exception as exc:
            logging.exception("处理 ScrollMulti 结果失败: %s", exc)
            try:
                StateManager.log("ERROR", "ScrollMulti", error=str(exc))
            except Exception:
                pass

    def _on_scroll_lift_result(self, result, meta):
        try:
            logging.info("ScrollLift result: %s", result)
            selected = 0
            if isinstance(result, dict):
                quantity = result.get("quantity", {})
                if isinstance(quantity, dict):
                    selected = quantity.get("selected", 0)
            self._show_status_message(
                self._t("state.scroll_lift_result", count=selected)
            )
            self._update_status_info()
            state = StateManager.load_memory()
            state.setdefault("last_results", {})["ScrollLift"] = {"result": result, "meta": meta}
            StateManager.save_memory(state)
            StateManager.log("INFO", "ScrollLift", result=result)
        except Exception as exc:
            logging.exception("处理 ScrollLift 结果失败: %s", exc)
            try:
                StateManager.log("ERROR", "ScrollLift", error=str(exc))
            except Exception:
                pass

    def _on_scroll_warning(self, mode, count):
        try:
            if mode == MODE_SCROLL_LIFT and count == 0:
                key = "state.scroll_lift_empty"
                self._show_status_message(self._t(key))
            elif mode == MODE_SCROLL_LIFT:
                key = "state.scroll_lift_invalid"
                self._show_status_message(self._t(key, count=count))
            else:
                key = "state.scroll_multi_invalid"
                self._show_status_message(self._t(key, count=count))
            StateManager.log("WARN", mode, error=f"requested more than {count}")
        except Exception:
            pass

    def _quantity_controls(self, mode):
        """返回指定模式的（滑动条、数值标签、滚动控制器）。"""
        return {
            MODE_MULTI: (self.multi_quantity_slider, self.multi_quantity_label, None),
            MODE_LIFT: (self.lift_quantity_slider, self.lift_quantity_label, None),
            MODE_SCROLL_MULTI: (
                self.scroll_multi_quantity_slider,
                self.scroll_multi_quantity_label,
                self.scroll_multi_controller,
            ),
            MODE_SCROLL_LIFT: (
                self.scroll_lift_quantity_slider,
                self.scroll_lift_quantity_label,
                self.scroll_lift_controller,
            ),
        }.get(mode, (None, None, None))

    def _prepare_quantity_slider(self, slider, mode):
        """安装触控过滤器并连接数值变化信号。"""
        if slider is None:
            return
        slider.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        touch_filter = _QuantitySliderTouchFilter(slider)
        slider.installEventFilter(touch_filter)
        self._quantity_touch_filters.append(touch_filter)
        slider.valueChanged.connect(
            lambda value, selected_mode=mode: self._on_quantity_slider_changed(selected_mode, value)
        )

    def _set_quantity(self, mode, value, *, log=True):
        """统一更新数量值、标签、滑动条和滚动控制器。"""
        maximum = max(1, len(self.names))
        value = _clamp_quantity(value, maximum)
        if mode == MODE_MULTI:
            self.multi_quantity = value
            logging_message = "更新多抽数量=%s"
        elif mode == MODE_LIFT:
            self.lift_quantity = value
            logging_message = "更新减量抽数量=%s"
        elif mode == MODE_SCROLL_MULTI:
            self.scroll_multi_quantity = value
            logging_message = "更新滚动多抽数量=%s"
        elif mode == MODE_SCROLL_LIFT:
            self.scroll_lift_quantity = value
            logging_message = "更新滚动减量抽数量=%s"
        else:
            return value

        slider, label, controller = self._quantity_controls(mode)
        self._syncing_quantity = True
        try:
            if label is not None:
                label.setText(str(value))
            if slider is not None:
                slider.setRange(1, maximum)
                slider.setPageStep(max(1, (maximum - 1) // 10))
                if slider.value() != value:
                    slider.setValue(value)
        finally:
            self._syncing_quantity = False
        if controller is not None:
            controller.set_quantity(value)
        if log:
            logging.info(logging_message, value)
        return value

    def _quantity_value(self, mode):
        return {
            MODE_MULTI: self.multi_quantity,
            MODE_LIFT: self.lift_quantity,
            MODE_SCROLL_MULTI: self.scroll_multi_quantity,
            MODE_SCROLL_LIFT: self.scroll_lift_quantity,
        }.get(mode, 1)

    def _refresh_quantity_ranges(self):
        """名单或数量上下限变化后，同步四个模式的全部数量控件。"""
        for mode in (MODE_MULTI, MODE_LIFT, MODE_SCROLL_MULTI, MODE_SCROLL_LIFT):
            self._set_quantity(mode, self._quantity_value(mode), log=False)

    def _on_quantity_slider_changed(self, mode, value):
        if self._syncing_quantity:
            return
        self._set_quantity(mode, value, log=False)
        self._update_status_info()

    def _adjust_quantity(self, mode, delta):
        self._set_quantity(mode, self._quantity_value(mode) + delta)
        self._update_status_info()

    def _reset_lift_page(self):
        self.lift_current_dict = None
        self.lift_result = None
        self.lift_result_names = []
        self._set_quantity_label(self.lift_quantity_label, self.lift_quantity)
        if self.lift_view is not None:
            self.lift_view.set_message(self._t("state.waiting"))
        self._show_status_message(self._t("state.waiting"))

    def _reset_scroll_lift_page(self):
        if self.scroll_lift_controller is not None:
            self.scroll_lift_controller.reset()
        if self.scroll_lift_view is not None:
            self.scroll_lift_view.set_message(self._t("state.waiting"))
        self._show_status_message(self._t("state.waiting"))

    # ------------------------------------------------------------------ display helpers
    def _set_quantity_label(self, label, value):
        if label is not None:
            label.setText(str(value))

    def _format_output_result(self, result):
        if not isinstance(result, dict):
            return str(result)
        names = self._names_from_result(result)
        if names:
            return "  ".join(names)
        return self._t("state.no_result")

    # ------------------------------------------------------------------ file menu
    def _on_import_memory(self):
        try:
            fname, _ = QFileDialog.getOpenFileName(
                self, self._t("dialog.import_title"), "", self._t("dialog.json_filter")
            )
            if not fname:
                return
            StateManager.import_memory(
                Path(fname),
                apply_callback=self._apply_memory_import,
            )
            QMessageBox.information(
                self, self._t("dialog.import_title"), self._t("dialog.import_success", path=fname)
            )
        except Exception as exc:
            logging.exception("导入记忆失败: %s", exc)
            QMessageBox.warning(
                self, self._t("dialog.import_title"),
                self._t("dialog.operation_failed", error=str(exc)),
            )

    def _on_export_memory(self):
        try:
            fname, _ = QFileDialog.getSaveFileName(
                self, self._t("dialog.export_title"), "memory-export.json",
                self._t("dialog.json_filter"),
            )
            if not fname:
                return
            StateManager.export_memory(Path(fname))
            QMessageBox.information(
                self, self._t("dialog.export_title"), self._t("dialog.export_success", path=fname)
            )
        except Exception as exc:
            logging.exception("导出记忆失败: %s", exc)
            QMessageBox.warning(
                self, self._t("dialog.export_title"),
                self._t("dialog.operation_failed", error=str(exc)),
            )

    def _on_reload_config(self):
        try:
            previous_theme = self.selected_theme
            previous_language = self.current_language
            previous_roster = self.current_roster
            previous_names = self.names.copy()
            previous_status = (self.status_message_label.text()
                               if self.status_message_label is not None else "")
            importnames.reload_data()
            cfg = importnames.loaded_config
            self.rosters = importnames.rosters
            roster_key = previous_roster if previous_roster in self.rosters else importnames.active_roster
            self.names = importnames.select_roster(roster_key)
            self.current_roster = importnames.active_roster
            roster_changed = previous_names != self.names
            if roster_changed:
                self.lift_current_dict = None
            self._refresh_quantity_ranges()
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
            self._apply_ui_config()
            self._apply_config_window()
            self._refresh_status_visibility()
            rate = _rate_from_config(cfg)
            if self.multi_view is not None:
                self.multi_view.configure(cfg, 30)
            if self.lift_view is not None:
                self.lift_view.configure(cfg, 30)
            if self.scroll_multi_view is not None:
                self.scroll_multi_view.configure(cfg, 30)
            if self.scroll_multi_controller is not None:
                self.scroll_multi_controller.update_rate(rate)
                self.scroll_multi_controller.set_quantity(self.scroll_multi_quantity)
                if roster_changed:
                    self.scroll_multi_controller.update_names(self.names)
            if self.scroll_lift_view is not None:
                self.scroll_lift_view.configure(cfg, 30)
            if self.scroll_lift_controller is not None:
                self.scroll_lift_controller.update_rate(rate)
                self.scroll_lift_controller.set_quantity(self.scroll_lift_quantity)
                if roster_changed:
                    self.scroll_lift_controller.update_names(self.names)
            if self.themes:
                app = QApplication.instance()
                if isinstance(app, QApplication):
                    self.selected_theme = ThemeManager.apply_theme(app, self.selected_theme, self.themes)
            self._apply_theme_background(self.selected_theme)
            self._apply_window_frame()
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
                self._show_status_message(
                    self._t("state.startup_warning", files=", ".join(warnings)), 0
                )
            else:
                self._show_status_message(previous_status)
            self._update_status_info()
        except Exception as exc:
            logging.exception("重新加载配置失败: %s", exc)
            QMessageBox.warning(
                self, self._t("action.reload"),
                self._t("dialog.operation_failed", error=str(exc)),
            )

    # ------------------------------------------------------------------ initialize
    def _on_initialize(self):
        """清空记忆与本次运行状态，所有模式回到数量 1。"""
        answer = QMessageBox.question(
            self,
            self._t("dialog.init_title"),
            self._t("dialog.init_confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            StateManager.reset_memory()
            for mode in (MODE_MULTI, MODE_LIFT, MODE_SCROLL_MULTI, MODE_SCROLL_LIFT):
                self._set_quantity(mode, 1, log=False)
            self.multi_result = None
            self.multi_result_names = []
            self.lift_current_dict = None
            self.lift_result = None
            self.lift_result_names = []
            if self.multi_view is not None:
                self.multi_view.set_message(self._t("state.waiting"))
            if self.lift_view is not None:
                self.lift_view.set_message(self._t("state.waiting"))
            if self.scroll_multi_controller is not None:
                self.scroll_multi_controller.reset()
            if self.scroll_lift_controller is not None:
                self.scroll_lift_controller.reset()
            if self.background_layer is not None:
                self.background_layer.clear_cache()
            QPixmapCache.clear()
            gc.collect()
            self._update_status_info()
            self._show_status_message(self._t("state.initialized"))
            # 初始化本身要留痕，但不清空任何历史日志。
            StateManager.log("INFO", "initialize", result="all modes reset")
        except Exception as exc:
            logging.exception("初始化失败: %s", exc)
            QMessageBox.warning(
                self, self._t("dialog.init_title"),
                self._t("dialog.operation_failed", error=str(exc)),
            )

    # ------------------------------------------------------------------ about menu
    def _viewer_option(self):
        return self._app_config()

    def _open_viewer(self, title, path: Path, *, markdown: bool, empty_text: str = "",
                     text_provider=None, highlight_log: bool = False):
        key = str(path.resolve()) if path.exists() else str(path)
        if text_provider is not None:
            key = f"{key}#session"
        existing = self.viewer_dialogs.get(key)
        if existing is not None:
            try:
                existing.show()
                existing.raise_()
                existing.activateWindow()
                return True
            except Exception:
                self.viewer_dialogs.pop(key, None)
        dialog = TextViewerDialog(
            self, title, path, markdown=markdown, config=self._viewer_option(),
            translate=self._t, empty_text=empty_text, close_text=self._t("action.close"),
            text_provider=text_provider, highlight_log=highlight_log,
        )
        self.viewer_dialogs[key] = dialog
        dialog.destroyed.connect(lambda _obj=None, k=key: self.viewer_dialogs.pop(k, None))
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        return True

    def _show_document(self, title: str, path: Path, *, markdown: bool) -> bool:
        if not path.is_file():
            StateManager.log("ERROR", "read_document", error=f"{path}: missing")
            self._show_error(title, self._t("dialog.operation_failed", error=str(path)))
            return False
        self._open_viewer(title, path, markdown=markdown)
        StateManager.log("INFO", "open_document", result=path.name)
        return True

    def _show_program_log(self):
        self._open_viewer(
            self._t("action.program_log"), StateManager.LOG_PATH, markdown=False,
            empty_text=self._t("state.no_logs"),
            text_provider=StateManager.session_log_text,
            highlight_log=True,
        )

    def _open_help(self):
        language = self.current_language if self.current_language in {"en_US", "zh_CN", "zh_TW"} else "en_US"
        help_paths = [DOC_DIR / f"help_{language}.md"]
        if language != "en_US":
            help_paths.append(DOC_DIR / "help_en_US.md")
        for help_path in help_paths:
            if help_path.is_file():
                self._show_document(self._t("action.help"), help_path, markdown=True)
                return
        self._show_error(
            self._t("action.help"), self._t("error.help_missing", path=str(help_paths[-1]))
        )

    def _open_license(self):
        try:
            license_path = LICENSE_PATH
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
            logging.info("打开项目仓库: %s", REPOSITORY_URL)
            QDesktopServices.openUrl(QUrl(REPOSITORY_URL))
        except Exception as exc:
            logging.exception("打开仓库链接失败: %s", exc)
            self._show_error(
                self._t("action.repository"),
                self._t("error.open_repository", error=str(exc)),
            )

    def _open_feedback_github(self):
        try:
            logging.info("打开反馈页面: %s", FEEDBACK_URL)
            QDesktopServices.openUrl(QUrl(FEEDBACK_URL))
        except Exception as exc:
            logging.exception("打开反馈链接失败: %s", exc)
            self._show_error(
                self._t("menu.feedback"),
                self._t("error.open_feedback", error=str(exc)),
            )

    def _open_feedback_email(self):
        mailto = f"mailto:{EMAIL_ADDRESS}?subject=randname%20feedback"
        try:
            logging.info("打开邮件反馈: %s", EMAIL_ADDRESS)
            if QDesktopServices.openUrl(QUrl(mailto)):
                return
        except Exception:
            logging.exception("打开邮件客户端失败")
        QMessageBox.information(
            self,
            self._t("menu.feedback"),
            self._t("dialog.email_fallback", email=EMAIL_ADDRESS),
        )

    def _open_update_check(self):
        """打开检查更新窗口，联网查询 GitHub Releases。"""
        config = self._app_config()
        from lib.UpdateDialog import UpdateDialog

        dialog = UpdateDialog(
            self,
            history_path=HISTORY_PATH,
            translate=self._t,
            config=config,
            releases_url=RELEASES_URL,
        )
        dialog.exec()

    def _on_exit(self):
        logging.info("用户请求退出程序")
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _show_error(self, title, message):
        QMessageBox.critical(self, title, message)


def _splash_version_pixel_size(measured_width: float, target_width: float, reference_px: int = 100) -> int:
    """按目标宽度反推版本号字号；measured_width 是 reference_px 下的文字宽度。"""
    try:
        measured = float(measured_width)
        target = float(target_width)
        reference = int(reference_px)
    except (TypeError, ValueError):
        return 1
    if measured <= 0 or target <= 0 or reference <= 0:
        return 1
    return max(1, int(round(reference * target / measured)))


def _draw_splash_version(pixmap: QPixmap) -> QPixmap:
    """在启动画面右下角绘制纯白版本号，宽度固定为图片宽度的三分之一。"""
    text = f"v{APP_VERSION}"
    painter = QPainter(pixmap)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # 用 100px 探针测量文字宽度，再按图片宽度等比换算实际字号。
        probe_font = QFont()
        probe_font.setBold(True)
        probe_font.setPixelSize(100)
        measured_width = QFontMetricsF(probe_font).horizontalAdvance(text)
        pixel_size = _splash_version_pixel_size(measured_width, pixmap.width() / 3.0)
        font = QFont()
        font.setBold(True)
        font.setPixelSize(pixel_size)
        painter.setFont(font)
        margin = max(1, int(round(min(pixmap.width(), pixmap.height()) * 0.03)))
        metrics = QFontMetricsF(font)
        # 直接按基线定位，避免 Qt 的 Bottom 对齐额外留出字体下降部空白。
        x = pixmap.width() - margin - metrics.horizontalAdvance(text)
        baseline = pixmap.height() - margin
        shadow = max(1, pixel_size // 32)
        painter.setPen(QColor(0, 0, 0, 170))
        painter.drawText(QPointF(x + shadow, baseline + shadow), text)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(QPointF(x, baseline), text)
    finally:
        painter.end()
    return pixmap


def main():
    global lift_module, multi_module, ScrollMulti, ScrollLift
    global StateManager, ThemeManager, importnames, OutputView, SlotOutputView, TextViewerDialog
    global LanguageManager
    global BackgroundWidget, WindowTheme
    global ui_main, ui_widgetlift, ui_widgetmulti, ui_widgetscrollmulti, ui_widgetscrolllift

    app = QApplication(sys.argv)
    bootstrap_config, bootstrap_warnings = _bootstrap_config()
    icon_path = ICON_PATH
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
    splash_path = SPLASH_IMAGE_PATH
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
        splash_pixmap = _draw_splash_version(splash_pixmap)
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
        from lib import ScrollMulti
        from lib import ScrollLift
        from lib import ThemeManager
        from lib import LanguageManager
        from lib.OutputView import OutputView, SlotOutputView
        from lib.BackgroundWidget import BackgroundWidget
        from lib.TextViewer import TextViewerDialog
        from lib import WindowTheme
        from lib import ui_main
        from lib import ui_widgetmulti
        from lib import ui_widgetlift
        from lib import ui_widgetscrollmulti
        from lib import ui_widgetscrolllift
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
    try:
        # 启动时规范化记忆文件，移除旧版偏好与窗口尺寸。
        StateManager.load_memory()
    except Exception:
        logging.exception("规范化记忆文件失败")
    app_config = config.get("app", {}) if isinstance(config, dict) else {}
    if not isinstance(app_config, dict):
        app_config = {}
    logging_config = config.get("logging", {}) if isinstance(config, dict) else {}
    if not isinstance(logging_config, dict):
        logging_config = {}
    log_level = logging_config.get("level", "INFO")
    StateManager.configure_logging(log_level)

    themes = ThemeManager.discover_themes()
    languages, preferred_language, language_warning = LanguageManager.load_languages()
    selected_theme = ThemeManager.resolve_startup_theme(
        themes, app_config.get("theme", "")
    )
    selected_language = LanguageManager.resolve_startup_language(
        languages, preferred_language, app_config.get("language", "")
    )
    selected_roster = importnames.active_roster
    startup_mode = app_config.get("default_mode")
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

    window = MainWindow(
        themes,
        selected_theme,
        languages,
        selected_language,
        importnames.rosters,
        selected_roster,
        startup_warnings,
        startup_mode=startup_mode,
    )
    try:
        ThemeManager.apply_theme(app, selected_theme, themes)
    except (OSError, ValueError, KeyError) as exc:
        logging.exception("应用启动主题失败: %s", exc)
        StateManager.log("ERROR", "startup_theme", error=str(exc))
    def reveal_window():
        if getattr(window, "_start_maximized", False):
            window.showMaximized()
        else:
            window.show()
        if splash is not None:
            splash.finish(window)

    if splash is None:
        reveal_window()
    else:
        # mode=1：先只显示启动画面，时间到再显示主窗口。
        # Wayland 不支持启动画面置顶，提前显示主窗口会把启动画面完全盖住。
        wait_ms = _splash_wait_ms(splash_mode, splash_duration_ms, splash_timer.elapsed())
        if wait_ms:
            QTimer.singleShot(wait_ms, reveal_window)
        else:
            reveal_window()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
