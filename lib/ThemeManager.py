"""Load and apply TOML color themes to every Qt page and common widget."""

from pathlib import Path
import tomllib

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent.parent
THEME_DIR = ROOT / "theme"


def available_themes() -> list[str]:
    return sorted(path.stem for path in THEME_DIR.glob("*.toml"))


def load_theme(name: str) -> dict:
    path = THEME_DIR / f"{name}.toml"
    with path.open("rb") as theme_file:
        return tomllib.load(theme_file)


def _color(value: str, color_format: str, allow_alpha: bool = True) -> str:
    """Convert configured RGB/RGBA/Hex/HexA values to a Qt stylesheet color."""
    if color_format in {"RGB", "RGBA"}:
        channels = [int(channel.strip()) for channel in value.split(",")]
        if color_format == "RGB":
            channels.append(255)
        if len(channels) != 4:
            raise ValueError(f"Invalid {color_format} color: {value}")
        if not allow_alpha:
            channels[3] = 255
        return f"rgba({channels[0]}, {channels[1]}, {channels[2]}, {channels[3] / 255:.3f})"
    if color_format in {"Hex", "HexA"}:
        if color_format == "HexA" and value.startswith("#") and len(value) == 9:
            # TOML themes use the familiar #RRGGBBAA order.
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
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha() / 255:.3f})"
    raise ValueError(f"Unsupported color format: {color_format}")


def apply_theme(app: QApplication, name: str) -> None:
    theme = load_theme(name)
    colors = theme.get("colors", {})
    color_format = theme.get("color_format", "Hex")
    background = _color(colors.get("background", "#202124"), color_format, False)
    foreground = _color(colors.get("foreground", "#f5f5f5"), color_format)
    display_background = _color(colors.get("display_background", "#292a2d"), color_format)
    display_foreground = _color(colors.get("display_foreground", "#f5f5f5"), color_format)
    display_border = _color(colors.get("display_border", "#5f6368"), color_format)
    panel = _color(colors.get("panel", "#292a2d"), color_format)
    button = _color(colors.get("button", "#303134"), color_format)
    button_hover = _color(colors.get("button_hover", "#45474d"), color_format)
    button_pressed = _color(colors.get("button_pressed", "#5f6368"), color_format)
    border = _color(colors.get("border", "#5f6368"), color_format)
    accent = _color(colors.get("accent", "#3f51b5"), color_format)
    style = f"""
    QMainWindow, QWidget, QStackedWidget, QFrame {{
        background-color: {background};
        color: {foreground};
    }}
    QLabel, QStatusBar, QMenuBar, QMenu, QAction {{
        color: {foreground};
    }}
    QLabel#label_SingleOutput, QLabel#label_MultiOutput,
    QLabel#label_LiftOutput, QLabel#label_ScrollSingleOutput {{
        background-color: {display_background};
        color: {display_foreground};
        border: 1px solid {display_border};
    }}
    QPushButton {{
        background-color: {button};
        color: {foreground};
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
    """
    app.setStyleSheet(style)
