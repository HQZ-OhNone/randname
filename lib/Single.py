"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
"""
实现:
    单抽
输出:
    {"module": "Single", "output": {0: 11}}
    打印输出
"""

import random

def Single(names):
    """
    单抽
    :param names: dict
    :return: str
    """
    # 隨機選擇
    slected_key = random.choice(list(names.keys()))
    slected_value = names[slected_key]

    # 生成输出字典
    output = {slected_key: slected_value}

    # 輸出結果
    print(f"=> Single: {output}")
    return slected_value

