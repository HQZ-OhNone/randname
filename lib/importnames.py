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
# load configuration via StateManager if available
from pathlib import Path
import json

# Try to use StateManager.load_config to centralize config handling
names = {}
loaded_config = None
try:
    from lib import StateManager
    cfg = StateManager.load_config()
    if isinstance(cfg, dict):
        loaded_config = cfg
        names = cfg.get('names', {}) if isinstance(cfg.get('names', {}), dict) else {}
        print('Loaded configuration via StateManager')
except Exception as exc:
    # Fallback: try to read doc/config.json directly
    path_root = Path(__file__).parent.parent
    path_doc_config = path_root / 'doc' / 'config.json'
    path_default = path_root / 'config.default.json'
    try:
        if path_doc_config.exists():
            loaded_config = json.loads(path_doc_config.read_text(encoding='utf-8'))
            names = loaded_config.get('names', {}) if isinstance(loaded_config, dict) else {}
            print('Loaded doc/config.json (fallback)')
        elif path_default.exists():
            loaded_config = json.loads(path_default.read_text(encoding='utf-8'))
            names = loaded_config.get('names', {}) if isinstance(loaded_config, dict) else {}
            print('Loaded config.default.json (fallback)')
    except Exception as exc2:
        print('Failed to load configuration:', exc2)

if not isinstance(names, dict):
    names = {}

# expose for other modules
__all__ = ['names', 'loaded_config']
print('names count:', len(names))
