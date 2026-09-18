"""Configuration, memory and concise structured logging for randname."""

from datetime import datetime
import json
from pathlib import Path
import tomllib
from typing import Any, Callable, Optional

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "doc"
DOC.mkdir(exist_ok=True)
MEMORY_PATH = DOC / "memory.json"
LOG_PATH = DOC / "log.json"
CONFIG_SOURCE = ""
CONFIG_FALLBACK_USED = False


def _now_iso() -> str:
    return datetime.now().isoformat(sep=" ", timespec="seconds")


def _default_memory() -> dict:
    return {
        "loaded_config": None,
        "last_results": {
            "Single": None,
            "Multi": None,
            "Lift": None,
            "ScrollSingle": None,
        },
    }


def log(level: str, action: str, result: Optional[Any] = None,
        error: Optional[str] = None) -> None:
    """Append only important, stable English fields to the JSON log."""
    try:
        data = json.loads(LOG_PATH.read_text(encoding="utf-8")) if LOG_PATH.exists() else []
        if not isinstance(data, list):
            data = []
        entry = {"time": _now_iso(), "level": level.upper(), "action": action}
        if result is not None:
            entry["result"] = result
        if error is not None:
            entry["error"] = error
        data.append(entry)
        LOG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # Logging must never prevent a classroom draw from completing.
        pass


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
    """Read TOML config, falling back to the bundled default TOML."""
    global CONFIG_SOURCE, CONFIG_FALLBACK_USED
    configured = ROOT / "doc" / "config.toml"
    default = ROOT / "config.default.toml"
    for path, level in ((configured, "INFO"), (default, "WARN")):
        try:
            with path.open("rb") as config_file:
                config = tomllib.load(config_file)
            CONFIG_SOURCE = path.name
            CONFIG_FALLBACK_USED = path == default
            log(level, "load_config", result=path.name)
            return config
        except FileNotFoundError:
            continue
        except (OSError, tomllib.TOMLDecodeError) as exc:
            log("ERROR", "load_config", error=f"{path.name}: {exc}")
    return {}
