"""Load human-readable language packs and resolve localized labels."""

from pathlib import Path
import logging
import tomllib

from PySide6.QtCore import QLocale

ROOT = Path(__file__).resolve().parent.parent
LANGUAGE_PATH = ROOT / "config" / "language.toml"
LOGGER = logging.getLogger(__name__)

ENGLISH = {
    "menu.file": "File",
    "menu.mode": "Mode",
    "menu.theme": "Theme",
    "menu.language": "Language",
    "menu.roster": "Roster",
    "menu.about": "About",
    "menu.log_level": "Log level",
    "action.import": "Import memory...",
    "action.export": "Export memory...",
    "action.reload": "Refresh application data",
    "action.exit": "Exit",
    "action.license": "License",
    "action.repository": "Source repository",
    "action.help": "Help",
    "action.program_log": "Program log",
    "action.close": "Close",
    "mode.multi": "Draw names",
    "mode.lift": "Elimination draw",
    "mode.scroll": "Rolling draw",
    "button.draw": "Draw",
    "button.increase": "Increase",
    "button.decrease": "Decrease",
    "button.reset": "Reset",
    "button.start": "Start",
    "button.stop": "Stop",
    "state.waiting": "Ready",
    "state.multi_result": "Draw complete: {count}",
    "state.lift_result": "Elimination draw complete: {count}",
    "state.roster_changed": "Roster: {name}",
    "state.theme_changed": "Theme: {name}",
    "state.language_changed": "Language: {name}",
    "state.no_logs": "No log entries have been recorded in this session.",
    "state.log_level_changed": "Log level: {level}",
    "state.startup_warning": "Startup used fallback data: {files}",
    "state.startup_error": "Required application files are missing: {files}",
    "dialog.import_title": "Import memory",
    "dialog.export_title": "Export memory",
    "dialog.json_filter": "JSON Files (*.json);;All Files (*)",
    "dialog.import_done": "Memory imported.",
    "dialog.export_done": "Memory exported.",
    "dialog.import_success": "Memory imported: {path}",
    "dialog.export_success": "Memory exported: {path}",
    "dialog.operation_failed": "Operation failed: {error}",
    "log.DEBUG": "Debug",
    "log.INFO": "Information",
    "log.WARNING": "Warning",
    "log.ERROR": "Error",
    "log.CRITICAL": "Critical",
    "error.license_missing": "The license file is missing: {path}",
    "error.open_license": "Could not open the license: {error}",
    "error.open_repository": "Could not open the repository: {error}",
    "error.window_init": "Could not initialize the main window: {error}",
    "error.controls_init": "Could not initialize the interface: {error}",
    "error.open_help": "Could not open the help file: {path}",
    "error.help_missing": "The help file is missing: {path}",
}


def load_languages(path: Path = LANGUAGE_PATH) -> tuple[dict, str, str | None]:
    languages = {"en_US": {"display_name": "English (United States)", "text": ENGLISH}}
    preferred = "en_US"
    warning = None
    try:
        with path.open("rb") as language_file:
            data = tomllib.load(language_file)
        packs = data.get("languages", {})
        if not isinstance(packs, dict):
            raise ValueError("languages must be a table")
        for code, pack in packs.items():
            if not isinstance(pack, dict) or not isinstance(pack.get("text", {}), dict):
                LOGGER.warning("Ignoring invalid language pack %s", code)
                continue
            languages[code] = {
                "display_name": str(pack.get("display_name", code)),
                "text": {**ENGLISH, **pack.get("text", {})},
            }
        configured_preferred = data.get("preferred", "en_US")
        if isinstance(configured_preferred, str):
            preferred = configured_preferred
    except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
        warning = f"{path.name}: {exc}"
        LOGGER.warning("Using built-in English language: %s", warning)
    return languages, preferred, warning


def system_language(languages: dict) -> str:
    locale_name = QLocale.system().name().replace("-", "_")
    if locale_name in languages:
        return locale_name
    language_prefix = locale_name.split("_", 1)[0].lower()
    return next(
        (code for code in languages if code.split("_", 1)[0].lower() == language_prefix),
        "en_US",
    )


def resolve_language(requested: str, languages: dict) -> str:
    if requested in languages:
        return requested
    return system_language(languages)


def translate(languages: dict, language: str, key: str, **values) -> str:
    pack = languages.get(language, languages["en_US"])
    text = pack["text"].get(key, ENGLISH.get(key, key))
    try:
        return text.format(**values)
    except (KeyError, ValueError):
        return text


def localized_name(names: object, language: str, languages: dict) -> str:
    if not isinstance(names, dict):
        return ""
    preference = (language, system_language(languages), "en_US")
    for code in preference:
        value = names.get(code)
        if isinstance(value, str) and value:
            return value
    return ""