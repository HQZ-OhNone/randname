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
- **抽取靈活**，支持多抽、減量抽與、滾動抽取等多種模式。
- **多語言與主題**，支持简体中文、正體中文和英语，六種主题色系均提供明暗版本。
- **開源免費**，本程序在 [GPL v3.0](./doc/gpl-3.0.md) 下發佈，任何人可以使用。

### 技術實現
- python3.12.10
- qt6.11.1(pyside6)

### 許可證
[GNU General Public License v3.0](./doc/gpl-3.0.md)

-----

### 使用

帮助文档： [简体中文](./doc/help_zh_CN.md) | [正體中文](./doc/help_zh_TW.md) | [English (US)](./doc/help_en_US.md)

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
python -m pip install --upgrade pip
pip install pyside6==6.11.1
```
4. 運行 main.py

#### 配置与运行记录
- 程序配置位于 `config/config.toml`，名单位于 `config/name.toml`，语言包位于 `config/language.toml`，均使用 TOML。
- `config/theme.toml` 集中保存主题颜色、多语言名称和默认主题；配置或名单缺失时分别回退到 `.config.default.toml` 和 `.name.default.toml`。
- 当 `config/config.toml` 与独立配置档的同类设置不同时，优先使用独立配置档：主题以 `theme.toml` 的 `default`、语言以 `language.toml` 的 `preferred` 为准，`config.toml` 的同名项仅作后备。
- 启动画面与主窗口均可选择固定尺寸或屏幕比例尺寸；`[splash]` 支持关闭、就绪后关闭或固定显示时间。
- `doc/memory.json` 保存各模式最近结果，`doc/log.log` 保存精简的英文逐行日志；两者均不会提交到 Git。
- 菜单栏“文件 -> 导入...”和“导出...”用于记忆文件，不会覆盖 `config/` 下的配置。

#### 方案三、自行編譯二進制文件
1. 在本機配置 Python 環境，可贊考 [Python官方網站](https://www.python.org/)
2. 將倉庫克隆到本地，如：
```git
git clone https://github.com/HQZ-OhNone/randname.git
```
3. 安裝 ```nuitka``` 庫與 ```pyside6``` 庫，推薦使用 ```pip```，如：
```pip
python -m pip install --upgrade pip
pip install nuitka==4.1.3 pyside6==6.11.1
```
4. 使用 Nuitka 經行編譯，如：

直接运行仓库中的 [`build_linux.sh`](./build_linux.sh) 或 [`build_windows.bat`](./build_windows.bat)。

5. 找到 ```build``` 目錄下的可執行文件，運行即可。
6. 編譯完成後亦可打包分發
- Linux
```zsh
cd build
mv main.dist randname3
tar -cavf randname3_linux.tar.xz randname3
```

-----

### 未來開發
项目 TODO:

- 导入：
  - [x] 学号JSON
  - [w] 座位分布JSON
  - [w] 多字典映射不同属性

- GUI：
  - 主界面：
    - [x] Multi: 多抽
    - [x] Lift: 减量抽
    - [x] ScrollSingle: 滚动抽取（默认模式）
    - [w] Seats: 抽座位坐标
  - 菜单栏：
    - [x] 文件：退出、保存状态
    - [x] 模式：多抽/减量抽/滚动抽取
    - [x] 关于：许可证、仓库
    - [x] 主题：深色、浅色、蓝色、琥珀、绿色、紫色
    - [x] 反馈

- 抽取：
  - [x] Multi: 连抽
  - [x] Lift: 减量抽
  - [w] Seats: 抽座位坐标

- 技术实现：
  - python3.12.10
  - qt6.11.1


### 反饋
歡迎提 issue 或發郵件

-----
HQZ-OhNone \<ohnone_hqz@outlook.com>  
lastedit: 2026-09-19
