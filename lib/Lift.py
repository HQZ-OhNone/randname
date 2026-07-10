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

def Lift(names, quantity):
    """
    減量抽取
    :param names: dict
    :param quantity: int
    :return: dict
    """
    # 初始化量
    print(f"=> mode: Lift")
    print(f"==> quantity: {quantity}")
    output = {"mode": "Lift"}
    outdict = {}
    outlist = []
    selected_keys = []

    # 判斷是否滿足減量抽取
    if quantity > len(names):  # 如果不滿足，則提示後退出
        print(f"==> warn: 給定數量({quantity})大於總數({len(names)})")
        print("==> exit: warn")
    else:    # 如果滿足減量抽取，則執行
        keys_remain = list(names.keys())
        for i in range(quantity):
            # 隨機選擇出鍵
            selected_key = random.choice(keys_remain)
            selected_keys.append(selected_key)
            keys_remain.remove(selected_key)
            print(keys_remain)

        # 生成输出，每次循環加入一個選中的鍵值對
        for i in range(len(selected_keys)):
            outdict[i] = {selected_keys[i]: names[selected_keys[i]]}
        output["outdict"] = outdict

        # 輸出結果
        print(f"==> output: {output}")
        print("==> exit: Lift")
        return output

