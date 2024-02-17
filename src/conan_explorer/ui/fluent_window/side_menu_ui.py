# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'side_menu.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLayout, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_SideMenu(object):
    def setupUi(self, SideMenu):
        if not SideMenu.objectName():
            SideMenu.setObjectName(u"SideMenu")
        SideMenu.resize(179, 182)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SideMenu.sizePolicy().hasHeightForWidth())
        SideMenu.setSizePolicy(sizePolicy)
        self.main_layout = QVBoxLayout(SideMenu)
        self.main_layout.setSpacing(2)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.side_menu_title_frame = QFrame(SideMenu)
        self.side_menu_title_frame.setObjectName(u"side_menu_title_frame")
        self.side_menu_title_frame.setFrameShape(QFrame.NoFrame)
        self.title_layout = QHBoxLayout(self.side_menu_title_frame)
        self.title_layout.setSpacing(4)
        self.title_layout.setObjectName(u"title_layout")
        self.title_layout.setSizeConstraint(QLayout.SetNoConstraint)
        self.title_layout.setContentsMargins(-1, 4, 0, 8)
        self.side_menu_title_button = QPushButton(self.side_menu_title_frame)
        self.side_menu_title_button.setObjectName(u"side_menu_title_button")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.side_menu_title_button.sizePolicy().hasHeightForWidth())
        self.side_menu_title_button.setSizePolicy(sizePolicy1)
        self.side_menu_title_button.setMinimumSize(QSize(32, 32))
        self.side_menu_title_button.setMaximumSize(QSize(50, 50))
        self.side_menu_title_button.setFlat(True)

        self.title_layout.addWidget(self.side_menu_title_button)

        self.side_menu_title_label = QLabel(self.side_menu_title_frame)
        self.side_menu_title_label.setObjectName(u"side_menu_title_label")

        self.title_layout.addWidget(self.side_menu_title_label)


        self.main_layout.addWidget(self.side_menu_title_frame)

        self.side_menu_content_frame = QFrame(SideMenu)
        self.side_menu_content_frame.setObjectName(u"side_menu_content_frame")
        self.side_menu_content_frame.setFrameShape(QFrame.NoFrame)
        self.side_menu_content_frame.setFrameShadow(QFrame.Raised)
        self.content_frame_layout = QVBoxLayout(self.side_menu_content_frame)
        self.content_frame_layout.setSpacing(4)
        self.content_frame_layout.setObjectName(u"content_frame_layout")
        self.content_frame_layout.setContentsMargins(0, 0, 9, 0)
        self.side_menu_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.content_frame_layout.addItem(self.side_menu_spacer)


        self.main_layout.addWidget(self.side_menu_content_frame)


        self.retranslateUi(SideMenu)

        QMetaObject.connectSlotsByName(SideMenu)
    # setupUi

    def retranslateUi(self, SideMenu):
        SideMenu.setWindowTitle(QCoreApplication.translate("SideMenu", u"Form", None))
        self.side_menu_title_button.setText("")
        self.side_menu_title_label.setText(QCoreApplication.translate("SideMenu", u"TextLabel", None))
    # retranslateUi

