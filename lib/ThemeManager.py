"""Load and apply TOML color themes to every Qt page and common widget."""

from pathlib import Path
import tomllib

from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent.parent
THEME_DIR = ROOT / "theme"


def available_themes() -> list[str]:
    return sorted(path.stem for path in THEME_DIR.glob("*.toml"))


def load_theme(name: str) -> dict:
    path = THEME_DIR / f"{name}.toml"
    with path.open("rb") as theme_file:
        return tomllib.load(theme_file)


def apply_theme(app: QApplication, name: str) -> None:
    theme = load_theme(name)
    colors = theme.get("colors", {})
    style = f"""
    QMainWindow, QWidget, QStackedWidget, QFrame {{
        background-color: {colors.get("background", "#202124")};
        color: {colors.get("foreground", "#f5f5f5")};
    }}
    QLabel, QStatusBar, QMenuBar, QMenu, QAction {{
        color: {colors.get("foreground", "#f5f5f5")};
    }}
    QPushButton {{
        background-color: {colors.get("button", "#303134")};
        color: {colors.get("foreground", "#f5f5f5")};
        border: 1px solid {colors.get("border", "#5f6368")};
        border-radius: 4px;
        padding: 6px 12px;
    }}
    QPushButton:hover {{ background-color: {colors.get("button_hover", "#45474d")}; }}
    QPushButton:pressed {{ background-color: {colors.get("button_pressed", "#5f6368")}; }}
    QMenuBar::item:selected, QMenu::item:selected {{
        background-color: {colors.get("accent", "#3f51b5")};
    }}
    QStatusBar {{ background-color: {colors.get("panel", "#292a2d")}; }}
    """
    app.setStyleSheet(style)
