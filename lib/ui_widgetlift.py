# -*- coding: utf-8 -*-
"""
編譯自 ui/WidgetLift.ui 的簡化 Python 模塊。
提供程式需要的 widget 屬性：pushButton_Lift, label_LiftOutput, label_LiftQuantity,
pushButton_LiftQuantityUp, pushButton_LiftQuantityDown, pushButton_LiftRenew。
"""

from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout
from PySide6.QtCore import Qt


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(732, 542)

        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")

        # 減量抽結果顯示
        self.label_LiftOutput = QLabel(Form)
        self.label_LiftOutput.setObjectName("label_LiftOutput")
        self.label_LiftOutput.setText("等待输入")
        self.label_LiftOutput.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout.addWidget(self.label_LiftOutput, 1, 1, 1, 1)

        # Lift 按鈕
        self.pushButton_Lift = QPushButton(Form)
        self.pushButton_Lift.setObjectName("pushButton_Lift")
        self.pushButton_Lift.setText("多抽")
        self.gridLayout.addWidget(self.pushButton_Lift, 2, 1, 1, 1)

        # 數量控制
        self.verticalLayout_LiftQuantity = QVBoxLayout()
        self.pushButton_LiftQuantityUp = QPushButton(Form)
        self.pushButton_LiftQuantityUp.setObjectName("pushButton_LiftQuantityUp")
        self.pushButton_LiftQuantityUp.setText("增加")
        self.label_LiftQuantity = QLabel(Form)
        self.label_LiftQuantity.setObjectName("label_LiftQuantity")
        self.label_LiftQuantity.setText("1")
        self.label_LiftQuantity.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pushButton_LiftQuantityDown = QPushButton(Form)
        self.pushButton_LiftQuantityDown.setObjectName("pushButton_LiftQuantityDown")
        self.pushButton_LiftQuantityDown.setText("减少")

        # 刷新按鈕
        self.pushButton_LiftRenew = QPushButton(Form)
        self.pushButton_LiftRenew.setObjectName("pushButton_LiftRenew")
        self.pushButton_LiftRenew.setText("刷新")

        # 將數量控件加入垂直佈局（位置由原 .ui 決定，此處僅提供屬性）
        self.verticalLayout_LiftQuantity.addWidget(self.pushButton_LiftQuantityUp)
        self.verticalLayout_LiftQuantity.addWidget(self.label_LiftQuantity)
        self.verticalLayout_LiftQuantity.addWidget(self.pushButton_LiftQuantityDown)


# end of ui_widgetlift.py
