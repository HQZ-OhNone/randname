"""Discover and apply TOML color themes."""

import logging
from pathlib import Path
import tomllib

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent.parent
THEME_PATH = ROOT / "config" / "theme.toml"
LOGGER = logging.getLogger(__name__)
THEME_LOAD_WARNING: str | None = None
DEFAULT_THEME = "randname-dark"
# Explicit ``default`` from config/theme.toml, or None when unset/invalid.
CONFIGURED_DEFAULT: str | None = None


BUILTIN_THEME = {
    "color_format": "HexA",
    "name": {"en_US": "Randname Dark", "zh_CN": "随机名深色", "zh_TW": "隨機名深色"},
    "colors": {
        "background": "#211823FF",
        "foreground": "#F9EDF7FF",
        "panel": "#302333FF",
        "display_background": "#38283BEE",
        "display_foreground": "#FFF6FCFF",
        "display_border": "#C47DB5FF",
        "button": "#493149FF",
        "button_hover": "#633F60FF",
        "button_pressed": "#7A4B75FF",
        "border": "#B86AA8FF",
        "accent": "#D44EADFF",
    },
}


def discover_themes(path: Path = THEME_PATH) -> dict[str, dict]:
    """Load the consolidated theme catalog or a built-in fallback theme."""
    global THEME_LOAD_WARNING, DEFAULT_THEME, CONFIGURED_DEFAULT
    THEME_LOAD_WARNING = None
    CONFIGURED_DEFAULT = None
    try:
        with path.open("rb") as theme_file:
            data = tomllib.load(theme_file)
        themes = data.get("themes")
        if not isinstance(themes, dict) or not themes:
            raise ValueError("missing [themes.*] entries")
        loaded = {
            name: theme
            for name, theme in themes.items()
            if isinstance(theme, dict)
            and isinstance(theme.get("colors"), dict)
            and isinstance(theme.get("name"), dict)
        }
        if loaded:
            requested_default = data.get("default", "randname-dark")
            CONFIGURED_DEFAULT = (
                requested_default
                if isinstance(requested_default, str) and requested_default in loaded
                else None
            )
            DEFAULT_THEME = (
                requested_default
                if isinstance(requested_default, str) and requested_default in loaded
                else "randname-dark" if "randname-dark" in loaded else next(iter(loaded))
            )
            if requested_default != DEFAULT_THEME:
                LOGGER.warning("Unknown default theme %r; using %s", requested_default, DEFAULT_THEME)
            return loaded
        raise ValueError("no valid theme entries")
    except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
        THEME_LOAD_WARNING = f"{path}: {exc}"
        DEFAULT_THEME = "randname-dark"
        CONFIGURED_DEFAULT = None
        LOGGER.warning("Using built-in theme: %s", exc)
        return {"randname-dark": BUILTIN_THEME}


def available_themes() -> list[str]:
    return sorted(discover_themes())


def resolve_startup_theme(themes: dict[str, dict], configured: str = "") -> str:
    """Pick the startup theme, preferring the dedicated theme file.

    ``config/theme.toml`` exposes ``default``; ``config/config.toml`` may also
    carry ``[app].theme``. When both differ, the dedicated file wins. The
    ``configured`` value is only consulted when the dedicated file omits
    ``default`` (or names an unavailable theme). The catalog's resolved default
    and then the first available theme are the fallbacks.
    """
    if not themes:
        return ""
    for candidate in (CONFIGURED_DEFAULT, configured):
        if isinstance(candidate, str) and candidate in themes:
            return candidate
    if DEFAULT_THEME in themes:
        return DEFAULT_THEME
    return next(iter(themes))


def load_theme(name: str) -> dict:
    return discover_themes().get(name, BUILTIN_THEME)


def _color(value: str, color_format: str, allow_alpha: bool = True) -> str:
    color = parse_color(value, color_format, allow_alpha)
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha() / 255:.3f})"


def parse_color(value: str, color_format: str, allow_alpha: bool = True) -> QColor:
    """把主题文件中的颜色解析为 QColor，兼容 HexA/Hex/RGBA/RGB。"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Invalid {color_format} color: {value!r}")
    if color_format in {"RGB", "RGBA"}:
        channels = [int(channel.strip()) for channel in value.split(",")]
        if color_format == "RGB":
            channels.append(255)
        if len(channels) != 4:
            raise ValueError(f"Invalid {color_format} color: {value}")
        if not allow_alpha:
            channels[3] = 255
        return QColor(channels[0], channels[1], channels[2], channels[3])
    if color_format in {"Hex", "HexA"}:
        if color_format == "HexA" and value.startswith("#") and len(value) == 9:
            color = QColor(
                int(value[1:3], 16),
                int(value[3:5], 16),
                int(value[5:7], 16),
                int(value[7:9], 16),
            )
        else:
            color = QColor(value)
        if not color.isValid():
            raise ValueError(f"Invalid {color_format} color: {value}")
        if not allow_alpha:
            color.setAlpha(255)
        return color
    raise ValueError(f"Unsupported color format: {color_format}")


BACKGROUND_DEFAULTS = {
    "fit_mode": "cover",
    "blur_radius": 24.0,
    "blur_direction": "uniform",
    "opacity": 1.0,
    "dim": 0.0,
    "shadow_size": 12.0,
    "shadow_opacity": 0.35,
}
BLUR_DIRECTIONS = (
    "uniform",
    "horizontal",
    "vertical",
    "diagonal",
    "center-out",
    "out-center",
)
FIT_MODES = ("cover", "contain", "center", "tile")


def _number(value, default, minimum, maximum):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if result != result or result in (float("inf"), float("-inf")):
        return default
    return max(minimum, min(maximum, result))


def background_config(theme: dict) -> dict | None:
    """读取并规范化主题内的 [background] 表；没有图片时返回 None。"""
    raw = theme.get("background") if isinstance(theme, dict) else None
    if not isinstance(raw, dict):
        return None
    image = raw.get("image")
    if not isinstance(image, str) or not image.strip():
        return None
    fit_mode = raw.get("fit_mode", BACKGROUND_DEFAULTS["fit_mode"])
    if fit_mode not in FIT_MODES:
        fit_mode = BACKGROUND_DEFAULTS["fit_mode"]
    direction = raw.get("blur_direction", BACKGROUND_DEFAULTS["blur_direction"])
    if direction not in BLUR_DIRECTIONS:
        direction = BACKGROUND_DEFAULTS["blur_direction"]
    return {
        "image": image.strip(),
        "fit_mode": fit_mode,
        "blur_radius": _number(
            raw.get("blur_radius"), BACKGROUND_DEFAULTS["blur_radius"], 0.0, 80.0
        ),
        "blur_direction": direction,
        "opacity": _number(raw.get("opacity"), BACKGROUND_DEFAULTS["opacity"], 0.0, 1.0),
        "dim": _number(raw.get("dim"), BACKGROUND_DEFAULTS["dim"], 0.0, 1.0),
        "shadow_size": _number(
            raw.get("shadow_size"), BACKGROUND_DEFAULTS["shadow_size"], 0.0, 64.0
        ),
        "shadow_opacity": _number(
            raw.get("shadow_opacity"), BACKGROUND_DEFAULTS["shadow_opacity"], 0.0, 1.0
        ),
    }


def resolve_background_image(image: str) -> Path:
    """相对路径一律以 ui/ 为基准，绝对路径原样返回。"""
    path = Path(image).expanduser()
    if path.is_absolute():
        return path
    return ROOT / "ui" / path


def _stylesheet(theme: dict) -> str:
    colors = theme.get("colors", {})
    color_format = theme.get("color_format", "Hex")
    foreground = _color(colors.get("foreground", "#f5f5f5"), color_format)
    background = _color(colors.get("background", "#202124"), color_format, False)
    panel = _color(colors.get("panel", "#292a2d"), color_format)
    button = _color(colors.get("button", "#303134"), color_format)
    button_foreground = _color(colors.get("button_foreground", colors.get("foreground", "#f5f5f5")), color_format)
    button_hover = _color(colors.get("button_hover", "#45474d"), color_format)
    button_pressed = _color(colors.get("button_pressed", "#5f6368"), color_format)
    border = _color(colors.get("border", "#5f6368"), color_format)
    accent = _color(colors.get("accent", "#3f51b5"), color_format)
    display_background = _color(colors.get("display_background", "#292a2d"), color_format)
    display_foreground = _color(colors.get("display_foreground", "#f5f5f5"), color_format)
    display_border = _color(colors.get("display_border", "#5f6368"), color_format)
    return f"""
    QMainWindow, QWidget, QStackedWidget, QFrame {{
        background-color: {background};
        color: {foreground};
    }}
    QLabel, QStatusBar, QMenuBar, QMenu {{
        color: {foreground};
    }}
    QLabel#label_MultiOutput,
    QLabel#label_LiftOutput, QLabel#label_ScrollMultiOutput,
    QLabel#label_ScrollLiftOutput {{
        background-color: {display_background};
        color: {display_foreground};
        border: 1px solid {display_border};
    }}
    QPushButton {{
        background-color: {button};
        color: {button_foreground};
        border: 1px solid {border};
        border-radius: 4px;
        padding: 6px 12px;
    }}
    QPushButton:hover {{ background-color: {button_hover}; }}
    QPushButton:pressed {{ background-color: {button_pressed}; }}
    QMenuBar::item:selected, QMenu::item:selected {{
        background-color: {accent};
    }}
    QStatusBar {{ background-color: {panel}; }}
    QWidget#background_layer {{ background-color: transparent; }}
    QMainWindow[hasBackgroundImage="true"] QWidget#centralwidget,
    QMainWindow[hasBackgroundImage="true"] QStackedWidget,
    QMainWindow[hasBackgroundImage="true"] QStackedWidget > QWidget {{
        background-color: transparent;
    }}
    """


def apply_theme(app: QApplication, name: str, themes: dict[str, dict] | None = None) -> str:
    """Apply a named discovered theme, falling back to the first valid theme."""
    loaded = themes if themes is not None else discover_themes()
    if not loaded:
        return ""
    selected = (
        name if name in loaded
        else DEFAULT_THEME if DEFAULT_THEME in loaded
        else next(iter(loaded))
    )
    app.setStyleSheet(_stylesheet(loaded[selected]))
    return selected
