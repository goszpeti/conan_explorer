# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plugins.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QTreeView, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(645, 454)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, -1, 2, 0)
        self.buttons_frame = QFrame(Form)
        self.buttons_frame.setObjectName(u"buttons_frame")
        self.buttons_frame.setFrameShape(QFrame.StyledPanel)
        self.buttons_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.buttons_frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, 0, -1)
        self.add_plugin_button = QPushButton(self.buttons_frame)
        self.add_plugin_button.setObjectName(u"add_plugin_button")
        icon = QIcon()
        icon.addFile(u"../../assets/icons/plus_rounded.svg", QSize(), QIcon.Normal, QIcon.On)
        self.add_plugin_button.setIcon(icon)

        self.verticalLayout.addWidget(self.add_plugin_button)

        self.toggle_plugin_button = QPushButton(self.buttons_frame)
        self.toggle_plugin_button.setObjectName(u"toggle_plugin_button")
        icon1 = QIcon()
        icon1.addFile(u"../../assets/icons/hide.svg", QSize(), QIcon.Normal, QIcon.On)
        self.toggle_plugin_button.setIcon(icon1)

        self.verticalLayout.addWidget(self.toggle_plugin_button)

        self.remove_plugin_button = QPushButton(self.buttons_frame)
        self.remove_plugin_button.setObjectName(u"remove_plugin_button")
        icon2 = QIcon()
        icon2.addFile(u"../../assets/icons/minus_rounded.svg", QSize(), QIcon.Normal, QIcon.On)
        self.remove_plugin_button.setIcon(icon2)

        self.verticalLayout.addWidget(self.remove_plugin_button)

        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.vertical_spacer)


        self.gridLayout.addWidget(self.buttons_frame, 1, 1, 2, 1)

        self.plugins_tree_view = QTreeView(Form)
        self.plugins_tree_view.setObjectName(u"plugins_tree_view")

        self.gridLayout.addWidget(self.plugins_tree_view, 1, 0, 1, 1)

        self.path_label = QLabel(Form)
        self.path_label.setObjectName(u"path_label")

        self.gridLayout.addWidget(self.path_label, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.add_plugin_button.setText(QCoreApplication.translate("Form", u"Add new Plugin", None))
        self.toggle_plugin_button.setText(QCoreApplication.translate("Form", u"Enable / Disable", None))
        self.remove_plugin_button.setText(QCoreApplication.translate("Form", u"Remove Plugin", None))
        self.path_label.setText("")
    # retranslateUi

