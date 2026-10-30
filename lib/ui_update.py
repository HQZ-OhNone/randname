# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Update.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QPlainTextEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_UpdateDialog(object):
    def setupUi(self, UpdateDialog):
        if not UpdateDialog.objectName():
            UpdateDialog.setObjectName(u"UpdateDialog")
        UpdateDialog.resize(860, 640)
        self.verticalLayout = QVBoxLayout(UpdateDialog)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(16, 16, 16, 16)
        self.statusLabel = QLabel(UpdateDialog)
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setMinimumSize(QSize(0, 72))
        font = QFont()
        font.setFamilies([u"\u6587\u6cc9\u9a7f\u7b49\u5bbd\u5fae\u7c73\u9ed1"])
        font.setPointSize(28)
        font.setBold(True)
        self.statusLabel.setFont(font)
        self.statusLabel.setStyleSheet(u"QLabel#statusLabel {\n"
"    padding: 8px;\n"
"}\n"
"")
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statusLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.statusLabel)

        self.historyEdit = QPlainTextEdit(UpdateDialog)
        self.historyEdit.setObjectName(u"historyEdit")
        font1 = QFont()
        font1.setPointSize(12)
        self.historyEdit.setFont(font1)
        self.historyEdit.setStyleSheet(u"QScrollBar:vertical { width: 22px; }\n"
"QScrollBar:horizontal { height: 22px; }\n"
"")
        self.historyEdit.setReadOnly(True)
        self.historyEdit.setUndoRedoEnabled(False)

        self.verticalLayout.addWidget(self.historyEdit)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(12)
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.updateButton = QPushButton(UpdateDialog)
        self.updateButton.setObjectName(u"updateButton")
        self.updateButton.setMinimumSize(QSize(132, 44))
        font2 = QFont()
        font2.setPointSize(14)
        self.updateButton.setFont(font2)

        self.buttonLayout.addWidget(self.updateButton)

        self.manualButton = QPushButton(UpdateDialog)
        self.manualButton.setObjectName(u"manualButton")
        self.manualButton.setMinimumSize(QSize(132, 44))
        self.manualButton.setFont(font2)

        self.buttonLayout.addWidget(self.manualButton)

        self.okButton = QPushButton(UpdateDialog)
        self.okButton.setObjectName(u"okButton")
        self.okButton.setMinimumSize(QSize(132, 44))
        self.okButton.setFont(font2)

        self.buttonLayout.addWidget(self.okButton)


        self.verticalLayout.addLayout(self.buttonLayout)


        self.retranslateUi(UpdateDialog)

        QMetaObject.connectSlotsByName(UpdateDialog)
    # setupUi

    def retranslateUi(self, UpdateDialog):
        UpdateDialog.setWindowTitle(QCoreApplication.translate("UpdateDialog", u"\u68c0\u67e5\u66f4\u65b0", None))
        self.statusLabel.setText(QCoreApplication.translate("UpdateDialog", u"\u68c0\u6d4b\u4e2d", None))
        self.updateButton.setText(QCoreApplication.translate("UpdateDialog", u"\u66f4\u65b0", None))
        self.manualButton.setText(QCoreApplication.translate("UpdateDialog", u"\u624b\u52a8\u67e5\u8be2", None))
        self.okButton.setText(QCoreApplication.translate("UpdateDialog", u"\u786e\u5b9a", None))
    # retranslateUi
