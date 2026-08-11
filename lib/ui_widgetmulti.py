# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WidgetMulti.ui'
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

        self.verticalLayout_MultiQuantity = QVBoxLayout()
        self.verticalLayout_MultiQuantity.setObjectName(u"verticalLayout_MultiQuantity")
        self.pushButton_MultiQuantityUp = QPushButton(Form)
        self.pushButton_MultiQuantityUp.setObjectName(u"pushButton_MultiQuantityUp")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_MultiQuantityUp.sizePolicy().hasHeightForWidth())
        self.pushButton_MultiQuantityUp.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font.setPointSize(18)
        self.pushButton_MultiQuantityUp.setFont(font)
        self.pushButton_MultiQuantityUp.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.verticalLayout_MultiQuantity.addWidget(self.pushButton_MultiQuantityUp)

        self.label_MultiQuantity = QLabel(Form)
        self.label_MultiQuantity.setObjectName(u"label_MultiQuantity")
        font1 = QFont()
        font1.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font1.setPointSize(20)
        self.label_MultiQuantity.setFont(font1)
        self.label_MultiQuantity.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.label_MultiQuantity.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_MultiQuantity.addWidget(self.label_MultiQuantity)

        self.pushButton_MultiQuantityDown = QPushButton(Form)
        self.pushButton_MultiQuantityDown.setObjectName(u"pushButton_MultiQuantityDown")
        sizePolicy.setHeightForWidth(self.pushButton_MultiQuantityDown.sizePolicy().hasHeightForWidth())
        self.pushButton_MultiQuantityDown.setSizePolicy(sizePolicy)
        self.pushButton_MultiQuantityDown.setFont(font)
        self.pushButton_MultiQuantityDown.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.verticalLayout_MultiQuantity.addWidget(self.pushButton_MultiQuantityDown)


        self.gridLayout.addLayout(self.verticalLayout_MultiQuantity, 1, 2, 1, 1)

        self.label_MultiOutput = QLabel(Form)
        self.label_MultiOutput.setObjectName(u"label_MultiOutput")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(160)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_MultiOutput.sizePolicy().hasHeightForWidth())
        self.label_MultiOutput.setSizePolicy(sizePolicy1)
        font2 = QFont()
        font2.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font2.setPointSize(36)
        self.label_MultiOutput.setFont(font2)
        self.label_MultiOutput.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(20, 20, 20, 255);  /* \u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 8px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")
        self.label_MultiOutput.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_MultiOutput, 1, 1, 1, 1)

        self.pushButton_Multi = QPushButton(Form)
        self.pushButton_Multi.setObjectName(u"pushButton_Multi")
        sizePolicy.setHeightForWidth(self.pushButton_Multi.sizePolicy().hasHeightForWidth())
        self.pushButton_Multi.setSizePolicy(sizePolicy)
        font3 = QFont()
        font3.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font3.setPointSize(24)
        self.pushButton_Multi.setFont(font3)
        self.pushButton_Multi.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u4eae\u8272\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.gridLayout.addWidget(self.pushButton_Multi, 2, 1, 1, 1)

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
        self.pushButton_MultiQuantityUp.setText(QCoreApplication.translate("Form", u"\u589e\u52a0", None))
        self.label_MultiQuantity.setText(QCoreApplication.translate("Form", u"1", None))
        self.pushButton_MultiQuantityDown.setText(QCoreApplication.translate("Form", u"\u51cf\u5c11", None))
        self.label_MultiOutput.setText(QCoreApplication.translate("Form", u"\u7b49\u5f85\u8f93\u5165", None))
        self.pushButton_Multi.setText(QCoreApplication.translate("Form", u"\u591a\u62bd", None))
    # retranslateUi

