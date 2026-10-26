# AGENTS.md
> randname
## 项目概览
- 入口：main.py
- 环境：.venv
- Python 3.12.10
- pyside 6.11.1
## 目录边界
- main.py  程序入口
- lib/  业务模块与生成的 `ui_*.py`
- script/  构建、测试与辅助脚本；测试统一为 `script/test_*.py`
- doc/  文档与项目清单，不动代码
- ui/  Qt Designer 源文件与图片资源
- build/ __pycache__/ .venv/  生成物，禁止手改
## 开工定位
1. 先读 `doc/project-manifest.json`，按清单定位需要改动的脚本、模块、文档与配置
2. 只读取清单指向的必要片段，禁止整仓读取或整档读取大型日志/文档
3. 新增、删除或移动脚本、模块、文档、配置、工作流后，同步更新 `doc/project-manifest.json`
## 改代码前
1. 先 Plan 模式定位影响文件
2. 只改请求涉及的范围，不顺手重构
3. 测试不过不要提交，先修或问
## 提交规则
- 不自动 git push
- commit 用已有风格：x.y.z_解释
- 一次 commit 只做一件事
## 禁止项
- 不写硬编码密钥、token、密码
- 不删文件、不 mv 整个目录（除非用户明确说）
## 卡住时
- 别大面积猜改
- 先给：定位结论 + 怀疑文件 + 需要确认的问题
## 更改
### 对于所有文件更改
- 所有更改都放在 dev 分支，只在发布版本时（由我指定，默认不发布）合并到 main
- 同步追加更新 `history.md` ，`history.md`详细记录当次会话发现但未解决的问题、完成的任务等内容；`history.md`使用中英双语
- 文件加上 GPL 标识
### 对于所有代码更改
- 同步更新 `logic.md`
- 若某一模块更改，（如需要则）同步改进其关联文件
- 若打包命令更改，同步在 `.github/workflows/BuildAndRelease.yml`、`script/build.sh`、`script/build.bat` 与 `doc/project-manifest.json` 更新
- 以后所有测试脚本一律放入 `script/`；单测命名 `script/test_*.py`，运行方式：
  `.venv/bin/python -m unittest discover -s script -p 'test_*.py'`
- 会话中若有代码更改且足够完善（可以提交），则提交一个小版本（如：3.4.4 -> 3.4.5），同步更新启动框版本号
## 语言规范
- 文件名一律使用英文
- 注释一律使用简体中文
- 文档所使用的语言在文件名加后缀，如 `doc_zh-TW.md`、`doc_zh-CN.md`、`doc_en-US.md`。
- 在文档、用户界面对一种语言的更改要立即同步对其他语言的支持
## 其他
- 阅读变更历史一律使用 `script/last-history-reader.sh`，输出到 `/tmp`，不要让全文进入对话
- `doc/releasenote.md` 日常禁止读取，只由 CI 读取；仅在版本更新（提交含 `[upgrade]`）或用户明确要求时追加，最新版本置顶
- 对于一切输出较长的终端命令，将其输出到 /tmp/ 下的文件，避免直接出现在上下文
- 对于任意会话：在不降低回复质量时，精简输入输出并使用结构化语言以节省token，避免大段自然语言输出
- 若执行时我不在（需要我参与时无反馈），有需要我参与的环节（如填写PGP密钥），先尝试跳过或使用备选方案，如果不能跳过则先执行其他任务，在输出时提醒我
