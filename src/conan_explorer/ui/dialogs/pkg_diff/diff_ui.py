# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'diff.ui'
##
## Created by: Qt User Interface Compiler version 6.5.3
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
    QHBoxLayout, QListWidget, QListWidgetItem, QSizePolicy,
    QTextBrowser, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(671, 512)
        Dialog.setSizeGripEnabled(True)
        self.horizontalLayout_2 = QHBoxLayout(Dialog)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.pkgs_list_widget = QListWidget(Dialog)
        self.pkgs_list_widget.setObjectName(u"pkgs_list_widget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pkgs_list_widget.sizePolicy().hasHeightForWidth())
        self.pkgs_list_widget.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.pkgs_list_widget)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.left_text_browser = QTextBrowser(Dialog)
        self.left_text_browser.setObjectName(u"left_text_browser")

        self.horizontalLayout.addWidget(self.left_text_browser)

        self.right_text_browser = QTextBrowser(Dialog)
        self.right_text_browser.setObjectName(u"right_text_browser")

        self.horizontalLayout.addWidget(self.right_text_browser)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.button_box = QDialogButtonBox(Dialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.button_box)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
    # retranslateUi

