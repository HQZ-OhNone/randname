# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TextViewer.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QSizePolicy, QTextBrowser, QVBoxLayout, QWidget)

class Ui_TextViewerDialog(object):
    def setupUi(self, TextViewerDialog):
        if not TextViewerDialog.objectName():
            TextViewerDialog.setObjectName(u"TextViewerDialog")
        TextViewerDialog.resize(900, 680)
        self.verticalLayout = QVBoxLayout(TextViewerDialog)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(12, 12, 12, 12)
        self.textView = QTextBrowser(TextViewerDialog)
        self.textView.setObjectName(u"textView")
        self.textView.setStyleSheet(u"QScrollBar:vertical { width: 22px; }\n"
"QScrollBar:horizontal { height: 22px; }\n"
"")

        self.verticalLayout.addWidget(self.textView)

        self.buttonBox = QDialogButtonBox(TextViewerDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(TextViewerDialog)

        QMetaObject.connectSlotsByName(TextViewerDialog)
    # setupUi

    def retranslateUi(self, TextViewerDialog):
        TextViewerDialog.setWindowTitle(QCoreApplication.translate("TextViewerDialog", u"\u67e5\u770b", None))
    # retranslateUi
