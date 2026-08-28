"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

print(r"""
randname Copyright(C) 2026 HQZ-OhNone
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute
it under certain conditions; check GPLv3 for details.

                      _                            
  _ __ __ _ _ __   __| |_ __   __ _ _ __ ___   ___  
 | '__/ _` | '_ \ / _` | '_ \ / _` | '_ ` _ \ / _ \ 
 | | | (_| | | | | (_| | | | | (_| | | | | | |  __/ 
 |_|  \__,_|_| |_|\__,_|_| |_|\__,_|_| |_| |_|\___| 
---HQZ-OhNone <ohnone_hqz@outlook.com>
""", end="\n\n")


import logging
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox, QPushButton, QStackedWidget, QWidget, QMenuBar, QStatusBar

from lib import Lift as lift_module
from lib import Multi as multi_module
from lib import Single as single_module
from lib import importnames
from lib import StateManager
from lib import ScrollSingle
# 導入已經由 pyside6-uic 編譯並放在 lib/ 的 UI 模塊
from lib import ui_main
from lib import ui_widgetsingle
from lib import ui_widgetmulti
from lib import ui_widgetlift
from lib import ui_widgetscrollsingle

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

ROOT_DIR = Path(__file__).resolve().parent
UI_DIR = ROOT_DIR / "ui"
LICENSE_PATH = ROOT_DIR / "doc" / "gpl-3.0.txt"
REPO_URL = "https://www.github.com/HQZ-OhNone/randname"


"""
主窗口

整个程序只有一个 MainWindow。

MainWindow 负责：

1. 菜单栏
2. 工具栏
3. 状态栏
4. 页面管理（QStackedWidget）
5. 页面切换
6. 打开各种 Dialog
"""


# 注意：UI 不再在运行时从 .ui 动态加载
# 已改为在构建前用 pyside6-uic 编译 .ui 为 Python 模块，放在 lib/ 目录下
# 因此不需要 load_ui 函数（也避免运行时依赖 ui/ 目录）


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.names = self._load_names()
        self.multi_quantity = 1
        self.lift_quantity = 1
        self.lift_current_dict = None  # 保存当前减量抽的字典

        self.ui = None
        self.page_single = None
        self.page_multi = None
        self.page_lift = None
        self.page_scrollsingle = None
        self.stacked_widget = None

        self.action_single = None
        self.action_multi = None
        self.action_lift = None
        self.action_scrollsingle = None
        self.action_exit = None
        self.action_license = None
        self.action_repository = None

        self.single_button = None
        self.single_label = None
        self.multi_button = None
        self.multi_label = None
        self.multi_quantity_label = None
        self.multi_up_button = None
        self.multi_down_button = None
        self.lift_button = None
        self.lift_label = None
        self.lift_quantity_label = None
        self.lift_up_button = None
        self.lift_down_button = None
        self.lift_renew_button = None

        # ScrollSingle widgets & controller
        self.scroll_button = None
        self.scroll_label = None
        self.scroll_controller = None

        self._build_ui()

    def _load_names(self):
        names = getattr(importnames, "names", None)
        if isinstance(names, dict) and names:
            return names
        logging.warning("未能从 importnames 中读取姓名数据，使用空列表。")
        return {}

    def _build_ui(self):
        # 使用已編譯的 Python UI 模塊（lib/ui_*.py），避免運行時依賴 .ui 文件
        try:
            # Ui_MainWindow.setupUi 會把 menubar, centralwidget, statusbar 等設置到本 QMainWindow 實例上
            self.ui_main = ui_main.Ui_MainWindow()
            self.ui_main.setupUi(self)

            # 獲取 stacked widget（必須由 Ui 定義為屬性 stackedWidget）
            self.stacked_widget = getattr(self.ui_main, "stackedWidget", None)
            if self.stacked_widget is None:
                raise RuntimeError("未找到 stackedWidget")

            # 設置標題（Ui.setupUi 通常已經設置，但保險起見保留回退值）
            self.setWindowTitle(self.windowTitle() or "randname")
        except Exception as exc:  # pragma: no cover - defensive path for runtime errors
            logging.exception("加载主窗口失败: %s", exc)
            self._show_error("主窗口加载失败", str(exc))
            return

        try:
            self._bind_menu_actions()
            self._load_pages()
            self._bind_page_actions()
        except Exception as exc:  # pragma: no cover - defensive path for runtime errors
            logging.exception("初始化界面控件失败: %s", exc)
            self._show_error("界面初始化失败", str(exc))

    def _bind_menu_actions(self):
        # 從編譯後的 Ui_MainWindow 模塊獲取 QAction，避免使用 findChild
        self.action_single = getattr(self.ui_main, "action_Single", None)
        self.action_multi = getattr(self.ui_main, "action_Multi", None)
        self.action_lift = getattr(self.ui_main, "action_Lift", None)
        self.action_scrollsingle = getattr(self.ui_main, "action_ScrollSingle", None)
        self.action_exit = getattr(self.ui_main, "action_exit", None)
        self.action_license = getattr(self.ui_main, "action_license", None)
        self.action_repository = getattr(self.ui_main, "action_repository", None)

        if self.action_single:
            self.action_single.triggered.connect(self._show_single_page)
        if self.action_multi:
            self.action_multi.triggered.connect(self._show_multi_page)
        if self.action_lift:
            self.action_lift.triggered.connect(self._show_lift_page)
        if self.action_scrollsingle:
            self.action_scrollsingle.triggered.connect(self._show_scrollsingle_page)
        if self.action_exit:
            self.action_exit.triggered.connect(self._on_exit)
        if self.action_license:
            self.action_license.triggered.connect(self._open_license)
        if self.action_repository:
            self.action_repository.triggered.connect(self._open_repository)

    def _load_pages(self):
        if self.stacked_widget is None:
            raise RuntimeError("stackedWidget 未初始化")

        # 使用已編譯的 UI 類來建立各頁面（避免依賴 ui/ 目錄）
        # Single 頁面
        self.page_single = QWidget()
        self.ui_single = ui_widgetsingle.Ui_Form()
        self.ui_single.setupUi(self.page_single)

        # Multi 頁面
        self.page_multi = QWidget()
        self.ui_multi = ui_widgetmulti.Ui_Form()
        self.ui_multi.setupUi(self.page_multi)

        # Lift 頁面
        self.page_lift = QWidget()
        self.ui_lift = ui_widgetlift.Ui_Form()
        self.ui_lift.setupUi(self.page_lift)

        # ScrollSingle 頁面（使用專用 UI: WidgetScrollSingle.ui -> lib/ui_widgetscrollsingle.py）
        self.page_scrollsingle = QWidget()
        self.ui_scrollsingle = ui_widgetscrollsingle.Ui_Form()
        self.ui_scrollsingle.setupUi(self.page_scrollsingle)

        self.stacked_widget.addWidget(self.page_single)
        self.stacked_widget.addWidget(self.page_multi)
        self.stacked_widget.addWidget(self.page_lift)
        self.stacked_widget.addWidget(self.page_scrollsingle)
        self.stacked_widget.setCurrentWidget(self.page_single)

    def _bind_page_actions(self):
        # Single 頁面綁定
        self.single_button = getattr(self.ui_single, "pushButton", None)
        self.single_label = getattr(self.ui_single, "label_SingleOutput", None)
        if self.single_button and self.single_label:
            self.single_button.clicked.connect(self._handle_single)
            self.single_label.setText("等待输入")

        # Multi 頁面綁定
        self.multi_button = getattr(self.ui_multi, "pushButton_Multi", None)
        self.multi_label = getattr(self.ui_multi, "label_MultiOutput", None)
        self.multi_quantity_label = getattr(self.ui_multi, "label_MultiQuantity", None)
        self.multi_up_button = getattr(self.ui_multi, "pushButton_MultiQuantityUp", None)
        self.multi_down_button = getattr(self.ui_multi, "pushButton_MultiQuantityDown", None)
        if self.multi_quantity_label is not None:
            self._set_quantity_label(self.multi_quantity_label, self.multi_quantity)
        if self.multi_up_button is not None:
            self.multi_up_button.clicked.connect(lambda: self._adjust_quantity("multi", 1))
        if self.multi_down_button is not None:
            self.multi_down_button.clicked.connect(lambda: self._adjust_quantity("multi", -1))
        if self.multi_button and self.multi_label:
            self.multi_button.clicked.connect(self._handle_multi)
            self.multi_label.setText("等待输入")

        # ScrollSingle 綁定（使用 WidgetScrollSingle 的專用控件）
        try:
            self.scroll_label = getattr(self.ui_scrollsingle, "label_ScrollSingleOutput", None)
            self.scroll_start_button = getattr(self.ui_scrollsingle, "pushButton_ScrollSingleStart", None)
            self.scroll_stop_button = getattr(self.ui_scrollsingle, "pushButton_ScrollSingleStop", None)
            if self.scroll_label is not None:
                # 默認顯示模式名稱
                try:
                    self.scroll_label.setText("滚动单抽")
                except Exception:
                    pass
            # 创建控制器，但不自动启动
            if self.scroll_start_button is not None and self.scroll_stop_button is not None and self.scroll_label is not None:
                self.scroll_controller = ScrollSingle.ScrollController(self.scroll_label, self.scroll_start_button, self.scroll_stop_button, self.names, on_result=self._on_scroll_result)
        except Exception as exc:
            logging.exception("初始化 ScrollSingle 失败: %s", exc)

        # Lift 頁面綁定
        self.lift_button = getattr(self.ui_lift, "pushButton_Lift", None)
        self.lift_label = getattr(self.ui_lift, "label_LiftOutput", None)
        self.lift_quantity_label = getattr(self.ui_lift, "label_LiftQuantity", None)
        self.lift_up_button = getattr(self.ui_lift, "pushButton_LiftQuantityUp", None)
        self.lift_down_button = getattr(self.ui_lift, "pushButton_LiftQuantityDown", None)
        self.lift_renew_button = getattr(self.ui_lift, "pushButton_LiftRenew", None)
        if self.lift_quantity_label is not None:
            self._set_quantity_label(self.lift_quantity_label, self.lift_quantity)
        if self.lift_up_button is not None:
            self.lift_up_button.clicked.connect(lambda: self._adjust_quantity("lift", 1))
        if self.lift_down_button is not None:
            self.lift_down_button.clicked.connect(lambda: self._adjust_quantity("lift", -1))
        if self.lift_renew_button is not None:
            self.lift_renew_button.clicked.connect(self._reset_lift_page)
        if self.lift_button and self.lift_label:
            self.lift_button.clicked.connect(self._handle_lift)
            self.lift_label.setText("等待输入")

    def _show_single_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_single)

    def _show_multi_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_multi)

    def _show_lift_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_lift)

    def _show_scrollsingle_page(self):
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentWidget(self.page_scrollsingle)

    def _handle_single(self):
        try:
            logging.info("执行单抽")
            result = single_module.Single(self.names)
            self._set_output_text(self.single_label, self._format_single_result(result))
            self.statusBar().showMessage(f"单抽结果: {result}")
            # 记录到内存与日志
            try:
                state = StateManager.load_memory()
                state["loaded_config"] = getattr(importnames, 'loaded_config', None)
                state.setdefault("last_results", {})["single"] = {"result": result, "time": StateManager._now_iso() if hasattr(StateManager, '_now_iso') else None}
                StateManager.save_memory(state)
                StateManager.log("INFO", "single", result=result)
            except Exception:
                logging.exception("记录 single 结果失败")
        except Exception as exc:
            logging.exception("单抽执行失败: %s", exc)
            self._set_output_text(self.single_label, "单抽失败")
            self._show_error("单抽失败", str(exc))
            try:
                StateManager.log("ERROR", "single", error=str(exc))
            except Exception:
                pass

    def _handle_multi(self):
        try:
            logging.info("执行多抽，数量=%s", self.multi_quantity)
            result = multi_module.Multi(self.names, self.multi_quantity)
            self._set_output_text(self.multi_label, self._format_output_result(result))
            self.statusBar().showMessage(f"多抽完成，数量={self.multi_quantity}")
            # 记录到内存与日志
            try:
                state = StateManager.load_memory()
                state["loaded_config"] = getattr(importnames, 'loaded_config', None)
                state.setdefault("last_results", {})["multi"] = {"result": result, "time": StateManager._now_iso() if hasattr(StateManager, '_now_iso') else None}
                StateManager.save_memory(state)
                StateManager.log("INFO", "multi", result=result)
            except Exception:
                logging.exception("记录 multi 结果失败")
        except Exception as exc:
            logging.exception("多抽执行失败: %s", exc)
            self._set_output_text(self.multi_label, "多抽失败")
            self._show_error("多抽失败", str(exc))
            try:
                StateManager.log("ERROR", "multi", error=str(exc))
            except Exception:
                pass

    def _handle_lift(self):
        try:
            logging.info("执行减量抽，数量=%s", self.lift_quantity)
            # 如果是第一次或者被重置，使用原始names字典
            if self.lift_current_dict is None:
                lift_dict = self.names
            else:
                lift_dict = self.lift_current_dict
            
            result = lift_module.Lift(self.names, lift_dict, self.lift_quantity)
            self._set_output_text(self.lift_label, self._format_output_result(result))
            
            # 保存本次结果的Liftdict，供下一次使用
            if "Liftdict" in result:
                self.lift_current_dict = result["Liftdict"]
            
            self.statusBar().showMessage(f"减量抽完成，数量={self.lift_quantity}")
            # 记录到内存与日志
            try:
                state = StateManager.load_memory()
                state["loaded_config"] = getattr(importnames, 'loaded_config', None)
                state.setdefault("last_results", {})["lift"] = {"result": result, "time": StateManager._now_iso() if hasattr(StateManager, '_now_iso') else None}
                StateManager.save_memory(state)
                StateManager.log("INFO", "lift", result=result)
            except Exception:
                logging.exception("记录 lift 结果失败")
        except Exception as exc:
            logging.exception("减量抽执行失败: %s", exc)
            self._set_output_text(self.lift_label, "减量抽失败")
            self._show_error("减量抽失败", str(exc))
            try:
                StateManager.log("ERROR", "lift", error=str(exc))
            except Exception:
                pass

    def _on_scroll_result(self, result, meta):
        # Called by ScrollSingle controller when a result is produced
        try:
            logging.info("scrollsingle result: %s", result)
            if self.scroll_label is not None:
                self.scroll_label.setText(str(result))
            # 保存到记忆与日志
            state = StateManager.load_memory()
            state["loaded_config"] = getattr(importnames, 'loaded_config', None)
            state.setdefault("last_results", {})["scrollsingle"] = {"result": result, "meta": meta}
            StateManager.save_memory(state)
            StateManager.log("INFO", "scrollsingle", result={"name": result, "meta": meta})
        except Exception as exc:
            logging.exception("处理 scrollsingle 结果失败: %s", exc)
            try:
                StateManager.log("ERROR", "scrollsingle", error=str(exc))
            except Exception:
                pass

    def _adjust_quantity(self, mode, delta):
        max_count = max(1, len(self.names))
        if mode == "multi":
            self.multi_quantity = max(1, min(max_count, self.multi_quantity + delta))
            self._set_quantity_label(self.multi_quantity_label, self.multi_quantity)
            logging.info("更新多抽数量=%s", self.multi_quantity)
        elif mode == "lift":
            self.lift_quantity = max(1, min(max_count, self.lift_quantity + delta))
            self._set_quantity_label(self.lift_quantity_label, self.lift_quantity)
            logging.info("更新减量抽数量=%s", self.lift_quantity)

    def _reset_lift_page(self):
        # 刷新减量抽页面：不改变 lift_quantity，只重置当前的 Liftdict
        self.lift_current_dict = None  # 重置减量抽字典
        # 保持数量值不变，仅更新显示
        self._set_quantity_label(self.lift_quantity_label, self.lift_quantity)
        if self.lift_label is not None:
            self.lift_label.setText("等待输入")
        self.statusBar().showMessage("减量抽已重置")

    def _set_quantity_label(self, label, value):
        if label is not None:
            label.setText(str(value))

    def _set_output_text(self, label, text):
        if label is not None:
            label.setText(text)

    def _format_single_result(self, result):
        if isinstance(result, str) and result:
            return result
        if isinstance(result, dict):
            return self._format_output_result(result)
        return "未返回结果"

    def _format_output_result(self, result):
        if not isinstance(result, dict):
            return str(result)

        outdict = result.get("outdict", {})
        if isinstance(outdict, dict) and outdict:
            items = []
            for value in outdict.values():
                if isinstance(value, dict):
                    # Multi模式：{"code": "...", "name": "..."}
                    if "name" in value:
                        item_name = value["name"]
                    # Lift模式：{"code": "name_value"}
                    elif len(value) == 1:
                        item_name = next(iter(value.values()))
                    else:
                        item_name = str(value)
                else:
                    item_name = str(value)
                items.append(str(item_name))
            if items:
                # 改进：名字较多时，一行显示多个名字，之间用空格隔开
                # 每4个名字为一行（可根据需要调整）
                if len(items) <= 4:
                    return "  ".join(items)
                else:
                    lines = []
                    for i in range(0, len(items), 4):
                        lines.append("  ".join(items[i:i+4]))
                    return "\n".join(lines)

        if isinstance(result.get("Liftdict"), dict):
            remaining = list(result["Liftdict"].values())
            if remaining:
                if len(remaining) <= 4:
                    return "  ".join(str(item) for item in remaining)
                else:
                    lines = []
                    for i in range(0, len(remaining), 4):
                        lines.append("  ".join(str(item) for item in remaining[i:i+4]))
                    return "\n".join(lines)
        return "暂无结果"

    def _on_exit(self):
        logging.info("用户请求退出程序")
        QApplication.instance().quit()

    def _open_license(self):
        try:
            if LICENSE_PATH.exists():
                logging.info("打开许可证文件: %s", LICENSE_PATH)
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(LICENSE_PATH)))
            else:
                self._show_error("许可证文件不存在", str(LICENSE_PATH))
        except Exception as exc:
            logging.exception("打开许可证文件失败: %s", exc)
            self._show_error("打开许可证失败", str(exc))

    def _open_repository(self):
        try:
            logging.info("打开项目仓库: %s", REPO_URL)
            QDesktopServices.openUrl(QUrl(REPO_URL))
        except Exception as exc:
            logging.exception("打开仓库链接失败: %s", exc)
            self._show_error("打开仓库失败", str(exc))

    def _show_error(self, title, message):
        QMessageBox.critical(self, title, message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
