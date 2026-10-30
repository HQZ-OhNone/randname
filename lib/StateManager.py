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
    "app": {
        "default_mode": "Multi",
        "roster": "class_1",
    },
    "splash": {
        "enabled": True,
        "mode": 0,
        "duration_ms": 1000,
        "size_mode": "screen_ratio",
        "screen_ratio": 0.25,
        "width": 500,
        "height": 250,
    },
    "window": {
        "size_mode": "screen_ratio",
        "screen_ratio": 0.75,
        "aspect_ratio": 1.5,
        "width": 1000,
        "height": 600,
        "resizable": True,
        "fullscreen": False,
    },
    "ui": {
        "font_family": "",
        "display_font_size": 33,
        "display_min_font_size": 12,
        "display_font_step": 1,
        "display_line_spacing": 1.0,
        "display_padding": 8,
        "button_font_size": 24,
        "quantity_font_size": 20,
    },
    "scroll": {"rate": 30},
    "viewer": {
        "refresh_ms": 500,
        "font_size": 12,
        "max_screen_ratio": 0.85,
        "touch_scroll": True,
    },
    "statusbar": {
        "show_mode": True,
        "show_roster": True,
        "show_quantity": True,
        "show_theme": True,
        "show_language": True,
        "show_log_level": True,
        "show_version": True,
    },
    "logging": {"level": "INFO"},
    "update": {"timeout_ms": 15000},
}


def _now_iso() -> str:
    return datetime.now().isoformat(sep=" ", timespec="seconds")


class _SessionLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        line = self.format(record)
        SESSION_LOG_RECORDS.append(line)
        if record.levelno < LOG_LEVELS[CURRENT_LOG_LEVEL]:
            return
        try:
            with LOG_PATH.open("a", encoding="utf-8") as log_file:
                log_file.write(line + "\n")
        except OSError:
            pass


def configure_logging(level: str = "INFO") -> str:
    """Set the file log threshold and capture every record in this session."""
    global CURRENT_LOG_LEVEL
    selected = level.upper() if isinstance(level, str) else "INFO"
    if selected == "WARN":
        selected = "WARNING"
    if selected not in LOG_LEVELS:
        selected = "INFO"
    CURRENT_LOG_LEVEL = selected
    root_logger = logging.getLogger()
    # 会话缓冲区必须收到全部等级；实际写文件时再按 CURRENT_LOG_LEVEL 过滤。
    root_logger.setLevel(logging.DEBUG)
    handler = next(
        (item for item in root_logger.handlers if isinstance(item, _SessionLogHandler)),
        None,
    )
    if handler is None:
        handler = _SessionLogHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        root_logger.addHandler(handler)
    handler.setLevel(logging.DEBUG)
    # 控制台/其它 handler 仍按所选等级输出，避免 DEBUG 噪音。
    for item in root_logger.handlers:
        if isinstance(item, logging.StreamHandler) and not isinstance(item, _SessionLogHandler):
            item.setLevel(LOG_LEVELS[selected])
    return selected


def session_log_text() -> str:
    """Return all records captured since this process imported StateManager."""
    return "\n".join(SESSION_LOG_RECORDS)


def _default_memory() -> dict:
    return {
        "last_results": {
            "Multi": None,
            "Lift": None,
            "ScrollMulti": None,
            "ScrollLift": None,
        },
    }


def reset_memory() -> dict:
    """把记忆文件恢复为初始状态，仅保留空的最近结果。"""
    memory = _default_memory()
    save_memory(memory)
    log("INFO", "reset_memory", result="default")
    return memory


def _normalize_memory(memory: Any) -> dict:
    """只保留最近结果；旧记忆中的偏好与配置快照会被忽略。"""
    default = _default_memory()
    if not isinstance(memory, dict):
        return default
    last_results = memory.get("last_results")
    if isinstance(last_results, dict):
        for key in default["last_results"]:
            default["last_results"][key] = last_results.get(key)
    return default


def log(level: str, action: str, result: Optional[Any] = None,
        error: Optional[str] = None) -> None:
    """Append one concise, machine-readable English text line."""
    normalized_level = level.upper()
    if normalized_level == "WARN":
        normalized_level = "WARNING"
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
        if LOG_LEVELS.get(normalized_level, logging.INFO) < LOG_LEVELS[CURRENT_LOG_LEVEL]:
            return
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
    except (OSError, json.JSONDecodeError):
        return _default_memory()
    normalized = _normalize_memory(memory)
    if normalized != memory:
        try:
            save_memory(normalized)
        except OSError:
            pass
    return normalized


def save_memory(state: dict) -> None:
    """原子写入记忆文件，避免程序中断时留下半个 JSON。"""
    payload = json.dumps(state, ensure_ascii=False, indent=2)
    tmp_path = MEMORY_PATH.with_suffix(MEMORY_PATH.suffix + ".tmp")
    tmp_path.write_text(payload, encoding="utf-8")
    tmp_path.replace(MEMORY_PATH)


def export_memory(path: Optional[Path] = None) -> Path:
    destination = path or MEMORY_PATH
    state = load_memory()
    destination.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log("INFO", "export_memory", result=str(destination))
    return destination


def import_memory(path: Path, apply_callback: Optional[Callable[[dict], None]] = None) -> dict:
    """导入最近结果；不会写入 config/ 下的配置，也不会恢复旧版界面偏好。"""
    content = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict):
        raise ValueError("Memory file must contain an object")
    normalized = _normalize_memory(content)
    save_memory(normalized)
    if apply_callback is not None:
        apply_callback(normalized)
    log("INFO", "import_memory", result=str(path))
    return normalized


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
