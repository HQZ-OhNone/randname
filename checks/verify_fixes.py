#!/usr/bin/env python3
"""randname 修复回归检查（开发用）

用途：验证 ``dev-bugs`` 分支上的缺陷修复，并锁定原有行为不被破坏。
运行：``QT_QPA_PLATFORM=offscreen .venv/bin/python checks/verify_fixes.py``

设计约束：
- 只依赖项目已有依赖（PySide6）+ 标准库，不引入 pytest。
- 不修改仓库内的任何配置文件；可写路径（memory/log）被重定向到临时目录。
- 支持 ``--only <关键字>`` 过滤用例。
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

TMP = tempfile.mkdtemp(prefix="randname-checks-")

_RESULTS: list[tuple[str, str, str]] = []
_FILTER = ""


# --------------------------------------------------------------------------
# 迷你测试框架
# --------------------------------------------------------------------------
def check(name: str):
    def decorator(func):
        func._check_name = name
        return func

    return decorator


def eq(actual, expected, note=""):
    if actual != expected:
        raise AssertionError(f"{note}\n  期望: {expected!r}\n  实际: {actual!r}")


def ok(condition, note=""):
    if not condition:
        raise AssertionError(note or "条件不成立")


def raises(exc_type, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except exc_type:
        return True
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(
            f"期望 {exc_type.__name__}，实际 {type(exc).__name__}: {exc}"
        ) from exc
    raise AssertionError(f"期望抛出 {exc_type.__name__}，但没有异常")


# --------------------------------------------------------------------------
# 导入项目模块（Qt 部分延后到需要时）
# --------------------------------------------------------------------------
# 先导入 StateManager 并重定向可写产物，再导入会记录日志的模块，
# 避免检查过程把 load_config 等日志写进仓库的 doc/log.log。
from lib import StateManager  # noqa: E402

StateManager.configure_paths(
    {
        "paths": {
            "memory_file": os.path.join(TMP, "memory.json"),
            "log_file": os.path.join(TMP, "log.log"),
        }
    }
)
StateManager.configure_logging("DEBUG")

from lib import LanguageManager, Lift, Multi, ScrollSingle, ThemeManager  # noqa: E402
from lib import importnames  # noqa: E402

# QApplication 必须在任何 QWidget 之前创建（ScrollSingle 控制器会构造控件）
from PySide6.QtWidgets import QApplication  # noqa: E402

_APP = QApplication.instance() or QApplication([])

ROSTER = {"0": "周〇", "1": "张三", "2": "李四", "3": "王五", "4": "赵六", "5": "孙七"}


# ==========================================================================
# A. 抽取算法行为保持不变
# ==========================================================================
@check("A1 Multi：抽取数量正确、无重复、outdict 结构不变")
def _a1():
    out = Multi.Multi(ROSTER, 3)
    eq(out["mode"], "Multi")
    eq(out["quantity"], {"total": 6, "selected": 3})
    eq(len(out["outdict"]), 3)
    eq(sorted(out["outdict"]), ["0", "1", "2"])
    names = [v["name"] for v in out["outdict"].values()]
    eq(len(set(names)), 3, "同一次抽取不得重复")
    for key, value in out["outdict"].items():
        eq(set(value), {"code", "name"}, "Multi 的 value 必须是 {code,name}")
        eq(ROSTER[value["code"]], value["name"])


@check("A2 Multi：数量超出总数返回空 outdict 且不消耗名单")
def _a2():
    out = Multi.Multi(ROSTER, 99)
    eq(out["outdict"], {})
    eq(out["quantity"], {"total": 6, "selected": 99})
    eq(len(ROSTER), 6, "原名单不得被修改")


@check("A3 Lift：抽中者移出剩余名单，剩余保持字典形态")
def _a3():
    out = Lift.Lift(ROSTER, ROSTER, 2)
    eq(out["mode"], "Lift")
    eq(out["quantity"]["total"], 6)
    eq(out["quantity"]["wasted"], 0)
    eq(out["quantity"]["selected"], 2)
    eq(out["quantity"]["Lift"], 4)
    eq(len(out["outdict"]), 2)
    eq(len(out["Liftdict"]), 4)
    picked = {k for v in out["outdict"].values() for k in v}
    eq(len(picked), 2)
    ok(not (picked & set(out["Liftdict"])), "抽中者不得留在剩余名单中")
    eq(out["alllist"], ROSTER, "alllist 必须原样保留完整名单")


@check("A4 Lift：剩余为空时返回空 outdict 并保留空剩余")
def _a4():
    out = Lift.Lift(ROSTER, {}, 1)
    eq(out["outdict"], {})
    eq(out["Liftdict"], {})


@check("A5 Lift：数量大于剩余时返回空 outdict 并原样保留剩余")
def _a5():
    remain = {"0": "周〇", "1": "张三"}
    out = Lift.Lift(ROSTER, remain, 5)
    eq(out["outdict"], {})
    eq(out["Liftdict"], remain, "失败时剩余名单不得丢失")


# ==========================================================================
# B. 修复：主配置回退为深拷贝（原为浅拷贝，嵌套表被污染后无法再次回退）
# ==========================================================================
@check("B1 StateManager：内建配置改为深拷贝，调用方改写不污染模块常量")
def _b1():
    from pathlib import Path

    original_paths = (StateManager.CONFIG_PATH, StateManager.DEFAULT_CONFIG_PATH)
    try:
        # 注意：假路径必须位于 ROOT 之下，否则 load_config 的 relative_to(ROOT) 会抛错
        StateManager.CONFIG_PATH = Path(ROOT) / "checks" / "_absent-a.toml"
        StateManager.DEFAULT_CONFIG_PATH = Path(ROOT) / "checks" / "_absent-b.toml"
        cfg = StateManager.load_config()
        eq(StateManager.CONFIG_SOURCE, "built-in")
        # 模拟调用方改写嵌套表
        cfg["app"]["default_mode"] = "Lift"
        cfg["splash"]["duration_ms"] = 99999
        eq(StateManager.BUILTIN_CONFIG["app"]["default_mode"], "Multi",
           "BUILTIN_CONFIG 被污染了")
        eq(StateManager.BUILTIN_CONFIG["splash"]["duration_ms"], 1000,
           "BUILTIN_CONFIG 嵌套表被污染了")
        cfg2 = StateManager.load_config()
        eq(cfg2["app"]["default_mode"], "Multi", "第二次回退应重新得到干净的默认值")
    finally:
        StateManager.CONFIG_PATH, StateManager.DEFAULT_CONFIG_PATH = original_paths
        StateManager.load_config()


# ==========================================================================
# C. 修复：reload_data 与导入时的空名单回退保持一致
# ==========================================================================
@check("C1 importnames：reload_data 遇到空 names 时回退到单人名单")
def _c1():
    saved_loader = StateManager.load_rosters
    saved_rosters = dict(importnames.rosters)
    saved_active = importnames.active_roster
    saved_names = dict(importnames.names)
    try:
        # 模拟 name.toml 解析成功但 names 为空字典（load_rosters 未过滤干净的极端情况）
        StateManager.load_rosters = lambda: (
            {"class_1": {"name": {"en_US": "X"}, "names": {}}},
            False,
        )
        importnames.reload_data()
        eq(importnames.names, {"0": "Student 1"},
           "空的 names 必须回退，不得让程序无可抽之人")
    finally:
        StateManager.load_rosters = saved_loader
        importnames.rosters = saved_rosters
        importnames.active_roster = saved_active
        importnames.names = saved_names


@check("C2 importnames：_names_for 对缺失/非字典/空表均回退")
def _c2():
    eq(importnames._names_for({}, "class_1"), {"0": "Student 1"})
    eq(importnames._names_for({"c": {"names": {"1": "A"}}}, "c"), {"1": "A"})
    eq(importnames._names_for({"c": {"names": {}}}, "c"), {"0": "Student 1"})
    eq(importnames._names_for({"c": {"names": "bad"}}, "c"), {"0": "Student 1"})


@check("C3 importnames：select_roster 遇无效名单保持原状态不变")
def _c3():
    saved_names = dict(importnames.names)
    saved_active = importnames.active_roster
    try:
        before = importnames.select_roster("不存在的名单")
        eq(before, saved_names, "无效名单不得改变当前名单")
        eq(importnames.active_roster, saved_active)
    finally:
        importnames.names = saved_names
        importnames.active_roster = saved_active


# ==========================================================================
# D. 修复：主题颜色解析对非法类型抛 ValueError（原先抛 AttributeError）
# ==========================================================================
@check("D1 ThemeManager：非字符串颜色抛 ValueError 而非 AttributeError")
def _d1():
    raises(ValueError, ThemeManager._color, 12345, "HexA")
    raises(ValueError, ThemeManager._color, None, "HexA")
    raises(ValueError, ThemeManager._color, "", "Hex")
    raises(ValueError, ThemeManager._color, "   ", "Hex")
    raises(ValueError, ThemeManager._color, {"r": 1}, "HexA")


@check("D2 ThemeManager：既有合法颜色转换结果不变")
def _d2():
    eq(ThemeManager._color("#211823FF", "HexA"), "rgba(33, 24, 35, 1.000)")
    eq(ThemeManager._color("#211823FF", "HexA", False), "rgba(33, 24, 35, 1.000)")
    eq(ThemeManager._color("#211823", "Hex"), "rgba(33, 24, 35, 1.000)")
    eq(ThemeManager._color("33,24,35", "RGB"), "rgba(33, 24, 35, 1.000)")
    eq(ThemeManager._color("33,24,35,128", "RGBA"), "rgba(33, 24, 35, 0.502)")
    eq(ThemeManager._color("33,24,35,128", "RGBA", False), "rgba(33, 24, 35, 1.000)")
    raises(ValueError, ThemeManager._color, "1,2", "RGB")
    raises(ValueError, ThemeManager._color, "#GGG", "Hex")
    raises(ValueError, ThemeManager._color, "#fff", "CMYK")


@check("D3 ThemeManager：主题目录加载与默认主题解析不变")
def _d3():
    themes = ThemeManager.discover_themes()
    ok(len(themes) >= 13, f"应至少加载 13 套主题，实际 {len(themes)}")
    eq(ThemeManager.THEME_LOAD_WARNING, None)
    eq(ThemeManager.CONFIGURED_DEFAULT, "randname-dark")
    eq(ThemeManager.resolve_startup_theme(themes, "blue-light"), "randname-dark",
       "theme.toml 的 default 优先于 config.toml")
    eq(ThemeManager.resolve_startup_theme(themes, "blue-light" if not
                                          ThemeManager.CONFIGURED_DEFAULT else "x"),
       ThemeManager.CONFIGURED_DEFAULT)


@check("D4 ThemeManager：损坏的 theme.toml 回退到内建主题并记录警告")
def _d4():
    from pathlib import Path

    bad = Path(TMP) / "bad-theme.toml"
    bad.write_text("[themes.x]\ncolor_format = 'HexA'\n", encoding="utf-8")  # 缺 name/colors
    themes = ThemeManager.discover_themes(bad)
    eq(list(themes), ["randname-dark"])
    ok(ThemeManager.THEME_LOAD_WARNING and "bad-theme.toml" in ThemeManager.THEME_LOAD_WARNING)
    # 恢复真实主题目录
    ThemeManager.discover_themes()


# ==========================================================================
# E. 修复/加固：ScrollController
# ==========================================================================
def _make_controller(**kwargs):
    from PySide6.QtWidgets import QLabel, QPushButton

    params = dict(
        label_widget=QLabel("等待输入"),
        start_button=QPushButton("开始"),
        stop_button=QPushButton("停止"),
        names_dict=dict(ROSTER),
        on_result=None,
        rate=30,
    )
    params.update(kwargs)
    return ScrollSingle.ScrollController(**params)


@check("E1 修复：未运行时调用 stop() 不再触发 on_result（原会写入伪造记忆）")
def _e1():
    calls = []
    ctrl = _make_controller(on_result=lambda r, m: calls.append((r, m)))
    ctrl.label.setText("张三")
    eq(ctrl.running, False)
    eq(ctrl.stop(), "张三", "返回值仍为当前标签文本")
    eq(calls, [], "未运行时的 stop() 不得触发回调")


@check("E2 行为不变：start→stop 恰好触发一次 on_result")
def _e2():
    calls = []
    ctrl = _make_controller(on_result=lambda r, m: calls.append((r, m)))
    ctrl.start()
    ok(ctrl.running)
    ctrl.start()  # 幂等
    ctrl._tick()
    result = ctrl.stop()
    ok(not ctrl.running)
    eq(len(calls), 1, f"应只触发一次回调，实际 {len(calls)}")
    eq(calls[0][0], ctrl.label.text())
    eq(calls[0][1]["mode"], "ScrollSingle")
    eq(result, ctrl.label.text(), "结果必须等于停止瞬间标签文本")
    ok(result in ROSTER.values(), "结果必须是名单中的人")


@check("E3 修复：update_rate 可在刷新后生效")
def _e3():
    ctrl = _make_controller(rate=30)
    eq(ctrl.timer.interval(), 33)
    eq(ctrl.update_rate(10), 100)
    eq(ctrl.timer.interval(), 100)
    eq(ctrl.update_rate(1), 1000)
    ok(not ctrl.running, "改速率不得改变运行状态")


@check("E4 加固：非法 rate 不抛异常；数值语义与改动前完全一致")
def _e4():
    # 原实现为 max(1, 1000 // max(1, int(rate)))，此处必须逐值对齐
    eq(ScrollSingle._interval_for_rate(30), 33)
    eq(ScrollSingle._interval_for_rate(1), 1000)
    eq(ScrollSingle._interval_for_rate(60), 16)
    eq(ScrollSingle._interval_for_rate(100000), 1)
    # 非正数被夹到 1 tick/s（与改动前一致）
    eq(ScrollSingle._interval_for_rate(0), 1000)
    eq(ScrollSingle._interval_for_rate(-5), 1000)
    # 新增：无法转成整数的值不再抛 TypeError/ValueError
    eq(ScrollSingle._interval_for_rate("abc"), 33)
    eq(ScrollSingle._interval_for_rate(None), 33)
    eq(ScrollSingle._interval_for_rate([1]), 33)
    eq(ScrollSingle._interval_for_rate(30.0), 33)


@check("E5 修复：reset 使用传入的本地化文案")
def _e5():
    ctrl = _make_controller(reset_text="Ready")
    ctrl.label.setText("张三")
    ctrl.reset()
    eq(ctrl.label.text(), "Ready")
    eq(ctrl.selected, None)


@check("E6 行为不变：update_names 热替换不打断滚动")
def _e6():
    ctrl = _make_controller()
    ctrl.start()
    ctrl.update_names({"9": "新同学"})
    ok(ctrl.running, "update_names 不得停止滚动")
    ok(ctrl.start_button.isEnabled() is False, "按钮启用态不得被 update_names 改动")
    ok(ctrl.stop_button.isEnabled() is True)
    eq(sorted(ctrl.names), ["9"])
    eq(sorted({v for v in ctrl.current_order}), ["新同学"])


# ==========================================================================
# F/G/H. 主窗口相关（需要 QApplication，offscreen）
# ==========================================================================
def _load_main_module():
    import main
    from lib import (Lift as lift_module, Multi as multi_module,
                     ui_main, ui_widgetlift, ui_widgetmulti, ui_widgetscrollsingle)

    main.lift_module = lift_module
    main.multi_module = multi_module
    main.ScrollSingle = ScrollSingle
    main.StateManager = StateManager
    main.ThemeManager = ThemeManager
    main.importnames = importnames
    main.LanguageManager = LanguageManager
    main.ui_main = ui_main
    main.ui_widgetmulti = ui_widgetmulti
    main.ui_widgetlift = ui_widgetlift
    main.ui_widgetscrollsingle = ui_widgetscrollsingle
    return main


_app = _APP
_window = None


def _ensure_window():
    """构造一次共享的 MainWindow，供 F/G/H 组用例复用。"""
    global _window
    if _window is not None:
        return _window
    main = _load_main_module()
    themes = ThemeManager.discover_themes()
    languages, preferred, _warn = LanguageManager.load_languages()
    theme = ThemeManager.resolve_startup_theme(themes, "randname-dark")
    language = LanguageManager.resolve_startup_language(languages, preferred, "en_US")
    _window = main.MainWindow(
        themes, theme, languages, language,
        importnames.rosters, importnames.active_roster, [],
    )
    _window.show()
    _APP.processEvents()
    return _window


@check("F1 修复：导入记忆时结果为 null 不得显示字面量 None")
def _f1():
    win = _ensure_window()
    win._handle_multi()
    eq(win.multi_label.text() != "None", True)
    before_multi = win.multi_label.text()
    before_lift = win.lift_label.text()
    before_scroll = win.scroll_label.text()

    win._apply_memory_import(
        {"loaded_config": None, "last_results": {"Multi": None, "Lift": None,
                                                 "ScrollSingle": None}}
    )
    eq(win.multi_label.text(), before_multi, "null 结果不得覆盖现有显示")
    eq(win.lift_label.text(), before_lift)
    eq(win.scroll_label.text(), before_scroll)
    ok("None" not in (win.multi_label.text(), win.lift_label.text(),
                      win.scroll_label.text()), "标签不得出现字面量 None")


@check("F2 行为不变：导入记忆时正常回填结果文本")
def _f2():
    win = _ensure_window()
    win._apply_memory_import(
        {
            "loaded_config": None,
            "last_results": {
                # 改动前 dict 结果就是 str(dict) 直出，这里锁定该行为不变
                "Multi": {"result": {"outdict": {"0": {"code": "1", "name": "张三"}}}},
                "Lift": {"result": {"outdict": {"0": {"1": "张三"}}}},
                "ScrollSingle": {"result": "李四", "meta": {}},
            },
        }
    )
    ok("张三" in win.multi_label.text(), "Multi 结果应包含姓名")
    eq(type(win.multi_label.text()), str)
    ok("张三" in win.lift_label.text(), "Lift 结果应包含姓名")
    eq(win.scroll_label.text(), "李四")
    eq(win.scroll_has_result, True)
    # 兼容小写键
    win._apply_memory_import({"last_results": {"multi": "小写兼容"}})
    eq(win.multi_label.text(), "小写兼容")
    # 非字典内容静默忽略
    size_before = win.size()
    win._apply_memory_import("不是字典")
    eq(win.size(), size_before, "导入不得改变窗口尺寸")


@check("G1 修复：切换语言时已产生的滚动结果不被占位文案覆盖")
def _g1():
    win = _ensure_window()
    win.scroll_has_result = True
    win.scroll_label.setText("王五")
    win._select_language("en_US")
    eq(win.scroll_label.text(), "王五", "已有结果必须保留")
    win._select_language("zh_CN")
    eq(win.scroll_label.text(), "王五")


@check("G2 修复：无结果时切换语言会刷新占位文案（不再依赖硬编码字面量）")
def _g2():
    win = _ensure_window()
    win.scroll_has_result = False
    win.scroll_label.setText(win._t("state.waiting"))
    win._select_language("en_US")
    eq(win.scroll_label.text(), "Ready")
    win._select_language("zh_CN")
    eq(win.scroll_label.text(), "等待输入")
    win._select_language("zh_TW")
    eq(win.scroll_label.text(), "等待輸入")
    win._select_language("zh_CN")


@check("G3 行为不变：多抽/减量抽结果在切换语言后保留")
def _g3():
    win = _ensure_window()
    win._select_language("zh_CN")
    win.multi_quantity = 2
    win._handle_multi()
    multi_before = win.multi_label.text()
    lift_before = win.lift_label.text()
    win._select_language("en_US")
    eq(win.multi_label.text(), multi_before)
    eq(win.lift_label.text(), lift_before)
    win._select_language("zh_CN")


@check("H1 修复：暂无结果改为国际化文案")
def _h1():
    win = _ensure_window()
    win._select_language("en_US")
    eq(win._format_output_result({}), "No result")
    eq(win._format_output_result({"outdict": {}}), "No result")
    eq(win._format_output_result({"outdict": {}, "Liftdict": {}}), "No result")
    win._select_language("zh_CN")
    eq(win._format_output_result({}), "暂无结果")
    win._select_language("zh_TW")
    eq(win._format_output_result({}), "暫無結果")
    win._select_language("zh_CN")


@check("H2 修复：减量抽重置使用本地化等待文案")
def _h2():
    win = _ensure_window()
    win._select_language("en_US")
    win._reset_lift_page()
    eq(win.lift_label.text(), "Ready")
    win._select_language("zh_CN")
    win._reset_lift_page()
    eq(win.lift_label.text(), "等待输入")


@check("H3 修复：新增文案键已进入内建英语与三个语言包")
def _h3():
    eq(LanguageManager.ENGLISH["state.no_result"], "No result")
    eq(LanguageManager.ENGLISH["error.theme_failed"], "Could not apply the theme: {error}")
    languages, preferred, warning = LanguageManager.load_languages()
    eq(warning, None)
    eq(sorted(k for k in languages if k != "en_US"), ["zh_CN", "zh_TW"])
    eq(languages["zh_CN"]["text"]["state.no_result"], "暂无结果")
    eq(languages["zh_CN"]["text"]["error.theme_failed"], "无法应用主题：{error}")
    eq(languages["zh_TW"]["text"]["state.no_result"], "暫無結果")
    eq(languages["zh_TW"]["text"]["error.theme_failed"], "無法套用主題：{error}")
    # 每个语言包都必须覆盖全部内建键
    for code, pack in languages.items():
        missing = set(LanguageManager.ENGLISH) - set(pack["text"])
        eq(missing, set(), f"语言包 {code} 缺少文案键")
    # 翻译时占位符可用
    eq(
        LanguageManager.translate(languages, "en_US", "error.theme_failed",
                                  error="boom"),
        "Could not apply the theme: boom",
    )


@check("H4 行为不变：语言切换会重建四个互斥菜单")
def _h4():
    win = _ensure_window()
    for code in ("en_US", "zh_CN", "zh_TW"):
        win._select_language(code)
        eq(win.current_language, code)
        eq(win.language_actions.isExclusive(), True)
        checked = [a for a in win.language_actions.actions() if a.isChecked()]
        eq(len(checked), 1, "互斥组必须恰有一个勾选项")
        eq(checked[0].data(), code)
        eq(win.theme_actions.isExclusive(), True)
        eq(win.roster_actions.isExclusive(), True)
        eq(win.log_level_actions.isExclusive(), True)
    win._select_language("zh_CN")


# ==========================================================================
# I. 端到端：损坏的 theme.toml 不得阻断启动
# ==========================================================================
@check("I1 集成：theme.toml 颜色非法时程序仍能启动（不崩溃）")
def _i1():
    sandbox = os.path.join(TMP, "e2e")
    if os.path.isdir(sandbox):
        shutil.rmtree(sandbox)
    os.makedirs(sandbox)
    for item in ("main.py", ".config.default.toml", ".name.default.toml"):
        shutil.copy2(os.path.join(ROOT, item), sandbox)
    for item in ("lib", "config", "ui", "doc"):
        shutil.copytree(
            os.path.join(ROOT, item), os.path.join(sandbox, item),
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "memory.json", "log.log"),
        )
    # 注入非法颜色：非字符串，discover_themes 的结构校验放行，_stylesheet 才失败
    theme_file = os.path.join(sandbox, "config", "theme.toml")
    with open(theme_file, "r", encoding="utf-8") as handle:
        text = handle.read()
    text = text.replace('background = "#211823FF"', "background = 12345", 1)
    with open(theme_file, "w", encoding="utf-8") as handle:
        handle.write(text)

    env = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONPATH=sandbox)
    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=sandbox, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    deadline = time.time() + 12
    crashed = None
    while time.time() < deadline:
        if proc.poll() is not None:
            out, err = proc.communicate()
            crashed = (proc.returncode, out.decode(errors="replace"),
                       err.decode(errors="replace"))
            break
        time.sleep(0.4)
    if crashed is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        ok(True, "程序保持运行（app.exec() 未退出），启动未被阻断")
        return
    code, out, err = crashed
    raise AssertionError(
        f"程序启动失败，退出码 {code}\n--- stdout ---\n{out[-2000:]}\n--- stderr ---\n{err[-3000:]}"
    )


@check("I2 集成：正常配置下程序同样能进入事件循环")
def _i2():
    sandbox = os.path.join(TMP, "e2e-ok")
    if os.path.isdir(sandbox):
        shutil.rmtree(sandbox)
    os.makedirs(sandbox)
    for item in ("main.py", ".config.default.toml", ".name.default.toml"):
        shutil.copy2(os.path.join(ROOT, item), sandbox)
    for item in ("lib", "config", "ui", "doc"):
        shutil.copytree(
            os.path.join(ROOT, item), os.path.join(sandbox, item),
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "memory.json", "log.log"),
        )
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONPATH=sandbox)
    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=sandbox, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    deadline = time.time() + 12
    while time.time() < deadline:
        if proc.poll() is not None:
            out, err = proc.communicate()
            raise AssertionError(
                f"程序异常退出，退出码 {proc.returncode}\n"
                f"--- stdout ---\n{out[-2000:]}\n--- stderr ---\n{err[-3000:]}"
            )
        time.sleep(0.4)
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


# ==========================================================================
# J. 其他行为保持不变
# ==========================================================================
@check("J1 行为不变：数量加减按名单长度夹紧")
def _j1():
    win = _ensure_window()
    saved_names = win.names
    win.names = {"0": "A", "1": "B", "2": "C"}
    win.multi_quantity = 3
    win._adjust_quantity("multi", 1)
    eq(win.multi_quantity, 3, "不得超出名单长度")
    eq(win.multi_quantity_label.text(), "3")
    win._adjust_quantity("multi", -5)
    eq(win.multi_quantity, 1, "不得低于 1")
    eq(win.multi_quantity_label.text(), "1")
    win.lift_quantity = 1
    win._adjust_quantity("lift", 1)
    eq(win.lift_quantity, 2)
    eq(win.lift_quantity_label.text(), "2")
    win._adjust_quantity("multi", 99)
    eq(win.multi_quantity, 3)
    win.multi_quantity = 1
    win.lift_quantity = 1
    win._set_quantity_label(win.multi_quantity_label, win.multi_quantity)
    win._set_quantity_label(win.lift_quantity_label, win.lift_quantity)
    win.names = saved_names


@check("J2 行为不变：结果排版每行 4 人、两空格分隔")
def _j2():
    win = _ensure_window()
    out = {"outdict": {str(i): {"code": str(i), "name": f"N{i}"} for i in range(4)}}
    eq(win._format_output_result(out), "N0  N1  N2  N3")
    out5 = {"outdict": {str(i): {"code": str(i), "name": f"N{i}"} for i in range(5)}}
    eq(win._format_output_result(out5), "N0  N1  N2  N3\nN4")
    lift_out = {"outdict": {}, "Liftdict": {"0": "张三", "1": "李四"}}
    eq(win._format_output_result(lift_out), "张三  李四")
    multi_out = {"outdict": {"0": {"1": "张三"}}}
    eq(win._format_output_result(multi_out), "张三")
    eq(win._format_output_result("纯字符串"), "纯字符串")


@check("J3 行为不变：减量抽跨轮消耗，记忆按轮次累积")
def _j3():
    win = _ensure_window()
    win._select_language("zh_CN")
    win._reset_lift_page()
    win.names = dict(ROSTER)
    win.lift_quantity = 2
    win._handle_lift()
    first = set(win.lift_current_dict)
    eq(len(first), 4)
    win._handle_lift()
    eq(len(win.lift_current_dict), 2)
    ok(not (set(win.lift_current_dict) & (set(ROSTER) - first)),
       "第二轮不得抽到已抽走的人")
    win._reset_lift_page()
    eq(win.lift_current_dict, None, "重置后应回到完整名单")
    eq(win.lift_label.text(), "等待输入")


@check("J4 行为不变：滚动抽结果写入记忆且 on_result 正常触发")
def _j4():
    win = _ensure_window()
    StateManager.save_memory(StateManager._default_memory())
    win._select_language("zh_CN")
    win.scroll_controller.start()
    win.scroll_controller._tick()
    result = win.scroll_controller.stop()
    eq(result, win.scroll_label.text())
    eq(win.scroll_has_result, True)
    memory = StateManager.load_memory()
    eq(memory["last_results"]["ScrollSingle"]["result"], result)
    eq(memory["last_results"]["ScrollSingle"]["meta"]["mode"], "ScrollSingle")


@check("J5 行为不变：配置回退优先级链")
def _j5():
    languages, preferred, _ = LanguageManager.load_languages()
    eq(LanguageManager.resolve_startup_language(languages, "en_US", "zh_CN"), "en_US",
       "language.toml 的 preferred 优先")
    eq(LanguageManager.resolve_startup_language(languages, "", "zh_CN"), "zh_CN",
       "preferred 缺失时用 config.toml")
    eq(LanguageManager.resolve_startup_language(languages, "", "") in languages, True)
    eq(LanguageManager.resolve_language("不存在", languages) in languages, True)
    themes = ThemeManager.discover_themes()
    eq(ThemeManager.resolve_startup_theme(themes, "blue-light"), "randname-dark")
    eq(ThemeManager.resolve_startup_theme({}, "blue-light"), "")


@check("J6 行为不变：日志为单行且不含 JSON 括号")
def _j6():
    line = []
    saved = StateManager.SESSION_LOG_RECORDS
    StateManager.SESSION_LOG_RECORDS = line
    try:
        StateManager.log("WARN", "demo", result={"a": [1, 2]}, error="bad\nvalue")
    finally:
        StateManager.SESSION_LOG_RECORDS = saved
    eq(len(line), 1)
    text = line[0]
    ok("\n" not in text, "日志必须单行")
    ok("level=WARNING" in text, "'WARN' 应归一化为 'WARNING'")
    ok("{" not in text and "[" not in text, "花括号/方括号应被替换")
    ok("action=demo" in text)


@check("J7 行为不变：日志等级过滤生效")
def _j7():
    saved = StateManager.CURRENT_LOG_LEVEL
    captured = []
    saved_records = StateManager.SESSION_LOG_RECORDS
    StateManager.SESSION_LOG_RECORDS = captured
    try:
        StateManager.CURRENT_LOG_LEVEL = "WARNING"
        StateManager.log("INFO", "被过滤", result="x")
        StateManager.log("ERROR", "被保留", result="x")
        eq(len(captured), 1)
        eq("action=被保留" in captured[0], True)
    finally:
        StateManager.SESSION_LOG_RECORDS = saved_records
        StateManager.CURRENT_LOG_LEVEL = saved


@check("J8 行为不变：记忆导入导出不写回 config/")
def _j8():
    from pathlib import Path

    config_before = {}
    config_dir = os.path.join(ROOT, "config")
    for name in os.listdir(config_dir):
        path = os.path.join(config_dir, name)
        config_before[path] = os.stat(path).st_mtime_ns

    import json

    payload = {"loaded_config": {"app": {"default_mode": "Lift"}},
               "last_results": {"Multi": {"result": {"outdict": {}}}}}
    target = Path(TMP) / "in.json"
    target.write_text(json.dumps(payload), encoding="utf-8")

    StateManager.import_memory(target, apply_callback=lambda content: None)
    eq(StateManager.load_memory()["loaded_config"]["app"]["default_mode"], "Lift")

    out_path = Path(TMP) / "out.json"
    StateManager.export_memory(out_path)
    ok(out_path.is_file())

    for path, mtime in config_before.items():
        eq(os.stat(path).st_mtime_ns, mtime, f"config/ 文件被改写: {path}")


# ==========================================================================
# 运行
# ==========================================================================
def _collect():
    return [value for value in globals().values()
            if callable(value) and hasattr(value, "_check_name")]


def main() -> int:
    global _FILTER
    if "--only" in sys.argv:
        _FILTER = sys.argv[sys.argv.index("--only") + 1]

    checks = _collect()
    if _FILTER:
        checks = [c for c in checks if _FILTER in c._check_name]

    passed = 0
    failed: list[tuple[str, str]] = []
    for func in checks:
        name = func._check_name
        started = time.time()
        try:
            func()
        except Exception:  # noqa: BLE001
            failed.append((name, traceback.format_exc()))
            print(f"  [FAIL] {name}")
        else:
            passed += 1
            print(f"  [ OK ] {name}  ({time.time() - started:.2f}s)")

    print("-" * 70)
    print(f"总计 {len(checks)} 项：通过 {passed}，失败 {len(failed)}")
    for name, tb in failed:
        print("=" * 70)
        print(f"失败用例：{name}")
        print(tb)

    shutil.rmtree(TMP, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
