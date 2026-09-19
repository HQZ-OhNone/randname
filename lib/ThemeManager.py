"""Discover, validate, and apply user-defined TOML themes at startup."""

from pathlib import Path
import logging
import tomllib

from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent.parent
THEME_DIR = ROOT / "theme"
LOGGER = logging.getLogger(__name__)


def discover_themes() -> dict[str, dict]:
    """Load every valid ``theme/*.toml`` file, including user-added files."""
    themes = {}
    if not THEME_DIR.is_dir():
        return themes
    for path in sorted(THEME_DIR.glob("*.toml")):
        try:
            with path.open("rb") as theme_file:
                theme = tomllib.load(theme_file)
            if not isinstance(theme.get("colors"), dict):
                raise ValueError("missing [colors] table")
            themes[path.stem] = theme
        except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
            LOGGER.warning("Ignoring invalid theme %s: %s", path.name, exc)
    return themes


def _stylesheet(theme: dict) -> str:
    colors = theme["colors"]
    background = colors.get("background", "#202124")
    foreground = colors.get("foreground", "#f5f5f5")
    panel = colors.get("panel", background)
    button = colors.get("button", panel)
    accent = colors.get("accent", foreground)
    return f"""
    QMainWindow, QWidget, QStackedWidget, QFrame {{
        background-color: {background};
        color: {foreground};
    }}
    QLabel, QStatusBar, QMenuBar, QMenu {{
        color: {foreground};
    }}
    QPushButton {{
        background-color: {button};
        color: {foreground};
        border: 1px solid {colors.get("border", foreground)};
        border-radius: 4px;
        padding: 6px 12px;
    }}
    QPushButton:hover, QMenuBar::item:selected, QMenu::item:selected {{
        background-color: {colors.get("button_hover", accent)};
    }}
    QStatusBar {{ background-color: {panel}; }}
    QLabel#label_SingleOutput, QLabel#label_MultiOutput,
    QLabel#label_LiftOutput {{
        background-color: {colors.get("display_background", panel)};
        color: {colors.get("display_foreground", foreground)};
        border: 1px solid {colors.get("display_border", colors.get("border", foreground))};
    }}
    """


def apply_theme(app: QApplication, name: str, themes: dict[str, dict] | None = None) -> str:
    """Apply a discovered theme and return the selected theme name."""
    loaded = themes if themes is not None else discover_themes()
    if not loaded:
        return ""
    selected = name if name in loaded else next(iter(loaded))
    app.setStyleSheet(_stylesheet(loaded[selected]))
    return selected
