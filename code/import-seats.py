"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
"""
读取:
    randname/config/
    randname/config/seats.json
执行:
    将 seats.json 读取为字典
    打印测试
"""
from pathlib import Path
import json

# 设定文件路径
path_code = Path(__file__).parent
path_root = path_code.parent
path_config = path_root / "config"
path_seats = path_config / "seats.json"

# 判断所需文件是否齐全
passon = True
if path_config.exists():
    print("找到: config")
elif not path_seats.exists():
    print("seats.json 不存在！")
    print("退出")
    passon = False
else:
    print("config 文件夹不存在！")
    print("退出")
    passon = False
print("找到: seats.json")

# 如果文件齐全，则执行：
if passon:
    # 读取JSON
    seats = json.loads(path_seats.read_text(encoding="utf-8"))
    print("已导入: seats.json")
    print(seats)

