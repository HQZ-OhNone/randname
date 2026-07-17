"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
"""
实现:
    多抽
输出示例:
example = {"mode":"Multi",
           "time":"2026-03-15-12:30:23",
           "quantity":{"total":6,
                       "selected":3},
           "outdict":{"0":{"name":"李華","code":"1"},
                      "1":{"name":"周原","code":"0"},
                      "2":{"name":"珍瑞","code":"3"}}
           }
"""

import random
from datetime import datetime

def Multi(alllist, quantity):
    """
    多抽
    """
    # 初始化量
    print(f"=> mode: Multi")
    output = {"mode": "Multi",
              "quantity": {"total": len(alllist),
                           "selected": quantity},
    }
    outdict = {}
    selected_keys = []

    # 獲取當前時間
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d-%H:%M:%S")
    output["time"] = time_str

    # 判斷是否滿足多抽
    if quantity > len(alllist):  # 如果不滿足，則提示後退出
        print(f"===> warn: 給定數量({quantity})大於總數({len(alllist)})，無法進行多抽。")
        # 生成 outdict ，直接返回空字典
        output["outdict"] = {}
        # 輸出結果
        print(f"===> output: {output}")
        print("===> exit: Multi")
        return output
    else:    # 如果滿足多抽，則執行
        keys_remain = list(alllist.keys())
        for i in range(quantity):
            # 隨機選擇出鍵
            selected_key = random.choice(keys_remain)
            selected_keys.append(selected_key)
            keys_remain.remove(selected_key)
            print(keys_remain)

        # 生成 outdict ，每次循環加入一個選中的鍵值對
        for i in range(len(selected_keys)):
            outdict[str(i)] = {"code":selected_keys[i],
                               "name": alllist[selected_keys[i]]}
        output["outdict"] = outdict

        # 輸出結果
        print(f"===> output: {output}")
        print("===> exit: Multi\n")
        return output
