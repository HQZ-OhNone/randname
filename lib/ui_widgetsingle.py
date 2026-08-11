# -*- coding: utf-8 -*-
"""
編譯自 ui/WidgetSingle.ui 的簡化 Python 模塊。
只建立程式運行所需的 widget 與命名屬性（pushButton, label_SingleOutput）。
"""

from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(734, 539)

        self.gridLayout_2 = QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")

        # 主顯示 Label
        self.label_SingleOutput = QLabel(Form)
        self.label_SingleOutput.setObjectName("label_SingleOutput")
        self.label_SingleOutput.setText("等待输入")
        self.label_SingleOutput.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout_2.addWidget(self.label_SingleOutput, 1, 1, 1, 1)

        # 按鈕
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("单抽")
        self.gridLayout_2.addWidget(self.pushButton, 3, 1, 1, 1)

        # 若需要，可在此添加 spacer 等佈局項（保持與 .ui 對應的插槽）


# end of ui_widgetsingle.py
