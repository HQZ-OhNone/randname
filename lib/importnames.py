"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
"""
读取:
    randname/config/
    randname/config/names.json
执行:
    将 names.json 读取为字典
    打印测试
"""
from pathlib import Path
import json

# 设定文件路径
"""
path_code = Path(__file__).parent
path_root = path_code.parent
path_config = path_root / "config"
path_names = path_config / "names.json"
"""
# 新的配置加载：优先读取 doc/config.json（只读），若不可用则回退到 config.default.json
from pathlib import Path
import json
from PySide6.QtWidgets import QMessageBox

path_root = Path(__file__).parent.parent
path_doc_config = path_root / "doc" / "config.json"
path_default = path_root / "config.default.json"

names = {}
loaded_config = None

# 尝试加载 doc/config.json
if path_doc_config.exists():
    try:
        loaded_config = json.loads(path_doc_config.read_text(encoding="utf-8"))
        names = loaded_config.get("names", {}) if isinstance(loaded_config, dict) else {}
        print("已从 doc/config.json 读取配置")
    except Exception as exc:
        print("读取 doc/config.json 失败：", exc)
        loaded_config = None

# 若未能加载，则回退到 config.default.json 并弹窗提示（GUI 环境）
if not names and path_default.exists():
    try:
        default_config = json.loads(path_default.read_text(encoding="utf-8"))
        names = default_config.get("names", {}) if isinstance(default_config, dict) else {}
        loaded_config = default_config
        # 弹窗提示（如果在 QApplication 中）
        try:
            QMessageBox.information(None, "配置提示", "未找到有效的 doc/config.json，已加载 config.default.json（只读）。")
        except Exception:
            # 如果尚未创建 QApplication 或者在非 GUI 线程，忽略弹窗
            print("提示：未找到有效的 doc/config.json，已使用默认配置。")
        print("已加载默认配置 config.default.json")
    except Exception as exc:
        print("读取 config.default.json 失败：", exc)

# 最终确保 names 为 dict
if not isinstance(names, dict):
    names = {}

print("names count:", len(names))
