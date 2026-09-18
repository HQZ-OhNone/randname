```ascii art
                      _                            
  _ __ __ _ _ __   __| |_ __   __ _ _ __ ___   ___  
 | '__/ _` | '_ \ / _` | '_ \ / _` | '_ ` _ \ / _ \ 
 | | | (_| | | | | (_| | | | | (_| | | | | | |  __/ 
 |_|  \__,_|_| |_|\__,_|_| |_|\__,_|_| |_| |_|\___| 
---HQZ-OhNone <ohnone_hqz@outlook.com>
```
## 全新的課堂小工具

### 特點
- **簡潔易用**，無需任何經驗、開箱即用、上手就會，學習成本極低。
- **功能豐富**，支持 Single、Multi、Lift、ScrollSingle 四种模式，启动后默认进入 ScrollSingle。
- **可换主题**，菜单栏“主题”提供深色、浅色、蓝色、琥珀、绿色和紫色主题；主题配置位于 `theme/*.toml`。
- **開源免費**，本程序在 [GPL v3.0](./doc/gpl-3.0.txt) 下發佈，任何人可以使用。

### 技術實現
- python3.12.10
- qt6.11.1(pyside6)

### 許可證
[GNU General Public License v3.0](./doc/gpl-3.0.txt)

-----

### 使用

#### 方案一、使用預編譯程序
1. 請從 [releases](https://github.com/HQZ-OhNone/randname/releases) 下載預編譯程序
2. 將壓縮包解壓到合適的目錄
3. 運行 ```randname``` 程序

#### 方案二、從 Python 源碼運行
1. 在本機配置 Python 環境，可贊考 [Python官方網站](https://www.python.org/)
2. 將倉庫克隆到本地，如：
```git
git clone https://github.com/HQZ-OhNone/randname.git
```
3. 安裝 ```pyside6``` 庫，推薦使用 ```pip```，如：
```pip
pip install pyside6
```
4. 運行 main.py

#### 配置与运行记录
- 当前配置为 `doc/config.toml`，程序只读加载；文件缺失或损坏时使用隐藏的 `.config.default.toml` 并提示。
- 配置使用 TOML，包含姓名、窗口初始尺寸、默认模式、滚动速度和主题等选项，可直接编辑注释旁的值。
- `doc/memory.json` 保存各模式最近结果，`doc/log.log` 保存精简的英文逐行日志；两者均不会提交到 Git。
- 菜单栏“文件 -> 导入...”和“导出...”用于记忆文件，不会覆盖 `doc/config.toml`。

#### 方案三、自行編譯二進制文件
1. 在本機配置 Python 環境，可贊考 [Python官方網站](https://www.python.org/)
2. 將倉庫克隆到本地，如：
```git
git clone https://github.com/HQZ-OhNone/randname.git
```
3. 安裝 ```pyside6``` 庫，推薦使用 ```pip```，如：
```pip
pip install pyside6
```
4. 安裝 ```nuitka``` 庫，推薦使用 ```pip```，如：
```pip
pip install nuitka
```
5. 使用 Nuitka 經行編譯，如：
- Linux
```nuitka
nuitka \
--standalone \
--enable-plugin=pyside6 \
--include-data-file=.config.default.toml=.config.default.toml \
--include-data-dir=doc=doc \
--include-data-dir=theme=theme \
--output-dir=build \
--output-filename=randname \
--show-progress \
--lto=yes \
--assume-yes-for-downloads \
--nofollow-import-to=PySide6.QtDesigner \
--nofollow-import-to=PySide6.QtUiTools \
--nofollow-import-to=PySide6.QtNetwork \
--nofollow-import-to=PySide6.QtSql \
--nofollow-import-to=PySide6.QtTest \
--nofollow-import-to=PySide6.QtXml \
main.py
```

- Windows
```nuitka
nuitka `
--standalone `
--enable-plugin=pyside6 `
--include-data-file=.config.default.toml=.config.default.toml `
--include-data-dir=doc=doc `
--include-data-dir=theme=theme `
--output-dir=build `
--output-filename=randname.exe `
--show-progress `
--lto=yes `
--assume-yes-for-downloads `
--nofollow-import-to=PySide6.QtDesigner `
--nofollow-import-to=PySide6.QtUiTools `
--nofollow-import-to=PySide6.QtNetwork `
--nofollow-import-to=PySide6.QtSql `
--nofollow-import-to=PySide6.QtTest `
--nofollow-import-to=PySide6.QtXml `
--windows-disable-console `
main.py
```
6. 找到 ```build``` 目錄下的可執行文件，運行即可。
7. 編譯完成後亦可打包分發
- Linux
```Zsh
cd build
mv main.dist randname3
tar -cavf randname3_linux.tar.zst randname3
```

-----

### 未來開發
项目TODO:

- 导入：
  - [x] 学号JSON
  - [ ] 座位分布JSON
  - [ ] 多字典映射不同属性

- GUI：
  - 主界面：
    - [x] Single: 单抽
    - [x] Multi: 多抽
    - [x] Lift: 减量抽
    - [x] ScrollSingle: 滚动单抽（默认模式）
    - [ ] Seats: 抽座位坐标
  - 菜单栏：
    - [x] 文件：退出、保存状态
    - [x] 模式：单抽/连抽/减量抽/抽座位坐标
    - [x] 关于：许可证、仓库
    - [x] 主题：深色、浅色、蓝色、琥珀、绿色、紫色
    - [ ] 捐赠、反馈

- 抽取：
  - [x] Single: 单抽
  - [x] Multi: 连抽
  - [x] Lift: 减量抽
  - [ ] Seats: 抽座位坐标

- 技术实现：
  - python3.12.10
  - qt6.11.1


### 反饋
歡迎提 issue 或發郵件

-----
HQZ-OhNone \<ohnone_hqz@outlook.com>  
lastedit: 2026-09-19
