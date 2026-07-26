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

from PySide6.QtCore import QFile, QUrl
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox, QPushButton, QStackedWidget

from lib import Lift as lift_module
from lib import Multi as multi_module
from lib import Single as single_module
from lib import importnames

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

ROOT_DIR = Path(__file__).resolve().parent
UI_DIR = ROOT_DIR / "ui"
LICENSE_PATH = ROOT_DIR / "doc" / "LICENCE.md"
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


def load_ui(ui_path):
    """加载 .ui 文件并返回对应的 QWidget。"""
    ui_file_path = Path(ui_path)
    if not ui_file_path.is_absolute():
        ui_file_path = ROOT_DIR / ui_file_path

    ui_file = QFile(str(ui_file_path))
    if not ui_file.open(QFile.ReadOnly):
        raise RuntimeError(f"无法打开 UI 文件: {ui_file_path}")

    loader = QUiLoader()
    widget = loader.load(ui_file)
    ui_file.close()

    if widget is None:
        raise RuntimeError(f"无法加载 UI 文件: {ui_file_path}")

    logging.info("Loaded UI: %s", ui_file_path)
    return widget


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
        self.stacked_widget = None

        self.action_single = None
        self.action_multi = None
        self.action_lift = None
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

        self._build_ui()

    def _load_names(self):
        names = getattr(importnames, "names", None)
        if isinstance(names, dict) and names:
            return names
        logging.warning("未能从 importnames 中读取姓名数据，使用空列表。")
        return {}

    def _build_ui(self):
        try:
            self.ui = load_ui(UI_DIR / "Main.ui")
            # 在移动 UI 元素之前查找 stackedWidget
            self.stacked_widget = self.ui.findChild(QStackedWidget, "stackedWidget")
            if self.stacked_widget is None:
                raise RuntimeError("未找到 stackedWidget")
            
            self.setWindowTitle(self.ui.windowTitle() or "randname")
            self.setCentralWidget(self.ui.centralWidget())
            self.setMenuBar(self.ui.menuBar())
            self.setStatusBar(self.ui.statusBar())
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
        self.action_single = self.ui.findChild(QAction, "action_Single")
        self.action_multi = self.ui.findChild(QAction, "action_Multi")
        self.action_lift = self.ui.findChild(QAction, "action_Lift")
        self.action_exit = self.ui.findChild(QAction, "action_exit")
        self.action_license = self.ui.findChild(QAction, "action_license")
        self.action_repository = self.ui.findChild(QAction, "action_repository")

        if self.action_single:
            self.action_single.triggered.connect(self._show_single_page)
        if self.action_multi:
            self.action_multi.triggered.connect(self._show_multi_page)
        if self.action_lift:
            self.action_lift.triggered.connect(self._show_lift_page)
        if self.action_exit:
            self.action_exit.triggered.connect(self._on_exit)
        if self.action_license:
            self.action_license.triggered.connect(self._open_license)
        if self.action_repository:
            self.action_repository.triggered.connect(self._open_repository)

    def _load_pages(self):
        if self.stacked_widget is None:
            raise RuntimeError("stackedWidget 未初始化")

        self.page_single = load_ui(UI_DIR / "WidgetSingle.ui")
        self.page_multi = load_ui(UI_DIR / "WidgetMulti.ui")
        self.page_lift = load_ui(UI_DIR / "WidgetLift.ui")

        self.stacked_widget.addWidget(self.page_single)
        self.stacked_widget.addWidget(self.page_multi)
        self.stacked_widget.addWidget(self.page_lift)
        self.stacked_widget.setCurrentWidget(self.page_single)

    def _bind_page_actions(self):
        self.single_button = self.page_single.findChild(QPushButton, "pushButton")
        self.single_label = self.page_single.findChild(QLabel, "label_SingleOutput")
        if self.single_button and self.single_label:
            self.single_button.clicked.connect(self._handle_single)
            self.single_label.setText("等待输入")

        self.multi_button = self.page_multi.findChild(QPushButton, "pushButton_Multi")
        self.multi_label = self.page_multi.findChild(QLabel, "label_MultiOutput")
        self.multi_quantity_label = self.page_multi.findChild(QLabel, "label_MultiQuantity")
        self.multi_up_button = self.page_multi.findChild(QPushButton, "pushButton_MultiQuantityUp")
        self.multi_down_button = self.page_multi.findChild(QPushButton, "pushButton_MultiQuantityDown")
        if self.multi_quantity_label is not None:
            self._set_quantity_label(self.multi_quantity_label, self.multi_quantity)
        if self.multi_up_button is not None:
            self.multi_up_button.clicked.connect(lambda: self._adjust_quantity("multi", 1))
        if self.multi_down_button is not None:
            self.multi_down_button.clicked.connect(lambda: self._adjust_quantity("multi", -1))
        if self.multi_button and self.multi_label:
            self.multi_button.clicked.connect(self._handle_multi)
            self.multi_label.setText("等待输入")

        self.lift_button = self.page_lift.findChild(QPushButton, "pushButton_Lift")
        self.lift_label = self.page_lift.findChild(QLabel, "label_LiftOutput")
        self.lift_quantity_label = self.page_lift.findChild(QLabel, "label_LiftQuantity")
        self.lift_up_button = self.page_lift.findChild(QPushButton, "pushButton_LiftQuantityUp")
        self.lift_down_button = self.page_lift.findChild(QPushButton, "pushButton_LiftQuantityDown")
        self.lift_renew_button = self.page_lift.findChild(QPushButton, "pushButton_LiftRenew")
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

    def _handle_single(self):
        try:
            logging.info("执行单抽")
            result = single_module.Single(self.names)
            self._set_output_text(self.single_label, self._format_single_result(result))
            self.statusBar().showMessage(f"单抽结果: {result}")
        except Exception as exc:
            logging.exception("单抽执行失败: %s", exc)
            self._set_output_text(self.single_label, "单抽失败")
            self._show_error("单抽失败", str(exc))

    def _handle_multi(self):
        try:
            logging.info("执行多抽，数量=%s", self.multi_quantity)
            result = multi_module.Multi(self.names, self.multi_quantity)
            self._set_output_text(self.multi_label, self._format_output_result(result))
            self.statusBar().showMessage(f"多抽完成，数量={self.multi_quantity}")
        except Exception as exc:
            logging.exception("多抽执行失败: %s", exc)
            self._set_output_text(self.multi_label, "多抽失败")
            self._show_error("多抽失败", str(exc))

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
        except Exception as exc:
            logging.exception("减量抽执行失败: %s", exc)
            self._set_output_text(self.lift_label, "减量抽失败")
            self._show_error("减量抽失败", str(exc))

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
        self.lift_quantity = 1
        self.lift_current_dict = None  # 重置减量抽字典
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
