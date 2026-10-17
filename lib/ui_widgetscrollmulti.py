# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WidgetScrollMulti.ui'
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

        self.verticalLayout_ScrollMultiQuantity = QVBoxLayout()
        self.verticalLayout_ScrollMultiQuantity.setObjectName(u"verticalLayout_ScrollMultiQuantity")
        self.pushButton_ScrollMultiQuantityUp = QPushButton(Form)
        self.pushButton_ScrollMultiQuantityUp.setObjectName(u"pushButton_ScrollMultiQuantityUp")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_ScrollMultiQuantityUp.sizePolicy().hasHeightForWidth())
        self.pushButton_ScrollMultiQuantityUp.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font.setPointSize(18)
        self.pushButton_ScrollMultiQuantityUp.setFont(font)
        self.pushButton_ScrollMultiQuantityUp.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.verticalLayout_ScrollMultiQuantity.addWidget(self.pushButton_ScrollMultiQuantityUp)

        self.label_ScrollMultiQuantity = QLabel(Form)
        self.label_ScrollMultiQuantity.setObjectName(u"label_ScrollMultiQuantity")
        font1 = QFont()
        font1.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font1.setPointSize(20)
        self.label_ScrollMultiQuantity.setFont(font1)
        self.label_ScrollMultiQuantity.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.label_ScrollMultiQuantity.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_ScrollMultiQuantity.addWidget(self.label_ScrollMultiQuantity)

        self.pushButton_ScrollMultiQuantityDown = QPushButton(Form)
        self.pushButton_ScrollMultiQuantityDown.setObjectName(u"pushButton_ScrollMultiQuantityDown")
        sizePolicy.setHeightForWidth(self.pushButton_ScrollMultiQuantityDown.sizePolicy().hasHeightForWidth())
        self.pushButton_ScrollMultiQuantityDown.setSizePolicy(sizePolicy)
        self.pushButton_ScrollMultiQuantityDown.setFont(font)
        self.pushButton_ScrollMultiQuantityDown.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.verticalLayout_ScrollMultiQuantity.addWidget(self.pushButton_ScrollMultiQuantityDown)


        self.gridLayout.addLayout(self.verticalLayout_ScrollMultiQuantity, 1, 2, 1, 1)

        self.label_ScrollMultiOutput = QLabel(Form)
        self.label_ScrollMultiOutput.setObjectName(u"label_ScrollMultiOutput")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(160)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_ScrollMultiOutput.sizePolicy().hasHeightForWidth())
        self.label_ScrollMultiOutput.setSizePolicy(sizePolicy1)
        font2 = QFont()
        font2.setFamilies([u"\u6587\u6cc9\u9a5b\u5fae\u7c73\u9ed1"])
        font2.setPointSize(30)
        self.label_ScrollMultiOutput.setFont(font2)
        self.label_ScrollMultiOutput.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(20, 20, 20, 255);  /* \u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 8px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")
        self.label_ScrollMultiOutput.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_ScrollMultiOutput, 1, 1, 1, 1)

        self.pushButton_ScrollMulti = QPushButton(Form)
        self.pushButton_ScrollMulti.setObjectName(u"pushButton_ScrollMulti")
        sizePolicy.setHeightForWidth(self.pushButton_ScrollMulti.sizePolicy().hasHeightForWidth())
        self.pushButton_ScrollMulti.setSizePolicy(sizePolicy)
        font3 = QFont()
        font3.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font3.setPointSize(24)
        self.pushButton_ScrollMulti.setFont(font3)
        self.pushButton_ScrollMulti.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u4eae\u8272\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.gridLayout.addWidget(self.pushButton_ScrollMulti, 2, 1, 1, 1)

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
        self.pushButton_ScrollMultiQuantityUp.setText(QCoreApplication.translate("Form", u"\u589e\u52a0", None))
        self.label_ScrollMultiQuantity.setText(QCoreApplication.translate("Form", u"1", None))
        self.pushButton_ScrollMultiQuantityDown.setText(QCoreApplication.translate("Form", u"\u51cf\u5c11", None))
        self.label_ScrollMultiOutput.setText(QCoreApplication.translate("Form", u"\u6eda\u52a8\u591a\u62bd", None))
        self.pushButton_ScrollMulti.setText(QCoreApplication.translate("Form", u"\u62bd\u53d6", None))
    # retranslateUi

