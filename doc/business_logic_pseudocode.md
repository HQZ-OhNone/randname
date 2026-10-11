# randname 业务逻辑伪代码说明书

> 本文档以**中文伪代码**完整描述 `randname` 课堂点名工具的全部业务逻辑。
> 覆盖范围：`main.py`（入口 + 主窗口）、`lib/` 下全部模块（状态管理、名单、主题、语言、四种抽取模式）、
> `config/` 与 `.config.default.toml` / `.name.default.toml` 全部配置字段、`ui/` 界面结构、
> `doc/` 运行时产物、构建脚本与 CI 发布流程。
>
> 文档以实际源码为准（核对版本：Python 3.12.10 / PySide6 6.11.1 / 项目 lastedit 2026-10-12）。
> 凡源码中的硬编码常量、中文兜底文案、边界回退分支，均在正文中**原样标注**，
> 并在第 16 章「实现细节与已知特癖」中集中汇总，便于后续维护核对。

---

## 目录

| 章节 | 内容 |
| --- | --- |
| [1](#1-阅读约定) | 阅读约定与伪代码图例 |
| [2](#2-项目总览) | 项目总览、目录结构、运行总流程 |
| [3](#3-数据模型与文件格式) | 配置体系、内建兜底数据、记忆与日志格式、结果结构 |
| [4](#4-启动阶段-startup) | 启动阶段全部函数与 `main()` 完整伪代码 |
| [5](#5-状态管理层-statemanager) | `StateManager`：配置 / 记忆 / 日志 |
| [6](#6-名单管理层-importnames) | `importnames`：名单加载与切换 |
| [7](#7-主题管理层-thememanager) | `ThemeManager`：主题发现、颜色转换、样式表 |
| [8](#8-语言管理层-languagemanager) | `LanguageManager`：语言包、翻译、本地化名称 |
| [9](#9-主窗口-mainwindow) | `MainWindow`：全部成员、菜单、页面、槽函数 |
| [10](#10-四种抽取模式算法) | Multi / Lift / ScrollSingle / ScrollMulti 核心算法 |
| [11](#11-界面结构-ui) | UI 布局与控件对象名全表 |
| [12](#12-国际化键位全表) | 国际化文案键全表 |
| [13](#13-日志与等级过滤) | 日志系统、等级过滤、会话日志 |
| [14](#14-容错与降级矩阵) | 容错与降级矩阵 |
| [15](#15-构建与发布) | 构建脚本与 CI/CD |
| [16](#16-实现细节与已知特癖) | 实现细节与已知特癖清单 |
| [17](#17-附录完整函数索引) | 附录：完整函数索引表 |

---

## 1. 阅读约定

### 1.1 伪代码风格

本文伪代码沿用 Python 语义但去除实现噪音，使用如下约定：

| 记号 | 含义 |
| --- | --- |
| `函数(参数)` | 函数调用，参数为实参 |
| `→` | 返回值 / 赋值结果 |
| `IF ... ELSE ...` | 分支 |
| `FOR x IN 集合` | 遍历 |
| `TRY ... EXCEPT 类型` | 异常捕获，伪代码中显式列出捕获类型 |
| `全局变量` | 模块级全局状态 |
| `#` | 注释 |

### 1.2 术语表

| 术语 | 含义 |
| --- | --- |
| 名单 / roster | 一组可被抽取的人员集合，键为稳定人员编号，值为显示姓名 |
| 多抽 / Multi | 一次性抽取 N 人，本次结果互不重复，**不消耗名单** |
| 减量抽 / Lift | 抽取 N 人，抽中者**从剩余名单中移除**，可连续多轮 |
| 滚动单抽 / ScrollSingle | 名单高速轮播，点「停止」时当前显示者为结果 |
| 滚动多抽 / ScrollMulti | 显示 N 个转盘同时轮播，逐个点「停止」定人，本轮不重复、**不消耗名单** |
| 记忆 / memory | `doc/memory.json`，保存各模式最近一次结果 |
| 会话日志 | 本进程启动以来收集到的日志文本，用于「关于 > 程序日志」 |
| 持久日志 | `doc/log.log`，追加写入的英文单行结构化日志 |
| 启动警告 | 配置/名单/语言/主题缺失或无效时，在状态栏与日志中提示，**不阻断启动** |

### 1.3 全局路径常量

```
ROOT_DIR = Path(main.py 所在目录).resolve().parent        # 项目根 / 可执行文件所在目录
UI_DIR   = ROOT_DIR / "ui"
DOC_DIR  = ROOT_DIR / "doc"
```

`StateManager.ROOT` 与 `ThemeManager.ROOT` / `LanguageManager.ROOT` 均以 `lib/` 的父目录计算，
在打包场景下与 `main.py` 的 `ROOT_DIR` 一致。

---

## 2. 项目总览

### 2.1 定位与特性

- **课堂点名桌面程序**，Python 3.12.10 + Qt 6.11.1（PySide6），GPL v3.0 开源。
- **四种抽取模式**：多抽（Multi）、减量抽（Lift）、滚动单抽（ScrollSingle，默认模式）、滚动多抽（ScrollMulti）。
- **三语言**：简体中文 `zh_CN`、正體中文 `zh_TW`、English `en_US`（内建兜底）。
- **十三套主题**：琥珀、蓝色、深色（经典）、绿色、中性（浅/深）、紫色 各深浅两色 + Randname 粉色调色。
- **全配置化**：启动模式、名单、主题、语言、启动画面、窗口尺寸、滚动速度、日志等级均来自 TOML。
- **只读配置 + 可写记忆分离**：`config/` 下为只读配置，`doc/memory.json` 为可写运行记忆；
  导入/导出记忆**永不写回** `config/`。
- **零运行时 UI 依赖**：`ui/*.ui` 在构建期由 `pyside6-uic` 编译为 `lib/ui_*.py`，运行时不再读取 `.ui`。

### 2.2 目录结构与文件职责

```
randname/
├── main.py                       入口：启动流程 + MainWindow（唯一的 QMainWindow）
├── .config.default.toml          配置备份（config.toml 缺失/损坏时回退）
├── .name.default.toml            名单备份（name.toml 缺失/无可用名单时回退）
├── config/                       只读用户配置
│   ├── config.toml               主配置：app/assets/paths/splash/window/scroll_single/scroll_multi/logging
│   ├── name.toml                 名单目录：[rosters.<键>.name] 与 [rosters.<键>.names]
│   ├── theme.toml                主题目录：default + [themes.<键>]（color_format/name/colors）
│   └── language.toml             语言包：preferred + [languages.<locale>]（display_name/text）
├── lib/
│   ├── StateManager.py           配置 / 名单读取、记忆读写、会话与持久日志
│   ├── importnames.py            名单层：导入即加载，导出 select_roster / reload_data
│   ├── ThemeManager.py           主题发现、颜色格式转换、QSS 生成与应用
│   ├── LanguageManager.py        语言包加载、翻译、本地化名称、系统语言匹配
│   ├── Multi.py                  多抽算法（纯函数）
│   ├── Lift.py                   减量抽算法（纯函数）
│   ├── ScrollSingle.py           滚动单抽控制器 ScrollController（QTimer 驱动）
│   ├── ScrollMulti.py            滚动多抽控制器 ScrollMultiController（QTimer 驱动）
│   ├── ui_main.py                Main.ui 的编译产物 Ui_MainWindow
│   ├── ui_widgetmulti.py         WidgetMulti.ui 的编译产物 Ui_Form
│   ├── ui_widgetlift.py          WidgetLift.ui 的编译产物 Ui_Form
│   ├── ui_widgetscrollsingle.py  WidgetScrollSingle.ui 的编译产物 Ui_Form
│   └── ui_widgetscrollmulti.py   WidgetScrollMulti.ui 的编译产物 Ui_Form
├── ui/                           Qt Designer 源文件 + 图片资源
│   ├── Main.ui  WidgetMulti.ui  WidgetLift.ui  WidgetScrollSingle.ui  WidgetScrollMulti.ui
│   ├── randname1.png / randname1.ico
│   └── randname-start_v3.6.png / randname-start_v3.7.png
├── doc/
│   ├── help_zh_CN.md  help_zh_TW.md  help_en_US.md    帮助文档（应用内渲染）
│   ├── gpl-3.0.md                                    许可证（应用内渲染）
│   ├── memory.json                                   运行记忆（Git 忽略）
│   └── log.log                                       持久日志（Git 忽略）
├── build_linux.sh / build_windows.bat                本地 Nuitka 构建
├── .github/workflows/BuildAndRelease.yml              CI 构建与发布
└── build/                                           构建产物（Git 忽略）
```

**已废弃的历史残留**（无对应源文件，仅存在于 `lib/__pycache__/`）：
`Single.py`（旧单抽模式）与 `ui_widgetsingle.py`（旧单抽界面）。
当前「抽取人数设为 1 即为单抽」，故单抽模式已被合并进 Multi。

空目录 `theme/`、`var/`、`dev-test-0/` 不被任何代码引用，属于历史遗留或本地实验目录。

### 2.3 程序运行总流程

```
程序启动
  │
  ├─[1] 打印 ASCII 版权横幅（stdout）
  ├─[2] QApplication(sys.argv)            ← 必须先建 QApplication 才能取屏幕信息
  ├─[3] 引导配置：config.toml → .config.default.toml → {}
  ├─[4] 应用图标：assets.icon → QIcon → QApplication.setWindowIcon
  ├─[5] 读取主屏幕可用区域 (width, height)
  ├─[6] 启动画面：[splash] enabled/mode/duration_ms/size_mode
  │        └─ 居中显示 → app.processEvents() → 启动计时器
  ├─[7] 可恢复文件体检（缺失仅警告）
  ├─[8] 装载 lib/* 组件（失败 → 弹窗并 return 1）
  ├─[9] StateManager.configure_paths(config)   ← 应用 paths.memory_file / paths.log_file
  ├─[10] StateManager.configure_logging(level)  ← 应用 logging.level
  ├─[11] ThemeManager.discover_themes()
  ├─[12] LanguageManager.load_languages()
  ├─[13] 汇总并去重启动警告 → StateManager.log("WARN","startup_fallback", ...)
  ├─[14] 解析启动主题 / 语言 / 名单
  ├─[15] 创建 MainWindow（含 _build_ui → _apply_config_window → _retranslate）
  ├─[16] ThemeManager.apply_theme(app, ...)
  ├─[17] window.show()
  ├─[18] 关闭启动画面（mode=0 立即；mode=1 至少 duration_ms）
  └─[19] app.exec() → 事件循环 → 返回退出码
```

---

## 3. 数据模型与文件格式

### 3.1 `config/config.toml`（主配置）全字段

```
[app]
default_mode     : 字符串，启动后打开的页面。"Multi" | "Lift" | "ScrollMulti" | 其他（视为 ScrollSingle）
theme            : 字符串，启动主题「后备项」（仅 theme.toml 未指定/无效 default 时使用）
language         : 字符串，启动语言「后备项」（仅 language.toml 未指定/无效 preferred 时使用）
roster           : 字符串，启动名单键名，必须存在于 name.toml 的 [rosters.*]
repository_url   : 字符串，「关于 > 项目仓库」打开的网址，默认
                   "https://www.github.com/HQZ-OhNone/randname"

[assets]
icon             : 路径，Qt 应用与窗口图标，默认 "ui/randname1.png"
splash_image     : 路径，启动画面图片，默认 "ui/randname-start_v3.6.png"

[paths]          ← 以下支持相对路径（相对 ROOT_DIR）或绝对路径
license_file     : 路径，默认 "doc/gpl-3.0.md"      （关于 > 许可证）
help_directory   : 路径，默认 "doc"                 （关于 > 帮助，拼接 help_<locale>.md）
log_file         : 路径，默认 "doc/log.log"         （持久日志，可写）
memory_file      : 路径，默认 "doc/memory.json"     （运行记忆，可写）

[splash]
enabled          : 布尔，仅当严格等于 true 才启用；默认 true
mode             : 0 = 主窗口就绪即关闭；1 或 "fixed" = 至少显示 duration_ms
duration_ms      : 整数毫秒，必须是非负整数；非整数回退 1000
size_mode        : "screen_ratio" | "fixed"
width / height   : fixed 模式的逻辑像素尺寸（screen_ratio 时作备用）

[window]
size_mode        : "screen_ratio" | "fixed"
width / height   : fixed 模式的逻辑像素尺寸
aspect_ratio     : 比例模式的 宽/高，必须 > 0 的数值；非数值或 ≤0 回退 1.5（3:2）

[scroll_single]
rate             : 正整数，每秒轮播刷新次数；默认 30 → 定时器间隔 1000 // 30 = 33 ms

[scroll_multi]
rate             : 正整数，滚动多抽每秒轮播刷新次数；默认 30（回退逻辑同 scroll_single）

[logging]
level            : "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL"（"WARN" 归一为 "WARNING"）
```

### 3.2 `config/name.toml`（名单目录）

```
[rosters.<键名>.name]      多语言显示名，供「名单」菜单使用
en_US = "Example Class"
zh_CN = "示例班级"
zh_TW = "示例班級"

[rosters.<键名>.names]     人员表：键 = 稳定唯一人员编号，值 = 界面显示姓名
"0" = "周〇"
"1" = "张三"
...
"8" = "郑睿"
```

**有效性判定**：一个 roster 有效 ⇔ 它是字典 且 其 `names` 是非空字典。
无效条目被静默剔除。

### 3.3 `config/theme.toml`（主题目录）

```
default = "randname-dark"                 ← 启动默认主题；与 config.toml 的 app.theme 冲突时此项优先

[themes.<键名>]
color_format = "HexA"                     ← HexA(#RRGGBBAA) | Hex(#RRGGBB) | RGBA(r,g,b,a) | RGB(r,g,b)

[themes.<键名>.name]                      多语言显示名（菜单用）
en_US / zh_CN / zh_TW

[themes.<键名>.colors]                    11 个语义色（可少写，走代码默认值）
background            页面底色（强制不透明，alpha 强制为 255）
foreground            正文文字色
panel                 状态栏底色
display_background    结果框底色
display_foreground    结果框文字色
display_border        结果框边框色
button                按钮底色
button_foreground     按钮文字色（缺省回落到 foreground）
button_hover          按钮悬停底色
button_pressed        按钮按下底色
border                边框色
accent                菜单项选中强调色
```

**内置的 13 套主题键名**：
`amber-dark/light`、`blue-dark/light`、`dark-dark/light`（经典）、`green-dark/light`、
`light-dark/light`（中性）、`purple-dark/light`、`randname-dark/light`。

**有效性判定**：一个主题有效 ⇔ 它是字典 且 `colors` 是字典 且 `name` 是字典。

### 3.4 `config/language.toml`（语言包）

```
preferred = "zh_CN"                       ← 启动首选语言；与 config.toml 的 app.language 冲突时此项优先

[languages.<locale>]
display_name = "简体中文"                 ← 「语言」菜单显示名

[languages.<locale>.text]                ← 文案表；键名固定，仅改译文
"menu.file" = "文件"
...（完整键表见第 12 章）
```

**合并规则**：每个语言包的 `text` 与内建 `ENGLISH` 做**浅合并**（`{**ENGLISH, **pack.text}`），
因此语言包可以只写需要覆盖的键。
**有效性判定**：一个语言包有效 ⇔ 它是字典 且其 `text` 是字典；无效包记录 warning 并跳过。
`en_US` 恒存在（内建）。

### 3.5 内建兜底数据

#### 3.5.1 `StateManager.BUILTIN_CONFIG`（config.toml 与备份都不可用时）

```
app       = { default_mode: "Multi", theme: "randname-dark", roster: "class_1" }
splash    = { enabled: true, mode: 0, duration_ms: 1000,
              size_mode: "screen_ratio", width: 480, height: 270 }
window    = { size_mode: "screen_ratio", width: 800, height: 600, aspect_ratio: 1.5 }
scroll_single = { rate: 30 }
scroll_multi  = { rate: 30 }
logging   = { level: "INFO" }
```

> 注意：内建配置**不含** `language`、`repository_url`、`assets`、`paths`，
> 故回退到内建时这些项均由各函数的 `default` 参数兜底。

#### 3.5.2 `ThemeManager.BUILTIN_THEME`（theme.toml 不可用时）

```
键名 = "randname-dark"，color_format = "HexA"，name 为三语言
background #211823FF  foreground #F9EDF7FF  panel #302333FF
display_background #38283BEE  display_foreground #FFF6FCFF  display_border #C47DB5FF
button #493149FF  button_hover #633F60FF  button_pressed #7A4B75FF
border #B86AA8FF  accent #D44EADFF
```

#### 3.5.3 `LanguageManager.ENGLISH`（语言文件不可用时的唯一可用语言）

包含第 12 章全部 61 个文案键的英文译文；任何语言包都以此为基底合并。

#### 3.5.4 内建名单（name.toml 与备份都不可用时）

```
{ "class_1": { "name": { "en_US": "Default roster" }, "names": { "0": "Student 1" } } }
```

并在 `importnames` 装载时，若最终 `names` 仍为空，再兜底为 `{ "0": "Student 1" }`，
同时记录 `logging.error("No usable roster was loaded")`。

### 3.6 运行记忆 `doc/memory.json`

```jsonc
{
  "loaded_config": { /* 最近一次抽取时快照的 importnames.loaded_config 原样内容 */ },
  "last_results": {
    "Multi":       { "result": { /* Multi 结果结构 */ }, "time": "2026-10-11 13:18:44" },
    "Lift":        null,
    "ScrollSingle":{ "result": "吴九", "meta": { "time": "...", "mode": "ScrollSingle" } },
    "ScrollMulti": { "result": { /* ScrollMulti 结果结构，同构 Multi */ }, "meta": { "mode": "ScrollMulti" } }
  }
}
```

默认结构（文件不存在时自动写入 `doc/memory.json`）：

```
{ "loaded_config": null,
  "last_results": { "Multi": null, "Lift": null, "ScrollSingle": null, "ScrollMulti": null } }
```

写入格式：`json.dumps(state, ensure_ascii=False, indent=2)`，编码 UTF-8。

### 3.7 持久日志 `doc/log.log` 行格式

```
time=2026-10-11 13:18:44 level=INFO action=Multi result=('mode': 'Multi', ...)
```

字段顺序固定：`time` → `level` → `action` → `result`（可选） → `error`（可选）。
`_log_value()` 会把 `\r \n \t` 替换为空格，并把 `{ } [ ]` 替换成 `( )`，
保证**每条日志严格单行且不含 JSON 风格括号**。

### 3.8 四种模式的结果结构

#### Multi 结果

```jsonc
{
  "mode": "Multi",
  "quantity": { "total": <名单总数>, "selected": <本次抽取数> },
  "time": "2026-10-11-13:18:44",                 // 注意分隔符是 "-"
  "outdict": {                                   // 抽中者，下标重排为 "0","1",...
    "0": { "code": "<原人员编号>", "name": "<姓名>" },
    "1": { "code": "7",        "name": "吴九" }
  }
}
```

条件不满足时：`outdict = {}`。

#### Lift 结果

```jsonc
{
  "mode": "Lift",
  "quantity": {
    "total":   <原始名单总数>,
    "wasted":  total - len(剩余字典),            // 已抽走的人数
    "selected": <本次抽取数>,
    "Lift":    len(剩余字典) - 本次抽取数         // 本次之后还剩多少人（命名易误解，见第 16 章）
  },
  "alllist":  <原始名单字典，原样引用>,
  "time": "2026-03-15-12:30:23",
  "outdict": { "0": { "<原人员编号>": "<姓名>" }, ... },   // 注意：单键包裹形式，与 Multi 不同
  "Liftdict": { "<未抽中人员编号>": "<姓名>", ... }        // 本次之后的剩余名单
}
```

条件不满足时：`outdict = {}`，`Liftdict` 原样返回。

#### ScrollSingle 结果

```jsonc
// 回调签名：on_result(result: str, meta: dict)
meta   = { "time": "2026-10-11 13:20:05", "mode": "ScrollSingle" }   // 注意分隔符是 " " 和 ":"
result = <停止瞬间 label 上的文本>
```

#### ScrollMulti 结果

```jsonc
// 回调签名：on_result(result: dict, meta: dict)
// 结构对齐 Multi，便于 _format_output_result 复用。
{
  "mode": "ScrollMulti",
  "time": "2026-10-11-13:18:44",                 // 与 Multi 相同：分隔符 "-"
  "quantity": { "total": <名单总数>, "selected": <本次抽取数 n> },
  "outdict": {                                   // 逐个停下的转盘，按停止顺序 "0","1",...
    "0": { "code": "<原人员编号>", "name": "<姓名>" },
    "1": { "code": "7",        "name": "吴九" }
  }
}
meta = { "time": "2026-10-11-13:20:05", "mode": "ScrollMulti" }
```

同一轮内已停下的编号会从本轮池中移除，因此 `outdict` 各 `code` 互不重复。

---

## 4. 启动阶段（startup）

### 4.1 版权横幅

```
打印到 stdout（end="\n\n"）：
  randname Copyright(C) 2026 HQZ-OhNone
  This program comes with ABSOLUTELY NO WARRANTY.
  ...
  <ASCII art>  randname
  ---HQZ-OhNone <ohnone_hqz@outlook.com>
```

### 4.2 日志初始化

```
logging.basicConfig(level=INFO, format="%(asctime)s [%(levelname)s] %(message)s")
```

此阶段日志只输出到控制台；`StateManager.configure_logging()` 执行后才额外挂载
`_SessionLogHandler`（同时写会话列表与 `doc/log.log`）。

### 4.3 `_configured_path(config, section, key, default) → Path`

```
函数 配置路径解析(config, 节名, 键名, 默认串):
    IF config 不是字典:            段 = {}
    ELSE:                          段 = config[节名]（不存在则 {}）
    IF 段 不是字典:                 值 = 默认串
    ELSE:
        值 = 段[键名]（不存在则 默认串）

    IF 值 是非空字符串:  选中 = Path(值)
    ELSE:                选中 = Path(默认串)

    IF 选中 是绝对路径:  返回 选中
    ELSE:                返回 ROOT_DIR / 选中          ← 相对路径以项目根为基准
```

调用点：`assets.icon`、`assets.splash_image`、`paths.help_directory`、`paths.license_file`。

### 4.4 `_bootstrap_config() → (config, warnings)`

```
函数 引导配置():
    警告列表 = []
    FOR 路径 IN [ROOT_DIR/config/config.toml, ROOT_DIR/.config.default.toml]:
        TRY:
            配置 = TOML解析(路径)
            IF 路径.文件名 == ".config.default.toml":
                追加(警告列表, "config/config.toml")      ← 标记「用了备份」
            返回 (配置, 警告列表)
        EXCEPT 文件不存在:
            追加(警告列表, 路径.相对ROOT_DIR)              ← 如 "config/config.toml"
        EXCEPT (OSError, TOMLDecodeError) AS e:
            追加(警告列表, "config/config.toml: " + str(e))
    返回 ({}, 警告列表)
```

| 场景 | 返回 config | warnings |
| --- | --- | --- |
| `config.toml` 正常 | 其内容 | `[]` |
| `config.toml` 缺失，备份正常 | 备份内容 | `["config/config.toml"]` |
| `config.toml` 损坏，备份正常 | 备份内容 | `["config/config.toml: <错误>"]` |
| 两者都不可用 | `{}` | `["config/config.toml", ".config.default.toml"]` |

> 本函数是**启动早期**的粗粒度引导（此时 `lib` 尚未导入），
> 正式的「程序配置」由 `StateManager.load_config()` 再次读取（见 5.4）。

### 4.5 `_configured_size(section, screen_width, screen_height, *, splash=False) → (w, h)`

```
函数 计算尺寸(段, 屏宽, 屏高, 是否启动画面=false):
    IF 段.size_mode == "fixed":
        宽 = 段.width
        高 = 段.height
        IF 宽 是 int 且 宽 > 0 且 高 是 int 且 高 > 0:
            返回 (宽, 高)                            ← fixed 直用，不校验屏幕大小

    IF 是否启动画面:
        返回 (max(1, int(屏宽 * 0.25)), max(1, int(屏高 * 0.25)))   ← 启动画面固定 1/4 屏

    比例 = 段.aspect_ratio（缺省 1.5）
    IF 比例 不是 (int|float) OR 比例 是 bool OR 比例 <= 0:
        比例 = 1.5
    宽 = min(屏宽 * 0.75, 屏高 * 0.75 * 比例)          ← 主窗口宽高均不超过 3/4 屏
    返回 (max(1, int(宽)), max(1, int(宽 / 比例)))
```

| 配置 | 启动画面尺寸 | 主窗口尺寸 |
| --- | --- | --- |
| `size_mode="fixed"`, 480×270 | 480×270 | 800×600 |
| `size_mode="screen_ratio"`, aspect=1.5 | 屏宽×0.25 × 屏高×0.25 | 屏 1920×1080 → `min(1440, 1215)=1215`，输出 1215×810<br>屏 1280×800 → `min(960, 900)=900`，输出 900×600 |

### 4.6 `_startup_file_check(config) → (recoverable, required)`

```
函数 启动文件体检(配置):
    帮助目录 = _configured_path(配置, "paths", "help_directory", "doc")

    可恢复清单 = [
        ROOT/config/config.toml,
        ROOT/.config.default.toml,
        ROOT/config/name.toml,
        ROOT/.name.default.toml,
        ROOT/config/language.toml,
        ROOT/config/theme.toml,
        _configured_path(配置, "assets", "icon",            "ui/randname1.png"),
        _configured_path(配置, "assets", "splash_image",    "ui/randname-start_v3.6.png"),
        _configured_path(配置, "paths",  "license_file",    "doc/gpl-3.0.md"),
        帮助目录 / "help_en_US.md"
    ]

    recoverable = [相对路径(p) FOR p IN 可恢复清单 IF NOT p 是文件]
    RETURN (recoverable, [])          ← 当前实现中 required 恒为空列表
```

> `required` 恒为空意味着 `main()` 中的「Startup check failed」弹窗分支
> 目前是**不可达的防御性代码**（见第 16 章）。

### 4.7 `main()` 完整伪代码

```
函数 main() → 退出码:
    声明全局 lift_module, multi_module, ScrollSingle,
               StateManager, ThemeManager, importnames, LanguageManager,
               ui_main, ui_widgetlift, ui_widgetmulti, ui_widgetscrollsingle

    # ── 阶段 A：Qt 应用与引导配置 ─────────────────────────────
    app = QApplication(sys.argv)

    (引导配置, 引导警告) = _bootstrap_config()

    # ── 阶段 B：图标 ────────────────────────────────────────
    图标路径 = _configured_path(引导配置, "assets", "icon", "ui/randname1.png")
    应用图标 = QIcon(图标路径)
    IF 应用图标 不是 null:
        app.setWindowIcon(应用图标)
    ELSE:
        引导警告 += "Invalid application icon: " + 图标路径

    # ── 阶段 C：屏幕几何 ─────────────────────────────────────
    屏幕 = app.primaryScreen()
    几何 = 屏幕.availableGeometry() IF 屏幕 存在 ELSE None
    屏宽 = 几何.width()  IF 几何 存在 ELSE 1280
    屏高 = 几何.height() IF 几何 存在 ELSE 800

    # ── 阶段 D：启动画面参数 ─────────────────────────────────
    启动配置 = 引导配置["splash"]（不存在或非字典 → {}）
    启动启用 = (启动配置.enabled 缺省 true) 严格等于 True       ← 仅 true 才启用
    启动模式 = 启动配置.mode 缺省 0                            ← 0 / 1 或 "fixed"
    启动时长 = 启动配置.duration_ms 缺省 1000
    IF 启动时长 不是 int OR 是 bool:  启动时长 = 1000
    启动时长 = max(0, 启动时长)

    启动画面 = None
    计时器   = QElapsedTimer()
    画面路径 = _configured_path(引导配置, "assets", "splash_image",
                                "ui/randname-start_v3.6.png")
    画面     = QPixmap(画面路径)

    IF 启动启用 AND 画面 不是 null:
        (宽, 高) = _configured_size(启动配置, 屏宽, 屏高, splash=true)
        画面 = 画面.scaled(宽, 高, KeepAspectRatio, SmoothTransformation)
        启动画面 = QSplashScreen(画面)
        启动画面.show()
        IF 几何 存在:
            启动画面.move(几何.中心.x - 宽//2, 几何.中心.y - 高//2)
        app.processEvents()
        计时器.start()                                ← 记录已耗时
    ELSE IF 启动启用:
        引导警告 += "Missing or invalid splash image: " + 画面路径

    # ── 阶段 E：可恢复文件体检 ───────────────────────────────
    (可恢复缺失, 必要缺失) = _startup_file_check(引导配置)
    引导警告 += 可恢复缺失
    IF 必要缺失 非空:                                 ← 当前恒不进入
        关闭启动画面
        QMessageBox.critical(None, "Startup check failed",
                             "Required application files are missing:\n" + 换行拼接)
        RETURN 1

    app.processEvents()

    # ── 阶段 F：装载内部组件 ─────────────────────────────────
    TRY:
        from lib import Lift, Multi, importnames, StateManager,
                      ScrollSingle, ThemeManager, LanguageManager,
                      ui_main, ui_widgetmulti, ui_widgetlift, ui_widgetscrollsingle
    EXCEPT Exception AS e:
        关闭启动画面
        QMessageBox.critical(None, "Startup failed",
            "A required application component could not be loaded:\n"
            + 类型名(e) + ": " + str(e))
        RETURN 1

    # ── 阶段 G：应用配置（路径 + 日志等级） ───────────────────
    配置 = importnames.loaded_config
    StateManager.configure_paths(配置)                  ← paths.memory_file / paths.log_file
    日志配置 = 配置["logging"]（非字典 → {}）
    StateManager.configure_logging(日志配置.level 缺省 "INFO")

    # ── 阶段 H：主题 / 语言 ─────────────────────────────────
    主题集 = ThemeManager.discover_themes()
    (语言集, 首选语言, 语言警告) = LanguageManager.load_languages()

    应用配置 = 配置["app"]（非字典 → {}）
    请求主题 = 应用配置.theme 缺省 ""
    选定主题 = ThemeManager.resolve_startup_theme(主题集, 请求主题)
    选定名单 = importnames.active_roster

    # ── 阶段 I：汇总启动警告 ─────────────────────────────────
    启动警告 = 去重保序(引导警告 + StateManager.CONFIG_WARNINGS)
    IF importnames.ROSTER_FALLBACK_USED:  启动警告 += "config/name.toml"
    IF 语言警告 非空:                      启动警告 += 语言警告
    IF ThemeManager.THEME_LOAD_WARNING:   启动警告 += ThemeManager.THEME_LOAD_WARNING
    IF ROOT/config/theme.toml 不是文件:   启动警告 += "config/theme.toml"
    启动警告 = 去重保序(启动警告)
    FOR w IN 启动警告:
        StateManager.log("WARN", "startup_fallback", error=w)

    # ── 阶段 J：构建窗口 ─────────────────────────────────────
    选定语言 = LanguageManager.resolve_startup_language(
                  语言集, 首选语言, 应用配置.language 缺省 "")

    窗口 = MainWindow(主题集, 选定主题, 语言集, 选定语言,
                      importnames.rosters, 选定名单, 启动警告)

    ThemeManager.apply_theme(app, 选定主题, 主题集)
    窗口.show()

    # ── 阶段 K：关闭启动画面 ─────────────────────────────────
    IF 启动画面 存在:
        IF 启动模式 IN (1, "fixed"):
            剩余 = max(0, 启动时长 - 计时器.elapsed())
            IF 剩余 > 0:
                QTimer.singleShot(剩余, lambda: 启动画面.finish(窗口))
            ELSE:
                启动画面.finish(窗口)                   ← 已超时，立即关闭
        ELSE:
            启动画面.finish(窗口)                       ← mode=0：就绪即关

    RETURN app.exec()
```

**入口**：`IF __name__ == "__main__": sys.exit(main())`

---

## 5. 状态管理层（StateManager）

文件：`lib/StateManager.py`。职责：**只读配置读取 + 名单读取 + 记忆读写 + 双通道日志**。

### 5.1 模块级全局状态

```
ROOT              = lib/ 的父目录
DOC               = ROOT/doc ; 导入时立即 DOC.mkdir(exist_ok=True)   ← 目录不存在则创建
MEMORY_PATH       = DOC/memory.json
LOG_PATH          = DOC/log.log
CONFIG_DIR        = ROOT/config
CONFIG_PATH       = CONFIG_DIR/config.toml
DEFAULT_CONFIG_PATH = ROOT/.config.default.toml
NAME_PATH         = CONFIG_DIR/name.toml
DEFAULT_NAME_PATH = ROOT/.name.default.toml

CONFIG_SOURCE        = ""        ← 最近一次 load_config 实际读取的文件名
CONFIG_FALLBACK_USED = False     ← 是否使用了备份
CONFIG_WARNINGS      : list[str] ← 本次 load_config + load_rosters 产生的警告

LOG_LEVELS      = { DEBUG, INFO, WARNING, WARN→WARNING, ERROR, CRITICAL } → logging 常量
LOG_LEVEL_CHOICES = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")   ← 菜单展示项
CURRENT_LOG_LEVEL = "INFO"
SESSION_LOG_RECORDS : list[str] ← 本进程收集到的全部日志行
BUILTIN_CONFIG  = { ... }       ← 见 3.5.1
```

### 5.2 `_now_iso() → str`

```
返回 datetime.now().isoformat(sep=" ", timespec="seconds")
     例："2026-10-11 13:18:44"        ← 空格分隔，秒精度
```

### 5.3 `configure_paths(config)`

```
函数 配置路径(配置):
    路径段 = 配置["paths"]（非字典 → {}）
    FOR (键, 默认) IN [("memory_file", DOC/memory.json), ("log_file", DOC/log.log)]:
        值 = 路径段[键]
        选中 = Path(值) IF 值 是非空字符串 ELSE 默认
        IF NOT 选中.is_absolute():  选中 = ROOT / 选中        ← 相对路径以项目根为基准
        选中 = 选中.resolve()                                 ← 展开 .. 与符号链接
        选中.parent.mkdir(parents=True, exist_ok=True)        ← 父目录不存在则创建
        IF 键 == "memory_file":  MEMORY_PATH = 选中
        ELSE:                    LOG_PATH    = 选中
```

调用时机：`main()` 阶段 G，在 `configure_logging` **之前**，
确保后续日志写入使用配置后的路径。

### 5.4 `load_config() → dict`

```
函数 读取主配置():
    CONFIG_WARNINGS = []
    FOR (路径, 日志等级) IN [(CONFIG_PATH, "INFO"), (DEFAULT_CONFIG_PATH, "WARN")]:
        TRY:
            配置 = TOML解析(路径)
            CONFIG_SOURCE = 路径.文件名
            CONFIG_FALLBACK_USED = (路径 == DEFAULT_CONFIG_PATH)
            IF CONFIG_FALLBACK_USED:
                CONFIG_WARNINGS += "config/config.toml -> .config.default.toml"
            log(日志等级, "load_config", result=路径.文件名)
            RETURN 配置
        EXCEPT 文件不存在:
            IF 路径 == CONFIG_PATH:
                CONFIG_WARNINGS += "missing config/config.toml"
            CONTINUE                     ← 备份缺失时不再追加警告
        EXCEPT (OSError, TOMLDecodeError) AS e:
            CONFIG_WARNINGS += "invalid " + 相对路径 + ": " + str(e)
            log("ERROR", "load_config", error=路径.文件名 + ": " + str(e))
    CONFIG_SOURCE = "built-in"
    CONFIG_FALLBACK_USED = True
    CONFIG_WARNINGS += "using built-in configuration"
    RETURN copy.deepcopy(BUILTIN_CONFIG)   ← 深拷贝：调用方可能改写嵌套表（见第 16 章）
```

### 5.5 `load_rosters() → (rosters, 回退标记)`

```
函数 读取名单() → (有效名单字典, 是否用了备份):
    FOR (路径, 是备份) IN [(NAME_PATH, False), (DEFAULT_NAME_PATH, True)]:
        TRY:
            数据 = TOML解析(路径)
            名单表 = 数据["rosters"]
            IF 名单表 不是字典 OR 名单表 为空:
                RAISE ValueError("missing [rosters.*.names] entries")
            有效 = { 键: 名单 FOR 键, 名单 IN 名单表.items()
                     IF 名单 是字典 AND 名单.names 是非空字典 }
            IF 有效 非空:
                IF 是备份:
                    CONFIG_WARNINGS += "config/name.toml -> .name.default.toml"
                RETURN (有效, 是备份)
        EXCEPT 文件不存在:
            CONFIG_WARNINGS += "missing " + 相对路径
        EXCEPT (OSError, TOMLDecodeError, ValueError) AS e:
            CONFIG_WARNINGS += "invalid " + 相对路径 + ": " + str(e)
            log("ERROR", "load_rosters", error=路径.文件名 + ": " + str(e))
    RETURN ({ "class_1": { "name": {"en_US":"Default roster"},
                           "names": {"0":"Student 1"} } }, True)
```

### 5.6 `configure_logging(level="INFO") → 归一后的等级`

```
函数 配置日志(等级="INFO") → 实际等级:
    选定 = 等级.upper() IF 等级 是字符串 ELSE "INFO"
    IF 选定 == "WARN":  选定 = "WARNING"
    IF 选定 NOT IN LOG_LEVELS:  选定 = "INFO"
    CURRENT_LOG_LEVEL = 选定

    根记录器 = logging.getLogger()
    根记录器.setLevel(LOG_LEVELS[选定])

    处理器 = 根记录器中第一个 isinstance(_SessionLogHandler) 的 handler（找不到则 None）
    IF 处理器 == None:
        处理器 = _SessionLogHandler()
        处理器.setFormatter("%(asctime)s [%(levelname)s] %(message)s")
        根记录器.addHandler(处理器)              ← 幂等：重复调用不会叠加处理器
    处理器.setLevel(LOG_LEVELS[选定])
    RETURN 选定
```

**效果**：
- `[logging]` 菜单勾选 `level == CURRENT_LOG_LEVEL`。
- 通过 `logging.info/warning/error` 写的记录也进入会话日志与 `doc/log.log`
  （格式为 `2026-10-11 13:18:43,845 [INFO] 执行多抽，数量=1`）。

### 5.7 `_SessionLogHandler.emit(record)`

```
类 _SessionLogHandler(logging.Handler):
    函数 emit(记录):
        行 = self.format(记录)
        SESSION_LOG_RECORDS.append(行)
        TRY:
            以 "a" 追加模式、UTF-8 打开 LOG_PATH，写入 行 + "\n"
        EXCEPT OSError:
            静默忽略                      ← 磁盘不可写不影响课堂抽取
```

### 5.8 `session_log_text() → str`

```
返回 "\n".join(SESSION_LOG_RECORDS)      ← 本进程启动以来的全部日志
```

### 5.9 `log(level, action, result=None, error=None)` —— 结构化单行日志

```
函数 记日志(等级, 动作, 结果=None, 错误=None):
    归一 = 等级.upper()
    IF 归一 == "WARN":  归一 = "WARNING"

    IF 数值(归一) < 数值(CURRENT_LOG_LEVEL):
        RETURN                                    ← 低于阈值直接丢弃

    TRY:
        字段 = ["time=" + _now_iso(), "level=" + 归一, "action=" + 动作]
        IF 结果 != None:  字段 += "result=" + _log_value(结果)
        IF 错误 != None:  字段 += "error="  + _log_value(错误)
        行 = " ".join(字段)
        SESSION_LOG_RECORDS.append(行)
        追加写入 LOG_PATH：行 + "\n"
    EXCEPT Exception:
        静默忽略            ← 「日志绝不能阻止课堂抽取完成」
```

**`_log_value(value)`**：
```
文本 = str(value)
文本 = 文本.replace("\r"," ").replace("\n"," ").replace("\t"," ")
返回 文本.replace("{","(").replace("}",")").replace("[","(").replace("]"," ")
```

### 5.10 记忆读写

```
函数 _default_memory() → { "loaded_config": null,
                           "last_results": {"Multi":null,"Lift":null,"ScrollSingle":null,"ScrollMulti":null} }

函数 load_memory() → dict:
    IF MEMORY_PATH 不存在:
        记忆 = _default_memory()
        写入 MEMORY_PATH（UTF-8, indent=2, ensure_ascii=False）
        RETURN 记忆
    TRY:
        记忆 = json.loads(读 MEMORY_PATH)
        RETURN 记忆 IF 是字典 ELSE _default_memory()
    EXCEPT (OSError, JSONDecodeError):
        RETURN _default_memory()                 ← 损坏记忆不阻断启动

函数 save_memory(状态):
    写入 MEMORY_PATH = json.dumps(状态, ensure_ascii=False, indent=2)

函数 export_memory(路径=None) → Path:
    目标 = 路径 OR MEMORY_PATH
    源文 = 读 MEMORY_PATH IF 存在 ELSE "{}"       ← 记忆不存在时导出空对象
    写入 目标 = 源文                              ← 逐字节复制，不做内容改写
    log("INFO", "export_memory", result=str(目标))
    RETURN 目标

函数 import_memory(路径, 应用回调=None) → dict:
    内容 = json.loads(读 路径)
    IF 内容 不是字典:  RAISE ValueError("Memory file must contain an object")
    写入 MEMORY_PATH = json.dumps(内容, ensure_ascii=False, indent=2)   ← 只写记忆文件
    IF 应用回调 != None:  应用回调(内容)          ← 由 MainWindow._apply_memory_import 处理
    log("INFO", "import_memory", result=str(路径))
    RETURN 内容
```

> **不变式**：`import_memory` / `export_memory` **永不写入 `config/` 下任何文件**。

---

## 6. 名单管理层（importnames）

文件：`lib/importnames.py`。设计要点：**模块导入时一次性加载**，之后只维护内存中的字典。

### 6.1 导入时执行（模块顶层代码）

```
loaded_config = StateManager.load_config()
(rosters, ROSTER_FALLBACK_USED) = StateManager.load_rosters()

app配置 = loaded_config["app"]（非字典 → {}）
配置名单 = app配置.roster 缺省 "class_1"
IF 配置名单 不是字符串 OR 配置名单 NOT IN rosters:
    配置名单 = next(iter(rosters), "class_1")      ← 取字典第一项（TOML 保序 → 文件中首个）

active_roster = 配置名单
names = rosters[active_roster].names
IF names 为空:
    names = {"0": "Student 1"}
    logging.error("No usable roster was loaded")
```

**导出符号**：`names`、`loaded_config`、`rosters`、`active_roster`、
`ROSTER_FALLBACK_USED`、`select_roster`、`reload_data`。

### 6.2 `select_roster(name) → names`

```
函数 选择名单(键名) → 名单字典:
    名单 = rosters[键名]
    IF 名单 不是字典 OR 名单.names 不是字典:
        RETURN names                       ← 无效名单：静默返回当前名单，不改变状态
    active_roster = 键名
    names = 名单.names
    RETURN names
```

### 6.3 `reload_data()`

```
函数 重载数据():
    loaded_config        = StateManager.load_config()
    (rosters, ROSTER_FALLBACK_USED) = StateManager.load_rosters()
    app配置 = loaded_config["app"]（非字典 → {}）
    配置名单 = app配置.roster 缺省 "class_1"
    active_roster = 配置名单 IF 配置名单 IN rosters ELSE next(iter(rosters), "class_1")
    names = rosters[active_roster].names 缺省 {"0": "Student 1"}
```

> 与模块顶层唯一的差别：`reload_data` 的 `names` 使用 `.get("names", 默认)`，
> 若该键存在但为空字典则**不再**二次兜底（顶层会兜底）。

---

## 7. 主题管理层（ThemeManager）

文件：`lib/ThemeManager.py`。

### 7.1 模块级状态

```
ROOT = lib/ 的父目录
THEME_PATH = ROOT/config/theme.toml
THEME_LOAD_WARNING : str|None = None    ← 最近一次 discover_themes 的失败原因
DEFAULT_THEME = "randname-dark"         ← 解析出的默认主题键
CONFIGURED_DEFAULT : str|None = None    ← theme.toml 中显式声明且有效的 default
BUILTIN_THEME = { ... }                 ← 见 3.5.2
```

### 7.2 `discover_themes(path=THEME_PATH) → {键名: 主题}`

```
函数 发现主题(路径=THEME_PATH):
    THEME_LOAD_WARNING = None
    CONFIGURED_DEFAULT = None
    TRY:
        数据 = TOML解析(路径)
        主题表 = 数据["themes"]
        IF 主题表 不是字典 OR 主题表 为空:
            RAISE ValueError("missing [themes.*] entries")

        已载入 = { 名: 主题 FOR 名, 主题 IN 主题表.items()
                   IF 主题 是字典 AND 主题.colors 是字典 AND 主题.name 是字典 }

        IF 已载入 非空:
            请求默认 = 数据.default 缺省 "randname-dark"
            IF 请求默认 是字符串 AND 请求默认 IN 已载入:
                CONFIGURED_DEFAULT = 请求默认
                DEFAULT_THEME       = 请求默认
            ELSE:
                DEFAULT_THEME = ("randname-dark" IF "randname-dark" IN 已载入
                                 ELSE next(iter(已载入)))
            IF 请求默认 != DEFAULT_THEME:
                LOGGER.warning("Unknown default theme %r; using %s", 请求默认, DEFAULT_THEME)
            RETURN 已载入

        RAISE ValueError("no valid theme entries")

    EXCEPT (OSError, TOMLDecodeError, ValueError) AS e:
        THEME_LOAD_WARNING = str(路径) + ": " + str(e)
        DEFAULT_THEME       = "randname-dark"
        CONFIGURED_DEFAULT  = None
        LOGGER.warning("Using built-in theme: %s", e)
        RETURN { "randname-dark": BUILTIN_THEME }
```

### 7.3 `available_themes() → [键名]`

```
返回 sorted(discover_themes())      ← 每次调用都会重新读盘
```

### 7.4 `resolve_startup_theme(themes, configured="") → 键名`

```
函数 解析启动主题(主题集, 配置值=""):
    IF 主题集 为空:  RETURN ""
    FOR 候选 IN [CONFIGURED_DEFAULT, 配置值]:        ← 独立配置档优先
        IF 候选 是字符串 AND 候选 IN 主题集:  RETURN 候选
    IF DEFAULT_THEME IN 主题集:  RETURN DEFAULT_THEME
    RETURN next(iter(主题集))
```

**优先级链**：`theme.toml 的 default` → `config.toml 的 app.theme` → `DEFAULT_THEME` → 首个主题。

### 7.5 `load_theme(name) → dict`

```
RETURN discover_themes().get(name, BUILTIN_THEME)
```

### 7.6 `_color(value, color_format, allow_alpha=True) → "rgba(r, g, b, a)"`

```
函数 颜色转换(值, 格式, 允许透明度=True):
    IF 格式 IN {"RGB", "RGBA"}:
        通道 = [int(项.strip()) FOR 项 IN 值.split(",")]
        IF 格式 == "RGB":  通道.append(255)          ← RGB 自动补 alpha
        IF 长度(通道) != 4:  RAISE ValueError("Invalid <格式> color: " + 值)
        IF NOT 允许透明度:  通道[3] = 255
        RETURN "rgba(R, G, B, A/255 保留3位小数)"

    IF 格式 IN {"Hex", "HexA"}:
        IF 格式 == "HexA" AND 值 以 "#" 开头 AND len(值) == 9:
            color = QColor(int(值[1:3],16), int(值[3:5],16), int(值[5:7],16), int(值[7:9],16))
        ELSE:
            color = QColor(值)                        ← 支持 #RRGGBB 与 Qt 命名色
        IF NOT color.isValid():  RAISE ValueError("Invalid <格式> color: " + 值)
        IF NOT 允许透明度:  color.setAlpha(255)
        RETURN "rgba(R, G, B, A/255 保留3位小数)"

    RAISE ValueError("Unsupported color format: " + 格式)
```

> `allow_alpha=False` 仅用于 `background`（页面底色强制不透明）。

### 7.7 `_stylesheet(theme) → QSS 字符串`

```
函数 生成样式表(主题):
    颜色 = 主题.colors 缺省 {}
    格式 = 主题.color_format 缺省 "Hex"
    # 以下均为「键缺失时的代码默认值」
    前景 = _color(颜色.foreground       缺省 "#f5f5f5", 格式)
    背景 = _color(颜色.background       缺省 "#202124", 格式, allow_alpha=False)
    面板 = _color(颜色.panel            缺省 "#292a2d", 格式)
    按钮 = _color(颜色.button           缺省 "#303134", 格式)
    按钮前景 = _color(颜色.button_foreground 缺省 颜色.foreground 缺省 "#f5f5f5", 格式)
    按钮悬停 = _color(颜色.button_hover     缺省 "#45474d", 格式)
    按钮按下 = _color(颜色.button_pressed  缺省 "#5f6368", 格式)
    边框 = _color(颜色.border           缺省 "#5f6368", 格式)
    强调 = _color(颜色.accent           缺省 "#3f51b5", 格式)
    结果底 = _color(颜色.display_background 缺省 "#292a2d", 格式)
    结果字 = _color(颜色.display_foreground 缺省 "#f5f5f5", 格式)
    结果框 = _color(颜色.display_border     缺省 "#5f6368", 格式)

    RETURN """
    QMainWindow, QWidget, QStackedWidget, QFrame {
        background-color: <背景>;
        color:           <前景>;
    }
    QLabel, QStatusBar, QMenuBar, QMenu { color: <前景>; }

    QLabel#label_SingleOutput, QLabel#label_MultiOutput,
    QLabel#label_LiftOutput, QLabel#label_ScrollSingleOutput {
        background-color: <结果底>;
        color:           <结果字>;
        border: 1px solid <结果框>;
    }

    QPushButton {
        background-color: <按钮>; color: <按钮前景>;
        border: 1px solid <边框>; border-radius: 4px; padding: 6px 12px;
    }
    QPushButton:hover  { background-color: <按钮悬停>; }
    QPushButton:pressed{ background-color: <按钮按下>; }

    QMenuBar::item:selected, QMenu::item:selected { background-color: <强调>; }
    QStatusBar { background-color: <面板>; }
    """
```

> `QLabel#label_SingleOutput` 为历史遗留选择器（单抽模式已废弃，当前无此对象）。

### 7.8 `apply_theme(app, name, themes=None) → 实际主题键`

```
函数 应用主题(app, 名称, 主题集=None):
    已载入 = 主题集 IF 主题集 != None ELSE discover_themes()
    IF 已载入 为空:  RETURN ""
    选定 = (名称 IF 名称 IN 已载入
            ELSE DEFAULT_THEME IF DEFAULT_THEME IN 已载入
            ELSE next(iter(已载入)))
    app.setStyleSheet(_stylesheet(已载入[选定]))
    RETURN 选定
```

---

## 8. 语言管理层（LanguageManager）

文件：`lib/LanguageManager.py`。

### 8.1 `load_languages(path=LANGUAGE_PATH) → (语言集, preferred, warning)`

```
函数 加载语言(路径=LANGUAGE_PATH):
    语言集 = { "en_US": { "display_name": "English (United States)", "text": ENGLISH } }
    preferred = ""
    warning   = None
    TRY:
        数据 = TOML解析(路径)
        语言包表 = 数据.languages 缺省 {}
        IF 语言包表 不是字典:
            RAISE ValueError("languages must be a table")

        FOR 代码, 包 IN 语言包表.items():
            IF 包 不是字典 OR 包.text 不是字典:
                LOGGER.warning("Ignoring invalid language pack %s", 代码)
                CONTINUE
            语言集[代码] = {
                "display_name": str(包.display_name 缺省 代码),
                "text": { **ENGLISH, **包.text }          ← 以英文为基底合并
            }

        配置首选 = 数据.preferred 缺省 ""
        IF 配置首选 是字符串:  preferred = 配置首选

    EXCEPT (OSError, TOMLDecodeError, ValueError) AS e:
        warning = 路径.文件名 + ": " + str(e)
        LOGGER.warning("Using built-in English language: %s", warning)

    RETURN (语言集, preferred, warning)
```

> `language.toml` 缺失时返回**仅含 `en_US`** 的语言集，`preferred = ""`，`warning` 非空。

### 8.2 `system_language(languages) → 代码`

```
函数 系统语言(语言集):
    区域名 = QLocale.system().name().replace("-", "_")     ← "zh-CN" → "zh_CN"
    IF 区域名 IN 语言集:  RETURN 区域名
    语言前缀 = 区域名.split("_", 1)[0].lower()             ← "zh"
    RETURN 第一个 代码.split("_",1)[0].lower() == 语言前缀 的代码
           IF 存在 ELSE "en_US"
```

### 8.3 `resolve_language(requested, languages) → 代码`

```
IF requested IN 语言集:  RETURN requested
RETURN system_language(语言集)
```

### 8.4 `resolve_startup_language(languages, preferred="", configured="") → 代码`

```
FOR 候选 IN [preferred, configured]:                ← language.toml 优先
    IF 候选 是字符串 AND 候选 IN 语言集:  RETURN 候选
RETURN system_language(语言集)
```

**优先级链**：`language.toml 的 preferred` → `config.toml 的 app.language` → 系统语言 → `en_US`。

### 8.5 `translate(languages, language, key, **values) → str`

```
函数 翻译(语言集, 语言, 键, **占位值):
    语言包 = 语言集[语言] IF 语言 IN 语言集 ELSE 语言集["en_US"]
    文本 = 语言包.text[键] IF 键 IN 语言包.text ELSE ENGLISH[键] IF 键 IN ENGLISH ELSE 键
    TRY:
        RETURN 文本.format(**占位值)
    EXCEPT (KeyError, ValueError):
        RETURN 文本            ← 占位符缺失/多余时不报错，原样显示模板
```

**三层回退**：当前语言 → 内建英文 → 键名本身。

### 8.6 `localized_name(names, language, languages) → str`

```
函数 本地化名称(名称表, 语言, 语言集):
    IF 名称表 不是字典:  RETURN ""
    偏好序列 = [语言, system_language(语言集), "en_US"]
    FOR 代码 IN 偏好序列:
        值 = 名称表[代码]
        IF 值 是非空字符串:  RETURN 值
    RETURN ""
```

用于**主题显示名**与**名单显示名**。

---

## 9. 主窗口（MainWindow）

文件：`main.py`。整个程序**只有一个** `QMainWindow`。

### 9.1 构造函数

```
类 MainWindow(QMainWindow):
    函数 __init__(主题集=None, 选定主题="", 语言集=None, 选定语言="en_US",
                  名单集=None, 选定名单="", 启动警告=None):
        super().__init__()

        # 继承应用图标
        应用 = QApplication.instance()
        IF 应用 是 QApplication:  self.setWindowIcon(应用.windowIcon())

        # ── 数据层 ──
        self.themes          = 主题集   IF 主题集   != None ELSE ThemeManager.discover_themes()
        self.selected_theme  = 选定主题
        self.languages       = 语言集   IF 语言集   != None ELSE LanguageManager.load_languages()[0]
        self.current_language = LanguageManager.resolve_language(选定语言, self.languages)
        self.rosters         = 名单集   IF 名单集   != None ELSE importnames.rosters
        self.current_roster  = 选定名单 OR importnames.active_roster
        self.startup_warnings = 启动警告 OR []
        self.names           = self._load_names()

        # ── 业务状态 ──
        self.multi_quantity     = 1
        self.lift_quantity      = 1
        self.lift_current_dict  = None      ← 减量抽的「剩余名单」，None 表示未开始
        self.multi_result       = None
        self.lift_result        = None

        # ── 控件与菜单引用全部先置 None（防止 AttributeError） ──
        self.ui / page_* / stacked_widget = None
        self.action_* / *_actions / *_menu 引用 = None
        self.*_button / *_label / *_quantity_label = None
        self.scroll_controller = None

        # ── 构建 ──
        self._build_ui()               ← 界面 + 菜单 + 页面 + 控件绑定
        self._apply_config_window()    ← 窗口尺寸与居中
        self._retranslate()            ← 全量文案刷新

        IF self.startup_warnings 非空:
            状态栏.showMessage(t("state.startup_warning",
                                 files=", ".join(self.startup_warnings)), 0)   ← 永久显示
```

### 9.2 `_load_names() → dict`

```
IF importnames.names 是字典 AND 非空:  RETURN importnames.names
logging.warning("未能从 importnames 中读取姓名数据，使用空列表。")
RETURN {}
```

### 9.3 `_apply_config_window()`

```
函数 应用窗口几何():
    配置 = importnames.loaded_config
    窗口段 = 配置["window"]（非字典 → {}）
    屏幕 = QApplication.primaryScreen()
    几何 = 屏幕.availableGeometry() IF 屏幕 存在 ELSE None
    屏宽 = 几何.width()  IF 几何 存在 ELSE 1280
    屏高 = 几何.height() IF 几何 存在 ELSE 800

    (宽, 高) = _configured_size(窗口段, 屏宽, 屏高)
    self.resize(宽, 高)
    self.setMinimumSize(0, 0)                       ← 允许自由缩放到极小
    IF 几何 存在:
        self.move(几何.中心.x - 宽//2, 几何.中心.y - 高//2)    ← 居中
```

### 9.4 `_build_ui()` —— 两段式容错

```
函数 构建界面():
    # 段一：主窗口骨架（失败则不再继续）
    TRY:
        self.ui_main = ui_main.Ui_MainWindow()
        self.ui_main.setupUi(self)                 ← 把 menubar/centralwidget/statusbar 装到 self
        self.stacked_widget = getattr(self.ui_main, "stackedWidget", None)
        IF self.stacked_widget == None:  RAISE RuntimeError("未找到 stackedWidget")
        self.setWindowTitle(self.windowTitle() OR "randname")
    EXCEPT Exception AS e:
        logging.exception("加载主窗口失败: %s", e)
        self._show_error(t("menu.about"), t("error.window_init", error=str(e)))
        RETURN                                       ← 直接放弃后续构建，窗口为空壳

    # 段二：菜单与页面（失败仅提示，窗口仍可显示）
    TRY:
        self._bind_menu_actions()
        self._build_theme_menu()
        self._build_language_menu()
        self._build_roster_menu()
        self._build_log_level_menu()
        self._load_pages()
        self._bind_page_actions()
    EXCEPT Exception AS e:
        logging.exception("初始化界面控件失败: %s", e)
        self._show_error(t("menu.about"), t("error.controls_init", error=str(e)))
```

### 9.5 `_bind_menu_actions()` —— QAction 绑定

```
从 ui_main 取 11 个 QAction 引用：
    action_multi / action_lift / action_scrollsingle
    action_inputconfig / action_outputconfig / action_reinputconfig / action_exit
    action_license / action_repository / action_help / action_program_log

逐个（存在才连）：
    action_Multi.triggered        → _show_multi_page()
    action_Lift.triggered         → _show_lift_page()
    action_ScrollSingle.triggered → _show_scrollsingle_page()
    action_inputconfig.triggered  → _on_import_memory()
    action_outputconfig.triggered → _on_export_memory()
    action_reinputconfig.triggered→ _on_reload_config()
    action_exit.triggered         → _on_exit()
    action_license.triggered      → _open_license()
    action_repository.triggered   → _open_repository()
    action_help.triggered         → _open_help()
    action_program_log.triggered  → _show_program_log()
```

### 9.6 四个动态菜单的构建

四个菜单结构一致：**清空 → 销毁旧 ActionGroup → 建互斥 QActionGroup → 逐项加入并连接**。

#### 9.6.1 `_build_theme_menu()`

```
主题菜单 = getattr(ui_main, "menu_theme", None)
IF 主题菜单 == None:                                ← 极老的 .ui 兼容分支
    主题菜单 = menubar.findChildren(QMenu) 中 title == "主题" 的第一个
IF 主题菜单 == None:
    主题菜单 = menubar.addMenu("主题")               ← 兜底新建
ELSE:
    主题菜单.clear()                                 ← 保留 QMenu 对象，仅清空项

IF self.theme_actions != None: self.theme_actions.deleteLater()   ← 释放旧 group
self.theme_actions = QActionGroup(主题菜单); setExclusive(True)

FOR 键名, 主题 IN self.themes.items():
    显示名 = LanguageManager.localized_name(主题.name, self.current_language, self.languages)
             OR 键名                                  ← 本地化失败则用键名
    action = QAction(显示名, self)
    action.setCheckable(True)
    action.setChecked(键名 == self.selected_theme)
    action.setData(键名)
    action.triggered.connect(lambda _checked=False, k=键名: self._select_theme(k))  ← 默认参数锁定键
    self.theme_actions.addAction(action)
    主题菜单.addAction(action)
```

#### 9.6.2 `_build_language_menu()`

```
FOR 代码, 语言包 IN self.languages.items():
    显示名 = 语言包.display_name OR 代码
    action.setChecked(代码 == self.current_language)
    → _select_language(代码)
```

#### 9.6.3 `_build_roster_menu()`

```
FOR 键名, 名单 IN self.rosters.items():
    显示名 = LanguageManager.localized_name(名单.name, self.current_language, self.languages)
             OR 键名
    action.setChecked(键名 == self.current_roster)
    → _select_roster(键名)
```

#### 9.6.4 `_build_log_level_menu()`

```
FOR 等级 IN StateManager.LOG_LEVEL_CHOICES:            ← ("DEBUG","INFO","WARNING","ERROR","CRITICAL")
    action = QAction(t("log." + 等级), self)
    action.setChecked(等级 == StateManager.CURRENT_LOG_LEVEL)
    → _select_log_level(等级)
```

> 四个菜单均为 **QActionGroup 互斥单选**：勾选态反映当前生效项。

### 9.7 翻译工具 `_t(key, **values)`

```
RETURN LanguageManager.translate(self.languages, self.current_language, key, **values)
```

### 9.8 `_select_log_level(level)`

```
选定 = StateManager.configure_logging(等级)
self._build_log_level_menu()                            ← 刷新勾选态
StateManager.log(选定, "log_level_changed", result=选定)
状态栏.showMessage(t("state.log_level_changed", level=t("log." + 选定)))
```

### 9.9 `_select_language(code)`

```
self.current_language = LanguageManager.resolve_language(code, self.languages)
self._build_language_menu()      ← 刷新语言勾选
self._build_theme_menu()         ← 主题名可能随语言变化
self._build_roster_menu()        ← 名单名可能随语言变化
self._build_log_level_menu()     ← 等级名随语言变化
self._retranslate()              ← 全量刷新菜单标题 + 动作文案 + 页面按钮
状态栏.showMessage(t("state.language_changed",
                     name=self.languages[self.current_language].display_name))
```

> **切换语言不清除任何抽取结果**；数量值也不变（数量标签在 `_retranslate` 中不被覆盖，
> 因 `_retranslate` 只处理按钮文案与输出标签）。

### 9.10 `_select_roster(key)` —— 切换名单

```
函数 选择名单(键名):
    self.names          = importnames.select_roster(键名)      ← 失败时返回原名单
    self.current_roster = importnames.active_roster
    self.lift_current_dict = None                               ← 剩余名单作废
    self.lift_result       = None

    上限 = max(1, len(self.names))
    self.multi_quantity = 截断(self.multi_quantity, 1, 上限)
    self.lift_quantity  = 截断(self.lift_quantity,  1, 上限)
    刷新 multi/lift 数量标签

    IF self.lift_label != None:  self.lift_label.setText(t("state.waiting"))
    IF self.scroll_controller != None:  self.scroll_controller.update_names(self.names)

    self._build_roster_menu()
    显示名 = localized_name(self.rosters[键名].name, 当前语言, 语言集) OR 键名
    状态栏.showMessage(t("state.roster_changed", name=显示名))
```

### 9.11 `_retranslate()` —— 全量文案刷新

```
函数 重译():
    # 1) 七个菜单标题
    menu_file      → t("menu.file")
    menu_mode      → t("menu.mode")
    menu_theme     → t("menu.theme")
    menu_language  → t("menu.language")
    menu_roster    → t("menu.roster")
    menu_about     → t("menu.about")
    menu_log_level → t("menu.log_level")

    # 2) 十一个 QAction 文案
    action_Multi         → "mode.multi"
    action_Lift          → "mode.lift"
    action_ScrollSingle  → "mode.scroll"
    action_inputconfig   → "action.import"
    action_outputconfig  → "action.export"
    action_reinputconfig → "action.reload"
    action_exit          → "action.exit"
    action_license       → "action.license"
    action_repository    → "action.repository"
    action_help          → "action.help"
    action_program_log   → "action.program_log"

    # 3) Multi 页
    IF hasattr(self, "ui_multi"):
        pushButton_Multi.setText(t("button.draw"))
        pushButton_MultiQuantityUp.setText   (t("button.increase"))
        pushButton_MultiQuantityDown.setText (t("button.decrease"))
        IF self.multi_label != None:
            self.multi_label.setText(self.multi_result OR t("state.waiting"))   ← 保留已有结果

    # 4) Lift 页
    IF hasattr(self, "ui_lift"):
        pushButton_Lift.setText(t("button.draw"))
        pushButton_LiftQuantityUp.setText   (t("button.increase"))
        pushButton_LiftQuantityDown.setText (t("button.decrease"))
        pushButton_LiftRenew.setText(t("button.reset"))
        IF self.lift_label != None:
            self.lift_label.setText(self.lift_result OR t("state.waiting"))     ← 保留已有结果

    # 5) ScrollSingle 页
    IF hasattr(self, "ui_scrollsingle"):
        pushButton_ScrollSingleStart.setText(t("button.start"))
        pushButton_ScrollSingleStop.setText (t("button.stop"))
        IF self.scroll_controller != None:
            self.scroll_controller.set_button_texts(t("button.start"), t("button.stop"))
        IF self.scroll_label != None AND NOT self.scroll_has_result:
            self.scroll_label.setText(t("state.waiting"))
            ← 用布尔量判定是否已有结果（不再依赖字面量集）

    # 6) ScrollMulti 页
    IF hasattr(self, "ui_scrollmulti"):
        pushButton_ScrollMulti.setText(t("button.draw"))
        pushButton_ScrollMultiQuantityUp.setText(t("button.increase"))
        pushButton_ScrollMultiQuantityDown.setText(t("button.decrease"))
        IF self.scroll_multi_controller != None:
            self.scroll_multi_controller.set_button_texts(
                t("button.draw"), t("button.stop_scrollmulti"), t("state.waiting"))
            ← reset 文案仅在空闲且无结果时刷新输出框，不覆盖已显示结果
```

> `hasattr(self, "ui_multi")` 是「该页面是否已成功构建」的探针
> —— 若 `_load_pages` 中途失败，`ui_lift` / `ui_scrollsingle` 可能不存在，
> 此时 `_retranslate` 跳过对应分支，避免 `AttributeError`。

### 9.12 `_select_theme(name)`

```
函数 选择主题(名称):
    应用 = QApplication.instance()
    IF 应用 不是 QApplication:  RETURN
    TRY:
        self.selected_theme = ThemeManager.apply_theme(应用, 名称, self.themes)
        StateManager.log("INFO", "theme", result=self.selected_theme)
        显示名 = localized_name(主题.name, 当前语言, 语言集) OR self.selected_theme
        状态栏.showMessage(t("state.theme_changed", name=显示名))
    EXCEPT (OSError, ValueError, KeyError) AS e:      ← 颜色解析失败的异常类型
        StateManager.log("ERROR", "theme", error=str(e))
        self._show_error("主题加载失败", str(e))       ← 注意：标题为硬编码中文，未国际化
```

### 9.13 `_load_pages()` —— 页面构建与默认页

```
IF self.stacked_widget == None:  RAISE RuntimeError("stackedWidget 未初始化")

# 四个页面均为独立 QWidget + 对应 Ui_Form
self.page_multi = QWidget(); ui_widgetmulti.Ui_Form().setupUi(self.page_multi)
self.page_lift  = QWidget(); ui_widgetlift.Ui_Form().setupUi(self.page_lift)
self.page_scrollsingle = QWidget(); ui_widgetscrollsingle.Ui_Form().setupUi(self.page_scrollsingle)
self.page_scrollmulti  = QWidget(); ui_widgetscrollmulti.Ui_Form().setupUi(self.page_scrollmulti)

self.stacked_widget.addWidget(page_multi)          # 索引 0
self.stacked_widget.addWidget(page_lift)           # 索引 1
self.stacked_widget.addWidget(page_scrollsingle)   # 索引 2
self.stacked_widget.addWidget(page_scrollmulti)    # 索引 3

应用配置 = importnames.loaded_config["app"]（非字典 → {}）
默认模式 = 应用配置.default_mode 缺省 "Multi"
IF 默认模式 == "Multi":       _show_multi_page()
ELIF 默认模式 == "Lift":      _show_lift_page()
ELIF 默认模式 == "ScrollMulti": _show_scrollmulti_page()
ELSE:                        _show_scrollsingle_page()   ← 含 "ScrollSingle" 及任何非法值
```

**页面切换**（四个方法，均为空操作保护）：

```
_show_multi_page()        → stacked_widget.setCurrentWidget(page_multi)
_show_lift_page()         → stacked_widget.setCurrentWidget(page_lift)
_show_scrollsingle_page() → stacked_widget.setCurrentWidget(page_scrollsingle)
_show_scrollmulti_page()  → stacked_widget.setCurrentWidget(page_scrollmulti)
```

> 「模式」菜单的三个动作绑定到这三个方法，**页面状态与记忆无关，切换不影响任何结果**。

### 9.14 `_bind_page_actions()` —— 控件绑定

```
函数 绑定页面动作():
    # ── Multi 页 ──
    multi_button         = ui_multi.pushButton_Multi
    multi_label          = ui_multi.label_MultiOutput
    multi_quantity_label = ui_multi.label_MultiQuantity
    multi_up_button      = ui_multi.pushButton_MultiQuantityUp
    multi_down_button    = ui_multi.pushButton_MultiQuantityDown

    _set_quantity_label(multi_quantity_label, self.multi_quantity)     ← 初始显示 "1"
    multi_up_button.clicked   → lambda: _adjust_quantity("multi", +1)
    multi_down_button.clicked → lambda: _adjust_quantity("multi", -1)
    IF multi_button AND multi_label:
        multi_button.clicked → _handle_multi()
        multi_label.setText(t("state.waiting"))                        ← 初始「等待输入」

    # ── ScrollSingle 页（独立 try/except，失败不影响其他页）──
    TRY:
        scroll_label       = ui_scrollsingle.label_ScrollSingleOutput
        scroll_start_button= ui_scrollsingle.pushButton_ScrollSingleStart
        scroll_stop_button = ui_scrollsingle.pushButton_ScrollSingleStop
        scroll_label.setText(t("state.waiting"))
        IF 三个控件都存在:
            速率 = _rate_from_config(importnames.loaded_config, "scroll_single")   ← 正数，缺省 30
            self.scroll_controller = ScrollSingle.ScrollController(
                scroll_label, scroll_start_button, scroll_stop_button,
                self.names,
                on_result = self._on_scroll_result,
                rate      = 速率,
                start_text= t("button.start"),
                stop_text = t("button.stop"),
                reset_text= t("state.waiting"))
            ← 构造后**不自动启动**
    EXCEPT Exception AS e:
        logging.exception("初始化 ScrollSingle 失败: %s", e)

    # ── ScrollMulti 页（独立 try/except，沿用 Multi 样式的单一输出框）──
    TRY:
        scroll_multi_button    = ui_scrollmulti.pushButton_ScrollMulti
        scroll_multi_label     = ui_scrollmulti.label_ScrollMultiOutput
        scroll_multi_quantity_label = ui_scrollmulti.label_ScrollMultiQuantity
        scroll_multi_up_button = ui_scrollmulti.pushButton_ScrollMultiQuantityUp
        scroll_multi_down_button = ui_scrollmulti.pushButton_ScrollMultiQuantityDown
        _set_quantity_label(scroll_multi_quantity_label, self.scroll_multi_quantity)
        scroll_multi_up_button.clicked   → lambda: _adjust_quantity("scrollmulti", +1)
        scroll_multi_down_button.clicked → lambda: _adjust_quantity("scrollmulti", -1)
        IF scroll_multi_button AND scroll_multi_label:
            self.scroll_multi_controller = ScrollMulti.ScrollMultiController(
                scroll_multi_label, scroll_multi_button, self.names,
                on_result  = self._on_scrollmulti_result,
                rate       = _rate_from_config(loaded_config, "scroll_multi"),
                draw_text  = t("button.draw"),
                stop_format= t("button.stop_scrollmulti"),
                reset_text = t("state.waiting"),
                on_warning = self._on_scrollmulti_warning)
            self.scroll_multi_controller.set_quantity(self.scroll_multi_quantity)
            ← 构造后显示占位 reset_text，**不自动启动**
    EXCEPT Exception AS e:
        logging.exception("初始化 ScrollMulti 失败: %s", e)

    # ── Lift 页 ──
    lift_button         = ui_lift.pushButton_Lift
    lift_label          = ui_lift.label_LiftOutput
    lift_quantity_label = ui_lift.label_LiftQuantity
    lift_up_button      = ui_lift.pushButton_LiftQuantityUp
    lift_down_button    = ui_lift.pushButton_LiftQuantityDown
    lift_renew_button   = ui_lift.pushButton_LiftRenew

    _set_quantity_label(lift_quantity_label, self.lift_quantity)
    lift_up_button.clicked   → lambda: _adjust_quantity("lift", +1)
    lift_down_button.clicked → lambda: _adjust_quantity("lift", -1)
    lift_renew_button.clicked→ _reset_lift_page()
    IF lift_button AND lift_label:
        lift_button.clicked → _handle_lift()
        lift_label.setText(t("state.waiting"))
```

### 9.15 数量调节 `_adjust_quantity(mode, delta)`

```
函数 调整数量(模式, 增量):
    上限 = max(1, len(self.names))                    ← 以「名单总数」为上限
    IF 模式 == "multi":
        self.multi_quantity = max(1, min(上限, self.multi_quantity + 增量))
        _set_quantity_label(self.multi_quantity_label, self.multi_quantity)
        logging.info("更新多抽数量=%s", self.multi_quantity)
    ELIF 模式 == "lift":
        self.lift_quantity = max(1, min(上限, self.lift_quantity + 增量))
        _set_quantity_label(self.lift_quantity_label, self.lift_quantity)
        logging.info("更新减量抽数量=%s", self.lift_quantity)
    ELIF 模式 == "scrollmulti":
        self.scroll_multi_quantity = max(1, min(上限, self.scroll_multi_quantity + 增量))
        _set_quantity_label(self.scroll_multi_quantity_label, self.scroll_multi_quantity)
        IF self.scroll_multi_controller != None:
            self.scroll_multi_controller.set_quantity(self.scroll_multi_quantity)
        logging.info("更新滚动多抽数量=%s", self.scroll_multi_quantity)
```

> **Lift 的数量上限是「名单总数」而非「剩余名单长度」**。
> 因此减量抽进行到剩余人数少于当前数量时，`Lift()` 会走「数量超出」分支返回空结果（见第 16 章）。

### 9.16 结果显示工具

```
函数 _set_quantity_label(标签, 值):  IF 标签 != None: 标签.setText(str(值))
函数 _set_output_text(标签, 文本):  IF 标签 != None: 标签.setText(文本)
函数 _show_error(标题, 消息):       QMessageBox.critical(self, 标题, 消息)
```

### 9.17 `_format_output_result(result) → 展示文本`

```
函数 格式化结果(结果) → str:
    IF 结果 不是字典:  RETURN str(结果)

    outdict = 结果.outdict 缺省 {}
    IF outdict 是字典 AND 非空:
        条目 = []
        FOR 值 IN outdict.values():
            IF 值 是字典:
                IF "name" IN 值:                                  ← Multi 形态
                    条目名 = 值.name
                ELSE IF len(值) == 1:                             ← Lift 形态 {code: name}
                    条目名 = 下一个(iter(值.values()))
                ELSE:
                    条目名 = str(值)
            ELSE:
                条目名 = str(值)
            条目.append(str(条目名))

        IF 条目 非空:
            IF len(条目) <= 4:  RETURN "  ".join(条目)            ← 两个空格分隔
            ELSE:                                                ← 每行 4 个
                行 = []
                FOR i IN range(0, len(条目), 4):
                    行.append("  ".join(条目[i:i+4]))
                RETURN "\n".join(行)

    # 无 outdict：Lift 被清空时改为展示剩余名单
    IF 结果.Liftdict 是字典:
        剩余 = list(结果.Liftdict.values())
        IF 剩余 非空:
            IF len(剩余) <= 4:  RETURN "  ".join(str(x) FOR x IN 剩余)
            ELSE:               RETURN "\n".join(每 4 个一行的 "  ".join(...))

    RETURN "暂无结果"          ← 硬编码中文，未国际化
```

**排版规则**：≤4 人单行，两个空格分隔；>4 人每行 4 人，行间 `\n` 换行。

### 9.18 `_handle_multi()` —— 多抽完整流程

```
函数 执行多抽():
    TRY:
        logging.info("执行多抽，数量=%s", self.multi_quantity)
        结果 = Multi.Multi(self.names, self.multi_quantity)          ← 纯算法
        self.multi_result = self._format_output_result(结果)
        self._set_output_text(self.multi_label, self.multi_result)
        状态栏.showMessage(t("state.multi_result", count=self.multi_quantity))

        TRY:                                                       ← 记忆写入单独兜底
            状态 = StateManager.load_memory()
            状态["loaded_config"] = importnames.loaded_config
            状态.setdefault("last_results", {})["Multi"] =
                { "result": 结果, "time": StateManager._now_iso() }
            StateManager.save_memory(状态)
            StateManager.log("INFO", "Multi", result=结果)
        EXCEPT Exception:
            logging.exception("记录 multi 结果失败")                ← 记忆失败不影响抽取

    EXCEPT Exception AS e:
        logging.exception("多抽执行失败: %s", e)
        self.multi_result = t("dialog.operation_failed", error=str(e))
        self._set_output_text(self.multi_label, self.multi_result)
        self._show_error(t("mode.multi"), str(e))
        TRY:  StateManager.log("ERROR", "Multi", error=str(e))
        EXCEPT:  pass
```

### 9.19 `_handle_lift()` —— 减量抽完整流程

```
函数 执行减量抽():
    TRY:
        logging.info("执行减量抽，数量=%s", self.lift_quantity)
        # 首轮或已重置 → 使用完整名单；否则使用上轮剩余
        待抽字典 = self.names IF self.lift_current_dict == None ELSE self.lift_current_dict

        结果 = Lift.Lift(self.names, 待抽字典, self.lift_quantity)
        self.lift_result = self._format_output_result(结果)
        self._set_output_text(self.lift_label, self.lift_result)

        IF "Liftdict" IN 结果:
            self.lift_current_dict = 结果.Liftdict        ← 保存剩余，供下一轮

        状态栏.showMessage(t("state.lift_result", count=self.lift_quantity))

        TRY:
            状态 = StateManager.load_memory()
            状态["loaded_config"] = importnames.loaded_config
            状态.setdefault("last_results", {})["Lift"] =
                { "result": 结果, "time": StateManager._now_iso() }
            StateManager.save_memory(状态)
            StateManager.log("INFO", "Lift", result=结果)
        EXCEPT Exception:
            logging.exception("记录 lift 结果失败")

    EXCEPT Exception AS e:
        logging.exception("减量抽执行失败: %s", e)
        self.lift_result = t("dialog.operation_failed", error=str(e))
        self._set_output_text(self.lift_label, self.lift_result)
        self._show_error(t("mode.lift"), str(e))
        TRY:  StateManager.log("ERROR", "Lift", error=str(e))
        EXCEPT:  pass
```

**关键不变式**：
- `self.names` **永不因抽取而改变**（永远是完整名单）。
- `self.lift_current_dict` 是唯一被消耗的状态；只有切换名单 / 刷新配置 / 点「重置」才清空。
- `Lift()` 失败时原样返回 `Liftdict`，因此失败不会丢失剩余名单。

### 9.20 `_reset_lift_page()` —— 减量抽「重置」

```
函数 重置减量抽页():
    self.lift_current_dict = None          ← 下一轮回到完整名单
    self.lift_result       = None
    _set_quantity_label(self.lift_quantity_label, self.lift_quantity)   ← 数量保持不变
    IF self.lift_label != None:
        self.lift_label.setText("等待输入")   ← 硬编码简体中文，未走 t()（见第 16 章）
    状态栏.showMessage(t("state.waiting"))
```

### 9.21 `_on_scroll_result(result, meta)` —— 滚动抽结果回调

```
函数 滚动抽结果(结果, 元信息):
    TRY:
        logging.info("scrollsingle result: %s", 结果)
        IF self.scroll_label != None:  self.scroll_label.setText(str(结果))    ← 与算法重复设置一次
        状态 = StateManager.load_memory()
        状态["loaded_config"] = importnames.loaded_config
        状态.setdefault("last_results", {})["ScrollSingle"] = { "result": 结果, "meta": 元信息 }
        StateManager.save_memory(状态)
        StateManager.log("INFO", "ScrollSingle", result={ "name": 结果, "meta": 元信息 })
    EXCEPT Exception AS e:
        logging.exception("处理 scrollsingle 结果失败: %s", e)
        TRY:  StateManager.log("ERROR", "ScrollSingle", error=str(e))
        EXCEPT:  pass
```

### 9.21.1 `_on_scrollmulti_result(result, meta)` / `_on_scrollmulti_warning(count)`

```
函数 滚动多抽结果(结果, 元信息):
    TRY:
        logging.info("scrollmulti result: %s", 结果)
        数量 = 结果.quantity.selected（非字典 → 0）
        状态栏.showMessage(t("state.scrollmulti_result", count=数量))
        状态 = StateManager.load_memory()
        状态["loaded_config"] = importnames.loaded_config
        状态.setdefault("last_results", {})["ScrollMulti"] = { "result": 结果, "meta": 元信息 }
        StateManager.save_memory(状态)
        StateManager.log("INFO", "ScrollMulti", result=结果)
    EXCEPT Exception AS e:
        logging.exception("处理 scrollmulti 结果失败: %s", e)
        TRY:  StateManager.log("ERROR", "ScrollMulti", error=str(e))
        EXCEPT:  pass

函数 滚动多抽警告(数量):
    TRY:
        状态栏.showMessage(t("state.scrollmulti_invalid", count=数量))
        StateManager.log("WARN", "ScrollMulti", error="requested more than {数量}")
    EXCEPT:  pass
```

> `ScrollMulti` 的记忆条目 `{ "result": <多抽同构字典>, "meta": {...} }` 与 `ScrollSingle` 风格一致；
> 导入记忆时 `_apply_memory_import` 取出 `result` 交给 `ScrollMultiController.show_result()` 一次性显示。

### 9.22 文件菜单

#### 9.22.1 `_on_import_memory()` —— 导入记忆

```
函数 导入记忆():
    TRY:
        (文件名, _) = QFileDialog.getOpenFileName(
            self, t("dialog.import_title"), "", t("dialog.json_filter"))
        IF 文件名 为空:  RETURN                        ← 取消即静默返回
        状态 = StateManager.import_memory(Path(文件名), 应用回调=self._apply_memory_import)
        QMessageBox.information(self, t("dialog.import_title"),
                                t("dialog.import_success", path=文件名))
    EXCEPT Exception AS e:
        logging.exception("导入记忆失败: %s", e)
        QMessageBox.warning(self, t("dialog.import_title"),
                            t("dialog.operation_failed", error=str(e)))
```

#### 9.22.2 `_on_export_memory()` —— 导出记忆

```
函数 导出记忆():
    TRY:
        (文件名, _) = QFileDialog.getSaveFileName(
            self, t("dialog.export_title"), "memory-export.json", t("dialog.json_filter"))
        IF 文件名 为空:  RETURN
        StateManager.export_memory(Path(文件名))
        QMessageBox.information(self, t("dialog.export_title"),
                                t("dialog.export_success", path=文件名))
    EXCEPT Exception AS e:
        logging.exception("导出记忆失败: %s", e)
        QMessageBox.warning(self, t("dialog.export_title"),
                            t("dialog.operation_failed", error=str(e)))
```

#### 9.22.3 `_apply_memory_import(content)` —— 导入后的界面回填

```
函数 应用导入记忆(内容):
    TRY:
        IF 内容 不是字典:  RETURN
        当前尺寸 = self.size()
        self.setMinimumSize(0, 0)                    ← 结果可能很长，先解除最小尺寸限制

        最近 = 内容.last_results 缺省 {}
        IF 最近 是字典:
            IF self.multi_label != None:
                v = 最近["Multi"]（兼容小写 "multi"）
                self.multi_result = str(v.result IF v 是字典 ELSE v)
                self.multi_label.setText(self.multi_result)
            IF self.lift_label != None:
                v = 最近["Lift"]（兼容 "lift"）
                self.lift_result = str(v.result IF v 是字典 ELSE v)
                self.lift_label.setText(self.lift_result)
            IF self.scroll_label != None:
                v = 最近["ScrollSingle"]（兼容 "scrollsingle"）
                self.scroll_label.setText(str(v.result IF v 是字典 ELSE v))

        self.resize(当前尺寸)                        ← 恢复原窗口大小
        self.setMinimumSize(0, 0)
    EXCEPT Exception AS e:
        logging.exception("应用导入记忆失败: %s", e)
```

> **不变式**：导入记忆**不改变窗口尺寸**、**不改变名单**、**不写入 `config/`**、**不写入 `lift_current_dict`**。

#### 9.22.4 `_on_reload_config()` —— 刷新程序状态（最复杂的状态迁移）

```
函数 重新加载配置():
    TRY:
        # ① 快照当前状态
        旧主题 = self.selected_theme
        旧语言 = self.current_language
        旧名单键 = self.current_roster
        旧姓名 = self.names.copy()
        旧状态栏 = 状态栏.currentMessage()

        # ② 重新读盘
        importnames.reload_data()
        配置 = importnames.loaded_config

        # ③ 名单：优先保留原名单键，否则回到配置文件指定名单
        self.rosters      = importnames.rosters
        目标键 = 旧名单键 IF 旧名单键 IN self.rosters ELSE importnames.active_roster
        self.names          = importnames.select_roster(目标键)
        self.current_roster = importnames.active_roster
        名单有变 = (旧姓名 != self.names)

        # ④ 减量抽剩余名单：仅当名单内容确实变化时才重置
        IF 名单有变:  self.lift_current_dict = None

        # ⑤ 数量夹紧到新名单范围
        self.multi_quantity = 截断到 [1, max(1, len(self.names))]
        self.lift_quantity  = 截断到 [1, max(1, len(self.names))]
        刷新两个数量标签

        # ⑥ 主题 / 语言：优先保留，仍可用则沿用
        self.themes = ThemeManager.discover_themes()
        (self.languages, 首选语言, 语言警告) = LanguageManager.load_languages()
        应用配置 = 配置["app"]（非字典 → {}）
        self.selected_theme = 旧主题 IF 旧主题 IN self.themes
                              ELSE ThemeManager.resolve_startup_theme(self.themes, 应用配置.theme)
        self.current_language = 旧语言 IF 旧语言 IN self.languages
                                ELSE LanguageManager.resolve_startup_language(
                                        self.languages, 首选语言, 应用配置.language)

        # ⑦ 重建四个菜单 + 全量重译
        _build_theme_menu(); _build_language_menu(); _build_roster_menu(); _build_log_level_menu()
        _retranslate()

        # ⑧ 重新应用主题样式表
        IF self.themes 非空:
            ThemeManager.apply_theme(QApplication.instance(), self.selected_theme, self.themes)

        # ⑨ 滚动抽：仅在名单变化时更新姓名池（保持运行/按钮状态不变）
        IF self.scroll_controller != None AND 名单有变:
            self.scroll_controller.update_names(self.names)

        # ⑩ 重新汇总警告
        警告 = list(StateManager.CONFIG_WARNINGS)
        IF importnames.ROSTER_FALLBACK_USED:  警告 += "config/name.toml"
        IF 语言警告:                          警告 += 语言警告
        IF ThemeManager.THEME_LOAD_WARNING:   警告 += ThemeManager.THEME_LOAD_WARNING
        self.startup_warnings = 去重保序(警告)

        IF 警告 非空:
            StateManager.log("WARN", "reload_fallback", error=", ".join(警告))
            状态栏.showMessage(t("state.startup_warning", files=", ".join(警告)), 0)
        ELSE:
            状态栏.showMessage(旧状态栏)            ← 无警告则恢复原状态栏文本
    EXCEPT Exception AS e:
        logging.exception("重新加载配置失败: %s", e)
        QMessageBox.warning(self, t("action.reload"),
                            t("dialog.operation_failed", error=str(e)))
```

**状态迁移表**：

| 项目 | 刷新后行为 |
| --- | --- |
| 当前页面 | **保持不变**（不重置到 `default_mode`） |
| 当前模式数量 / 减量抽数量 | 夹紧到新名单长度范围，**不重置为 1** |
| 减量抽剩余名单 | 名单内容变化才清空；内容未变则保留 |
| 多抽 / 减量抽结果标签 | **保持不变** |
| 滚动抽结果 | **保持不变**；按钮启用状态与运行状态不受影响 |
| 主题 / 语言 | 原值仍可用则沿用；否则回落到配置文件指定项 |
| 窗口尺寸 | **保持不变** |
| 名单键 | 原键仍存在则沿用；否则回到 `app.roster` 指定（再否则首个名单） |

### 9.23 关于菜单

#### 9.23.1 `_open_help()`

```
函数 打开帮助():
    语言 = self.current_language IF IN {"en_US","zh_CN","zh_TW"} ELSE "en_US"
    帮助目录 = _configured_path(importnames.loaded_config, "paths", "help_directory", "doc")
    候选路径 = [帮助目录 / ("help_" + 语言 + ".md")]
    IF 语言 != "en_US":
        候选路径.append(ROOT_DIR / "doc" / "help_en_US.md")        ← 非英文回落英文
    FOR 路径 IN 候选路径:
        IF 路径 是文件:
            _show_document(t("action.help"), 路径, markdown=True)
            RETURN
    _show_error(t("action.help"), t("error.help_missing", path=str(候选路径[-1])))
```

#### 9.23.2 `_show_document(title, path, *, markdown) → bool`

```
函数 显示文档(标题, 路径, 是否Markdown):
    TRY:
        内容 = 路径.read_text(encoding="utf-8")
    EXCEPT (OSError, UnicodeError) AS e:
        logging.exception("无法读取文档 %s", 路径)
        StateManager.log("ERROR", "read_document", error=路径 + ": " + str(e))
        _show_error(标题, t("dialog.operation_failed", error=str(e)))
        RETURN False

    对话框 = QDialog(self); 标题 = 标题
    对话框.resize(900, 680); setMinimumSize(620, 420)
    文本框 = QTextBrowser(对话框)
    setOpenLinks(False) ; setOpenExternalLinks(False) ; setReadOnly(True)   ← 禁止点击链接
    IF 是否Markdown:  setMarkdown(内容)  ELSE:  setPlainText(内容)
    文本框.setStyleSheet("QTextBrowser { border: none; padding: 16px; }")
    按钮盒 = QDialogButtonBox(Close)
    按钮盒.Close.setText(t("action.close"))
    按钮盒.rejected → 对话框.reject() ; accepted → 对话框.accept()
    布局 = QVBoxLayout(对话框); 边距 12,12,12,12 ; 间距 10
    布局.addWidget(文本框); 布局.addWidget(按钮盒)
    StateManager.log("INFO", "open_document", result=路径.文件名)
    对话框.exec()                      ← 模态阻塞
    RETURN True
```

> 帮助与许可证均**在应用内渲染**，不调用外部浏览器/阅读器；
> 且链接被禁用（`setOpenLinks(False)` + `setOpenExternalLinks(False)`）。

#### 9.23.3 `_show_program_log()` —— 查看本次会话日志

```
函数 显示程序日志():
    对话框 = QDialog(self); 标题 = t("action.program_log"); resize(820, 520)
    文本框 = QPlainTextEdit(对话框); setReadOnly(True)
    文本框.setPlainText(StateManager.session_log_text() OR t("state.no_logs"))
    按钮盒 = QDialogButtonBox(Close); Close.setText(t("action.close"))
    rejected → reject ; accepted → accept
    布局 = QVBoxLayout(对话框); addWidget(文本框); addWidget(按钮盒)
    对话框.exec()
```

#### 9.23.4 `_open_license()`

```
TRY:
    许可路径 = _configured_path(importnames.loaded_config, "paths", "license_file", "doc/gpl-3.0.md")
    IF 许可路径 存在:  _show_document(t("action.license"), 许可路径, markdown=True)
    ELSE:             _show_error(t("action.license"), t("error.license_missing", path=str(许可路径)))
EXCEPT Exception AS e:
    logging.exception("打开许可证文件失败: %s", e)
    _show_error(t("action.license"), t("error.open_license", error=str(e)))
```

#### 9.23.5 `_open_repository()`

```
TRY:
    应用设置 = importnames.loaded_config["app"]（非字典 → {}）
    仓库网址 = 应用设置.repository_url 缺省 "https://www.github.com/HQZ-OhNone/randname"
    logging.info("打开项目仓库: %s", 仓库网址)
    QDesktopServices.openUrl(QUrl(仓库网址))
EXCEPT Exception AS e:
    logging.exception("打开仓库链接失败: %s", e)
    _show_error(t("action.repository"), t("error.open_repository", error=str(e)))
```

#### 9.23.6 `_on_exit()`

```
logging.info("用户请求退出程序")
应用 = QApplication.instance()
IF 应用 != None:  应用.quit()
RETURN app.exec()          ← 在 main() 中返回退出码
```

---

## 10. 四种抽取模式算法

### 10.1 多抽 `Multi.Multi(alllist, quantity) → output`

```
函数 Multi(全部名单, 抽取数) → output:
    print("=> mode: Multi")
    output = {
        "mode": "Multi",
        "quantity": { "total": len(全部名单), "selected": 抽取数 },
        "time": datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    }

    IF 抽取数 > len(全部名单):
        print("===> warn: 給定數量(...)大於總數(...)，無法進行多抽。")
        output["outdict"] = {}
        RETURN output                      ← 不抽取，outdict 为空

    剩余键 = list(全部名单.keys())
    已选键 = []
    FOR i IN range(抽取数):
        键 = random.choice(剩余键)         ← 均匀随机
        已选键.append(键)
        剩余键.remove(键)                  ← 立即移除 → 本次内不重复
        print(剩余键)                      ← 调试输出到 stdout

    outdict = {}
    FOR i IN range(len(已选键)):
        outdict[str(i)] = { "code": 已选键[i], "name": 全部名单[已选键[i]] }
    output["outdict"] = outdict
    RETURN output
```

**性质**：等概率无放回抽样；`alllist` **只读**，调用方名单永不变（多抽不消耗名单）。
**复杂度**：O(n + k)，k = 抽取数。

### 10.2 减量抽 `Lift.Lift(alllist, Liftdict, quantity) → output`

```
函数 Lift(完整名单, 当前剩余名单, 抽取数) → output:
    print("=> mode: Lift")
    print("===> quantity: " + 抽取数)
    output = {
        "mode": "Lift",
        "quantity": {
            "total":    len(完整名单),
            "wasted":   len(完整名单) - len(当前剩余名单),      ← 已被抽走的人数
            "selected": 抽取数,
            "Lift":     len(当前剩余名单) - 抽取数              ← 本轮结束后剩余人数
        },
        "alllist": 完整名单,                 ← 原样引用（未深拷贝）
        "time": datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    }

    IF len(当前剩余名单) == 0:               ← 剩余已空
        print("===> warn: Liftdict 為空，無法進行減量抽取。")
        output["Liftdict"] = 当前剩余名单
        output["outdict"]  = {}
        RETURN output                       ← 剩余名单原样返回（不丢失状态）

    IF 抽取数 > len(当前剩余名单):           ← 数量超出剩余
        print("===> warn: 給定數量(...)大於總數(...)，無法進行減量抽取。")
        output["Liftdict"] = 当前剩余名单
        output["outdict"]  = {}
        RETURN output                       ← 剩余名单原样返回

    剩余键 = list(当前剩余名单.keys())
    已选键 = []
    FOR i IN range(抽取数):
        键 = random.choice(剩余键)
        已选键.append(键)
        剩余键.remove(键)
        print(剩余键)

    outdict = {}
    FOR i IN range(len(已选键)):
        outdict[str(i)] = { 已选键[i]: 当前剩余名单[已选键[i]] }   ← 单键包裹，形态与 Multi 不同
    output["outdict"] = outdict

    新剩余 = {}
    FOR 键 IN 剩余键:
        新剩余[键] = 当前剩余名单[键]
    output["Liftdict"] = 新剩余              ← 本轮之后的剩余名单

    RETURN output
```

**性质**：跨轮无放回；抽中者**永久移出**剩余池，直到「重置」或切换名单/刷新。
**复杂度**：O(n + k)。

**「抽空后」的行为**：当剩余为 0 再次抽取 → `outdict = {}`、`Liftdict = {}`，
界面显示「暂无结果」（`_format_output_result` 的兜底）。

### 10.3 滚动单抽 `ScrollSingle.ScrollController`

文件：`lib/ScrollSingle.py`。UI 接线在 `main.py`，**所有逻辑在本类内**。

#### 10.3.1 构造

```
类 ScrollController:
    函数 __init__(标签控件, 开始按钮, 停止按钮, 姓名字典,
                  结果回调=None, 速率=30, 开始文本="开始", 停止文本="停止"):
        self.label        = 标签控件
        self.start_button = 开始按钮
        self.stop_button  = 停止按钮
        self.start_text   = 开始文本
        self.stop_text    = 停止文本
        self.names        = 姓名字典.copy() IF 是字典 ELSE {}      ← 防御性浅拷贝
        self.on_result    = 结果回调

        self.timer = QTimer()
        间隔 = max(1, 1000 // max(1, int(速率)))                 ← rate=30 → 33 ms
        self.timer.setInterval(间隔)
        self.timer.timeout.connect(self._tick)

        self.running       = False
        self.current_order = []
        self.index         = 0
        self.selected      = None

        TRY: 开始按钮.setText(开始文本); 开始按钮.clicked.connect(self.start)
        EXCEPT: pass
        TRY: 停止按钮.setText(停止文本); 停止按钮.clicked.connect(self.stop)
        EXCEPT: pass
        ← 不自动 start
```

#### 10.3.2 内部方法

```
函数 _now_str() → "2026-10-11 13:20:05"            （"%Y-%m-%d %H:%M:%S"，空格+冒号）

函数 _prepare_new_order():
    键列表 = list(self.names.keys())
    random.shuffle(键列表)                          ← 原地洗牌
    self.current_order = [self.names[键] FOR 键 IN 键列表]
    self.index = 0

函数 _tick():                                        ← 每个定时器周期调用一次
    IF self.current_order 为空:
        self._prepare_new_order()
    IF self.label != None:
        self.label.setText(str(self.current_order[self.index]))
    self.index += 1
    IF self.index >= len(self.current_order):
        self._prepare_new_order()                    ← 跑完一轮 → 重新洗牌
```

#### 10.3.3 公共方法

```
函数 start():
    IF self.running:  RETURN                          ← 幂等
    self.running = True
    self._prepare_new_order()                         ← 每次开始都重新洗牌
    self.timer.start()
    开始按钮.setEnabled(False)                        ← 按钮互斥
    停止按钮.setEnabled(True)

函数 stop() → 结果文本:
    IF NOT self.running:                              ← 重复点击「停止」
        结果 = self.label.text() IF label != None ELSE None
        元信息 = { "time": _now_str(), "mode": "ScrollSingle" }
        TRY: self.on_result(结果, 元信息)  EXCEPT: pass
        RETURN 结果

    self.timer.stop()
    self.running = False
    开始按钮.setEnabled(True)
    停止按钮.setEnabled(False)
    结果 = self.label.text()                          ← 停止瞬间显示的即为结果
    self.selected = 结果                               ← 仅记录，不改样式
    元信息 = { "time": _now_str(), "mode": "ScrollSingle" }
    TRY: self.on_result(结果, 元信息)  EXCEPT: pass
    RETURN 结果

函数 toggle():   RETURN self.stop() IF self.running ELSE self.start()

函数 reset():                                     ← 清空显示，恢复初始态
    self.label.setText("等待输入")                  ← 硬编码简体中文
    self.label.setStyleSheet('')
    self.selected = None

函数 update_names(新姓名):
    更新后 = 新姓名.copy() IF 是字典 ELSE {}
    IF 更新后 != self.names:
        self.names = 更新后
        self._prepare_new_order()                    ← 立即重排
        self.selected = None
    ← **不改变 running 状态、不改变按钮启用态、不重置标签文本**

函数 set_button_texts(开始文本, 停止文本):
    self.start_text = 开始文本 ; self.stop_text = 停止文本
    开始按钮.setText(开始文本) ; 停止按钮.setText(停止文本)
```

**性质**：
- 结果 = 「按下停止那一瞬间标签上的文字」，即 `names` 中某个值。
- 每跑完一轮即重新洗牌，避免固定顺序造成的视觉规律。
- 姓名池在**整个滚动会话中不变**（滚动抽不消耗名单）。
- `update_names` 在名单切换/刷新时热替换姓名池且**不打断正在进行的滚动**。

### 10.4 滚动多抽 `ScrollMulti.ScrollMultiController`

文件：`lib/ScrollMulti.py`。UI 接线在 `main.py`，逻辑全部在本类内。**沿用 Multi 页面样式**：
单一输出框 `label_ScrollMultiOutput` + 数量增减 + 一个大按钮（初始文案「抽取」）。多个「转盘」不各自建控件，
而是把 n 个当前名字**拼接成一个字符串**写入同一个输出框（排列规则同 Multi 结果）。

#### 10.4.1 构造

```
类 ScrollMultiController:
    函数 __init__(输出标签, 按钮, 姓名字典, 结果回调=None, 速率=30,
                  抽取文本="抽取", 停止格式="停止（{remaining}/{total}）",
                  等待文本="等待输入", 警告回调=None, 状态回调=None):
        self.label = 输出标签
        self.button = 按钮
        self.names = 姓名字典.copy() IF 是字典 ELSE {}
        self.draw_text / self.stop_format / self.reset_text = 对应参数
        self.quantity = 1
        self.running  = False
        self.pool     = {}        ← 本轮尚未停下的 编号→姓名
        self.total    = 0         ← 本轮转盘数量 n
        self.reels    = []        ← 逻辑转盘：[{active, order, index, key, name}, ...]
        self.timer = QTimer(); 间隔 = max(1, 1000 // max(1, int(速率))); timeout.connect(self._tick)
        TRY: 按钮.clicked.connect(self.handle_click)  EXCEPT: pass
        self._set_button_text()
        self._show_placeholder()          ← 空闲时输出框显示 reset_text
```

#### 10.4.2 状态机与按钮

```
handle_click():
    RETURN self.stop_next() IF self.running ELSE self.start()

start():
    IF self.running: RETURN
    IF names 为空: 警告回调(len(names)); RETURN
    n = self.quantity ; self.total = min(n, len(names))
    IF n > len(names): 警告回调(len(names))           ← 数量夹取并提示
    self.pool = dict(self.names)
    self.reels = [ {active=True, order=洗牌(pool.keys()), index=0, key=None, name=""} × self.total ]
    self.running = True
    self._tick()                                      ← 立即出一批名字
    self.timer.start()
    self._set_button_text()                           ← 按钮="停止（n/n）"

stop_next() → 本轮停下的名字:
    IF NOT self.running: RETURN
    取第一个 active 转盘 reel；若无 → _finish()
    reel.active = False
    固定键 = reel.key
    IF 固定键 NOT IN self.pool:                       ← 连续快速点击的兜底
        固定键 = random.choice(list(self.pool)) IF pool ELSE None
    reel.key / reel.name = 固定键 / pool[固定键] ; pool.pop(固定键)
    对其余 active 转盘重新洗牌其 order          ← 保证不会落到已停名字
    _update_label()
    IF 剩余转盘数 == 0: _finish() ELSE self._set_button_text()   ← 按钮="停止（x/n）"
    RETURN reel.name
```

#### 10.4.3 tick 与结果

```
_tick():                                             ← 每个定时器周期
    IF pool 为空: RETURN
    FOR reel IN self.reels:
        IF reel.active:
            若 order 用尽：reel.order = 洗牌(pool.keys()) ; index=0
            key = reel.order[index++] ; 越界或失效则重排
            reel.key, reel.name = key, pool[key]
    _update_label()                                  ← 把 n 个名字拼进同一个框

_finish():
    timer.stop() ; running=False
    result = { "mode":"ScrollMulti", "time":<"-"分隔>, 
               "quantity":{"total":len(names),"selected":self.total},
               "outdict": { "0": {code,name}, ... } }              ← 结构同 Multi
    按钮恢复 draw_text ；结果回调(result, meta={time,mode:"ScrollMulti"})
```

#### 10.4.4 输出文本排列 `_format_names`

与 `main._format_output_result` 的多抽展示规则**完全一致**：≤4 个名字单行、两空格分隔；
多于 4 个则每行 4 个、行间 `\n`、行内两空格分隔。

**性质**：
- 同一轮内已停下的编号会从 `pool` 移除，故**本轮不重复**；开始新一轮时重新使用完整名单。
- 停止顺序 = 转盘建立顺序（下标 0…n-1）。
- `show_result(result)`：把记忆中的 `outdict` 名字一次性显示在同一个框内（导入记忆用）。
- `set_button_texts(draw, stop, reset=None)`：`reset` 仅在**空闲且无结果**时刷新输出框，
  避免切换语言时覆盖已经显示的结果。
- `reset()`：停止计时器、清空转盘、输出框回到 `reset_text`。

---

## 11. 界面结构（UI）

### 11.1 主窗口 `ui/Main.ui` → `lib/ui_main.Ui_MainWindow`

```
QMainWindow "MainWindow"   初始 800×600，标题 "randname ---HQZ-OhNone"
├── centralwidget (QWidget)
│   └── gridLayout (QGridLayout)
│       └── stackedWidget (QStackedWidget)   currentIndex 初始 -1
│            ├── [0] page_multi          （运行时添加）
│            ├── [1] page_lift           （运行时添加）
│            └── [2] page_scrollsingle   （运行时添加）
├── menubar (QMenuBar)
│   ├── menu_file      文件
│   │     action_inputconfig / action_outputconfig / ─ / action_reinputconfig / ─ / action_exit
│   ├── menu_mode      模式      → action_Multi / action_Lift / action_ScrollSingle
│   ├── menu_theme     主题      （运行时填充 13 项）
│   ├── menu_language  语言      （运行时填充 3 项）
│   ├── menu_roster    名单      （运行时填充 n 项）
│   └── menu_about     关于
│         action_help / action_program_log / menu_log_level（子菜单） / ─
│         action_license / action_repository
└── statusbar (QStatusBar)
```

**「模式」菜单的三个动作未设为互斥组**（非 QActionGroup），因此可出现多选勾选态，
但实际页面只由 `setCurrentWidget` 决定。

### 11.2 Multi 页 `ui/WidgetMulti.ui` → `Ui_Form`

```
gridLayout (QGridLayout, 732×542)
├── (0,1) verticalSpacer_2      垂直弹簧
├── (1,0) horizontalSpacer      左侧弹簧
├── (1,1) label_MultiOutput     【结果框】36pt 文泉驿等宽微米黑，居中，
│                                 内联样式 rgba(20,20,20,255) + 2px #4A90E2 + 圆角 15 + padding 8
│                                 尺寸策略 Expanding/Expanding, horstretch 160
├── (1,2) verticalLayout_MultiQuantity （QVBoxLayout）
│     ├── pushButton_MultiQuantityUp    "增加" 18pt
│     ├── label_MultiQuantity           数量值 20pt 居中，NoContextMenu
│     └── pushButton_MultiQuantityDown  "减少" 18pt
├── (1,3) horizontalSpacer_2     右侧弹簧
├── (2,1) pushButton_Multi       "抽取" 24pt
└── (3,1) verticalSpacer         底部弹簧
```

### 11.3 Lift 页 `ui/WidgetLift.ui` → `Ui_Form`

```
gridLayout (QGridLayout, 732×542)
├── (0,1) verticalSpacer_2
├── (1,0) horizontalSpacer
├── (1,1) label_LiftOutput      【结果框】36pt 居中，样式同 Multi
├── (1,2) verticalLayout_LiftQuantity
│     ├── pushButton_LiftQuantityUp    "增加" 18pt
│     ├── label_LiftQuantity           20pt 居中，NoContextMenu
│     └── pushButton_LiftQuantityDown  "减少" 18pt
├── (1,3) horizontalSpacer_2
├── (2,1) pushButton_Lift        "抽取" 24pt
├── (2,2) pushButton_LiftRenew   "刷新" 18pt   ← 对应「重置」
└── (3,1) verticalSpacer
```

### 11.4 ScrollSingle 页 `ui/WidgetScrollSingle.ui` → `Ui_Form`

```
gridLayout_2 (QGridLayout, 734×539)
├── (0,1) verticalSpacer            顶部弹簧
├── (1,0) horizontalSpacer          左侧弹簧（MinimumExpanding）
├── (1,1) label_ScrollSingleOutput 【滚动显示框】36pt 居中
├── (1,2) horizontalSpacer_2        右侧弹簧（MinimumExpanding）
├── (2,1) verticalSpacer_3          中部弹簧
├── (3,1) horizontalLayout_2 （QHBoxLayout）
│     ├── pushButton_ScrollSingleStart  "开始" 24pt
│     └── pushButton_ScrollSingleStop   "停止" 24pt
└── (4,1) verticalSpacer_2          底部弹簧
```

### 11.5 ScrollMulti 页 `ui/WidgetScrollMulti.ui` → `Ui_Form`

> 由 `WidgetMulti.ui` **最小修改**而来：整体网格、字体、边框、配色与 Multi 完全一致；
> 仅把结果框、数量控件与动作按钮更名为 ScrollMulti 前缀。多个「转盘」共用同一个结果框，
> 不新增子控件。

```
gridLayout (QGridLayout, 732×542)
├── (0,1) verticalSpacer_2              垂直弹簧
├── (1,0) horizontalSpacer              左侧弹簧
├── (1,1) label_ScrollMultiOutput       【结果框】36pt 居中，样式同 Multi
│                                         尺寸策略 Expanding/Expanding, horstretch 160
├── (1,2) verticalLayout_ScrollMultiQuantity
│     ├── pushButton_ScrollMultiQuantityUp    "增加" 18pt
│     ├── label_ScrollMultiQuantity           数量值 20pt 居中，NoContextMenu
│     └── pushButton_ScrollMultiQuantityDown  "减少" 18pt
├── (1,3) horizontalSpacer_2            右侧弹簧
└── (2,1) pushButton_ScrollMulti        "抽取" 24pt
```

### 11.6 控件对象名总表（代码引用索引）

| 对象名 | 类型 | 页面 | 引用位置 |
| --- | --- | --- | --- |
| `stackedWidget` | QStackedWidget | 主 | `_build_ui` / `_show_*_page` |
| `menu_file/mode/theme/language/roster/about/log_level` | QMenu | 主 | `_retranslate` / 各菜单构建 |
| `action_Multi / Lift / ScrollSingle / ScrollMulti` | QAction | 主 | `_bind_menu_actions` |
| `action_inputconfig / outputconfig / reinputconfig / exit` | QAction | 主 | `_bind_menu_actions` |
| `action_license / repository / help / program_log` | QAction | 主 | `_bind_menu_actions` |
| `label_MultiOutput` | QLabel | Multi | `_handle_multi` / `_retranslate` |
| `label_MultiQuantity` | QLabel | Multi | `_set_quantity_label` |
| `pushButton_Multi` | QPushButton | Multi | `_handle_multi` |
| `pushButton_MultiQuantityUp / Down` | QPushButton | Multi | `_adjust_quantity("multi")` |
| `label_LiftOutput` | QLabel | Lift | `_handle_lift` / `_reset_lift_page` |
| `label_LiftQuantity` | QLabel | Lift | `_set_quantity_label` |
| `pushButton_Lift` | QPushButton | Lift | `_handle_lift` |
| `pushButton_LiftQuantityUp / Down` | QPushButton | Lift | `_adjust_quantity("lift")` |
| `pushButton_LiftRenew` | QPushButton | Lift | `_reset_lift_page` |
| `label_ScrollSingleOutput` | QLabel | Scroll | `ScrollController` |
| `pushButton_ScrollSingleStart / Stop` | QPushButton | Scroll | `ScrollController` |
| `label_ScrollMultiOutput` | QLabel | ScrollMulti | `ScrollMultiController` / `_retranslate` |
| `label_ScrollMultiQuantity` | QLabel | ScrollMulti | `_set_quantity_label` |
| `pushButton_ScrollMulti` | QPushButton | ScrollMulti | `ScrollMultiController` |
| `pushButton_ScrollMultiQuantityUp / Down` | QPushButton | ScrollMulti | `_adjust_quantity("scrollmulti")` |
| `label_SingleOutput` | — | — | **已废弃**，仅存在于 `ThemeManager` 样式表选择器 |

### 11.7 样式表优先级实测结论

`.ui` 中为结果框与按钮**内联**了硬编码样式（`setStyleSheet` 作用在控件自身），
而 `ThemeManager` 生成的是 `QApplication` 级样式表。

实测（offscreen 渲染）：

```
控件内联样式 background-color : rgba(20, 20, 20, 255)   ← #141414（内联生效）
主题样式     background-color : rgba(56, 40, 59, 238)   ← 被覆盖
```

**结论**：按 Qt 样式表优先级，**控件自身样式表优先于应用级样式表**，
因此主题中的 `display_*` 与 `button*` 颜色对三个结果框和三个页面按钮**不生效**；
主题实际影响范围为：主窗口/页面底色（`background`）、文字色（`foreground`）、
状态栏（`panel`）、菜单栏与菜单选中色（`accent`）、
以及**菜单栏与状态栏**区域的 `border`/`button` 相关项。

---

## 12. 国际化键位全表

`ENGLISH` 常量共 **61 键**；`language.toml` 的三个语言包均覆盖全部键。
文案中的 `{...}` 为 Python `str.format` 占位符，翻译时**必须保留**。

| 键名 | 英文 (en_US) | 简体中文 (zh_CN) | 正體中文 (zh_TW) |
| --- | --- | --- | --- |
| `menu.file` | File | 文件 | 檔案 |
| `menu.mode` | Mode | 模式 | 模式 |
| `menu.theme` | Theme | 主题 | 主題 |
| `menu.language` | Language | 语言 | 語言 |
| `menu.roster` | Roster | 名单 | 名單 |
| `menu.about` | About | 关于 | 關於 |
| `menu.log_level` | Log level | 日志等级 | 記錄等級 |
| `action.import` | Import memory... | 导入记忆... | 匯入記憶... |
| `action.export` | Export memory... | 导出记忆... | 匯出記憶... |
| `action.reload` | Refresh application data | 刷新程序状态 | 重新整理程式狀態 |
| `action.exit` | Exit | 退出 | 離開 |
| `action.license` | License | 许可证 | 授權條款 |
| `action.repository` | Source repository | 项目仓库 | 專案原始碼 |
| `action.help` | Help | 帮助 | 說明文件 |
| `action.program_log` | Program log | 程序日志 | 程式日誌 |
| `action.close` | Close | 关闭 | 關閉 |
| `mode.multi` | Multi draw | 多抽 | 多抽 |
| `mode.lift` | Elimination draw | 减量抽 | 減量抽 |
| `mode.scroll` | Rolling single draw | 滚动单抽 | 滾動單抽 |
| `mode.scrollmulti` | Scroll multi draw | 滚动多抽 | 滾動多抽 |
| `button.draw` | Draw | 抽取 | 抽取 |
| `button.increase` | Increase | 增加 | 增加 |
| `button.decrease` | Decrease | 减少 | 減少 |
| `button.reset` | Reset | 重置 | 重設 |
| `button.start` | Start | 开始 | 開始 |
| `button.stop` | Stop | 停止 | 停止 |
| `button.stop_scrollmulti` | Stop (`{remaining}`/`{total}`) | 停止（`{remaining}`/`{total}`） | 停止（`{remaining}`/`{total}`） |
| `state.waiting` | Ready | 等待输入 | 等待輸入 |
| `state.multi_result` | Draw complete: `{count}` | 抽取完成：`{count}` 人 | 抽取完成：`{count}` 人 |
| `state.lift_result` | Elimination draw complete: `{count}` | 减量抽完成：`{count}` 人 | 減量抽完成：`{count}` 人 |
| `state.scrollmulti_result` | Scroll multi draw complete: `{count}` | 滚动多抽完成：`{count}` 人 | 滾動多抽完成：`{count}` 人 |
| `state.no_result` | No result | 暂无结果 | 暫無結果 |
| `state.roster_changed` | Roster: `{name}` | 名单：`{name}` | 名單：`{name}` |
| `state.theme_changed` | Theme: `{name}` | 主题：`{name}` | 主題：`{name}` |
| `state.language_changed` | Language: `{name}` | 语言：`{name}` | 語言：`{name}` |
| `state.startup_warning` | Startup used fallback data: `{files}` | 已使用备用数据启动：`{files}` | 已使用備援資料啟動：`{files}` |
| `state.startup_error` | Required application files are missing: `{files}` | 缺少必要程序文件：`{files}` | 缺少必要程式檔案：`{files}` |
| `state.scrollmulti_invalid` | Draw count exceeds roster size; drawing `{count}` instead | 抽取人数超过总人数，已按 `{count}` 人抽取 | 抽取人數超過總人數，已按 `{count}` 人抽取 |
| `dialog.import_title` | Import memory | 导入记忆 | 匯入記憶 |
| `dialog.export_title` | Export memory | 导出记忆 | 匯出記憶 |
| `dialog.json_filter` | JSON Files (`*.json`);;All Files (`*`) | JSON 文件 (`*.json`);;所有文件 (`*`) | JSON 檔案 (`*.json`);;所有檔案 (`*`) |
| `dialog.import_done` | Memory imported. | 记忆已导入。 | 記憶已匯入。 |
| `dialog.export_done` | Memory exported. | 记忆已导出。 | 記憶已匯出。 |
| `dialog.import_success` | Memory imported: `{path}` | 已导入记忆：`{path}` | 已匯入記憶：`{path}` |
| `dialog.export_success` | Memory exported: `{path}` | 已导出记忆：`{path}` | 已匯出記憶：`{path}` |
| `dialog.operation_failed` | Operation failed: `{error}` | 操作失败：`{error}` | 操作失敗：`{error}` |
| `state.no_logs` | No log entries have been recorded in this session. | 本次启动尚无日志记录。 | 本次啟動尚無日誌記錄。 |
| `state.log_level_changed` | Log level: `{level}` | 日志等级：`{level}` | 記錄等級：`{level}` |
| `log.DEBUG` | Debug | 调试 | 除錯 |
| `log.INFO` | Information | 信息 | 資訊 |
| `log.WARNING` | Warning | 警告 | 警告 |
| `log.ERROR` | Error | 错误 | 錯誤 |
| `log.CRITICAL` | Critical | 严重错误 | 嚴重錯誤 |
| `error.license_missing` | The license file is missing: `{path}` | 许可证文件不存在：`{path}` | 授權檔案不存在：`{path}` |
| `error.open_license` | Could not open the license: `{error}` | 无法打开许可证：`{error}` | 無法開啟授權條款：`{error}` |
| `error.open_repository` | Could not open the repository: `{error}` | 无法打开项目仓库：`{error}` | 無法開啟專案原始碼：`{error}` |
| `error.window_init` | Could not initialize the main window: `{error}` | 无法初始化主窗口：`{error}` | 無法初始化主視窗：`{error}` |
| `error.controls_init` | Could not initialize the interface: `{error}` | 无法初始化界面：`{error}` | 無法初始化介面：`{error}` |
| `error.open_help` | Could not open the help file: `{path}` | 无法打开帮助文档：`{path}` | 無法開啟說明文件：`{path}` |
| `error.help_missing` | The help file is missing: `{path}` | 帮助文档不存在：`{path}` | 說明文件不存在：`{path}` |
| `error.theme_failed` | Could not apply the theme: `{error}` | 无法应用主题：`{error}` | 無法套用主題：`{error}` |

**未被使用的键**（已定义但当前代码未引用）：
`state.startup_error`、`dialog.import_done`、`dialog.export_done`、`error.open_help`。

**未被国际化的硬编码文案**（见第 16 章）：
- 启动阶段致命错误的弹窗标题与正文（`main()` 中 `"Startup check failed"`、`"Startup failed"` 等英文串）。
- 数据校验失败等处的 `logging`/`StateManager.log` 说明文字。
- 已国际化的旧硬编码已消除：主题加载失败改用 `error.theme_failed`，无结果改用 `state.no_result`，
  `_reset_lift_page`/`ScrollController.reset` 改用 `state.waiting`，`_retranslate` 改用 `scroll_has_result` 布尔量
  （不再依赖 `"滚动抽取"/"等待输入"/"Ready"` 字面量集）。
- `ScrollMultiController` 的所有按钮/占位文案均由 `main.py` 以 `_t(...)` 注入，无硬编码。

---

## 13. 日志与等级过滤

### 13.1 双通道日志

| 通道 | 去向 | 格式 | 生命周期 |
| --- | --- | --- | --- |
| Python `logging` 通道 | 根记录器 → 控制台 + `_SessionLogHandler` | `%(asctime)s [%(levelname)s] %(message)s` | 本进程 |
| `StateManager.log()` 通道 | `SESSION_LOG_RECORDS` + `doc/log.log` | `time=… level=… action=… [result=…] [error=…]` | 本进程 + 追加持久化 |

`StateManager.log()` **不经由** `logging` 框架，因此是独立过滤：
只有 `数值(等级) >= 数值(CURRENT_LOG_LEVEL)` 时才写入。

### 13.2 等级过滤矩阵

| 当前等级 | DEBUG | INFO | WARNING | ERROR | CRITICAL |
| --- | --- | --- | --- | --- | --- |
| DEBUG | ✅ | ✅ | ✅ | ✅ | ✅ |
| INFO | ❌ | ✅ | ✅ | ✅ | ✅ |
| WARNING | ❌ | ❌ | ✅ | ✅ | ✅ |
| ERROR | ❌ | ❌ | ❌ | ✅ | ✅ |
| CRITICAL | ❌ | ❌ | ❌ | ❌ | ✅ |

`configure_logging` 同时设置根记录器级别与 `_SessionLogHandler` 级别，
故 `logging.info(...)` 等调用与 `StateManager.log(...)` 遵循同一阈值。

### 13.3 关键 `action` 标识汇总

| action | 来源 | result / error 内容 |
| --- | --- | --- |
| `load_config` | `StateManager.load_config` | 实际读取的文件名 / 解析错误 |
| `load_rosters` | `StateManager.load_rosters` | 解析错误 |
| `startup_fallback` | `main()` | 触发回退的文件或原因（每条一行） |
| `reload_fallback` | `_on_reload_config` | 逗号拼接的全部警告 |
| `theme` | `_select_theme` | 生效主题键 / 错误 |
| `log_level_changed` | `_select_log_level` | 新等级 |
| `Multi` / `Lift` | `_handle_multi` / `_handle_lift` | 完整结果字典 / 错误 |
| `ScrollSingle` | `_on_scroll_result` | `{name, meta}` / 错误 |
| `open_document` | `_show_document` | 文档文件名 |
| `read_document` | `_show_document` | 路径与读取错误 |
| `import_memory` / `export_memory` | `StateManager` | 目标/源路径 |

---

## 14. 容错与降级矩阵

### 14.1 启动阶段降级链

| 数据 | 首选 | 二级回退 | 三级回退 | 是否阻断启动 |
| --- | --- | --- | --- | --- |
| 主配置 | `config/config.toml` | `.config.default.toml` | `BUILTIN_CONFIG`（深拷贝） | 否，仅警告 |
| 名单 | `config/name.toml` 中有效组 | `.name.default.toml` 中有效组 | 内建 1 人名单 | 否，仅警告 |
| 主题 | `config/theme.toml` 中 `[themes.*]` | `BUILTIN_THEME`（`randname-dark`） | — | 否，仅警告 |
| 语言 | `config/language.toml` 中 `[languages.*]` | 内建 `ENGLISH`（`en_US`） | — | 否，仅警告 |
| 应用图标 | `assets.icon` | `QIcon` 空对象 → 状态栏警告 | — | 否 |
| 启动画面 | `assets.splash_image` | 跳过启动画面 + 警告 | — | 否 |
| 帮助文档 | `help_<当前语言>.md` | `doc/help_en_US.md` | 弹窗 `error.help_missing` | 否，弹窗 |
| 许可证 | `paths.license_file` | 弹窗 `error.license_missing` | — | 否，弹窗 |
| **程序组件**（`lib/*`） | 正常导入 | — | — | **是，弹窗并 `return 1`** |

### 14.2 运行期异常处理

| 场景 | 处理方式 |
| --- | --- |
| 主窗口骨架构建失败 | `logging.exception` + `critical(error.window_init)`，窗口为空壳但进程存活 |
| 菜单/页面构建失败 | `logging.exception` + `critical(error.controls_init)`，已建部分保留 |
| `stackedWidget` 缺失 | `RuntimeError("未找到 stackedWidget")` → 同上 |
| ScrollSingle 初始化失败 | 仅 `logging.exception`，**其余两个页面完全可用** |
| 单次抽取异常 | 输出「操作失败：…」+ `critical(mode.*)` + `log("ERROR", 模式)` |
| 记忆写入失败 | 仅 `logging.exception("记录 xxx 结果失败")`，抽取结果仍显示 |
| 日志写入失败（`OSError`） | 静默吞掉，**日志永不阻断抽取** |
| 日志写入失败（`log()` 内部） | `except Exception: pass` |
| 主题颜色非法 | `log("ERROR","theme")` + `critical("主题加载失败", 错误)` |
| 记忆文件损坏 | `load_memory()` 返回默认结构，不报错 |
| 导入非 JSON 对象 | `raise ValueError` → 弹窗 `dialog.operation_failed` |
| 清单为空 / 名单项非法 | 静默跳过该项，不中断整体加载 |

---

## 15. 构建与发布

### 15.1 构建前置：`.ui` → Python

五个界面在**构建期**由 `pyside6-uic` 编译，运行时不再读取 `.ui`（避免 `QtUiTools` 依赖）：

```
pyside6-uic ui/Main.ui            → lib/ui_main.py
pyside6-uic ui/WidgetMulti.ui     → lib/ui_widgetmulti.py
pyside6-uic ui/WidgetLift.ui      → lib/ui_widgetlift.py
pyside6-uic ui/WidgetScrollSingle.ui → lib/ui_widgetscrollsingle.py
pyside6-uic ui/WidgetScrollMulti.ui  → lib/ui_widgetscrollmulti.py
```

### 15.2 `build_linux.sh`

```
① 安装依赖：pip install --upgrade pip ; pip install nuitka==4.1.3 PySide6==6.11.1
② mkdir -p lib
③ pyside6-uic 编译五个界面（见上）
④ nuitka --standalone --enable-plugin=pyside6 \
       --include-data-file=ui/randname1.png=ui/randname1.png \
       --include-data-file=ui/randname-start_v3.6.png=ui/randname-start_v3.6.png \
       --include-data-file=.config.default.toml=.config.default.toml \
       --include-data-file=.name.default.toml=.name.default.toml \
       --include-data-dir=config=config \
       --include-data-dir=doc=doc \
       --output-dir=build --output-filename=randname \
       --show-progress --lto=yes --assume-yes-for-downloads \
       --nofollow-import-to=PySide6.{QtDesigner,QtUiTools,QtNetwork,QtSql,QtTest,QtXml} \
       main.py
⑤ 输出：build/main.dist/randname（standalone 可执行文件）
```

### 15.3 `build_windows.bat`

与 Linux 版一致，差异点：

- `--windows-icon-from-ico=ui\randname1.ico`（使用 `.ico` 而非 `.png`）
- `--windows-disable-console`（双击运行不弹控制台窗口）
- `pip install ... || echo "..."`（失败不中断，便于离线环境手工装）
- 结束 `pause`（保持控制台可见）

**顺序差异**：Windows 脚本**先编译 UI 再安装依赖**，Linux 脚本**先安装依赖再编译 UI**。

### 15.4 手工打包

```
Linux:  cd build ; mv main.dist randname3 ; tar -cavf randname3_linux.tar.xz randname3
```

### 15.5 CI/CD `.github/workflows/BuildAndRelease.yml`

```
触发：push 到 main 分支，或 workflow_dispatch 手动触发

Job 1  extract-version (ubuntu-latest)
  ├─ checkout (fetch-depth: 1)
  ├─ 提交信息含 "[upgrade]" ? 否 → should_build=false，跳过全部构建
  └─ grep -oP '^\d+\.\d+\.\d+(?=\[upgrade\])' 提取版本号
     （提交信息格式约定：3.1.2[upgrade]_描述）

Job 2  build-linux (needs extract-version)
  ├─ Python 3.12.10 + pip cache
  ├─ actions/cache 还原 ~/.cache/nuitka
  ├─ apt 安装 Qt6 依赖 + xcb 组件 + zstd + patchelf
  ├─ pip install nuitka==4.1.3 PySide6==6.11.1
  ├─ pyside6-uic 编译四个界面
  ├─ nuitka --standalone 同 15.2
  ├─ 校验输出目录（兼容 main.dist 与 randname.dist 两种命名）
  ├─ cp -r $DIST_DIR randname-${VERSION}
  ├─ tar -caf randname-${VERSION}.linux.x64.tar.xz
  └─ upload-artifact（name: linux-package）

Job 3  build-windows (needs extract-version, windows-latest, x64)
  ├─ env NUITKA_ASSUME_YES_FOR_DOWNLOADS=1      ← 避免下载交互卡死
  ├─ Python 3.12.10 + pip cache + Nuitka cache（AppData 路径）
  ├─ pyside6-uic 编译四个界面
  ├─ nuitka 同 15.3（含 --windows-icon-from-ico 与 --windows-disable-console）
  ├─ 校验 dist 目录 + 断言 randname.exe 存在（不存在则打印全部内容后 exit 1）
  ├─ 列出 Qt*.dll / icu*.dll / 全部 *.dll 计数
  ├─ choco install 7zip ; Copy-Item 复制为 randname-${VERSION}
  ├─ 拒绝打空包（源文件数为 0 则 exit 1）
  ├─ 7z a -t7z randname-${VERSION}.windows.x64.7z
  └─ upload-artifact（name: windows-package）

Job 4  release (needs [extract-version, build-linux, build-windows])
  ├─ permissions: contents: write
  ├─ download-artifact（merge-multiple）
  ├─ 移动 *.tar.xz 与 *.7z 到工作区根
  └─ softprops/action-gh-release@v2
       tag_name = v${version} ; name = randname v${version}
       files   = 两个压缩包 ; draft=false ; prerelease=false
```

---

## 16. 实现细节与已知特癖

以下条目均为**源码实际行为**的客观记录，供维护与评审参考。

### 16.1 硬编码未国际化文案

| 位置 | 文案 | 说明 |
| --- | --- | --- |
| `main()` 启动致命错误 | `"Startup check failed"` / `"Startup failed"` 等 | 启动阶段弹窗，未国际化；其余运行期文案均已 `_t(...)` |
| `_select_theme` 异常分支 | `_t("error.theme_failed")` | 已国际化（原硬编码 `"主题加载失败"` 已移除） |
| `_format_output_result` 末尾 | `_t("state.no_result")` | 已国际化（原硬编码 `"暂无结果"` 已移除） |
| `_reset_lift_page` | `_t("state.waiting")` | 已国际化（原硬编码 `"等待输入"` 已移除） |
| `ScrollController.reset()` | `self.reset_text` 参数（默认「等待输入」） | 由 `main.py` 注入 `state.waiting`；`reset()` 在 `main.py` 中**未被调用** |
| `_retranslate` 滚动标签 | `self.scroll_has_result` 布尔量 | 不再依赖 `{"滚动抽取","等待输入","Ready"}` 字面量集（该判定易随译文失效） |

### 16.2 不可达 / 未使用的代码

| 项 | 说明 |
| --- | --- |
| `_startup_file_check` 的 `required` | 恒返回 `[]`，`main()` 的「Startup check failed」分支不可达 |
| `StateManager` 的 `CONFIG_SOURCE` / `CONFIG_FALLBACK_USED` | 被赋值但程序中**无任何读取点** |
| `StateManager.session_log_text()` | 仅被「关于 > 程序日志」使用（已使用） |
| `ThemeManager.available_themes()` / `load_theme()` | 定义后**无调用点** |
| `ScrollController.toggle()` / `reset()` | **无调用点**（按钮各自直连 `start` / `stop`） |
| `ScrollSingle` 模块的 `on_result` 双写 | `ScrollController.stop()` 已设一次，`MainWindow._on_scroll_result` 再设一次 |
| 国际化键 `state.startup_error` / `dialog.import_done` / `dialog.export_done` / `error.open_help` | 已定义但**无引用** |
| `ThemeManager` 样式表选择器 `QLabel#label_SingleOutput` | 单抽模式已废弃，该对象不存在 |
| `ThemeManager` 样式表选择器 `QLabel#label_ScrollMultiOutput` | 对应 `ScrollMultiController` 的输出框，**在用** |
| `lib/__pycache__/Single.*.pyc`、`ui_widgetsingle.*.pyc` | 已删除源文件的编译缓存残留 |

### 16.3 语义与命名

| 项 | 说明 |
| --- | --- |
| `Lift` 结果的 `quantity.Lift` | 值为 `len(剩余) - 抽取数`，即**本轮之后剩余人数**，而非「已提升数量」，命名易误解 |
| `Lift` 结果的 `alllist` | 直接引用传入的完整名单字典（未拷贝），随结果一起被 JSON 序列化写入记忆 |
| `Multi` / `Lift` / `ScrollMulti` 时间格式 | `"%Y-%m-%d-%H:%M:%S"`（**短横线**分隔） |
| `ScrollSingle` `meta.time` 格式 | `"%Y-%m-%d %H:%M:%S"`（**空格+冒号**） |
| `_now_iso()` 格式 | `"%Y-%m-%d %H:%M:%S"`（空格分隔，秒精度） |
| 各模式时间格式不统一 | 记忆文件中各结果的 `time` 字段解析方式不同 |

### 16.4 行为边界

| 项 | 说明 |
| --- | --- |
| Lift 数量上限 | `_adjust_quantity` 以**完整名单长度**为上限，而非剩余长度；剩余变少后点「抽取」会走「数量超出」分支显示「暂无结果」（`outdict={}`），需手动调小数量或点「重置」 |
| `_apply_memory_import` | `last_results` 中某模式为 `null` 时**跳过**该模式（`_remembered_text` 返回 `None`），不再显示字符串 `"None"` |
| `BUILTIN_CONFIG` 拷贝 | `load_config` 回退内建时用 `copy.deepcopy`，避免调用方改写嵌套表污染模块常量 |
| `importnames.reload_data()` vs 模块顶层 | 两者共用 `_names_for` 兜底：`names` 键存在但为空/非法时均回退到 `{"0": "Student 1"}` |
| `Memory` 导入 | 不恢复 `lift_current_dict`，因此减量抽的剩余状态**无法**通过导入记忆恢复 |
| `ScrollSingle` / `ScrollMulti` 速度 | `rate` 在构造时读取，「刷新程序状态」后 `update_rate()` 会重新应用新间隔，无需重启 |
| `ScrollSingle.update_names` | 名单未变化时不做任何事（含不重排顺序） |
| `ScrollController.stop()` 重复调用 | 未运行状态下再次点「停止」**静默返回**，不触发 `on_result`（避免写入伪造结果） |
| 主题样式覆盖范围 | 结果框/按钮的主题色由 `ThemeManager` 的 `QLabel#label_*` ID 选择器决定（ID 选择器优先级高于控件内联的 `QLabel` 元素选择器，见 11.7 实测） |
| 「模式」菜单 | 四个 `action` **未**归入 `QActionGroup`，可出现多选勾选态 |
| `Multi` / `Lift` 的 stdout | 每次抽取向控制台打印剩余键列表（教学/调试用途），Windows 版 `--windows-disable-console` 下不可见 |
| 导入/导出对话框 | 过滤器为 `dialog.json_filter`；导出默认文件名 `memory-export.json` |
| `state.startup_warning` 状态栏 | 使用 `showMessage(文本, 0)` → **永久显示**，直到下一次 `showMessage` 覆盖 |
| 无「保存状态」 | 记忆**仅在每次抽取/滚动停止后自动落盘**，无独立的「保存状态」动作 |

### 16.5 安全与隐私

- 不访问网络（唯一网络行为是用户主动点击「项目仓库」调用 `QDesktopServices.openUrl`）。
- 无任何凭据/密钥/遥测。
- `config/` 全程**只读**；可写范围仅 `doc/memory.json` 与 `doc/log.log`（路径可由 `paths` 配置）。
- 两者均已写入 `.gitignore`，不会被提交到 Git。

### 16.6 编码与格式约定

- 全部文本文件为 **UTF-8** + **LF** 换行。
- 配置与语言包均以 UTF-8 由 `tomllib` 直接解析（无 BOM）。
- 记忆 JSON 使用 `ensure_ascii=False`，中文原样存储。

---

## 17. 附录：完整函数索引

| # | 文件 | 函数 / 类 | 行号 | 职责 |
| --- | --- | --- | --- | --- |
| 1 | `main.py` | `_configured_path` | 56 | 配置路径解析（相对根 / 绝对） |
| 2 | `main.py` | `_bootstrap_config` | 63 | 启动早期配置引导与降级 |
| 3 | `main.py` | `_configured_size` | 79 | 固定 / 比例尺寸计算 |
| 4 | `main.py` | `_startup_file_check` | 94 | 可恢复文件体检 |
| 5 | `main.py` | `MainWindow.__init__` | 134 | 窗口初始化与状态字段 |
| 6 | `main.py` | `MainWindow._load_names` | 206 | 从 `importnames` 取姓名 |
| 7 | `main.py` | `MainWindow._apply_config_window` | 213 | 窗口尺寸与居中 |
| 8 | `main.py` | `MainWindow._build_ui` | 227 | 两段式界面构建 |
| 9 | `main.py` | `MainWindow._bind_menu_actions` | 262 | 11 个 QAction 信号绑定 |
| 10 | `main.py` | `MainWindow._build_theme_menu` | 299 | 主题菜单构建 |
| 11 | `main.py` | `MainWindow._build_language_menu` | 328 | 语言菜单构建 |
| 12 | `main.py` | `MainWindow._build_roster_menu` | 346 | 名单菜单构建 |
| 13 | `main.py` | `MainWindow._build_log_level_menu` | 367 | 日志等级菜单构建 |
| 14 | `main.py` | `MainWindow._select_log_level` | 385 | 切换日志等级 |
| 15 | `main.py` | `MainWindow._t` | 391 | 翻译快捷方法 |
| 16 | `main.py` | `MainWindow._select_language` | 394 | 切换界面语言 |
| 17 | `main.py` | `MainWindow._select_roster` | 405 | 切换名单并作废减量抽状态 |
| 18 | `main.py` | `MainWindow._retranslate` | 425 | 全量文案刷新 |
| 19 | `main.py` | `MainWindow._select_theme` | 471 | 应用主题 |
| 20 | `main.py` | `MainWindow._load_pages` | 487 | 三页构建 + 默认页 |
| 21 | `main.py` | `MainWindow._bind_page_actions` | 520 | 页面控件信号绑定 |
| 22 | `main.py` | `MainWindow._show_multi_page` | 583 | 切到 Multi 页 |
| 23 | `main.py` | `MainWindow._show_lift_page` | 587 | 切到 Lift 页 |
| 24 | `main.py` | `MainWindow._show_scrollsingle_page` | 591 | 切到 ScrollSingle 页 |
| 25 | `main.py` | `MainWindow._on_import_memory` | 595 | 导入记忆 |
| 26 | `main.py` | `MainWindow._on_export_memory` | 614 | 导出记忆 |
| 27 | `main.py` | `MainWindow._on_reload_config` | 635 | 刷新全部程序数据 |
| 28 | `main.py` | `MainWindow._apply_memory_import` | 707 | 导入后回填标签 |
| 29 | `main.py` | `MainWindow._handle_multi` | 734 | 多抽执行 + 记忆 + 日志 |
| 30 | `main.py` | `MainWindow._handle_lift` | 762 | 减量抽执行 + 记忆 + 日志 |
| 31 | `main.py` | `MainWindow._on_scroll_result` | 801 | 滚动抽结果回调 |
| 32 | `main.py` | `MainWindow._adjust_quantity` | 820 | 数量加减与夹紧 |
| 33 | `main.py` | `MainWindow._reset_lift_page` | 831 | 减量抽重置 |
| 34 | `main.py` | `MainWindow._set_quantity_label` | 841 | 数量标签写入 |
| 35 | `main.py` | `MainWindow._set_output_text` | 845 | 输出标签写入 |
| 36 | `main.py` | `MainWindow._format_output_result` | 849 | 结果排版（每行 4 人） |
| 37 | `main.py` | `MainWindow._on_exit` | 892 | 退出程序 |
| 38 | `main.py` | `MainWindow._open_help` | 898 | 打开帮助文档 |
| 39 | `main.py` | `MainWindow._show_document` | 913 | 通用文档对话框 |
| 40 | `main.py` | `MainWindow._show_program_log` | 948 | 显示会话日志 |
| 41 | `main.py` | `MainWindow._open_license` | 964 | 打开许可证 |
| 42 | `main.py` | `MainWindow._open_repository` | 981 | 打开项目仓库 |
| 43 | `main.py` | `MainWindow._show_error` | 998 | 错误弹窗 |
| 44 | `main.py` | `main` | 1002 | 程序入口主流程 |
| 45 | `lib/StateManager.py` | `_now_iso` | 50 | ISO 时间戳 |
| 46 | `lib/StateManager.py` | `configure_paths` | 54 | 应用记忆/日志路径 |
| 47 | `lib/StateManager.py` | `_SessionLogHandler.emit` | 74 | 写会话列表 + 持久日志 |
| 48 | `lib/StateManager.py` | `configure_logging` | 84 | 设置并归一日志等级 |
| 49 | `lib/StateManager.py` | `session_log_text` | 107 | 会话日志文本 |
| 50 | `lib/StateManager.py` | `_default_memory` | 112 | 默认记忆结构 |
| 51 | `lib/StateManager.py` | `log` | 123 | 结构化单行日志 |
| 52 | `lib/StateManager.py` | `_log_value` | 150 | 日志值单行化 |
| 53 | `lib/StateManager.py` | `load_memory` | 156 | 读记忆（容错） |
| 54 | `lib/StateManager.py` | `save_memory` | 168 | 写记忆 |
| 55 | `lib/StateManager.py` | `export_memory` | 172 | 导出记忆 |
| 56 | `lib/StateManager.py` | `import_memory` | 180 | 导入记忆 + 回调 |
| 57 | `lib/StateManager.py` | `load_config` | 192 | 读主配置（三级降级） |
| 58 | `lib/StateManager.py` | `load_rosters` | 219 | 读名单（三级降级） |
| 59 | `lib/importnames.py` | `select_roster` | 22 | 切换名单 |
| 60 | `lib/importnames.py` | `reload_data` | 32 | 全量重载 |
| 61 | `lib/ThemeManager.py` | `discover_themes` | 38 | 发现主题 + 解析默认 |
| 62 | `lib/ThemeManager.py` | `available_themes` | 80 | 排序主题键（未使用） |
| 63 | `lib/ThemeManager.py` | `resolve_startup_theme` | 84 | 启动主题优先级链 |
| 64 | `lib/ThemeManager.py` | `load_theme` | 103 | 单主题读取（未使用） |
| 65 | `lib/ThemeManager.py` | `_color` | 107 | 颜色格式 → rgba() |
| 66 | `lib/ThemeManager.py` | `_stylesheet` | 135 | 生成 QSS |
| 67 | `lib/ThemeManager.py` | `apply_theme` | 180 | 应用主题并返回实际键 |
| 68 | `lib/LanguageManager.py` | `load_languages` | 72 | 加载语言包 + 合并英文基底 |
| 69 | `lib/LanguageManager.py` | `system_language` | 101 | 系统语言匹配 |
| 70 | `lib/LanguageManager.py` | `resolve_language` | 112 | 语言有效性解析 |
| 71 | `lib/LanguageManager.py` | `resolve_startup_language` | 118 | 启动语言优先级链 |
| 72 | `lib/LanguageManager.py` | `translate` | 133 | 三层回退翻译 + 格式化 |
| 73 | `lib/LanguageManager.py` | `localized_name` | 142 | 主题/名单多语言名称 |
| 74 | `lib/Multi.py` | `Multi` | 28 | 多抽算法 |
| 75 | `lib/Lift.py` | `Lift` | 38 | 减量抽算法 |
| 76 | `lib/ScrollSingle.py` | `ScrollController.__init__` | 29 | 控制器构造与按钮绑定 |
| 77 | `lib/ScrollSingle.py` | `ScrollController._now_str` | 75 | 时间戳 |
| 78 | `lib/ScrollSingle.py` | `ScrollController._prepare_new_order` | 78 | 洗牌并生成滚动序列 |
| 79 | `lib/ScrollSingle.py` | `ScrollController._tick` | 85 | 定时器单步 |
| 80 | `lib/ScrollSingle.py` | `ScrollController.start` | 96 | 开始滚动 |
| 81 | `lib/ScrollSingle.py` | `ScrollController.stop` | 111 | 停止并产出结果 |
| 82 | `lib/ScrollSingle.py` | `ScrollController.toggle` | 144 | 启停切换（未使用） |
| 83 | `lib/ScrollSingle.py` | `ScrollController.reset` | 150 | 视觉重置（未使用） |
| 84 | `lib/ScrollSingle.py` | `ScrollController.update_names` | 160 | 热替换姓名池 |
| 85 | `lib/ScrollSingle.py` | `ScrollController.set_button_texts` | 168 | 按钮文案刷新 |

---

**文档结束。** 共覆盖 5 个源模块、4 个界面、4 份配置文件、3 份帮助文档、2 个构建脚本与 1 条 CI 流水线，
全部 85 个函数/方法已逐一给出中文伪代码。
