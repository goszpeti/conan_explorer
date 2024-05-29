# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'toast.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(409, 143)
        Dialog.setStyleSheet(u"")
        self.verticalLayout_5 = QVBoxLayout(Dialog)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.frame = QFrame(Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.icon_label = QLabel(self.frame)
        self.icon_label.setObjectName(u"icon_label")
        self.icon_label.setPixmap(QPixmap(u"../../assets/icons/material/about.svg"))

        self.verticalLayout_3.addWidget(self.icon_label)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.line = QFrame(self.frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShadow(QFrame.Shadow.Raised)
        self.line.setLineWidth(3)
        self.line.setFrameShape(QFrame.Shape.VLine)

        self.horizontalLayout.addWidget(self.line)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.title_label = QLabel(self.frame)
        self.title_label.setObjectName(u"title_label")
        self.title_label.setStyleSheet(u"font: 700 12pt;")

        self.verticalLayout.addWidget(self.title_label)

        self.detail_label = QLabel(self.frame)
        self.detail_label.setObjectName(u"detail_label")

        self.verticalLayout.addWidget(self.detail_label)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_4)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(2, 2)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.close_button = QPushButton(self.frame)
        self.close_button.setObjectName(u"close_button")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.close_button.sizePolicy().hasHeightForWidth())
        self.close_button.setSizePolicy(sizePolicy)
        icon = QIcon(QIcon.fromTheme(u"application-exit"))
        self.close_button.setIcon(icon)
        self.close_button.setAutoDefault(False)
        self.close_button.setFlat(True)

        self.verticalLayout_2.addWidget(self.close_button)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout.setStretch(2, 1)

        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.time_label = QLabel(self.frame)
        self.time_label.setObjectName(u"time_label")

        self.verticalLayout_4.addWidget(self.time_label)


        self.verticalLayout_5.addWidget(self.frame)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.icon_label.setText("")
        self.title_label.setText(QCoreApplication.translate("Dialog", u"Title", None))
        self.detail_label.setText(QCoreApplication.translate("Dialog", u"Detail", None))
        self.close_button.setText("")
        self.time_label.setText(QCoreApplication.translate("Dialog", u"Time...", None))
    # retranslateUi

