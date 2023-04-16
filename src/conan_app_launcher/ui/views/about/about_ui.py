# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QLabel, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(663, 456)
        Form.setAutoFillBackground(True)
        Form.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.about_scroll_area = QScrollArea(Form)
        self.about_scroll_area.setObjectName(u"about_scroll_area")
        self.about_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.about_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.about_scroll_area.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.about_scroll_area.setWidgetResizable(True)
        self.about_contents = QWidget()
        self.about_contents.setObjectName(u"about_contents")
        self.about_contents.setGeometry(QRect(0, 0, 644, 454))
        self.verticalLayout = QVBoxLayout(self.about_contents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.logo_label = QLabel(self.about_contents)
        self.logo_label.setObjectName(u"logo_label")
        self.logo_label.setMinimumSize(QSize(100, 100))
        self.logo_label.setMaximumSize(QSize(100, 100))
        self.logo_label.setPixmap(QPixmap(u"../../../assets/icons/icon.ico"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setWordWrap(False)

        self.verticalLayout.addWidget(self.logo_label)

        self.about_label = QLabel(self.about_contents)
        self.about_label.setObjectName(u"about_label")
        self.about_label.setTextFormat(Qt.RichText)
        self.about_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.about_label.setWordWrap(False)
        self.about_label.setOpenExternalLinks(True)

        self.verticalLayout.addWidget(self.about_label)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.about_scroll_area.setWidget(self.about_contents)

        self.verticalLayout_2.addWidget(self.about_scroll_area)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.logo_label.setText("")
        self.about_label.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><br/>Hallo </p></body></html>", None))
    # retranslateUi

