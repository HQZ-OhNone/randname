"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
"""
实现:
    減量抽取
输出示例:
example = {"mode":"Lift",
           "time":"2026-03-15-12:30:23",
           "quantity":{"total":6,
                       "wasted":1,
                       "selected":3,
                       "Lift":2},
           "outdict":{"0":{"name":"李華","code":"1"},
                      "1":{"name":"周原","code":"0"},
                      "2":{"name":"珍瑞","code":"3"}},
           "Liftdict":[{"name":"張三","code":"5"},
                       {"name":"李四","code":"2"}],
           "alllist":[{"name":"周原","code":"0"},
                      {"name":"李華","code":"1"},
                      {"name":"李四","code":"2"},
                      {"name":"珍瑞","code":"3"},
                      {"name":"王五","code":"4"},
                      {"name":"張三","code":"5"}]
           }
"""

import random
from datetime import datetime

def Lift(alllist, Liftdict, quantity):
    """
    減量抽取
    """
    # 初始化量
    print(f"=> mode: Lift")
    print(f"===> quantity: {quantity}")
    output = {"mode": "Lift",
              "quantity": {"total": len(alllist),
                           "wasted": len(alllist) - len(Liftdict),
                           "selected": quantity,
                           "Lift": len(Liftdict) - quantity},
              "alllist": alllist
    }
    outdict = {}
    selected_keys = []

    # 獲取當前時間
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d-%H:%M:%S")
    output["time"] = time_str

    # 判斷是否滿足減量抽取
    if quantity > len(Liftdict):  # 如果不滿足，則提示後退出
        print(f"===> warn: 給定數量({quantity})大於總數({len(Liftdict)})，無法進行減量抽取。")
        print("===> exit: warn")
    else:    # 如果滿足減量抽取，則執行
        keys_remain = list(Liftdict.keys())
        for i in range(quantity):
            # 隨機選擇出鍵
            selected_key = random.choice(keys_remain)
            selected_keys.append(selected_key)
            keys_remain.remove(selected_key)
            print(keys_remain)

        # 生成 outdict ，每次循環加入一個選中的鍵值對
        for i in range(len(selected_keys)):
            outdict[str(i)] = {selected_keys[i]: Liftdict[selected_keys[i]]}
        output["outdict"] = outdict
        
        # 生成 Liftdict ，每次循環加入一個未選中的鍵值對
        Liftdict_remain = {}
        for key in keys_remain:
            Liftdict_remain[key] = Liftdict[key]
        output["Liftdict"] = Liftdict_remain

        # 輸出結果
        print(f"===> output: {output}")
        print("===> exit: Lift")
        return output

