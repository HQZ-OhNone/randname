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
path_config = Path(__file__).parent.parent / "config"
path_names = path_config / "names.json"

# 判断所需文件是否齐全
passon = True
if path_config.exists():
    print("找到: config")
else:
    print("config 文件夹不存在！")
    passon = False
if path_names.exists():
    print("找到: names.json")
else:
    print("names.json 不存在！")
    passon = False

# 如果文件齐全，则执行：
if passon:
    # 读取JSON
    names = json.loads(path_names.read_text(encoding="utf-8"))
    print("已导入: names.json")
    print(names)
else:
    print("退出")
