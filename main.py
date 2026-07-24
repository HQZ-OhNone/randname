"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
logo_randname = r"""
                      _                            
  _ __ __ _ _ __   __| |_ __   __ _ _ __ ___   ___  
 | '__/ _` | '_ \ / _` | '_ \ / _` | '_ ` _ \ / _ \ 
 | | | (_| | | | | (_| | | | | (_| | | | | | |  __/ 
 |_|  \__,_|_| |_|\__,_|_| |_|\__,_|_| |_| |_|\___| 
---HQZ-OhNone <ohnone_hqz@outlook.com>
"""
print(logo_randname, end="\n\n")


"""
from PySide6.QtWidgets import QApplication, QMainWindow
from lib import importnames
from lib import Lift
from lib import Single
from lib import Multi
from lib.MainWindow import Ui_MainWindow
"""


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

from pathlib import Path
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QWidget,
)


class MainWindow(QMainWindow):
    """
    整个程序唯一的主窗口。

    所有功能页面都会放到 QStackedWidget 中。
    """

    def __init__(self):

        super().__init__()

        # -------------------------------
        # 加载 ui
        # -------------------------------

        self.load_ui()

        # -------------------------------
        # 保存所有页面
        #
        # 格式：
        #
        # {
        #     "mode_a": QWidget,
        #     "mode_b": QWidget,
        # }
        # -------------------------------

        self.pages = {}

        # 初始化界面
        self.initialize()

    # ==========================================================
    # UI
    # ==========================================================

    def load_ui(self):
        """
        加载 Qt Designer 设计的 MainWindow.ui
        """

        ui_file = Path(__file__).parent.parent / "ui" / "mainwindow.ui"

        loader = QUiLoader()

        file = QFile(str(ui_file))
        file.open(QFile.ReadOnly)

        #
        # 注意：
        #
        # load() 返回的是一个 QMainWindow
        #
        self.ui: QMainWindow = loader.load(file)

        file.close()

        #
        # 由于我们继承的是 QMainWindow，
        # 所以需要把 ui 的中央部件接管过来。
        #

        self.setCentralWidget(self.ui.centralWidget())

        # 菜单栏
        self.setMenuBar(self.ui.menuBar())

        # 状态栏
        self.setStatusBar(self.ui.statusBar())

        # 工具栏（Designer 中可以创建多个）
        for toolbar in self.ui.findChildren(type(self.ui.toolBar)):
            self.addToolBar(toolbar)

        self.setWindowTitle(self.ui.windowTitle())

        self.resize(self.ui.size())

        #
        # 获取 stackedWidget
        #

        self.stackedWidget = self.ui.findChild(
            QWidget,
            "stackedWidget"
        )

    # ==========================================================
    # 初始化
    # ==========================================================

    def initialize(self):
        """
        初始化整个程序
        """

        self.init_status_bar()

        self.connect_menu()

    # ==========================================================
    # StatusBar
    # ==========================================================

    def init_status_bar(self):
        """
        初始化状态栏
        """

        self.statusBar().showMessage("程序已启动")

    # ==========================================================
    # 页面管理
    # ==========================================================

    def register_page(self, name: str, page: QWidget):
        """
        注册一个页面。

        参数
        ----

        name:
            页面名字。

        page:
            QWidget。

        例如：

            register_page("mode_a", page)
        """

        self.pages[name] = page

        self.stackedWidget.addWidget(page)

    def switch_page(self, name: str):
        """
        根据名字切换页面。

        Parameters
        ----------

        name

            页面名称。
        """

        if name not in self.pages:

            QMessageBox.warning(
                self,
                "错误",
                f"页面 {name} 不存在"
            )

            return

        self.stackedWidget.setCurrentWidget(
            self.pages[name]
        )

        self.statusBar().showMessage(
            f"当前模式：{name}"
        )

    # ==========================================================
    # 菜单
    # ==========================================================

    def connect_menu(self):
        """
        连接菜单信号。

        这里只连接已经存在的菜单。

        后续 ModeA ModeB
        会继续补充。
        """

        self.ui.actionExit.triggered.connect(
            self.close
        )

        self.ui.actionAbout.triggered.connect(
            self.show_about
        )

    # ==========================================================
    # Dialog
    # ==========================================================

    def show_about(self):
        """
        关于窗口。

        目前先使用 QMessageBox。

        后面会替换为 AboutDialog。
        """

        QMessageBox.information(
            self,
            "关于",
            "PySide6 示例程序"
        )