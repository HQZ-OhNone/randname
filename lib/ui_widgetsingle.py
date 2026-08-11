# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WidgetSingle.ui'
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
    QSizePolicy, QSpacerItem, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(734, 539)
        self.gridLayout_2 = QGridLayout(Form)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_SingleOutput = QLabel(Form)
        self.label_SingleOutput.setObjectName(u"label_SingleOutput")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(160)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_SingleOutput.sizePolicy().hasHeightForWidth())
        self.label_SingleOutput.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font.setPointSize(36)
        self.label_SingleOutput.setFont(font)
        self.label_SingleOutput.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(20, 20, 20, 255);  /* \u6df1\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 8px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")
        self.label_SingleOutput.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_SingleOutput, 1, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(80, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        self.gridLayout_2.addItem(self.verticalSpacer_3, 2, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 0, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_2, 4, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(80, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 1, 2, 1, 1)

        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font1.setPointSize(24)
        self.pushButton.setFont(font1)
        self.pushButton.setStyleSheet(u"QLabel {\n"
"    background-color: rgba(100, 100, 100, 255);  /* \u8f83\u4eae\u8272\u8272\u80cc\u666f */\n"
"    border: 2px solid #4A90E2;                /* \u84dd\u8272\u8fb9\u6846 */\n"
"    border-radius: 15px;                      /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 6px;                             /* \u5185\u8fb9\u8ddd */\n"
"    color: white;                             /* \u5b57\u4f53\u989c\u8272 */\n"
"}\n"
"")

        self.gridLayout_2.addWidget(self.pushButton, 3, 1, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_SingleOutput.setText(QCoreApplication.translate("Form", u"\u7b49\u5f85\u8f93\u5165", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\u5355\u62bd", None))
    # retranslateUi

