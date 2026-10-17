# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WidgetScrollLift.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(732, 542)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 0, 1, 1, 1)

        self.verticalLayout_ScrollLiftQuantity = QVBoxLayout()
        self.verticalLayout_ScrollLiftQuantity.setObjectName(u"verticalLayout_ScrollLiftQuantity")
        self.pushButton_ScrollLiftQuantityUp = QPushButton(Form)
        self.pushButton_ScrollLiftQuantityUp.setObjectName(u"pushButton_ScrollLiftQuantityUp")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_ScrollLiftQuantityUp.sizePolicy().hasHeightForWidth())
        self.pushButton_ScrollLiftQuantityUp.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font.setPointSize(18)
        self.pushButton_ScrollLiftQuantityUp.setFont(font)
        self.pushButton_ScrollLiftQuantityUp.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.verticalLayout_ScrollLiftQuantity.addWidget(self.pushButton_ScrollLiftQuantityUp)

        self.label_ScrollLiftQuantity = QLabel(Form)
        self.label_ScrollLiftQuantity.setObjectName(u"label_ScrollLiftQuantity")
        font1 = QFont()
        font1.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font1.setPointSize(20)
        self.label_ScrollLiftQuantity.setFont(font1)
        self.label_ScrollLiftQuantity.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.label_ScrollLiftQuantity.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_ScrollLiftQuantity.addWidget(self.label_ScrollLiftQuantity)

        self.pushButton_ScrollLiftQuantityDown = QPushButton(Form)
        self.pushButton_ScrollLiftQuantityDown.setObjectName(u"pushButton_ScrollLiftQuantityDown")
        sizePolicy.setHeightForWidth(self.pushButton_ScrollLiftQuantityDown.sizePolicy().hasHeightForWidth())
        self.pushButton_ScrollLiftQuantityDown.setSizePolicy(sizePolicy)
        self.pushButton_ScrollLiftQuantityDown.setFont(font)
        self.pushButton_ScrollLiftQuantityDown.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.verticalLayout_ScrollLiftQuantity.addWidget(self.pushButton_ScrollLiftQuantityDown)


        self.gridLayout.addLayout(self.verticalLayout_ScrollLiftQuantity, 1, 2, 1, 1)

        self.label_ScrollLiftOutput = QLabel(Form)
        self.label_ScrollLiftOutput.setObjectName(u"label_ScrollLiftOutput")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(160)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_ScrollLiftOutput.sizePolicy().hasHeightForWidth())
        self.label_ScrollLiftOutput.setSizePolicy(sizePolicy1)
        font2 = QFont()
        font2.setFamilies([u"\u6587\u6cc9\u9a5b\u5fae\u7c73\u9ed1"])
        font2.setPointSize(30)
        self.label_ScrollLiftOutput.setFont(font2)
        self.label_ScrollLiftOutput.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(20, 20, 20, 255);  /* \u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 8px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")
        self.label_ScrollLiftOutput.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_ScrollLiftOutput, 1, 1, 1, 1)

        self.pushButton_ScrollLift = QPushButton(Form)
        self.pushButton_ScrollLift.setObjectName(u"pushButton_ScrollLift")
        sizePolicy.setHeightForWidth(self.pushButton_ScrollLift.sizePolicy().hasHeightForWidth())
        self.pushButton_ScrollLift.setSizePolicy(sizePolicy)
        font3 = QFont()
        font3.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font3.setPointSize(24)
        self.pushButton_ScrollLift.setFont(font3)
        self.pushButton_ScrollLift.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u4eae\u8272\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.gridLayout.addWidget(self.pushButton_ScrollLift, 2, 1, 1, 1)

        self.pushButton_ScrollLiftRenew = QPushButton(Form)
        self.pushButton_ScrollLiftRenew.setObjectName(u"pushButton_ScrollLiftRenew")
        sizePolicy.setHeightForWidth(self.pushButton_ScrollLiftRenew.sizePolicy().hasHeightForWidth())
        self.pushButton_ScrollLiftRenew.setSizePolicy(sizePolicy)
        self.pushButton_ScrollLiftRenew.setFont(font)
        self.pushButton_ScrollLiftRenew.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.gridLayout.addWidget(self.pushButton_ScrollLiftRenew, 2, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(80, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 3, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(80, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 3, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton_ScrollLiftQuantityUp.setText(QCoreApplication.translate("Form", u"\u589e\u52a0", None))
        self.label_ScrollLiftQuantity.setText(QCoreApplication.translate("Form", u"1", None))
        self.pushButton_ScrollLiftQuantityDown.setText(QCoreApplication.translate("Form", u"\u51cf\u5c11", None))
        self.label_ScrollLiftOutput.setText(QCoreApplication.translate("Form", u"\u6eda\u52a8\u51cf\u91cf\u62bd", None))
        self.pushButton_ScrollLift.setText(QCoreApplication.translate("Form", u"\u62bd\u53d6", None))
        self.pushButton_ScrollLiftRenew.setText(QCoreApplication.translate("Form", u"\u91cd\u7f6e", None))
    # retranslateUi
