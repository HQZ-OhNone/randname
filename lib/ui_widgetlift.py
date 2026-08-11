# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WidgetLift.ui'
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

        self.verticalLayout_LiftQuantity = QVBoxLayout()
        self.verticalLayout_LiftQuantity.setObjectName(u"verticalLayout_LiftQuantity")
        self.pushButton_LiftQuantityUp = QPushButton(Form)
        self.pushButton_LiftQuantityUp.setObjectName(u"pushButton_LiftQuantityUp")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_LiftQuantityUp.sizePolicy().hasHeightForWidth())
        self.pushButton_LiftQuantityUp.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font.setPointSize(18)
        self.pushButton_LiftQuantityUp.setFont(font)
        self.pushButton_LiftQuantityUp.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.verticalLayout_LiftQuantity.addWidget(self.pushButton_LiftQuantityUp)

        self.label_LiftQuantity = QLabel(Form)
        self.label_LiftQuantity.setObjectName(u"label_LiftQuantity")
        font1 = QFont()
        font1.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font1.setPointSize(20)
        self.label_LiftQuantity.setFont(font1)
        self.label_LiftQuantity.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.label_LiftQuantity.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_LiftQuantity.addWidget(self.label_LiftQuantity)

        self.pushButton_LiftQuantityDown = QPushButton(Form)
        self.pushButton_LiftQuantityDown.setObjectName(u"pushButton_LiftQuantityDown")
        sizePolicy.setHeightForWidth(self.pushButton_LiftQuantityDown.sizePolicy().hasHeightForWidth())
        self.pushButton_LiftQuantityDown.setSizePolicy(sizePolicy)
        self.pushButton_LiftQuantityDown.setFont(font)
        self.pushButton_LiftQuantityDown.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.verticalLayout_LiftQuantity.addWidget(self.pushButton_LiftQuantityDown)


        self.gridLayout.addLayout(self.verticalLayout_LiftQuantity, 1, 2, 1, 1)

        self.pushButton_Lift = QPushButton(Form)
        self.pushButton_Lift.setObjectName(u"pushButton_Lift")
        sizePolicy.setHeightForWidth(self.pushButton_Lift.sizePolicy().hasHeightForWidth())
        self.pushButton_Lift.setSizePolicy(sizePolicy)
        font2 = QFont()
        font2.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font2.setPointSize(24)
        self.pushButton_Lift.setFont(font2)
        self.pushButton_Lift.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u4eae\u8272\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.gridLayout.addWidget(self.pushButton_Lift, 2, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 3, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(80, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 3, 1, 1)

        self.horizontalSpacer = QSpacerItem(80, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.label_LiftOutput = QLabel(Form)
        self.label_LiftOutput.setObjectName(u"label_LiftOutput")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(160)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_LiftOutput.sizePolicy().hasHeightForWidth())
        self.label_LiftOutput.setSizePolicy(sizePolicy1)
        font3 = QFont()
        font3.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font3.setPointSize(36)
        self.label_LiftOutput.setFont(font3)
        self.label_LiftOutput.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(20, 20, 20, 255);  /* \u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 8px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")
        self.label_LiftOutput.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_LiftOutput, 1, 1, 1, 1)

        self.pushButton_LiftRenew = QPushButton(Form)
        self.pushButton_LiftRenew.setObjectName(u"pushButton_LiftRenew")
        sizePolicy.setHeightForWidth(self.pushButton_LiftRenew.sizePolicy().hasHeightForWidth())
        self.pushButton_LiftRenew.setSizePolicy(sizePolicy)
        self.pushButton_LiftRenew.setFont(font)
        self.pushButton_LiftRenew.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.gridLayout.addWidget(self.pushButton_LiftRenew, 2, 2, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton_LiftQuantityUp.setText(QCoreApplication.translate("Form", u"\u589e\u52a0", None))
        self.label_LiftQuantity.setText(QCoreApplication.translate("Form", u"1", None))
        self.pushButton_LiftQuantityDown.setText(QCoreApplication.translate("Form", u"\u51cf\u5c11", None))
        self.pushButton_Lift.setText(QCoreApplication.translate("Form", u"\u591a\u62bd", None))
        self.label_LiftOutput.setText(QCoreApplication.translate("Form", u"\u7b49\u5f85\u8f93\u5165", None))
        self.pushButton_LiftRenew.setText(QCoreApplication.translate("Form", u"\u5237\u65b0", None))
    # retranslateUi

