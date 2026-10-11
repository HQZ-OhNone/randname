"""Configuration, memory and concise structured logging for randname."""

import copy
from datetime import datetime
import json
import logging
from pathlib import Path
import tomllib
from typing import Any, Callable, Optional

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "doc"
DOC.mkdir(exist_ok=True)
MEMORY_PATH = DOC / "memory.json"
LOG_PATH = DOC / "log.log"
CONFIG_DIR = ROOT / "config"
CONFIG_PATH = CONFIG_DIR / "config.toml"
DEFAULT_CONFIG_PATH = ROOT / ".config.default.toml"
NAME_PATH = CONFIG_DIR / "name.toml"
DEFAULT_NAME_PATH = ROOT / ".name.default.toml"
CONFIG_SOURCE = ""
CONFIG_FALLBACK_USED = False
CONFIG_WARNINGS: list[str] = []
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
LOG_LEVEL_CHOICES = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
CURRENT_LOG_LEVEL = "INFO"
SESSION_LOG_RECORDS: list[str] = []
BUILTIN_CONFIG = {
    "app": {"default_mode": "Multi", "theme": "randname-dark", "roster": "class_1"},
    "splash": {
        "enabled": True,
        "mode": 0,
        "duration_ms": 1000,
        "size_mode": "screen_ratio",
        "width": 480,
        "height": 270,
    },
    "window": {"size_mode": "screen_ratio", "width": 800, "height": 600, "aspect_ratio": 1.5},
    "scroll_single": {"rate": 30},
    "logging": {"level": "INFO"},
}


def _now_iso() -> str:
    return datetime.now().isoformat(sep=" ", timespec="seconds")


def configure_paths(config: dict) -> None:
    """Apply configurable writable paths while keeping project-relative defaults."""
    global MEMORY_PATH, LOG_PATH
    paths = config.get("paths", {}) if isinstance(config, dict) else {}
    if not isinstance(paths, dict):
        paths = {}
    for key, default in (("memory_file", DOC / "memory.json"), ("log_file", DOC / "log.log")):
        value = paths.get(key)
        selected = Path(value) if isinstance(value, str) and value else default
        if not selected.is_absolute():
            selected = ROOT / selected
        selected = selected.resolve()
        selected.parent.mkdir(parents=True, exist_ok=True)
        if key == "memory_file":
            MEMORY_PATH = selected
        else:
            LOG_PATH = selected


class _SessionLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        line = self.format(record)
        SESSION_LOG_RECORDS.append(line)
        try:
            with LOG_PATH.open("a", encoding="utf-8") as log_file:
                log_file.write(line + "\n")
        except OSError:
            pass


def configure_logging(level: str = "INFO") -> str:
    """Set the logging threshold and capture this process's Python log records."""
    global CURRENT_LOG_LEVEL
    selected = level.upper() if isinstance(level, str) else "INFO"
    if selected == "WARN":
        selected = "WARNING"
    if selected not in LOG_LEVELS:
        selected = "INFO"
    CURRENT_LOG_LEVEL = selected
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVELS[selected])
    handler = next(
        (item for item in root_logger.handlers if isinstance(item, _SessionLogHandler)),
        None,
    )
    if handler is None:
        handler = _SessionLogHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        root_logger.addHandler(handler)
    handler.setLevel(LOG_LEVELS[selected])
    return selected


def session_log_text() -> str:
    """Return all records captured since this process imported StateManager."""
    return "\n".join(SESSION_LOG_RECORDS)


def _default_memory() -> dict:
    return {
        "loaded_config": None,
        "last_results": {
            "Multi": None,
            "Lift": None,
            "ScrollSingle": None,
        },
    }


def log(level: str, action: str, result: Optional[Any] = None,
        error: Optional[str] = None) -> None:
    """Append one concise, machine-readable English text line."""
    normalized_level = level.upper()
    if normalized_level == "WARN":
        normalized_level = "WARNING"
    if LOG_LEVELS.get(normalized_level, logging.INFO) < LOG_LEVELS[CURRENT_LOG_LEVEL]:
        return
    try:
        fields = [
            f"time={_now_iso()}",
            f"level={normalized_level}",
            f"action={action}",
        ]
        if result is not None:
            fields.append(f"result={_log_value(result)}")
        if error is not None:
            fields.append(f"error={_log_value(error)}")
        line = " ".join(fields)
        SESSION_LOG_RECORDS.append(line)
        with LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(line + "\n")
    except Exception:
        # Logging must never prevent a classroom draw from completing.
        pass


def _log_value(value: Any) -> str:
    """Keep log lines single-line and free from JSON-only punctuation."""
    text = str(value).replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return text.replace("{", "(").replace("}", ")").replace("[", "(").replace("]", ")")


def load_memory() -> dict:
    if not MEMORY_PATH.exists():
        memory = _default_memory()
        MEMORY_PATH.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")
        return memory
    try:
        memory = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        return memory if isinstance(memory, dict) else _default_memory()
    except (OSError, json.JSONDecodeError):
        return _default_memory()


def save_memory(state: dict) -> None:
    MEMORY_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def export_memory(path: Optional[Path] = None) -> Path:
    destination = path or MEMORY_PATH
    source = MEMORY_PATH.read_text(encoding="utf-8") if MEMORY_PATH.exists() else "{}"
    destination.write_text(source, encoding="utf-8")
    log("INFO", "export_memory", result=str(destination))
    return destination


def import_memory(path: Path, apply_callback: Optional[Callable[[dict], None]] = None) -> dict:
    """Import memory without ever writing to the read-only config file."""
    content = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict):
        raise ValueError("Memory file must contain an object")
    MEMORY_PATH.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    if apply_callback is not None:
        apply_callback(content)
    log("INFO", "import_memory", result=str(path))
    return content


def load_config() -> dict:
    """Read config/config.toml and fall back to the bundled default."""
    global CONFIG_SOURCE, CONFIG_FALLBACK_USED, CONFIG_WARNINGS
    CONFIG_WARNINGS = []
    for path, level in ((CONFIG_PATH, "INFO"), (DEFAULT_CONFIG_PATH, "WARN")):
        try:
            with path.open("rb") as config_file:
                config = tomllib.load(config_file)
            CONFIG_SOURCE = path.name
            CONFIG_FALLBACK_USED = path == DEFAULT_CONFIG_PATH
            if CONFIG_FALLBACK_USED:
                CONFIG_WARNINGS.append(f"{CONFIG_PATH.relative_to(ROOT)} -> {path.relative_to(ROOT)}")
            log(level, "load_config", result=path.name)
            return config
        except FileNotFoundError:
            if path == CONFIG_PATH:
                CONFIG_WARNINGS.append(f"missing {path.relative_to(ROOT)}")
            continue
        except (OSError, tomllib.TOMLDecodeError) as exc:
            CONFIG_WARNINGS.append(f"invalid {path.relative_to(ROOT)}: {exc}")
            log("ERROR", "load_config", error=f"{path.name}: {exc}")
    CONFIG_SOURCE = "built-in"
    CONFIG_FALLBACK_USED = True
    CONFIG_WARNINGS.append("using built-in configuration")
    # Deep copy: callers may mutate nested tables (e.g. app/splash) and must not
    # corrupt the module level BUILTIN_CONFIG used by later reloads.
    return copy.deepcopy(BUILTIN_CONFIG)


def load_rosters() -> tuple[dict, bool]:
    """Load named rosters, falling back to the bundled minimal roster."""
    for path, is_fallback in ((NAME_PATH, False), (DEFAULT_NAME_PATH, True)):
        try:
            with path.open("rb") as name_file:
                data = tomllib.load(name_file)
            rosters = data.get("rosters")
            if not isinstance(rosters, dict) or not rosters:
                raise ValueError("missing [rosters.*.names] entries")
            valid = {
                key: roster
                for key, roster in rosters.items()
                if isinstance(roster, dict)
                and isinstance(roster.get("names"), dict)
                and roster["names"]
            }
            if valid:
                if is_fallback:
                    CONFIG_WARNINGS.append(f"{NAME_PATH.relative_to(ROOT)} -> {path.relative_to(ROOT)}")
                return valid, is_fallback
        except FileNotFoundError:
            CONFIG_WARNINGS.append(f"missing {path.relative_to(ROOT)}")
        except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
            CONFIG_WARNINGS.append(f"invalid {path.relative_to(ROOT)}: {exc}")
            log("ERROR", "load_rosters", error=f"{path.name}: {exc}")
    return {"class_1": {"name": {"en_US": "Default roster"}, "names": {"0": "Student 1"}}}, True
