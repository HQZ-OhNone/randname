# -*- coding: utf-8 -*-
"""
編譯自 ui/WidgetMulti.ui 的簡化 Python 模塊。
提供程式需要的 widget 屬性：pushButton_Multi, label_MultiOutput, label_MultiQuantity,
pushButton_MultiQuantityUp, pushButton_MultiQuantityDown。
"""

from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout
from PySide6.QtCore import Qt


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(732, 542)

        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")

        # 多抽結果顯示
        self.label_MultiOutput = QLabel(Form)
        self.label_MultiOutput.setObjectName("label_MultiOutput")
        self.label_MultiOutput.setText("等待输入")
        self.label_MultiOutput.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout.addWidget(self.label_MultiOutput, 1, 1, 1, 1)

        # 多抽按鈕
        self.pushButton_Multi = QPushButton(Form)
        self.pushButton_Multi.setObjectName("pushButton_Multi")
        self.pushButton_Multi.setText("多抽")
        self.gridLayout.addWidget(self.pushButton_Multi, 2, 1, 1, 1)

        # 數量控制
        self.verticalLayout_MultiQuantity = QVBoxLayout()
        self.pushButton_MultiQuantityUp = QPushButton(Form)
        self.pushButton_MultiQuantityUp.setObjectName("pushButton_MultiQuantityUp")
        self.pushButton_MultiQuantityUp.setText("增加")
        self.label_MultiQuantity = QLabel(Form)
        self.label_MultiQuantity.setObjectName("label_MultiQuantity")
        self.label_MultiQuantity.setText("1")
        self.label_MultiQuantity.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pushButton_MultiQuantityDown = QPushButton(Form)
        self.pushButton_MultiQuantityDown.setObjectName("pushButton_MultiQuantityDown")
        self.pushButton_MultiQuantityDown.setText("减少")

        # 將數量控制加入佈局（實體放置位置由原始 .ui 決定；此處僅提供屬性）
        self.verticalLayout_MultiQuantity.addWidget(self.pushButton_MultiQuantityUp)
        self.verticalLayout_MultiQuantity.addWidget(self.label_MultiQuantity)
        self.verticalLayout_MultiQuantity.addWidget(self.pushButton_MultiQuantityDown)


# end of ui_widgetmulti.py
