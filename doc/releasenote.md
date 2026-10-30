# Release Notes

<!--
本文件仅供 CI 与发布流程读取，日常开发与 agent 会话禁止整档读取。
维护规则：
1. 最新版本放在最前，标题格式固定为 `## vX.Y.Z — YYYY-MM-DD`。
2. 仅在用户明确要求，或版本更新提交带 `[upgrade]` 时追加。
3. 每个版本使用「中文 / English」两段，内容来自 doc/history.md 与 git 记录。
-->

## v3.11.1 — 2026-10-30

### 中文

- 「主题」菜单改为深色／浅色两栏显示，切换语言后同步重建。
- 删除「中性深色」「中性浅色」主题，主题总数由 15 减为 13。
- 调整全部浅色主题：改用带主题色的柔和底色，页面、面板、按钮与边框同步协调，不再刺眼。
- 输出框颜色改由每个主题的 `[themes.<键名>.output]` 配置控制，移除界面中写死的底色、白字与蓝色边框；深色主题外观保持不变。
- 「检查更新」窗口改为跟随主题配色，并显示最新 Release 说明（离线时显示 `doc/releasenote.md` 的最新版本段落），不再显示变更历史。
- 修复 Windows 切换深浅主题时标题栏颜色延迟生效的问题。
- `[window]` 新增 `fullscreen`，设为 `true` 时启动即进入全屏，优先于 `size_mode`。
- 同一次抽取名字过多时，输出框会临时占用窗口上下的空白区域，人数减少后自动恢复。
- 版本更新为 3.11.1。

### English

- The Theme menu now shows dark and light themes in two columns and rebuilds after a language change.
- Removed the Neutral Dark and Neutral Light themes, reducing the catalog from 15 to 13.
- Retuned every light theme with softer, tinted surfaces so the page, panel, buttons, and borders feel coordinated instead of glaring.
- Output-box colours now come from each theme's `[themes.<key>.output]` table, removing the hard-coded background, white text, and blue border; dark themes look unchanged.
- The update window follows the active theme and shows the latest release notes (falling back to the newest `doc/releasenote.md` section when offline) instead of the change history.
- Fixed the delayed Windows title-bar colour change when switching between dark and light themes.
- Added `[window] fullscreen`; when `true`, the app starts in full screen and it takes precedence over `size_mode`.
- When a single draw shows too many names, the output box temporarily uses the blank space above and below, then restores its normal size.
- Version bumped to 3.11.1.

## v3.11.0 — 2026-10-27

### 中文

- 新增主題背景圖：在 `config/theme.toml` 的 `[themes.<鍵名>.background]` 設定，支援 `cover`、`contain`、`center`、`tile` 自動裁切。
- 模糊預設為整張均勻模糊，另支援 `horizontal`、`vertical`、`diagonal`、`center-out`、`out-center` 五種漸變方向；背景只覆蓋中央內容區，菜單列與狀態列保持主題底色並加陰影。
- 新增 `randname-bg-light` 範例主題，直接使用既有的 `ui/randname-start.png`；預設 `randname-dark` 外觀不變。
- 修正多抽與減量抽數量滑桿無法拖動的問題。
- 新增「檔案 > 初始化」：清空記憶檔、四模式數量回到 1、清除已顯示結果與滾動池；日誌保留，初始化動作本身會寫入日誌。
- 固定尺寸大於可用螢幕時暫時最大化，不改寫設定檔，還原時使用不超出螢幕的尺寸。
- Windows 11 標題欄透過 DWM 跟隨主題色，Windows 10 回退為深淺色切換；非 Windows 平台不受影響。
- 版本更新為 3.11.0。

### English

- Added theme background images through `[themes.<key>.background]` in `config/theme.toml`, with automatic `cover`, `contain`, `center`, and `tile` fitting.
- Blur defaults to a uniform full-image blur; `horizontal`, `vertical`, `diagonal`, `center-out`, and `out-center` gradients are also supported. The image covers only the central content area, while the menu bar and status bar keep the theme background and receive a shadow.
- Added the `randname-bg-light` example theme using the existing `ui/randname-start.png`; the default `randname-dark` appearance is unchanged.
- Fixed the Multi and Lift quantity sliders when dragging.
- Added **File > Initialize**, which clears the memory file, resets all four modes to quantity 1, and clears displayed results and rolling pools. Logs are preserved, and the initialization itself is logged.
- Fixed-size windows larger than the available screen now start temporarily maximised without rewriting the configuration and use an on-screen size when restored.
- On Windows 11 the title bar follows the theme through DWM; Windows 10 falls back to light/dark switching, and other platforms are unaffected.
- Version bumped to 3.11.0.

## v3.10.2 — 2026-10-27

### 中文

- 整理项目脚本：构建脚本移至 `script/build.sh`、`script/build.bat`，并从任意目录调用都能定位仓库根目录。
- 测试统一迁入 `script/`，删除无引用的 `tests/config_49/` 测试夹具；38 项测试保持通过。
- 新增机器可读的 `doc/project-manifest.json`，记录脚本、模块、文档、配置与工作流的用途、输入、输出和引用关系。
- 新增 `script/last-history-reader.sh`，把最新变更历史摘要写入 `/tmp`，避免 agent 整档读取 `history.md`。
- 新增本发布说明文件，并在 GitHub Release 工作流中按版本自动截取对应段落作为 release body。

### English

- Reorganized project scripts: build scripts now live at `script/build.sh` and `script/build.bat`, resolving the repository root regardless of the calling directory.
- Moved tests into `script/` and removed the unreferenced `tests/config_49/` fixtures; all 38 tests still pass.
- Added the machine-readable `doc/project-manifest.json` describing scripts, modules, documents, configuration, and workflows with inputs, outputs, and references.
- Added `script/last-history-reader.sh`, which writes the latest history entries to `/tmp` so agents avoid reading the entire `history.md`.
- Added this release-notes file and taught the GitHub Release workflow to extract the matching version section as the release body.

## v3.10.1 — 2026-10-25

### 中文

- 调查 3.10.0 打包过程的全部 annotations，确认没有步骤级警告。
- 将所有 GitHub Actions 升级到 node24 版本，并将 Ubuntu 任务固定到 `ubuntu-24.04`。
- 提交信息改由环境变量传入 shell，消除脚本注入风险。

### English

- Audited all annotations from the 3.10.0 packaging run and confirmed no step-level warnings.
- Upgraded every GitHub Action to its node24 release and pinned Ubuntu jobs to `ubuntu-24.04`.
- Passed the commit message to shell through an environment variable to remove script-injection risk.

## v3.10.0 — 2026-10-25

### 中文

- 将 3.9.2–3.9.4 的累积改动合并发布：数量滑条、启动最大化、检查更新、紧凑排版、固定资源路径与全量会话日志。
- 检查更新窗口仅在发现新版本时启用「更新」，「手动查询」始终打开 GitHub Releases。
- 同步 README、三语逻辑文档与版本号。

### English

- Released the accumulated 3.9.2–3.9.4 work: quantity sliders, maximum startup, update checker, compact layout, fixed asset paths, and full-session logs.
- The update dialog enables “Update” only for a newer release; “Manual check” always opens GitHub Releases.
- Synchronized README, all three logic documents, and the version number.

## v3.9.4 — 2026-10-25

### 中文

- 改用 `QJsonDocument.fromJson()` 解析更新响应，修复 Pylance 类型警告。
- 精简 `UpdateDialog` 的依赖与未使用导入。

### English

- Parsed update responses with `QJsonDocument.fromJson()` and fixed the Pylance type warning.
- Trimmed `UpdateDialog` dependencies and unused imports.

## v3.9.3 — 2026-10-25

### 中文

- 更新窗口区分「更新」与「手动查询」，并支持 `[update].timeout_ms` 超时配置。
- 收紧非滚动模式姓名间距，滚动模式改为按内容收拢并锁定格子位置。
- 固定图标、启动图、帮助、日志、记忆与许可证路径；模式名称统一为 `Multi`、`ScrollMulti`、`ScrollSingle`、`Single`、`Lift`、`ScrollLift`。

### English

- Split “Update” and “Manual check”, and added the `[update].timeout_ms` timeout setting.
- Tightened name spacing in non-scrolling modes and locked content-sized slots in scrolling modes.
- Hard-coded asset, help, log, memory, and license paths; standardized mode names across the app.

## v3.9.2 — 2026-10-25

### 中文

- 新增 `maximum` 窗口模式与四个模式的数量滑动条，支持触控并同步按钮和标签。
- 新增检查更新窗口、`lib/UpdateDialog.py`、`ui/Update.ui` 与 `ui/TextViewer.ui`。
- 构建脚本与 CI 改为遍历 `ui/*.ui` 自动生成界面模块。

### English

- Added the `maximum` window mode and quantity sliders for four modes with touch support and synchronized controls.
- Added the update dialog, `lib/UpdateDialog.py`, `ui/Update.ui`, and `ui/TextViewer.ui`.
- Build scripts and CI now compile every `ui/*.ui` automatically.

## v3.9.1 — 2026-10-18

### 中文

- 四个输出框字号由 30 调整为 33，并同步配置与运行期回退值。
- 将 `tests/` 取消追踪并加入 `.gitignore`。

### English

- Raised output font sizes from 30 to 33 and synchronized configuration and runtime fallbacks.
- Untracked `tests/` and added it to `.gitignore`.

## v3.9.0 — 2026-10-18

### 中文

- 校正 3.8 系列的版本号与发布配置，统一 README 和 `config/config.toml` 中的版本描述。

### English

- Corrected version numbering and release configuration for the 3.8 series, aligning README and `config/config.toml`.

## v3.8.4 — 2026-10-18

### 中文

- 移除记忆配置功能，启动状态统一从主题、语言与主配置读取。
- 滚动多抽与滚动减量抽改用固定格子，首次抽取后锁定位置，仅更新文字。

### English

- Removed memory-based preferences; startup state now comes from theme, language, and main configuration files.
- Rolling Multi and Rolling Elimination now use fixed slots locked after the first draw, updating text only.

## v3.8.3 — 2026-10-18

### 中文

- 启动画面版本号改为按图片宽度自动缩放，固定为纯白色并紧贴右下角。
- 移除 `[splash].version_font_size` 与 `[splash].version_color` 配置。

### English

- Splash version text now scales with the image width, stays pure white, and sits tight to the bottom-right corner.
- Removed the `[splash].version_font_size` and `[splash].version_color` options.

## v3.8.2 — 2026-10-18

### 中文

- 修复 Wayland 下启动画面一闪而过的问题，按 `duration_ms` 等待后再显示主窗口。
- 记忆偏好只保留主题、名单、日志等级和窗口尺寸。

### English

- Fixed the splash flashing by on Wayland; the main window now waits for the remaining `duration_ms`.
- Memory preferences now keep only theme, roster, log level, and window size.

## v3.8.1 — 2026-10-18

### 中文

- 修复输出框过小，恢复占满窗口的显示区域，长姓名不再撑大窗口。
- 状态栏改为左对齐，并将「反馈」设为 GitHub Issues 与 Email 二级菜单。

### English

- Fixed the tiny output box, restored its expanding area, and prevented long names from resizing the window.
- Left-aligned the status bar and turned Feedback into a GitHub Issues / Email submenu.

## v3.8.0 — 2026-10-18

### 中文

- 修复滚动窗口闪动、记忆导入拉宽窗口与字典内容误输出。
- 新增滚动减量抽、只读文本查看器，并统一输出框自适应逻辑。
- 版本号集中到 `lib/version.py`，业务逻辑文档多语言化并新增 `history.md`。

### English

- Fixed rolling-window flicker, memory-import window widening, and raw dictionary output.
- Added Rolling Elimination, a read-only text viewer, and shared auto-fit output logic.
- Centralized the version in `lib/version.py`, localized the logic docs, and added `history.md`.

## v3.7.0 — 2026-10-12

### 中文

- 滚动多抽的英文模式名更新为 `ScrollMulti`，同步界面、配置与文档。

### English

- Renamed the English Rolling Multi mode to `ScrollMulti` across the UI, configuration, and documentation.

## v3.6.3 — 2026-10-12

### 中文

- 滚动多抽改为单框显示，统一模式命名，并合并 dev-bugs 分支的防御性修正。

### English

- Changed Rolling Multi to a single output box, unified mode naming, and merged defensive fixes from the dev-bugs branch.

## v3.6.2 — 2026-10-11

### 中文

- 修复主题与语言配置冲突：独立配置档优先于记忆偏好。

### English

- Fixed theme and language configuration conflicts by giving dedicated config files precedence over stored preferences.

## v3.6.1 — 2026-10-11

### 中文

- 大幅调整窗口尺寸、主题、语言、文档配置与动画，并建立多语言文档体系。

### English

- Reworked window sizing, themes, languages, document configuration, and animations, and established multilingual documentation.

## v3.6.0 — 2026-10-02

### 中文

- 进入 3.6 系列，更新启动画面资源与版本标识。

### English

- Started the 3.6 series with updated splash resources and version branding.

## v3.5.1 — 2026-10-02

### 中文

- 修复单抽并增设启动窗口，使用文档加入扫描功能说明。

### English

- Fixed single draw and added a startup window; documented the scan feature.

## v3.5.0 — 2026-10-01

### 中文

- 美化界面并增设应用图标与启动画面。

### English

- Polished the interface and added the application icon and startup splash.

## v3.4.4 — 2026-09-19

### 中文

- 优化主题显示效果。

### English

- Improved theme rendering.

## v3.4.3 — 2026-09-19

### 中文

- 修复 3.4 系列遗留问题，完善界面细节。

### English

- Fixed remaining 3.4-series issues and refined interface details.

## v3.4.2 — 2026-09-19

### 中文

- 重新尝试发布流程并修正构建问题。

### English

- Retried the release process and fixed build issues.

## v3.4.1 — 2026-09-19

### 中文

- 更新编译脚本与构建配置。

### English

- Updated the compilation scripts and build configuration.

## v3.4.0 — 2026-09-19

### 中文

- 修复已知问题并加入新功能，更新 README。

### English

- Fixed known issues, added new features, and updated README.

## v3.3.1 — 2026-09-01

### 中文

- 重试发布并修正版本发布流程。

### English

- Retried the release and corrected the release workflow.

## v3.3.0 — 2026-08-29

### 中文

- 完善 GPL 许可证标识与应用内许可信息。

### English

- Completed GPL licensing notices and in-app license information.

## v3.2.1 — 2026-08-28

### 中文

- 调整界面文件并重新生成界面模块。

### English

- Adjusted UI files and regenerated the UI modules.

## v3.2.0 — 2026-08-12

### 中文

- 移除对 `.ui` 运行时依赖，改为提交预编译界面模块。
- 优化 README，并修复版本号错误导致的自动发布失败。

### English

- Removed the runtime dependency on `.ui` files by committing precompiled UI modules.
- Improved README and fixed automated releases failing due to an incorrect version number.

## v3.1.7 — 2026-07-27

### 中文

- 迁移到 Python 3.12.10，并取消 Windows 包的黑色控制台窗口。

### English

- Migrated to Python 3.12.10 and disabled the console window in Windows packages.

## v3.1.6 — 2026-07-27

### 中文

- 更新 README 的功能说明与编译示例。

### English

- Updated README feature notes and compilation examples.

## v3.1.5 — 2026-07-27

### 中文

- 重构 Build and Release 工作流，提高可读性。

### English

- Refactored the Build and Release workflow for clarity.

## v3.1.4 — 2026-07-27

### 中文

- 修复 GitHub Actions 发布工作流配置。

### English

- Fixed the GitHub Actions release workflow configuration.

## v3.1.3 — 2026-07-27

### 中文

- 修复界面问题，并首次验证 Actions 自动发布流程。

### English

- Fixed interface issues and validated the Actions release pipeline for the first time.

## v3.1.1 — 2026-07-27

### 中文

- 修复一个界面显示错误。

### English

- Fixed a display error.

## v3.1.0 — 2026-07-27

### 中文

- 修改 `main.py`，制作第一个正式版本。

### English

- Reworked `main.py` and shipped the first official release.

## v3.0.11.1 — 2026-07-25

### 中文

- 精简项目结构，方便后续维护。

### English

- Simplified the project structure for easier maintenance.

## v3.0.11 — 2026-07-17

### 中文

- 修复 README 链接指向错误。

### English

- Fixed incorrect README links.

## v3.0.10 — 2026-07-17

### 中文

- 修复 GitHub 上 README 显示异常。

### English

- Fixed README rendering issues on GitHub.

## v3.0.9 — 2026-07-17

### 中文

- 完善错误处理并新增 README。

### English

- Improved error handling and added README.

## v3.0.8 — 2026-07-17

### 中文

- 完成后端程序与内部交流规范。

### English

- Completed the backend logic and internal communication conventions.

## v3.0.7 — 2026-07-10

### 中文

- 完善 Single 与 Lift 抽取逻辑。

### English

- Refined the Single and Lift draw logic.

## v3.0.5 — 2026-06-28

### 中文

- 制作 Qt GUI 并再次重构项目结构。

### English

- Built the Qt GUI and reorganized the project again.

## v3.0.4 — 2026-06-20

### 中文

- 首个演示版本，重新整理文件结构。

### English

- First demo release with a reorganized file layout.
