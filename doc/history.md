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
