"""Load human-readable language packs and resolve localized labels."""

from pathlib import Path
import logging
import tomllib

from PySide6.QtCore import QLocale

ROOT = Path(__file__).resolve().parent.parent
LANGUAGE_PATH = ROOT / "config" / "language.toml"
LOGGER = logging.getLogger(__name__)

# 简体与繁体互为备援：一方缺少语言包或词条时自动使用另一方。
SIBLING_LANGUAGES = {"zh_CN": "zh_TW", "zh_TW": "zh_CN"}
DEFAULT_DISPLAY_NAMES = {
    "en_US": "English (United States)",
    "zh_CN": "简体中文",
    "zh_TW": "繁體中文",
}

ENGLISH = {
    "menu.file": "File",
    "menu.mode": "Mode",
    "menu.theme": "Theme",
    "menu.theme.dark": "Dark",
    "menu.theme.light": "Light",
    "menu.language": "Language",
    "menu.roster": "Roster",
    "menu.about": "About",
    "menu.log_level": "Log level",
    "action.import": "Import memory...",
    "action.export": "Export memory...",
    "action.reload": "Refresh application data",
    "action.init": "Initialize",
    "action.exit": "Exit",
    "action.license": "License",
    "action.repository": "Source repository",
    "action.feedback": "Feedback",
    "menu.feedback": "Feedback",
    "action.feedback.github": "GitHub Issues",
    "action.feedback.email": "Email",
    "action.help": "Help",
    "action.program_log": "Program log",
    "action.check_update": "Check for updates",
    "action.close": "Close",
    "update.title": "Check for updates",
    "update.checking": "Checking...",
    "update.latest": "You're up to date!",
    "update.available": "A new version is available!",
    "update.failed": "Check failed. Please check manually.",
    "update.button_update": "Update",
    "update.button_manual": "Manual check",
    "update.button_ok": "OK",
    "update.open_failed": "Could not open the browser. Please open this page manually: {url}",
    "mode.Multi": "Multi",
    "mode.Single": "Single",
    "mode.Lift": "Lift",
    "mode.ScrollSingle": "ScrollSingle",
    "mode.ScrollMulti": "ScrollMulti",
    "mode.ScrollLift": "ScrollLift",
    "button.draw": "Draw",
    "button.increase": "Increase",
    "button.decrease": "Decrease",
    "button.reset": "Reset",
    "button.start": "Start",
    "button.stop": "Stop",
    "button.stop_scroll_multi": "Stop ({remaining}/{total})",
    "state.waiting": "Ready",
    "state.multi_result": "Multi complete: {count}",
    "state.lift_result": "Lift complete: {count}",
    "state.scroll_multi_result": "ScrollMulti complete: {count}",
    "state.scroll_lift_result": "ScrollLift complete: {count}",
    "state.roster_changed": "Roster: {name}",
    "state.theme_changed": "Theme: {name}",
    "state.language_changed": "Language: {name}",
    "state.initialized": "All modes have been reset.",
    "state.no_logs": "No log entries have been recorded in this session.",
    "state.log_level_changed": "Log level: {level}",
    "state.startup_warning": "Startup used fallback data: {files}",
    "state.startup_error": "Required application files are missing: {files}",
    "state.no_result": "No result",
    "state.scroll_multi_invalid": "Draw count exceeds roster size; drawing {count} instead",
    "state.scroll_lift_invalid": "Draw count exceeds remaining names; drawing {count} instead",
    "state.scroll_lift_empty": "No names remain; reset to restore the roster",
    "status.mode": "Mode: {name}",
    "status.roster": "Roster: {name}",
    "status.quantity": "Count: {count}",
    "status.theme": "Theme: {name}",
    "status.language": "Language: {name}",
    "status.log_level": "Log: {name}",
    "status.version": "Version: {version}",
    "dialog.import_title": "Import memory",
    "dialog.export_title": "Export memory",
    "dialog.json_filter": "JSON Files (*.json);;All Files (*)",
    "dialog.import_done": "Memory imported.",
    "dialog.export_done": "Memory exported.",
    "dialog.import_success": "Memory imported: {path}",
    "dialog.export_success": "Memory exported: {path}",
    "dialog.operation_failed": "Operation failed: {error}",
    "dialog.init_title": "Initialize",
    "dialog.email_fallback": "Could not open your mail app. Please send an email to: {email}",
    "log.DEBUG": "Debug",
    "log.INFO": "Information",
    "log.WARNING": "Warning",
    "log.ERROR": "Error",
    "log.CRITICAL": "Critical",
    "error.license_missing": "The license file is missing: {path}",
    "error.open_license": "Could not open the license: {error}",
    "error.open_repository": "Could not open the repository: {error}",
    "error.open_feedback": "Could not open the feedback page: {error}",
    "error.window_init": "Could not initialize the main window: {error}",
    "error.controls_init": "Could not initialize the interface: {error}",
    "error.open_help": "Could not open the help file: {path}",
    "error.help_missing": "The help file is missing: {path}",
    "error.theme_failed": "Could not apply the theme: {error}",
}


def load_languages(path: Path = LANGUAGE_PATH) -> tuple[dict, str, str | None]:
    # ``preferred`` stays empty when the dedicated language file does not
    # specify one, so callers can fall back to config.toml's [app].language.
    languages = {
        "en_US": {
            "display_name": DEFAULT_DISPLAY_NAMES["en_US"],
            "text": ENGLISH,
            "own": dict(ENGLISH),
        }
    }
    preferred = ""
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
            own_text = dict(pack.get("text", {}))
            languages[code] = {
                "display_name": str(pack.get("display_name", code)),
                "text": {**ENGLISH, **own_text},
                "own": own_text,
            }
        configured_preferred = data.get("preferred", "")
        if isinstance(configured_preferred, str):
            preferred = configured_preferred
    except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
        warning = f"{path.name}: {exc}"
        LOGGER.warning("Using built-in English language: %s", warning)
    for code, sibling in SIBLING_LANGUAGES.items():
        if code in languages or sibling not in languages:
            continue
        source = languages[sibling]
        languages[code] = {
            "display_name": DEFAULT_DISPLAY_NAMES.get(code, code),
            "text": dict(source["text"]),
            "own": dict(source["own"]),
            "fallback_from": sibling,
        }
        LOGGER.warning("Language %s is unavailable; using %s", code, sibling)
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


def language_chain(language: str, languages: dict) -> list[str]:
    """返回翻译查找顺序：自身、简繁备援、系统语言、英文。"""
    chain = []
    for code in (
        language,
        SIBLING_LANGUAGES.get(language),
        system_language(languages),
        "en_US",
    ):
        if isinstance(code, str) and code in languages and code not in chain:
            chain.append(code)
    return chain


def resolve_language(requested: str, languages: dict) -> str:
    for code in (requested, SIBLING_LANGUAGES.get(requested)):
        if code in languages:
            return code
    return system_language(languages)


def resolve_startup_language(languages: dict, preferred: str = "", configured: str = "") -> str:
    """Pick the startup language, preferring the dedicated language file.

    ``config/language.toml`` exposes ``preferred``; ``config/config.toml`` may
    also carry ``[app].language``. When both differ, the dedicated file wins.
    The ``configured`` value is only consulted when the dedicated file omits
    ``preferred`` (or names an unavailable language). The system language is the
    final fallback.
    """
    for candidate in (preferred, configured):
        if not isinstance(candidate, str):
            continue
        for code in (candidate, SIBLING_LANGUAGES.get(candidate)):
            if code in languages:
                return code
    return system_language(languages)


def translate(languages: dict, language: str, key: str, **values) -> str:
    text = None
    for code in language_chain(language, languages):
        own = languages.get(code, {}).get("own")
        if isinstance(own, dict) and key in own:
            text = own[key]
            break
    if text is None:
        text = ENGLISH.get(key, key)
    try:
        return text.format(**values)
    except (KeyError, ValueError):
        return text


def localized_name(names: object, language: str, languages: dict) -> str:
    if not isinstance(names, dict):
        return ""
    for code in language_chain(language, languages):
        value = names.get(code)
        if isinstance(value, str) and value:
            return value
    return ""