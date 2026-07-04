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

def Lift(names, num):
    """
    減量抽取
    :param names: dict
    :param num: int
    :return: dict
    """
    # 初始化量
    output = {}
    selected_keys = []

    # 判斷是否滿足減量抽取
    if num > len(names):
        raise ValueError("減量抽取的數量不能大於字典的長度。")
    else:    # 如果滿足減量抽取，則執行
        print("=> Lift")
        for i in range(num):
            keys_remain = list(names.keys())
             # 隨機選擇出鍵
            selected_key = keys_remain.pop(int(random.choice(keys_remain)))
            selected_keys.append(selected_key)

        # 生成输出字典
        for i in selected_keys:
            output[i] = names[i]

        # 輸出結果
        print(f"=> Lift: {output}")
        return output

