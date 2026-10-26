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
- **抽取靈活**，支持單抽、多抽、減量抽、滾動單抽、滾動多抽與滾動減量抽。
- **多語言與主題**，支持简体中文、正體中文和英语，多種主题色系均提供明暗版本。
- **開源免費**，本程序在 [GPL v3.0](./doc/gpl-3.0.md) 下發佈，任何人可以使用。

### 技術實現
- python3.12.10
- qt6.11.1(pyside6)
- 目前版本：3.10.3

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
- `config/theme.toml` 集中保存主題顏色、多語言名稱、可選背景圖和預設主題；配置或名單缺失時分別回退到 `.config.default.toml` 和 `.name.default.toml`。背景圖只需在主題內新增 `[themes.<鍵名>.background]`，支援自動裁切與六種模糊方向；預設 `randname-dark` 不含背景圖，`randname-bg-light` 為示例主題。
- `config/config.toml` 内每一項都有面向首次使用者的注释，可直接照着修改。
- 每次启动都从配置档读取界面状态：主题以 `theme.toml` 的 `default`、语言以 `language.toml` 的 `preferred`、模式/名单/日志等级/窗口尺寸以 `config.toml` 为准，不读取记忆偏好。
- 主窗口可自由拉伸，但下次启动仍使用配置档的初始尺寸；`size_mode = "maximum"` 时启动即最大化；固定尺寸大于可用屏幕时会暂时最大化，且不改写配置文件。输出框不会因为名字过长而改变窗口大小，而是自动切换单行/多行显示，必要时缩小字号；滚动多抽与滚动减量抽使用固定格子，已抽出的名字位置不会随其他名字滚动。
- 多抽、减量抽、滚动多抽与滚动减量抽页面均提供纵向滑动条，可在 `1` 到当前名单人数之间调节，支持触控，并与加减按钮和数量显示框同步。
- 姓名排版经过紧凑化：非滚动模式缩短姓名间距，滚动模式在大屏上按内容收拢格子并保持同一轮位置固定。
- 启动画面与主窗口均支持固定尺寸、屏幕比例尺寸或最大化；`[splash]` 支持关闭、就绪后关闭或固定显示时间（时间到后才显示主窗口）。
- 图标、启动画面、帮助、许可证、日志与记忆文件位置固定于程序代码，不再通过配置改动。
- `doc/memory.json` 只保存各模式最近结果，`doc/log.log` 按所选等级保存精简的英文逐行日志；两者均不会提交到 Git。
- 菜单栏“文件 -> 导入记忆...”和“导出记忆...”用于导入/导出最近结果，不会覆盖 `config/` 下的配置；“文件 -> 初始化”会清空 `doc/memory.json`、把所有模式数量恢复为 1 并清除已显示结果，日志会保留。
- “关于 > 程序日志”显示本次运行的全部等级日志（按等级高亮行首），不受写文件等级限制；帮助、许可证也使用同一个只读查看器。
- “关于 > 检查更新”会查询 GitHub Releases，并在窗口中显示检测状态与 `doc/history.md`；仅在检测到新版本时启用“更新”，另提供“手动查询”打开 Releases 页面。
- 模式名称统一为 `Multi`、`ScrollMulti`、`ScrollSingle`、`Single`、`Lift`、`ScrollLift`，界面、配置与文档保持一致。

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

直接运行仓库中的 [`script/build.sh`](./script/build.sh) 或 [`script/build.bat`](./script/build.bat)。构建脚本会遍历 `ui/*.ui`，自动编译全套最新界面文件到 `lib/ui_*.py`。

5. 找到 ```build``` 目錄下的可執行文件，運行即可。
6. 編譯完成後亦可打包分發
- Linux
```zsh
cd build
mv main.dist randname3
tar -cavf randname3_linux.tar.xz randname3
```

### 反饋
歡迎提 [issue](https://github.com/HQZ-OhNone/randname/issues) 或寄信至 <ohnone_hqz@outlook.com>。

-----
HQZ-OhNone \<ohnone_hqz@outlook.com>  
lastedit: 2026-10-25
