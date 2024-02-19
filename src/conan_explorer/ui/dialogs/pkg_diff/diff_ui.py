# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'diff.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QLabel, QListView, QListWidget,
    QListWidgetItem, QSizePolicy, QSplitter, QTextBrowser,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(1000, 500)
        Dialog.setSizeGripEnabled(True)
        self.verticalLayout_4 = QVBoxLayout(Dialog)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.splitter_2 = QSplitter(Dialog)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.pkgs_list_widget = QListWidget(self.splitter_2)
        self.pkgs_list_widget.setObjectName(u"pkgs_list_widget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pkgs_list_widget.sizePolicy().hasHeightForWidth())
        self.pkgs_list_widget.setSizePolicy(sizePolicy)
        self.pkgs_list_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pkgs_list_widget.setTabKeyNavigation(True)
        self.pkgs_list_widget.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.pkgs_list_widget.setProperty("isWrapping", False)
        self.pkgs_list_widget.setViewMode(QListView.ListMode)
        self.pkgs_list_widget.setWordWrap(False)
        self.pkgs_list_widget.setSelectionRectVisible(True)
        self.splitter_2.addWidget(self.pkgs_list_widget)
        self.widget = QWidget(self.splitter_2)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_3 = QVBoxLayout(self.widget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(self.widget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.widget1 = QWidget(self.splitter)
        self.widget1.setObjectName(u"widget1")
        self.verticalLayout = QVBoxLayout(self.widget1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget1)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.left_text_browser = QTextBrowser(self.widget1)
        self.left_text_browser.setObjectName(u"left_text_browser")

        self.verticalLayout.addWidget(self.left_text_browser)

        self.splitter.addWidget(self.widget1)
        self.widget2 = QWidget(self.splitter)
        self.widget2.setObjectName(u"widget2")
        self.verticalLayout_2 = QVBoxLayout(self.widget2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.widget2)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.right_text_browser = QTextBrowser(self.widget2)
        self.right_text_browser.setObjectName(u"right_text_browser")

        self.verticalLayout_2.addWidget(self.right_text_browser)

        self.splitter.addWidget(self.widget2)

        self.verticalLayout_3.addWidget(self.splitter)

        self.button_box = QDialogButtonBox(self.widget)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Ok)

        self.verticalLayout_3.addWidget(self.button_box)

        self.splitter_2.addWidget(self.widget)

        self.verticalLayout_4.addWidget(self.splitter_2)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Reference (*):", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Compare to:", None))
    # retranslateUi

