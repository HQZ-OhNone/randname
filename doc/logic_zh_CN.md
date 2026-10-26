# randname 业务逻辑说明（简体中文）

Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; see the GNU General Public License for more details.

本文记录 randname 3.10.3 的实际业务逻辑、隐藏机制和容易踩坑的边界。英文版见
`logic_en_US.md`，正體中文版见 `logic_zh_TW.md`。

## 1. 术语与模式

| 内部标识 | 简体界面 | 繁體界面 | English | 页面 |
| --- | --- | --- | --- | --- |
| `Multi` | 多抽 | 多抽 | Multi | 多抽页面 |
| `Single` | 单抽 | 單抽 | Single | 多抽页面（数量 1） |
| `Lift` | 减量抽 | 減量抽 | Lift | 减量抽页面 |
| `ScrollMulti` | 滚动多抽 | 滾動多抽 | ScrollMulti | 滚动多抽页面 |
| `ScrollSingle` | 滚动单抽 | 滾動單抽 | ScrollSingle | 滚动多抽页面（数量 1） |
| `ScrollLift` | 滚动减量抽 | 滾動減量抽 | ScrollLift | 滚动减量抽页面 |

- “单抽”和“滚动单抽”只是菜单快捷方式，不创建独立控制器或页面。
- 内部结果、日志和记忆仍使用 `Multi`、`Lift`、`ScrollMulti`、`ScrollLift` 作为 `mode` 字段。
- 用户可见文本不再出现裸 `ScrollMulti` 等内部标识。

## 2. 文件与职责

| 路径 | 职责 |
| --- | --- |
| `main.py` | 启动、主窗口、菜单、状态栏、页面切换、记忆回填、查看器入口 |
| `lib/version.py` | `APP_VERSION = "3.10.3"` |
| `lib/Multi.py` | 多抽算法 |
| `lib/Lift.py` | 减量抽算法 |
| `lib/ScrollMulti.py` | 滚动多抽控制器 |
| `lib/ScrollLift.py` | 滚动减量抽控制器（继承 ScrollMultiController） |
| `lib/OutputView.py` | 非滚动输出框自适应；滚动模式固定格子 `SlotOutputView` |
| `lib/TextViewer.py` | 只读、实时刷新的帮助/许可证/日志查看器 |
| `lib/UpdateDialog.py` | 检查更新窗口、GitHub Releases 查询与版本比较 |
| `lib/StateManager.py` | 配置、记忆结果、日志 |
| `lib/importnames.py` | 启动时加载名单 |
| `lib/ThemeManager.py` | 主题读取、样式表 |
| `lib/BackgroundWidget.py` | 主题背景图、裁切、渐变模糊与阴影 |
| `lib/WindowTheme.py` | Windows 标题栏颜色 |
| `lib/LanguageManager.py` | 语言包、翻译、回退 |
| `ui/*.ui` | Qt Designer 源文件 |
| `lib/ui_*.py` | `pyside6-uic` 编译产物，构建前重新生成 |
| `config/config.toml` | 主配置 |
| `config/name.toml` | 名单 |
| `config/theme.toml` | 主题 |
| `config/language.toml` | 语言包 |
| `doc/memory.json` | 各模式最近结果（仅用于导出/导入） |
| `doc/log.log` | 持久日志 |
| `doc/logic_*.md` | 本业务逻辑文档 |

## 3. 启动流程

1. `main.py` 打印 GPL 横幅。
2. 创建 `QApplication`。
3. `_bootstrap_config()` 读取 `config/config.toml`；失败时读取 `.config.default.toml`，再失败使用内建配置。
4. 读取图标；创建启动画面。
5. 启动画面按 `[splash]` 的 `size_mode`/`screen_ratio`/`aspect_ratio` 缩放，保持宽高比。
6. `_draw_splash_version()` 在缩放后的图片右下角绘制 `v3.10.3`；字号始终按图片宽度的三分之一自动缩放，文字固定为纯白色，不提供字号或颜色配置。
7. `_startup_file_check()` 检查可恢复文件；缺失项加入启动警告。`required` 当前恒为空，因此“启动检查失败”分支不可达。
8. 导入 `lib` 模块。
9. 图标、启动图、帮助、许可证、日志与记忆路径固定于代码，不再有可配置路径段。
10. 不读取记忆偏好；每次启动都从配置档与独立配置档读取界面状态。
11. 日志等级：`[logging].level` > `INFO`；该等级只控制文件写入。
12. 主题：`theme.toml` 的 `default` > `config.toml` `app.theme`（旧键，兼容） > 主题目录第一项。
13. 语言：`language.toml` 的 `preferred` > `config.toml` `app.language`（旧键，兼容） > 系统语言 > `en_US`。
14. 名单：`config.toml` 的 `app.roster` > 名单目录第一项。
15. 模式：`config.toml` 的 `app.default_mode` > `Multi`；数量固定从 1 开始。
16. 创建 `MainWindow`，应用主题；主窗口是否立即显示取决于 `[splash].mode`。
17. `[splash].mode = 1` 时先只显示启动画面，剩余时间到后才显示主窗口并关闭启动画面；其他模式在主窗口准备好后立即显示并关闭启动画面。

## 4. 配置优先级

### 4.1 主题

```
theme.toml 的 default（有效）
  > config.toml [app].theme（旧键，兼容）
  > 主题目录第一项
```

### 4.2 语言

```
language.toml 的 preferred（有效）
  > config.toml [app].language（旧键，兼容）
  > 系统语言
  > en_US
```

### 4.3 其他

- 名单：`config.toml [app].roster` > 第一组名单。
- 模式：`config.toml [app].default_mode` > `Multi`。
- 日志等级：`config.toml [logging].level` > `INFO`。
- 数量：固定从 1 开始。
- 窗口：每次启动都由 `config.toml [window]` 计算初始尺寸，不读取记忆尺寸。

启动时不会从记忆文件恢复主题、名单、日志等级、模式、语言、数量或窗口尺寸。

## 5. 窗口尺寸与状态栏

### 5.1 初始尺寸

`_configured_size(section, screen_width, screen_height)`：

1. `size_mode = "fixed"` 且 `width`/`height` 为正整数：直接使用。
2. 否则读取 `screen_ratio`（默认 0.75，范围 0.05~1.0）和 `aspect_ratio`（默认 1.5）。
3. `width = screen_width * screen_ratio`。
4. `height = width / aspect_ratio`。
5. 若 `height > screen_height * screen_ratio`，则 `height = screen_height * screen_ratio`，`width = height * aspect_ratio`。
6. 结果转整数，至少为 1。

`size_mode = "maximum"` 时不计算上述尺寸；`_window_is_maximized()` 判断后只设置最小尺寸，并在 `reveal_window()` 中用 `showMaximized()` 显示主窗口。刷新配置时若可见，也会立即最大化。

启动画面使用相同算法，默认 `screen_ratio = 0.25`、`aspect_ratio = 2.0`。

启动画面关闭时机由 `[splash].mode` 决定：

- `mode = 0`：主窗口准备好后立即 `window.show()` 并关闭启动画面。
- `mode = 1`：只显示启动画面，等 `duration_ms - splash_timer.elapsed()` 到点后再 `window.show()` 并 `splash.finish(window)`。
- 延后显示主窗口是为了避开 Wayland：Wayland 不支持 `QSplashScreen` 置顶，主窗口一旦提前显示就会完全盖住启动画面。
- `_splash_wait_ms(mode, duration_ms, elapsed_ms)` 负责计算剩余毫秒数，其他模式返回 0。

### 5.2 拉伸与持久化

- `[window].resizable = true` 时允许用户拖动边缘；最小尺寸 640×480。
- `resizable = false` 时 `setFixedSize()`。
- 内容变化（长名字、导入记忆、滚动 tick、字号变化）不会改变窗口尺寸。
- 用户拉伸后，`resizeEvent` 启动 450ms 单次定时器；定时器触发时写入记忆。
- 窗口状态变化（最大化/还原）也触发保存。
- 关闭窗口时再次保存。
- 最大化时保存 `normalGeometry()` 的宽高和 `maximized: true`；还原时保存当前宽高和 `maximized: false`。
- 启动时记忆尺寸会被夹紧到当前屏幕可用区域，避免窗口超出屏幕。
- “文件 > 刷新程序状态”不重置当前窗口尺寸。

### 5.3 状态栏

- 左侧是 `QStatusBar.showMessage()` 临时消息。
- 右侧永久控件依次为：模式、名单、数量、主题、语言、日志等级、版本；每项前有 `|` 分隔符。
- `[statusbar]` 的 `show_*` 控制显示/隐藏。
- 切换模式、名单、数量、主题、语言、日志等级、刷新配置后调用 `_update_status_info()`。
- 版本来自 `lib/version.py`。

## 6. 输出框自适应

### 6.1 非滚动模式（OutputView）

`lib/OutputView.py` 包装一个 `QLabel`：

1. `setSizePolicy(Ignored, Ignored)`、`setMinimumSize(0, 0)`，防止 `QLabel.sizeHint()` 把窗口撑大。
2. 基准字号 `[ui].display_font_size`；下限 `display_min_font_size`；步长 `display_font_step`；行距 `display_line_spacing`；内边距 `display_padding`。
3. 显示姓名列表时按显示宽度贪婪分行，姓名之间两个空格，不会从姓名中间断开。
4. 先用基准字号尝试单行；单行放不下且高度足够时改为多行；仍放不下则逐步缩小字号。
5. 极端情况下单个姓名仍比结果框宽时，允许 Qt 在字符间换行，避免内容完全不可见。
6. `set_message()` 用于“等待输入”“暂无结果”等占位文案，始终使用基准字号。
7. `resizeEvent` 触发重新排版；用户拉伸窗口后自动重新选择单行/多行/字号。

### 6.2 滚动模式（SlotOutputView）

`SlotOutputView` 复用原输出 `QLabel` 作为背景容器，内部用 `_SlotGrid` 手动摆放子 `QLabel`：

1. `begin_round(pool, quantity)` 创建 `quantity` 个固定格子。
2. 第一次 `set_names()` 时计算布局并锁定：目标行数按 `round(sqrt(N * H / W))` 估算；比较所有栏数组合，优先字号最大，字号相同时选择最接近目标行数的配置。6 人、宽输出框通常为 2 行 × 3 列。
3. 每个格子等宽等高，文字水平/垂直居中；最后一行不足时整行居中。
4. 锁定后每次 tick 只更新格子文字，格子几何不变，已停止的名字不会移动。
5. 若当前姓名无法放进锁定格子，重新计算列数/行数/字号并再次锁定；这是布局唯一的变动时机。
6. `clear_round()`、下一轮 `start()`、更改数量、重置时清除锁定，下次抽取重新布局。
7. `set_message()` 显示占位文案；导入历史结果时按结果人数建立格子并计算一次布局。
8. ScrollMulti 与 ScrollLift 共用该视图。

## 7. 多抽（Multi）

`Multi.Multi(alllist, quantity)`：

1. 若 `quantity > len(alllist)`：`outdict = {}`，返回。
2. 否则从完整名单键中无放回随机抽取 `quantity` 个。
3. `outdict` 下标重排为 `"0"`, `"1"`, ...，每项为 `{"code": 原键, "name": 姓名}`。
4. 时间格式 `%Y-%m-%d-%H:%M:%S`（短横线分隔）。
5. 每次抽取都从完整名单开始，不消耗名单。

结果：

```json
{
  "mode": "Multi",
  "quantity": {"total": 9, "selected": 3},
  "time": "2026-10-18-12:00:00",
  "outdict": {
    "0": {"code": "1", "name": "张三"}
  }
}
```

## 8. 减量抽（Lift）

`Lift.Lift(alllist, Liftdict, quantity)`：

1. `Liftdict` 是当前剩余名单；首次为空时由 `MainWindow` 传入完整名单。
2. 若 `Liftdict` 为空或 `quantity > len(Liftdict)`：`outdict = {}`，`Liftdict` 原样返回，界面显示“暂无结果”。
3. 否则从 `Liftdict` 无放回抽取，`outdict` 每项为单键包裹 `{原键: 姓名}`（与 Multi 不同）。
4. `Liftdict` 更新为未抽中的人。
5. `quantity` 字段：
   - `total`：完整名单人数；
   - `wasted`：`total - len(抽取前 Liftdict)`；
   - `selected`：本次抽取数；
   - `Lift`：`len(抽取前 Liftdict) - selected`，即本轮之后剩余人数（命名容易误解）。
6. `alllist` 直接引用完整名单字典，会随结果写入记忆。
7. “重置”清空 `lift_current_dict`，下一次从完整名单开始；数量不变。
8. 切换名单或刷新后名单内容变化时，`lift_current_dict` 清空。

## 9. 滚动多抽（ScrollMulti）

`ScrollMultiController`：

- 构造时复制名单，`quantity` 默认 1，定时器间隔 `max(1, 1000 // rate)`。
- `start()`：
  1. 名单为空时调用 `on_warning(0)` 并返回。
  2. `total = min(quantity, len(names))`；请求数超过名单时警告。
  3. `pool = dict(names)`，为本轮建立共享池。
  4. 创建 `total` 个 reel，每个 reel 有独立随机顺序、当前索引、当前键/姓名。
  5. 调用 `view.begin_round(pool.values(), total)` 建立固定格子；第一次 tick 时锁定本轮布局与字号。
  6. 立即 `_tick()` 显示第一帧，再启动定时器。
- `_tick()`：
  - 对每个 active reel 取顺序中的下一个键；
  - 顺序用完则重新洗牌；
  - 若键已不在池中（快速点击造成的过期键），重新洗牌并跳过；
  - 更新 reel 的键/姓名；
  - 刷新输出框。
- `stop_next()`：
  1. 取第一个 active reel；
  2. 标记为 inactive；
  3. 若它当前键已被更早停止的 reel 占用，则从剩余池随机补一个；
  4. 从池中移除该键；
  5. 为所有仍 active 的 reel 重建顺序，保证不会再落到已固定名字；
  6. 刷新输出；
  7. 若没有 active reel，调用 `_finish()`；否则更新按钮文案。
- 按钮文案：运行中 `停止（剩余/总数）`，空闲 `抽取`。
- `_finish()`：停止定时器、置 `running = False`、构造结果、恢复按钮、回调 `on_result(result, meta)`。
- 结果：
  - `mode = "ScrollMulti"`；
  - `time` 短横线格式；
  - `quantity.total = len(names)`，`quantity.selected = total`；
  - `outdict` 按停止顺序 `"0"`, `"1"`, ...，每项 `{"code", "name"}`；
  - 同一轮 code 不重复。
- `show_result(result)`：从记忆恢复显示，不启动滚动；`outdict` 支持 `{"name","code"}` 和单键包裹两种旧格式。
- `update_names()`：名单变化时更新并重置；`update_rate()` 只改间隔；`set_quantity()` 在空闲时清除布局锁定，下一轮重新布局。

## 10. 滚动减量抽（ScrollLift）

`ScrollLiftController` 继承 `ScrollMultiController`，复用滚动/逐个停止逻辑，并增加“跨轮剩余池”：

- `lift_pool` 初始为完整名单。
- `start()`：
  1. `lift_pool` 为空时警告并返回；主窗口显示“剩余名单已空，请重置后继续”。
  2. `available = len(lift_pool)`；`total = min(quantity, available)`；请求数超过剩余时警告。
  3. 保存 `round_available = available`。
  4. 本轮池 `pool = dict(lift_pool)`。
  5. 创建 reel、锁定字号、启动定时器。
- 停止逻辑与 ScrollMulti 相同；本轮固定的人从 `pool` 移除。
- `_finish()`：先把 `lift_pool = dict(pool)`（本轮结束后剩余的人），再走父类完成逻辑。
- 结果：
  - `mode = "ScrollLift"`；
  - `quantity.total = len(names)`；
  - `quantity.wasted = total - round_available`；
  - `quantity.selected = total`；
  - `quantity.Lift = round_available - total`；
  - `outdict` 为本轮抽中者；
  - `alllist` 为完整名单；
  - `Liftdict` 为本轮之后剩余名单。
- `reset()`：恢复 `lift_pool = dict(names)`，清空输出，数量不变。
- `show_result()`：显示记忆结果；若存在 `Liftdict` 则恢复剩余池；旧记忆没有 `Liftdict` 时用完整名单减去 `outdict` 的 code 恢复。
- 切换名单/刷新后名单变化：`update_names()` 会重置剩余池。
- 导入记忆不会立即改变当前主题/语言；只恢复结果和剩余池。

## 11. 单抽与滚动单抽别名

- 菜单“单抽” → `_show_single_page()`：
  - `multi_quantity = 1`；
  - 更新数量标签；
  - 切到多抽页面。
- 菜单“滚动单抽” → `_show_scroll_single_page()`：
  - `scroll_multi_quantity = 1`；
  - 更新控制器数量；
  - 切到滚动多抽页面。
- `default_mode` 兼容：
  - `"Single"` → Multi 数量 1；
  - `"ScrollSingle"` → ScrollMulti 数量 1；
  - 其他非法值 → Multi。
- 不创建 `Single.py`、`ScrollSingle.py`、`WidgetScrollSingle.ui` 或对应页面。

## 12. 记忆文件

### 12.1 结构

```json
{
  "last_results": {
    "Multi": null,
    "Lift": null,
    "ScrollMulti": null,
    "ScrollLift": null
  }
}
```

- 记忆文件只保存各模式的最近结果，不再保存主题、名单、模式、语言、日志等级、数量或窗口尺寸。
- `last_results.*` 的运行期条目通常为 `{"result": ..., "meta": ...}`；Multi/Lift 使用 `{"result": ..., "time": ...}`。
- 写入使用 `json.dumps(..., ensure_ascii=False, indent=2)`，UTF-8。
- `save_memory()` 先写 `.tmp` 再 `replace()`，避免中断留下半个 JSON。
- 读取时 `_normalize_memory()` 只保留 `last_results`，丢弃旧的 `preferences` 与 `loaded_config`。
- 旧版 `ScrollSingle` 结果不再单独恢复；旧版 `last_results` 中的其他键会被忽略。

### 12.2 保存与导入

- 每次抽取/滚动停止后保存最近结果。
- 主题、名单、语言、日志等级、模式、数量和窗口尺寸变化都不再写入记忆文件。
- 导入/导出记忆不会写入 `config/`，也不会改变当前界面状态。
- 导入旧记忆文件时只恢复 `last_results`；其中的 `preferences`、`loaded_config` 会被忽略。
- 记忆文件损坏时回退到只含 `last_results` 的默认结构，不阻止程序启动。

## 13. 日志

- `StateManager.configure_logging(level)` 把根 logger 设为 DEBUG，并安装 `_SessionLogHandler`。
- `_SessionLogHandler` 始终把 Python logging 记录保存到 `SESSION_LOG_RECORDS`，再按所选等级写入 `doc/log.log`。
- `StateManager.log(level, action, result=None, error=None)` 写入精简单行：

```
time=2026-10-18 12:00:00 level=INFO action=Multi result=(...)
```

- 字段顺序固定：`time` → `level` → `action` → `result` → `error`。
- `StateManager.log()` 也会先写入 `SESSION_LOG_RECORDS`，再判断文件等级；因此日志窗口始终包含本次运行的全部等级。
- 日志查看器把会话记录渲染为 HTML，并给行首的 `level=...` 或 `[INFO]` 等级标记上色。
- `_log_value()` 把换行/制表符替换为空格，把 `{}[]` 替换为 `()`，保证严格单行。
- 日志等级低于当前等级时不写入。
- “关于 > 程序日志”读取日志文件，不是只读内存中的会话记录；因此可以看到程序启动以来的完整持久日志。
- 日志查看器每 `[viewer].refresh_ms` 毫秒检查一次文件修改时间/大小；文件追加、替换、删除都会刷新。

## 14. 内部文本查看器

`lib/TextViewer.py`：

- 帮助/许可证使用 `QTextBrowser` + `setMarkdown()`；日志使用 `QPlainTextEdit` + `setPlainText()`。
- 只读：`setReadOnly(True)`、禁用撤销/重做。
- 非模态：`setModal(False)`，可一边运行主程序一边查看。
- `QFileSystemWatcher` 监听文件和父目录；同时用 `QTimer` 轮询兜底。
- 刷新前记录滚动条位置；若原本在底部，刷新后自动跟随到底部；用户上滚后不强制跳到底部。
- 尺寸：
  - 使用父窗口所在屏幕的 `availableGeometry()`；
  - 宽高不超过 `available * max_screen_ratio`，再减 24px 边距；
  - 最大 900×680，最小尺寸按可用区域收缩；
  - 居中显示。
- 触屏：`QScroller.grabGesture(viewport, LeftMouseButtonGesture)`；滚动条宽 22px；关闭按钮最小高度 40px。
- 同一路径重复打开时激活已有窗口，不重复创建。
- 帮助/许可证文件内容变化时实时刷新，不需要重新打开。

## 15. 主题与语言

### 15.1 主题

- `config/theme.toml` 集中保存 `default` 与 `[themes.<键>]`。
- 每个主题含 `color_format`、`name`（多语言）和 `colors`。
- 支持 `HexA`、`Hex`、`RGBA`、`RGB`。
- `_stylesheet()` 生成全局 QSS：
  - 页面/控件背景、文字；
  - 输出框 ID 选择器：`label_MultiOutput`、`label_LiftOutput`、`label_ScrollMultiOutput`、`label_ScrollLiftOutput`；
  - 按钮正常/悬停/按下；
  - 菜单选中强调色；
  - 状态栏背景。
- ID 选择器优先级高于控件内联的 `QLabel` 元素选择器，因此主题色会覆盖 `.ui` 中的默认背景。
- 主题名按当前语言、系统语言、英语、主题键回退。

### 15.2 语言

- `config/language.toml` 的 `preferred` 是首次启动首选；旧 `app.language` 仅作为后备。
- `LanguageManager.ENGLISH` 是内建兜底包；语言文件缺失时仍可用英语。
- 翻译键缺失时回退到 `ENGLISH`，再回退键名。
- `{count}`、`{name}` 等占位符必须保留；格式化失败时返回原文。
- 切换语言立即刷新菜单、按钮、占位文案和状态栏，不清除当前结果。

## 16. UI 与菜单

- 主窗口：`ui/Main.ui` → `lib/ui_main.py`。
- 页面：
  - `ui/WidgetMulti.ui` → 多抽；
  - `ui/WidgetLift.ui` → 减量抽；
  - `ui/WidgetScrollMulti.ui` → 滚动多抽；
  - `ui/WidgetScrollLift.ui` → 滚动减量抽（比滚动多抽多一个“重置”按钮）。
- 四个数量页面在数量列右侧各有一个纵向 `QSlider`，范围 `1..len(names)`；`_prepare_quantity_slider()` 安装触控过滤器，`_set_quantity()` 统一同步数值、标签、滑条和滚动控制器。
- 文本窗口：`ui/TextViewer.ui` → `lib/ui_textviewer.py`；检查更新窗口：`ui/Update.ui` → `lib/ui_update.py`。
- 模式菜单顺序：单抽、多抽、减量抽、分隔线、滚动单抽、滚动多抽、滚动减量抽。
- 关于菜单：帮助、程序日志、检查更新、日志等级、分隔线、许可证、项目仓库、反馈。
- 仓库/反馈地址硬编码在 `main.py`：
  - `REPOSITORY_URL`
  - `FEEDBACK_URL`
- 配置文件中不再提供这两个网址。
- 模式 QAction 未归入 `QActionGroup`，可能出现多个勾选态；程序以当前页面/`current_mode` 为准。

## 17. 构建与发布

1. 用 `pyside6-uic` 遍历编译全部 `ui/*.ui`，文件名小写后输出为 `lib/ui_<name>.py`；新增 `.ui` 无需修改构建脚本。
2. Nuitka 打包时包含：
   - `ui/randname1.png`
   - `ui/randname-start.png`
   - `.config.default.toml`
   - `.name.default.toml`
   - `config/`
   - `doc/`
3. 旧文件 `WidgetScrollSingle.ui`、`ui_widgetscrollsingle.py`、`ScrollSingle.py`、`randname-start_v3.6.png`、`randname-start_v3.7.png` 已删除。
4. 版本号在 `lib/version.py`；提交信息使用 `3.10.1[upgrade]_...` 触发发布流程。检查更新使用 QtNetwork，构建时不再排除 `PySide6.QtNetwork`。
5. CI 在提交信息含 `[upgrade]` 时构建 Linux/Windows 包并创建 Release。

## 18. 隐藏机制与边界

### 18.1 输出与窗口

- 输出框的 `Ignored` 尺寸策略是防止窗口被长文本撑大的关键；不要改回默认 `Expanding`。
- `QLabel.setMinimumSize(0, 0)` 与手动分行共同保证布局不传播巨大最小尺寸。
- 滚动模式字号在每轮开始时锁定，避免 tick 过程中字号上下跳动。
- 用户拉伸窗口后，输出框会按新尺寸重新排版；窗口尺寸本身不会被内容修改。
- 极端长姓名在最小字号下可能仍超宽，此时允许字符间换行；不要假设一定能完整单行显示。

### 18.2 滚动

- ScrollMulti 的 `pool` 是本轮共享池，`start()` 时从完整名单重建。
- 快速点击“停止”可能发生在两个 tick 之间；`stop_next()` 会检查当前键是否仍可用，必要时从剩余池补抽。
- 每次停止后重建所有 active reel 的顺序，保证不会再次落到已固定名字。
- `quantity.total` 是完整名单人数，不是本轮实际抽取数；实际抽取数看 `quantity.selected`。
- ScrollLift 的 `lift_pool` 跨轮保留；`quantity.wasted` 表示此前已经减量掉的人数。
- ScrollLift 剩余池为空时不会自动重置，必须点“重置”。
- 导入记忆恢复 ScrollLift 时会恢复 `Liftdict`，因此可以继续上一轮的剩余名单。

### 18.3 减量抽

- `_set_quantity`（原 `_adjust_quantity`）的上限是完整名单长度，不是剩余长度；剩余不足时点“抽取”会走 `outdict={}` 分支显示“暂无结果”，需要手动调小数量或重置。
- `Lift` 结果的 `quantity.Lift` 是“本轮之后剩余人数”，不是“已减量数”。
- 导入历史记忆不会恢复 `lift_current_dict`；减量抽剩余状态只能通过当前会话继续。

### 18.4 记忆

- 记忆文件只保存 `last_results`；旧的 `preferences`、`loaded_config` 读取时会被丢弃。
- 导入记忆不会写入 `config/`，不会改变名单或当前界面状态。
- 记忆文件损坏时回退为只含 `last_results` 的默认结构，不阻止程序启动。
- `save_memory()` 原子替换；不要在别处直接 `write_text()` 写 `memory.json`。
- 旧版 `ScrollSingle` 记忆条目会被忽略；旧版 `scrollsingle` 小写键也不再生效。

### 18.5 日志与查看器

- 日志文件固定为 `doc/log.log`；程序日志窗口显示当前会话内存中的全部等级记录。
- 日志查看器是非模态的，关闭主窗口时会一并关闭。
- 文件被删除后查看器显示“暂无日志”，并继续监听父目录；文件重新创建后自动恢复。
- 触屏拖动依赖 `QScroller`；Windows/Linux 的触摸板/触屏行为可能不同，需要实机验证。

### 18.6 安全与隐私

- 程序只会在用户主动检查更新或点击“项目仓库”“反馈”时访问网络。
- 没有密钥、令牌、遥测或自动上传。
- `config/` 全程只读；程序只写固定的 `doc/memory.json` 和 `doc/log.log`。
- `doc/memory.json`、`doc/log.log` 已加入 `.gitignore`。

### 18.7 编码与格式

- 所有文本文件使用 UTF-8 + LF。
- TOML 由 `tomllib` 直接解析，不要使用 BOM。
- 记忆 JSON 使用 `ensure_ascii=False`，中文原样保存。
- 新代码文件包含 GPL 标识；配置/文档包含版权与许可说明。

## 19. 测试

- `script/test_output_fit.py`：非滚动单行/多行/缩字号；滚动固定格子、位置稳定、超长姓名重排、重置布局。
- `script/test_memory.py`：只保留结果、旧偏好丢弃、导入/导出结果。
- `script/test_scroll_lift.py`：剩余池、逐个停止、重置、数量越界。
- `script/test_config.py`：新旧配置键兼容、非法值回退、启动画面等待时间、版本号字号换算、最大化模式与数量夹紧。
- `script/test_update.py`：版本号解析与新版本比较。
- 运行：`QT_QPA_PLATFORM=offscreen python -m unittest discover -s script -p 'test_*.py'`。

## 20. 版本

当前版本：**3.10.3**。

3.8.x 主要变化：

- 修复滚动多抽窗口闪动；
- 修复导入记忆撑宽窗口和打印字典内容；
- 输出框全模式自适应；
- 窗口可拉伸，但每次启动使用配置尺寸；
- 状态栏信息扩展；
- 单抽/滚动单抽别名；
- 新增滚动减量抽；
- 实时只读文本查看器；
- 启动画面新图与动态版本号；
- 配置注释与精简；
- 业务逻辑文档多语言化；
- 启动画面版本号按图片宽度三分之一自动缩放并固定纯白。

## 21. 3.8.1 增补

- `OutputView` 尺寸策略从 `Ignored` 改为 `Expanding`，并保留 `.ui` 中 160 的水平 stretch；否则 `QGridLayout` 会把宽度分给左右 spacer，输出框只剩几十像素。
- `OutputView` 始终保持 `wordWrap = True`。手动分行仍由 `pack_names()` 完成；`wordWrap` 只用于降低 `QLabel.minimumSizeHint()`，避免长姓名撑大窗口。
- 状态栏改为一个占满宽度的 `QWidget` 容器，内部用 `QHBoxLayout` 左对齐临时消息和全部信息标签；不再使用 `QStatusBar.showMessage()`，避免普通 widget 被临时消息隐藏。
- 临时消息通过 `_show_status_message()` 写入 `status_message_label`；“刷新程序状态”保存/恢复的也是该标签文本。
- “关于 > 反馈”改为二级菜单：
  - `GitHub Issues`：打开 `https://github.com/HQZ-OhNone/randname/issues`；
  - `Email`：调用系统邮件客户端向 `ohnone_hqz@outlook.com` 发送邮件；
  - 邮件客户端无法唤起时，弹出信息框显示邮箱地址。
- 新增常量 `EMAIL_ADDRESS`；与仓库/反馈网址一样硬编码在 `main.py`。
- 版本号更新为 `3.8.1`。

## 22. 3.8.2 增补

- 启动画面 `mode = 1` 时不再提前显示主窗口；`reveal_window()` 在剩余时间到后才 `window.show()` 并关闭启动画面，修复 Wayland 下启动画面被主窗口完全遮住、“一闪而过”的问题。
- 新增 `_splash_wait_ms()` 计算启动画面剩余显示时间；`mode = 0` 和其他模式返回 0，保持“就绪即关闭”。
- 启动时语言回到 `language.toml` 的 `preferred`，模式回到 `[app].default_mode`，数量从 1 开始。
- 版本号更新为 `3.8.2`。

## 23. 3.8.3 增补

- `_draw_splash_version()` 改为按图片宽度自动缩放：用 100px 探针字体测量 `v3.8.3` 的宽度，再按目标宽度（图片宽度的三分之一）反推实际像素字号；`_splash_version_pixel_size()` 负责换算，非法输入回退为 1px。
- 字号严格随启动画面缩放比例变化，不再读取固定字号，也没有最小字号跳变。
- 版本号文字固定为纯白色 `#FFFFFF`；保留黑色半透明阴影以增强对比度。
- 移除 `[splash].version_font_size` 和 `[splash].version_color`；旧配置中的这两个键会被忽略。
- 边距与阴影偏移按图片尺寸等比缩放，避免不同分辨率下位置偏移。
- 版本号更新为 `3.8.3`。

## 24. 3.8.4 增补

- 删除记忆配置功能：启动时不再读取主题、名单、日志等级、模式、语言、数量或窗口尺寸偏好。
- 主题取 `theme.toml` 的 `default`；语言取 `language.toml` 的 `preferred`；名单、模式、日志等级与窗口尺寸取 `config.toml`；数量固定从 1 开始。
- 移除 `[app].remember_preferences`、`[window].remember_size`，并删除窗口尺寸防抖保存、关闭保存和启动恢复。
- 记忆文件只保留 `last_results`；旧文件中的 `preferences`、`loaded_config` 在读取/导入时被忽略，导出文件也不再包含它们。
- `lib/OutputView.py` 新增 `SlotOutputView`、`_SlotGrid` 与 `choose_slot_layout()`。
- ScrollMulti 与 ScrollLift 改用固定格子；第一次抽取确定位置，滚动时只更新文字，超长姓名触发重排并重新锁定。
- 下一轮抽取、更改数量、重置或导入结果时清除布局锁定。
- 新增固定格子布局、位置稳定、超长姓名重排与记忆导出导入测试。
- 版本号更新为 `3.8.4`。

## 25. 3.9.1 增补

- 输出框 `.ui` 字号由 30 调整为 33，并重新生成 4 个 `lib/ui_*.py`。
- `[ui].display_font_size` 同步改为 33，`BUILTIN_CONFIG` 与 `OutputView` 的 fallback 也改为 33，确保执行时实际生效。
- `tests/` 加入 `.gitignore`，并从新提交取消追踪；本机测试文件保留，历史提交不变。
- 版本号更新为 `3.9.1`。

## 26. 3.9.3 增补

- 检查更新仅在检测到新版本时启用“更新”；新增“手动查询”打开 Releases 页面。
- `[update].timeout_ms`（默认 15000）控制 GitHub 请求超时；修正屏幕与 `QByteArray` 类型问题。
- 姓名排版紧凑化；大屏下滚动格子按内容收拢并居中。
- 删除 `[assets]`、`[paths]`，资源与文档路径固定于代码。
- 日志等级只过滤文件输出；程序日志窗口显示当前会话全部等级并高亮。
- 模式名称与标识符统一为 Multi、ScrollMulti、ScrollSingle、Single、Lift、ScrollLift。
- 版本号更新到 3.9.3。

## 27. 3.9.2 增补

- `[window].size_mode` 新增 `maximum`：`_window_is_maximized()` 判断后跳过尺寸计算，只设最小尺寸；`reveal_window()` 调用 `showMaximized()`。刷新配置时可见窗口会立即最大化。
- 四个模式页在数量列右侧新增纵向 `QSlider`；`_prepare_quantity_slider()` 安装 `_QuantitySliderTouchFilter`，把触点纵向位置换算成数值，支持触控拖动。
- `_set_quantity()` 统一更新数量值、标签、滑条范围和滚动控制器；`_refresh_quantity_ranges()` 在切换名单或刷新配置时夹紧并同步四个模式。
- 新增 `lib/UpdateDialog.py`：用 `QNetworkAccessManager` 异步请求 GitHub Releases，`parse_version()`/`is_newer_version()` 比较版本；关闭窗口会中止未完成请求。
- 新增 `ui/Update.ui` 与 `ui/TextViewer.ui`，文本查看器改用 `.ui`；构建脚本与 CI 遍历全部 `ui/*.ui`。
- 检查更新使用 QtNetwork，三个构建配置均移除 `--nofollow-import-to=PySide6.QtNetwork`。
- 三语新增 `action.check_update`、`update.*` 文案；帮助、README、历史记录同步到 3.9.2。
- 新增最大化模式、数量夹紧、版本比较测试。

## 28. 3.9.4 增补

- `UpdateDialog` 改用 `QJsonDocument.fromJson()`/`toVariant()` 解析 GitHub 响应，消除 `QByteArray.data()` 的 `memoryview.decode` 类型警告。
- 移除 `json`、`re`、`QFont` 与未使用的 `Qt`；`parse_version()` 改为手写数字扫描，字体改用现有 `QFont` 副本。
- 缓存 GitHub API 与 Releases 的 `QUrl`；更新按钮状态、手动查询与超时行为不变。
- 全项目 AST 扫描仅发现并移除上述 `Qt` 未使用 import。
- 版本号更新到 3.9.4。

## 29. 3.10.0 发布说明

- 将 3.9.2–3.9.4 的累积改动合并到 `main`，并以 `3.10.0[upgrade]` 触发 GitHub Actions 发布。
- 本版本包含数量滑条、启动最大化、检查更新、姓名紧凑排版、固定资源路径、全量会话日志高亮与模式名称标准化。
- 版本号更新到 3.10.0。

## 30. 3.10.1 CI 维护

- 上次 3.10.0 打包的 annotations 仅有 Node.js 20 弃用警告与 `ubuntu-latest` 迁移提示。
- 所有官方 action 升级到 node24 版本：checkout v7.0.1、setup-python v7.1.0、cache v6.1.0、upload-artifact v7.0.2、download-artifact v8.0.2、action-gh-release v3.0.3。
- Ubuntu 任务固定为 `ubuntu-24.04`，避开 2026-10 至 2026-11 的 Ubuntu 26.04 迁移。
- 提交信息改由 `COMMIT_MSG` 环境变量传入 shell，避免表达式直接内插造成脚本注入风险。
- `actionlint v1.7.12` 校验通过；版本更新到 3.10.1，提交不带 `[upgrade]`，不触发发布。

## 31. 3.10.2 结构调整

- 构建脚本移至 `script/build.sh` 与 `script/build.bat`，执行时自动切回仓库根目录。
- 6 支单元测试移至 `script/`，运行方式为 `.venv/bin/python -m unittest discover -s script -p 'test_*.py'`；删除无引用的 `tests/config_49/`。
- 新增 `doc/project-manifest.json` 作为机器可读索引，开发前先查此文件再按需读取。
- 新增 `script/last-history-reader.sh`，历史摘要只写入 `/tmp`；`doc/releasenote.md` 仅供 CI 与发布流程读取。
- GitHub Release 的正文改为从 `doc/releasenote.md` 截取对应版本段落，缺少时使用后备说明。
- 版本更新为 3.10.2。

## 32. 3.10.3 补充

- 主题可选 `[themes.<键名>.background]`：`BackgroundWidget` 在中央内容区自绘背景，支持 `cover`、`contain`、`center`、`tile`；`blur_direction` 支持 `uniform`、`horizontal`、`vertical`、`diagonal`、`center-out`、`out-center`。未写 `blur_radius` 时默认 24，整张均匀模糊。相对 `image` 路径以 `ui/` 为基准。
- 默认主题 `randname-dark` 没有 background 表，外观不变；新增 `randname-bg-light` 示例主题使用 `ui/background-example.png`。
- 背景图只覆盖中央内容区；菜单栏与状态栏保持主题底色，并由背景图层在上下边缘绘制渐变阴影。
- 固定尺寸模式若宽或高大于可用屏幕，`_fixed_size_exceeds_screen()` 会让窗口临时最大化；不改写配置文件，还原时使用不超出屏幕的尺寸。
- “文件 > 初始化”调用 `StateManager.reset_memory()`，四模式数量回到 1、清除结果与滚动池，并清理 Qt pixmap 缓存；不清除日志，初始化动作写入 `initialize` 日志。
- 修复多抽与减量抽滑条：`_prepare_quantity_slider()` 原本传入小写 `"multi"`／`"lift"`，与 `_set_quantity()` 的标准模式常量不符，导致拖动无效。
- Windows 标题栏由 `WindowTheme.apply_titlebar()` 通过 DWM 设置；Win11 使用 caption/text/border color，Win10 回退 immersive dark mode，非 Windows 直接跳过。
- 新增 `ui/background-example.png` 与 `script/make_background_example.py`；构建脚本与 CI 一并打包新图。测试总数 54。
- 版本更新为 3.10.3。
