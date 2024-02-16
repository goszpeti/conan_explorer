# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plugins.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QTreeView, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(489, 333)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 1, 1, 1)
        self.buttons_frame = QFrame(Form)
        self.buttons_frame.setObjectName(u"buttons_frame")
        self.buttons_frame.setFrameShape(QFrame.StyledPanel)
        self.buttons_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.buttons_frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, -1, 0, -1)
        self.add_plugin_button = QPushButton(self.buttons_frame)
        self.add_plugin_button.setObjectName(u"add_plugin_button")
        icon = QIcon()
        icon.addFile(u"../../assets/icons/plus_rounded.png", QSize(), QIcon.Normal, QIcon.On)
        self.add_plugin_button.setIcon(icon)

        self.horizontalLayout.addWidget(self.add_plugin_button)

        self.remove_plugin_button = QPushButton(self.buttons_frame)
        self.remove_plugin_button.setObjectName(u"remove_plugin_button")
        icon1 = QIcon()
        icon1.addFile(u"../../assets/icons/minus_rounded.png", QSize(), QIcon.Normal, QIcon.On)
        self.remove_plugin_button.setIcon(icon1)

        self.horizontalLayout.addWidget(self.remove_plugin_button)

        self.reload_plugin_button = QPushButton(self.buttons_frame)
        self.reload_plugin_button.setObjectName(u"reload_plugin_button")

        self.horizontalLayout.addWidget(self.reload_plugin_button)

        self.buttons_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.buttons_spacer)


        self.verticalLayout.addWidget(self.buttons_frame)

        self.path_label = QLabel(Form)
        self.path_label.setObjectName(u"path_label")

        self.verticalLayout.addWidget(self.path_label)

        self.plugins_tree_view = QTreeView(Form)
        self.plugins_tree_view.setObjectName(u"plugins_tree_view")
        self.plugins_tree_view.setFrameShape(QFrame.NoFrame)

        self.verticalLayout.addWidget(self.plugins_tree_view)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.add_plugin_button.setText(QCoreApplication.translate("Form", u"Add new Plugin", None))
        self.remove_plugin_button.setText(QCoreApplication.translate("Form", u"Remove Plugin", None))
        self.reload_plugin_button.setText(QCoreApplication.translate("Form", u"Reload Plugin", None))
        self.path_label.setText("")
    # retranslateUi

