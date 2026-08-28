"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
"""
StateManager: 管理记忆文件（导入/导出/应用）与日志记录

功能：
- 程序启动时不自动覆盖 config.json，仅提供加载/保存记忆的方法
- 导出/导入记忆文件（doc/memory.json），导入后调用回调以刷新程序状态
- 记录规范化英文日志到 doc/log.json

注意：该模块仅负责数据层；UI 刷新回调应由 main.py 提供并传入 import_memory 的 callback。
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Optional, Callable, Any

ROOT = Path(__file__).parent.parent
DOC = ROOT / "doc"
DOC.mkdir(exist_ok=True)
MEMORY_PATH = DOC / "memory.json"
LOG_PATH = DOC / "log.json"


def _now_iso():
    return datetime.now().isoformat(sep=' ', timespec='seconds')


def _ensure_log_exists():
    if not LOG_PATH.exists():
        LOG_PATH.write_text("[]", encoding="utf-8")


def log(level: str, action: str, result: Optional[Any] = None, error: Optional[str] = None):
    """追加一条规范化英文日志到 doc/log.json

    字段：time, level, action, result, error
    """
    _ensure_log_exists()
    try:
        with LOG_PATH.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = []

    entry = {
        "time": _now_iso(),
        "level": level.upper(),
        "action": action,
        "result": result,
        "error": error
    }
    data.append(entry)
    try:
        with LOG_PATH.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        print("Failed to write log:", exc)


def export_memory(path: Optional[Path] = None) -> Path:
    """导出当前记忆（把 doc/memory.json 复制到指定位置或返回其路径）"""
    if path is None:
        return MEMORY_PATH
    else:
        content = MEMORY_PATH.read_text(encoding='utf-8') if MEMORY_PATH.exists() else "{}"
        path.write_text(content, encoding='utf-8')
        return path


def import_memory(path: Path, apply_callback: Optional[Callable[[dict], None]] = None) -> dict:
    """导入记忆文件到 doc/memory.json，但不更改 config.json。导入后调用 apply_callback(state_dict).

    返回导入的字典（或抛出异常）
    """
    content = json.loads(path.read_text(encoding='utf-8'))
    # 写入 doc/memory.json（覆盖）
    MEMORY_PATH.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding='utf-8')
    log("INFO", "import_memory", result=f"imported {str(path)}")
    # 立即应用（由主程序提供回调来刷新状态）
    if apply_callback is not None:
        try:
            apply_callback(content)
            log("INFO", "apply_memory", result="applied")
        except Exception as exc:
            log("ERROR", "apply_memory", error=str(exc))
            raise
    return content


def load_memory() -> dict:
    """读取当前 doc/memory.json 并返回 dict，如果不存在则返回默认结构并写入文件"""
    if not MEMORY_PATH.exists():
        default = {
            "loaded_config": None,
            "last_results": {
                "single": None,
                "multi": None,
                "lift": None,
                "scrollsingle": None
            }
        }
        MEMORY_PATH.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding='utf-8')
        return default
    try:
        return json.loads(MEMORY_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {"loaded_config": None, "last_results": {"single": None, "multi": None, "lift": None, "scrollsingle": None}}


def save_memory(state: dict):
    MEMORY_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    log("INFO", "save_memory", result="saved")


def load_config() -> dict:
    """读取 doc/config.json（只读），若不存在或损坏则回退到 config.default.json 并返回内容。不会修改任何配置文件。

    返回解析的配置字典（或空字典）。
    """
    doc_conf = ROOT / "doc" / "config.json"
    default_conf = ROOT / "config.default.json"
    cfg = None
    if doc_conf.exists():
        try:
            cfg = json.loads(doc_conf.read_text(encoding='utf-8'))
            log("INFO", "load_config", result=f"loaded doc/config.json")
            return cfg
        except Exception as exc:
            log("ERROR", "load_config", error=f"failed to parse doc/config.json: {exc}")
            cfg = None
    if default_conf.exists():
        try:
            cfg = json.loads(default_conf.read_text(encoding='utf-8'))
            log("WARN", "load_config", result=f"loaded config.default.json")
            return cfg
        except Exception as exc:
            log("ERROR", "load_config", error=f"failed to parse config.default.json: {exc}")
    # 最后返回空字典
    return {}
