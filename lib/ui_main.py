# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Main.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QStackedWidget, QStatusBar,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.action_Single = QAction(MainWindow)
        self.action_Single.setObjectName(u"action_Single")
        self.action_Multi = QAction(MainWindow)
        self.action_Multi.setObjectName(u"action_Multi")
        self.action_Lift = QAction(MainWindow)
        self.action_Lift.setObjectName(u"action_Lift")
        self.action_exit = QAction(MainWindow)
        self.action_exit.setObjectName(u"action_exit")
        self.action_license = QAction(MainWindow)
        self.action_license.setObjectName(u"action_license")
        self.action_repository = QAction(MainWindow)
        self.action_repository.setObjectName(u"action_repository")
        self.action_ScrollSingle = QAction(MainWindow)
        self.action_ScrollSingle.setObjectName(u"action_ScrollSingle")
        self.action_inputconfig = QAction(MainWindow)
        self.action_inputconfig.setObjectName(u"action_inputconfig")
        self.action_outputconfig = QAction(MainWindow)
        self.action_outputconfig.setObjectName(u"action_outputconfig")
        self.action_reinputconfig = QAction(MainWindow)
        self.action_reinputconfig.setObjectName(u"action_reinputconfig")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")

        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 31))
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setObjectName(u"menu_file")
        self.menu_mode = QMenu(self.menubar)
        self.menu_mode.setObjectName(u"menu_mode")
        self.menu_about = QMenu(self.menubar)
        self.menu_about.setObjectName(u"menu_about")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_mode.menuAction())
        self.menubar.addAction(self.menu_about.menuAction())
        self.menu_file.addAction(self.action_inputconfig)
        self.menu_file.addAction(self.action_outputconfig)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_reinputconfig)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)
        self.menu_mode.addAction(self.action_Single)
        self.menu_mode.addAction(self.action_Multi)
        self.menu_mode.addAction(self.action_Lift)
        self.menu_mode.addAction(self.action_ScrollSingle)
        self.menu_about.addAction(self.action_license)
        self.menu_about.addAction(self.action_repository)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"randname ---HQZ-OhNone", None))
        self.action_Single.setText(QCoreApplication.translate("MainWindow", u"\u5355\u62bd", None))
        self.action_Multi.setText(QCoreApplication.translate("MainWindow", u"\u591a\u62bd", None))
        self.action_Lift.setText(QCoreApplication.translate("MainWindow", u"\u51cf\u91cf\u62bd", None))
        self.action_exit.setText(QCoreApplication.translate("MainWindow", u"\u9000\u51fa", None))
        self.action_license.setText(QCoreApplication.translate("MainWindow", u"\u8bb8\u53ef\u8bc1", None))
        self.action_repository.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u6e90\u4ed3\u5e93", None))
        self.action_ScrollSingle.setText(QCoreApplication.translate("MainWindow", u"\u6eda\u52a8\u5355\u62bd", None))
        self.action_inputconfig.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u5165...", None))
        self.action_outputconfig.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u51fa...", None))
        self.action_reinputconfig.setText(QCoreApplication.translate("MainWindow", u"\u91cd\u65b0\u52a0\u8f7d\u914d\u7f6e", None))
        self.menu_file.setTitle(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6", None))
        self.menu_mode.setTitle(QCoreApplication.translate("MainWindow", u"\u6a21\u5f0f", None))
        self.menu_about.setTitle(QCoreApplication.translate("MainWindow", u"\u5173\u4e8e", None))
    # retranslateUi

