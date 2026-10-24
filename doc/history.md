# 变更历史 / Change History

Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; see the GNU General Public License for more details.

本文件按会话追加记录：已完成任务、发现但未解决的问题、验证结果。
This file is appended per session: completed work, unresolved findings, and
verification results.

## 2026-10-25 / 3.9.4

### 已完成 / Completed

- 修复检查更新窗口的 Pylance `memoryview.decode` 类型警告：改用 `QJsonDocument.fromJson()` 直接解析网络响应。
- 精简 `UpdateDialog` 依赖：移除 `json`、`re`、`QFont` 与未使用的 `Qt`；手写版本号扫描、复用现有字体对象，并缓存 `QUrl`。
- 全项目未使用 import 扫描后仅清理 `UpdateDialog` 的 `Qt`；其余模块无需改动。
- 三语帮助、逻辑文档、README 与版本号同步到 `3.9.4`。

### 发现但未解决 / Found but unresolved

- 本环境未直接运行 Pylance/Pyright，仅以等价运行测试、`compileall` 与 AST 扫描验证。
- 未进行打包后的 Windows/Linux 成品验证。

### English summary

- Fixed the Pylance `memoryview.decode` warning by parsing the network response with `QJsonDocument.fromJson()`.
- Removed unused `json`, `re`, `QFont`, and `Qt` dependencies from the update dialog; added a manual version scanner, reused the existing font object, and cached `QUrl` values.
- An AST scan found no other unused imports; version references and documentation are synchronized to 3.9.4.

## 2026-10-25 / 3.9.3

### 已完成 / Completed

- 检查更新窗口仅在检测到新版本时启用“更新”按钮，并在“更新”与“确定”之间新增“手动查询”。
- “手动查询”始终可打开 GitHub Releases；修复更新窗口获取屏幕与解析网络的类型问题。
- 更新查询超时改为 `[update].timeout_ms` 配置，默认 15000 毫秒。
- 非滚动模式的姓名间距缩小；滚动模式的格子宽度按内容收拢并在大屏中居中，保持同一轮位置锁定。
- 移除 `[assets]`、`[paths]` 配置，图标、启动图、帮助、日志、记忆与许可证路径固定于代码。
- 日志等级只控制写入文件的详细度；程序日志窗口显示本次运行全部等级并在行首高亮。
- 模式名称统一为 `Multi`、`ScrollMulti`、`ScrollSingle`、`Single`、`Lift`、`ScrollLift`，同步代码标识符、语言键与文档。
- 修正 `config.toml` 的 `eont_size` 拼写；三语帮助、逻辑文档、README 与版本号同步到 `3.9.3`。

### 发现但未解决 / Found but unresolved

- 紧凑排版在不同字体与超长姓名下的视觉平衡仍需真实课堂投影环境确认。
- 日志窗口只保留当前进程记录；程序重启后无法在窗口内回溯历史日志文件。
- 本轮未运行打包后的成品验证，触控与高 DPI 仍需实机测试。

### English summary

- The update dialog now enables “Update” only when a newer release exists and adds a “Manual check” button between “Update” and “OK”; screen and network type issues are fixed.
- Added configurable update timeout (`[update].timeout_ms`, default 15 s), compact name layout, fixed asset/document paths, full-session log viewer with level highlighting, and canonical mode names throughout.
- Version bumped to 3.9.3; local tests pass, packaged binaries were not verified in this session.

## 2026-10-25 / 3.9.2

### 已完成 / Completed

- `[window].size_mode` 新增 `maximum`，启动时以最大化显示主窗口；刷新配置时同步应用。
- Multi、Lift、ScrollMulti、ScrollLift 四个模式新增数量纵向滑动条，范围为 1 到当前名单人数。
- 滑动条、增加/减少按钮、数量标签与滚动控制器统一同步；切换名单或刷新配置时自动夹紧数值。
- 滑动条支持触控位置换算，加大触控命中区，并保留鼠标点击与拖动。
- 关于菜单新增“检查更新”，弹出窗口用大字号显示检测状态。
- 检查更新通过 GitHub Releases API 异步查询，并展示 `history.md` 正文。
- 检查更新窗口提供“更新”（打开 Releases）与“确定”（关闭）按钮。
- 新增 `lib/UpdateDialog.py`、`ui/Update.ui`、`ui/TextViewer.ui`；文本查看器改用 `.ui` 构建。
- 构建脚本与 CI 改为遍历 `ui/*.ui` 自动生成 `lib/ui_*.py`，并允许打包 QtNetwork。
- 三语语言包、帮助、逻辑文档、README 与版本号同步到 `3.9.2`。
- 新增窗口最大化、数量同步与版本比较测试。

### 发现但未解决 / Found but unresolved

- GitHub API 的匿名请求存在速率限制，触发限制时只能提示用户手动查询。
- 触控滑动条与 `QScroller` 的真实设备手感仍需在触屏硬件上验证。
- 本轮仅做本地测试，未运行打包后的 Windows/Linux 成品验证。

### English summary

- Added `maximum` window size mode, four quantity sliders with touch support, an update checker dialog backed by the GitHub Releases API, and complete `.ui`-based window construction.
- Build scripts now compile every `ui/*.ui` automatically and keep QtNetwork enabled.
- Version bumped to 3.9.2; local tests pass, packaged binaries not verified in this session.

## 2026-10-18 / 3.9.1

### 已完成 / Completed

- 将 4 个输出框 `.ui` 字号由 30 调整为 33，并用 `pyside6-uic` 重新生成对应的 `lib/ui_*.py`。
- 同步将 `config/config.toml`、`.config.default.toml`、`BUILTIN_CONFIG` 与 `OutputView` fallback 的 `display_font_size` 改为 33，确保运行期实际生效。
- 将 `tests/` 加入 `.gitignore`，并用 `git rm --cached -r tests` 从新提交取消追踪；本机测试文件保留，历史提交不变。
- 更新 README、三语言业务逻辑文档与本历史文件。
- 版本号更新为 `3.9.1`。

### 验证 / Verification

- 本机 28 项测试通过。
- `pyside6-uic` 生成结果只包含预期字号变化。
- Python 编译检查通过。

### English summary

- Raised all four output-label `.ui` font sizes from 30 to 33 and regenerated
  the corresponding `lib/ui_*.py` files with `pyside6-uic`.
- Synchronized `[ui].display_font_size` to 33 in `config/config.toml`,
  `.config.default.toml`, `BUILTIN_CONFIG`, and the `OutputView` fallback so
  the runtime actually uses it.
- Added `tests/` to `.gitignore` and untracked it in the new commit with
  `git rm --cached -r tests`; local test files remain and history is unchanged.
- Updated README, all three logic documents, and this history file.
- Version is now `3.9.1`.

## 2026-10-18 / 3.8.4

### 已完成 / Completed

- 删除记忆配置功能：启动时不再从 `doc/memory.json` 恢复主题、名单、日志等级、模式、语言、数量或窗口尺寸。
- 启动界面统一按配置档读取：主题取 `theme.toml` 的 `default`，语言取 `language.toml` 的 `preferred`，名单、模式、日志等级和窗口尺寸取 `config.toml`，数量从 1 开始。
- 移除 `[app].remember_preferences`、`[window].remember_size`，以及窗口尺寸防抖保存、关闭保存和启动恢复。
- 记忆文件只保存 `last_results`；旧档中的 `preferences`、`loaded_config` 在读取和导入时被忽略，导出也不再包含。
- 保留“文件 > 导入记忆...”与“导出记忆...”的结果导入/导出能力。
- 新增 `SlotOutputView`、`_SlotGrid`、`choose_slot_layout()`：滚动多抽与滚动减量抽使用固定格子。
- 第一次抽取按人数与输出框比例确定格子位置；6 人宽框通常为 2 列 × 3 栏，文字居中。
- 锁定后滚动 tick 只更新文字，已固定名字不移动；名字过长时自动重排列数/行数/字号并重新锁定。
- 下一轮抽取、更改数量、重置或导入结果时清除布局锁定。
- 更新记忆、配置、输出框测试；全部 28 项测试通过。
- 更新三语言帮助、三语言业务逻辑文档和 README。
- 版本号更新为 `3.8.4`。

### 发现但未解决 / Found but unresolved

- 固定格子的“过长”判断按当前滚动帧进行：临时滚过的长名字也可能触发一次全盘重排，之后保持锁定。
- 极长姓名在最小字号下仍可能在格子内换行，格子高度不足时可能被裁切，需要在真实字体与窗口尺寸下继续验证。
- 未在真实触摸屏上验证固定格子刷新时的视觉稳定性。

### English summary

- Removed memory-based configuration. Startup now reads theme from `theme.toml`,
  language from `language.toml`, and roster/mode/log level/window size from
  `config.toml`; quantities always start at 1.
- Removed `[app].remember_preferences`, `[window].remember_size`, window-size
  debounce/close saving, and startup restore.
- The memory file now stores only `last_results`. Legacy `preferences` and
  `loaded_config` are ignored on load/import and omitted from exports. Result
  import/export is retained.
- Added fixed-slot `SlotOutputView` for Rolling Multi and Rolling Elimination.
  The first draw decides positions, ticks only change text, and an overlong
  name triggers a re-layout that is then locked.
- The next draw, quantity change, reset, or result import clears the layout
  lock.
- Updated tests, all three help files, all three logic documents, README, and
  bumped the version to `3.8.4`.
- Unresolved: transient long rolling names can trigger one global re-layout;
  extreme names may still wrap or clip inside a slot; real-device touch
  stability was not tested.

## 2026-10-18 / 3.8.3

### 已完成 / Completed

- 启动画面版本号改为按图片宽度自动缩放：以 100px 探针字体测量 `v3.8.3` 宽度，再按图片宽度的三分之一反推像素字号。
- 新增 `_splash_version_pixel_size()`；无固定最小字号跳变，非法输入回退为 1px。
- 版本号文字固定为纯白色 `#FFFFFF`，保留黑色半透明阴影以增强对比度。
- 改为按基线定位，版本号紧贴右下角；边距和阴影偏移按图片尺寸等比缩放。
- 移除 `[splash].version_font_size` 和 `[splash].version_color`；旧配置中的这两个键会被忽略。
- `tests/test_config.py` 增加字号换算与非法值测试。
- 版本号更新为 `3.8.3`，同步 README 与三语言业务逻辑文档。
- 新增 `AGENTS.md`；删除已不再使用的开发检查脚本 `checks/verify_fixes.py`。

### English summary

- The splash version now scales from the image width: a 100px probe font
  measures `v3.8.3`, then the pixel size is derived from one third of the image
  width.
- Added `_splash_version_pixel_size()`; there is no fixed minimum-size jump,
  and invalid input falls back to 1px.
- The version text is always pure white `#FFFFFF`; the translucent black shadow
  remains for contrast.
- Baseline positioning keeps the version tight to the bottom-right corner;
  margins and shadow offset scale with the image.
- Removed `[splash].version_font_size` and `[splash].version_color`; older
  configuration keys are ignored.
- Added font-size conversion tests to `tests/test_config.py`.
- Bumped the version to `3.8.3` and updated README plus all three logic docs.
- Added `AGENTS.md`; removed the unused development check script
  `checks/verify_fixes.py`.

### 发现但未解决 / Found but unresolved

- 字号按字体度量换算，不同平台字体渲染可能存在 1-2px 的可见宽度差异；仍需在 Windows 与真实高分屏确认。
- 旧 `doc/memory.json` 仍保留 `version_font_size`、`version_color` 键，按运行期文件处理，不主动清除。
- 移除固定字号/颜色配置后，用户无法再通过配置微调版本号外观；这是本次需求的有意取舍。
- `checks/verify_fixes.py` 删除后，旧的开发回归脚本不可用；常规回归统一使用 `tests/`。

### 验证 / Verification

- `python -m compileall main.py lib tests` 通过。
- `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests`：24 项通过。
- 离屏渲染 1000×500、480×240、250×125 启动图：文字宽度比例分别为
  0.338、0.338、0.340；右边距 9/4/1px，底边距 9/4/2px。
- 1000×500 预览图中版本号为纯白，位于右下角且未裁切。
- 仍需在真实 Windows/Linux 高分屏确认字体渲染与视觉比例。

## 2026-10-18 / 3.8.2

### 已完成 / Completed

- 修复启动画面在 Wayland 下一闪而过：`mode = 1` 时不再提前显示主窗口，等 `duration_ms` 剩余时间到后才 `window.show()` 并关闭启动画面。
- 新增 `_splash_wait_ms()`；`mode = 0` 仍是主窗口就绪即关闭。
- 记忆偏好只保留主题、名单、日志等级和窗口尺寸；模式、语言和数量每次启动回到配置默认值。
- 新增 `_startup_preferences()` 过滤旧记忆；`_current_preferences()` 不再写入语言、模式和数量。
- `remember_preferences` 仍作为总开关，`false` 时忽略主题/名单/日志等级，窗口尺寸仍由 `remember_size` 控制。
- 版本号更新为 `3.8.2`。

### English summary

- Fixed the splash flashing by on Wayland: with `mode = 1` the main window is
  no longer shown early; it waits for the remaining `duration_ms`, then calls
  `window.show()` and closes the splash.
- Added `_splash_wait_ms()`; `mode = 0` still closes as soon as the window is
  ready.
- Memory preferences now keep only theme, roster, log level, and window size;
  mode, language, and quantities return to configuration defaults every startup.
- Added `_startup_preferences()` to filter old memory, and
  `_current_preferences()` no longer writes language, mode, or quantities.
- `remember_preferences` remains the master switch; `false` ignores theme,
  roster, and log level while `remember_size` still works independently.
- Bumped the version to `3.8.2`.

### 发现但未解决 / Found but unresolved

- 旧 `doc/memory.json` 仍保留 `language`、`mode`、`quantities` 键，按要求不主动清除；这些键启动时被忽略。
- Wayland 下启动画面位置由合成器决定，`move()` 不保证居中。
- 启动画面点击不能跳过等待；如有需要可后续增加点击提前显示主窗口。
- 启动画面被其它置顶窗口遮挡时仍需实机确认。

### 验证 / Verification

- `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests` 通过。
- 离屏计时探针：`QSplashScreen.show` 后约 4 秒才出现 `QMainWindow.show`，随后 `splash.finish`。
- 启动偏好过滤测试覆盖保留项、忽略项和 `remember_preferences = false`。
- 仍需在真实 Wayland 桌面确认启动画面完整停留 `duration_ms`。

## 2026-10-18 / 3.8.1

### 已完成 / Completed

- 修复输出框过小：`OutputView` 改用 `Expanding` 并保留 160 水平 stretch，恢复占满窗口的显示区域。
- 输出框始终保持 `wordWrap=True`，长姓名不会重新撑大窗口。
- 状态栏改为左对齐容器，临时消息与模式/名单/数量/主题/语言/日志/版本统一左对齐。
- 移除对 `QStatusBar.showMessage()` 的依赖，避免临时消息隐藏状态栏信息。
- “关于 > 反馈”改为二级菜单：
  - GitHub Issues；
  - Email（调用系统邮件客户端）。
- 邮件客户端无法唤起时弹窗显示 `ohnone_hqz@outlook.com`。
- 版本号更新为 `3.8.1`。

### English summary

- Fixed the tiny output box by restoring `Expanding` size policy and the 160
  horizontal stretch; long names still cannot resize the window.
- Left-aligned the status bar with a full-width container and a custom temporary
  message label instead of `QStatusBar.showMessage()`.
- Added a Feedback submenu with GitHub Issues and Email; email falls back to an
  information dialog showing the address when no mail client can be opened.
- Bumped the version to `3.8.1`.

### 发现但未解决 / Found but unresolved

- 邮件客户端能否成功唤起取决于系统 `mailto:` 关联，需要在 Windows/Linux 实机验证。
- 状态栏信息较多时，窄窗口仍可能显得拥挤；可继续用 `[statusbar]` 隐藏部分字段。
- 触屏滚动与超长姓名裁切仍需实机验证。

### 验证 / Verification

- `python -m compileall main.py lib tests` 通过。
- `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests`：19 项通过。
- 离屏窗口 1000px 宽时，输出框宽度恢复为约 718px，不再是 80px。
- 状态栏容器占满宽度，临时消息和信息标签从左侧开始排列。
- 三语言反馈菜单均显示 GitHub Issues / Email（或对应译名）。
- 模拟邮件客户端失败时，弹窗显示 `ohnone_hqz@outlook.com`。
- 仍需实机验证系统 `mailto:` 关联和真实窗口主题效果。

## 2026-10-18 / 3.8.0

### 已完成 / Completed

- 修复滚动多抽窗口闪动：输出框改为固定窗口内自适应，内容不再撑大窗口。
- 修复导入 memory 后窗口异常拉宽：导入只回填显示，不再 resize。
- 修复 memory 字典内容被打印到输出框：统一从 `outdict` 提取姓名。
- 所有模式共用 `lib/OutputView.py`：单行 -> 多行 -> 本次抽取缩小字号。
- 滚动模式在每轮开始时锁定字号，避免 tick 过程中字号抖动。
- 主窗口允许用户拉伸；尺寸 450ms 防抖写入 memory，关闭/最大化状态变化时也保存。
- 下次启动恢复 memory 中的窗口尺寸，并夹紧到当前屏幕可用区域。
- 状态栏右侧增加模式、名单、数量、主题、语言、日志等级、版本。
- memory 增加 `preferences`：主题、语言、名单、模式、日志等级、数量、窗口尺寸。
- 启动时优先使用 memory 中的有效偏好；`[app].remember_preferences` 可关闭。
- 关于菜单增加“反馈”，打开 GitHub Issues；仓库/反馈地址硬编码在 `main.py`。
- 新增 `Single` 菜单别名：切到多抽并设数量 1，不新增页面。
- 删除 `ScrollSingle` 页面/控制器/编译产物；菜单“滚动单抽”改为滚动多抽数量 1。
- 新增 `ScrollLift`（滚动减量抽）：跨轮剩余池、重置、结果含 `Liftdict`。
- 新增只读、实时刷新、非模态、触屏友好的内部文本查看器。
- 帮助、许可证、程序日志统一走 `TextViewerDialog`。
- 启动画面改用 `ui/randname-start.png`，删除 v3.6/v3.7 旧图，右下角动态绘制 `v3.8.0`。
- 版本号集中到 `lib/version.py`，当前 `3.8.0`。
- `config/config.toml`、`.config.default.toml` 重构并补充面向新手的注释。
- 删除配置中的 `repository_url`、`feedback_url`、`app.theme`、`app.language`、`[scroll_single]`；
  代码保留旧键兼容。
- 英文模式名去掉 draw 并首字母大写：Multi、Single、Elimination、Rolling Single、
  Rolling Multi、Rolling Elimination。
- 删除 README 的 TODO/未来开发内容，更新帮助、README、构建脚本和 CI。
- 业务逻辑文档更名并多语言化：
  - `doc/logic_zh_CN.md`
  - `doc/logic_zh_TW.md`
  - `doc/logic_en_US.md`
- 新增本 `doc/history.md`。
- 新增 `tests/` 下的输出、记忆、配置、滚动减量抽测试。

### 发现但未解决 / Found but unresolved

- 触屏拖动滚动依赖 `QScroller`，需要在真实触屏设备上验证手感与手势冲突。
- 极长单个姓名在最小字号下仍可能超过输出框宽度；当前回退为 Qt 字符间换行，
  仍可能被裁切。
- 滚动模式在每轮开始时按当时的输出框尺寸锁定字号；若用户在滚动过程中拉伸窗口，
  锁定字号要到下一轮才重新计算。
- 模式菜单的 QAction 仍未加入 `QActionGroup`，可能出现多个勾选态；程序以
  `current_mode` 和当前页面为准。
- `_startup_file_check()` 的 `required` 仍恒为空，致命启动检查分支不可达。
- 导入 memory 中的偏好按设计在下次启动生效，不在当前会话立即切换主题/语言；
  若用户期望立即切换，需要增加确认对话框。
- 旧版 memory 中的 `ScrollSingle` 结果会被忽略，不迁移到 `ScrollMulti`。
- 窗口位置（x/y）未持久化，只持久化宽高和最大化状态。
- 状态栏字段较多，窄窗口可能拥挤；可通过 `[statusbar]` 隐藏部分字段。
- 翻译文件已同步键位，但仍建议由母语使用者校对文案。
- 本地未执行 Nuitka 完整打包；只验证了源码运行、`pyside6-uic` 编译和离屏启动。
- `doc/log.log`、`doc/memory.json` 为运行时文件，已加入 `.gitignore`；测试期间的
  写入不应提交。

### English summary / 英文摘要

- Completed: fixed rolling-window flicker and memory-import widening/raw dict output;
  added shared auto-fit output; resizable persisted window; expanded status bar;
  memory preferences; Single/Rolling Single aliases; new Rolling Elimination mode;
  live read-only viewer; new splash image with dynamic version; simplified and
  documented configuration; multilingual logic docs; tests.
- Unresolved: real-device touch testing; extreme single-name clipping; locked font
  is not recalculated when the window is resized mid-round; mode actions are not
  in a QActionGroup; `required` startup check is still always empty; imported
  preferences apply on the next startup by design; legacy ScrollSingle results are
  not migrated; window position is not persisted; status bar may crowd narrow
  windows; native translation review; full Nuitka packaging not run locally.
- Verified: compileall; 17 offscreen unit tests; offscreen startup; 900×650 window
  stayed fixed with long names; alias switching; Rolling Elimination pool reduced
  from 9 to 7 after drawing two names; status bar fields; generated UI modules.

### 验证 / Verification

- `python -m compileall main.py lib` 通过。
- `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests`：17 项测试通过。
- `QT_QPA_PLATFORM=offscreen` 离屏启动主窗口通过。
- 长姓名测试：窗口尺寸保持 900×650，输出字号自动降到下限并换行。
- 单抽/滚动单抽别名切换通过。
- ScrollLift 首轮抽取 2 人后，剩余池从 9 变为 7。
- 状态栏显示模式、名单、数量、主题、语言、日志等级、版本。
- `pyside6-uic` 重新生成 `lib/ui_*.py`，删除 `ui_widgetscrollsingle.py`。
- 仍需手动验证：真实桌面主题/字体、触屏滚动、启动画面版本号位置、日志实时刷新、
  导入/导出对话框、Nuitka 打包。
