from pathlib import Path
import json

# 设定文件路径
path_code = Path(__file__).parent
path_root = path_code.parent
path_config = path_root / "config"
path_names = path_config / "names.json"
path_seats = path_config / "seats.json"

passon = True
if path_config.exists():
    if not path_names.exists():
        print("names.json 不存在！")
        passon = False
    if not path_seats.exists():
        print("seats.json 不存在！")
        passon = False
else:
    print("config 文件夹不存在！")
    passon = False

if passon:
    # 读取JSON
    names = json.loads(path_names.read_text(encoding="utf-8"))
    seats = json.loads(path_seats.read_text(encoding="utf-8"))

    # 打印测试
    print(names)
    print(seats)
