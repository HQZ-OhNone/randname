# -*- coding: utf-8 -*-
"""
由 pyside6-uic 編譯生成（或等效手動實現）的 UI 模塊（主視窗）。
此檔案經過簡化：只建立 main.ui 中在程式中需要的部份屬性（如 stackedWidget、actions、menubar、statusbar、centralwidget）。
註：運行時不再需要 ui/Main.ui，程式會直接 import 該模塊。
"""

from PySide6.QtWidgets import (
    QWidget, QGridLayout, QStackedWidget, QMenuBar, QMenu, QStatusBar
)
from PySide6.QtGui import QAction


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        # central widget 與 stackedWidget（Main.ui 中的結構）
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        # menubar 與 actions
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")

        # File 菜單
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setObjectName("menu_file")
        self.menu_file.setTitle("文件")

        # Mode 菜單
        self.menu_mode = QMenu(self.menubar)
        self.menu_mode.setObjectName("menu_mode")
        self.menu_mode.setTitle("模式")

        # About 菜單
        self.menu_about = QMenu(self.menubar)
        self.menu_about.setObjectName("menu_about")
        self.menu_about.setTitle("关于")

        # Actions（程式中使用到的名稱）
        self.action_Single = QAction(MainWindow)
        self.action_Single.setObjectName("action_Single")
        self.action_Single.setText("单抽")

        self.action_Multi = QAction(MainWindow)
        self.action_Multi.setObjectName("action_Multi")
        self.action_Multi.setText("多抽")

        self.action_Lift = QAction(MainWindow)
        self.action_Lift.setObjectName("action_Lift")
        self.action_Lift.setText("减量抽")

        self.action_exit = QAction(MainWindow)
        self.action_exit.setObjectName("action_exit")
        self.action_exit.setText("退出")

        self.action_license = QAction(MainWindow)
        self.action_license.setObjectName("action_license")
        self.action_license.setText("许可证")

        self.action_repository = QAction(MainWindow)
        self.action_repository.setObjectName("action_repository")
        self.action_repository.setText("开源仓库")

        # 將 actions 加入菜單
        self.menu_file.addAction(self.action_exit)
        self.menu_mode.addAction(self.action_Single)
        self.menu_mode.addAction(self.action_Multi)
        self.menu_mode.addAction(self.action_Lift)
        self.menu_about.addAction(self.action_license)
        self.menu_about.addAction(self.action_repository)

        # 將菜單加入 menubar
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_mode.menuAction())
        self.menubar.addAction(self.menu_about.menuAction())

        MainWindow.setMenuBar(self.menubar)

        # statusbar
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # window title（與原始 .ui 保持一致）
        MainWindow.setWindowTitle("MainWindow")


# end of ui_main.py
