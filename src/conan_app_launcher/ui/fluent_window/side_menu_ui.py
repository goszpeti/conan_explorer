# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\repos\app_grid_conan\src\conan_app_launcher\ui\fluent_window\side_menu.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SideMenu(object):
    def setupUi(self, SideMenu):
        SideMenu.setObjectName("SideMenu")
        SideMenu.resize(179, 182)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SideMenu.sizePolicy().hasHeightForWidth())
        SideMenu.setSizePolicy(sizePolicy)
        self.main_layout = QtWidgets.QVBoxLayout(SideMenu)
        self.main_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)
        self.main_layout.setObjectName("main_layout")
        self.side_menu_title_frame = QtWidgets.QFrame(SideMenu)
        self.side_menu_title_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.side_menu_title_frame.setObjectName("side_menu_title_frame")
        self.title_layout = QtWidgets.QHBoxLayout(self.side_menu_title_frame)
        self.title_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.title_layout.setContentsMargins(-1, 4, 0, 8)
        self.title_layout.setSpacing(4)
        self.title_layout.setObjectName("title_layout")
        self.side_menu_title_button = QtWidgets.QPushButton(self.side_menu_title_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.side_menu_title_button.sizePolicy().hasHeightForWidth())
        self.side_menu_title_button.setSizePolicy(sizePolicy)
        self.side_menu_title_button.setMinimumSize(QtCore.QSize(32, 32))
        self.side_menu_title_button.setMaximumSize(QtCore.QSize(50, 50))
        self.side_menu_title_button.setText("")
        self.side_menu_title_button.setFlat(True)
        self.side_menu_title_button.setObjectName("side_menu_title_button")
        self.title_layout.addWidget(self.side_menu_title_button)
        self.side_menu_title_label = QtWidgets.QLabel(self.side_menu_title_frame)
        self.side_menu_title_label.setObjectName("side_menu_title_label")
        self.title_layout.addWidget(self.side_menu_title_label)
        self.main_layout.addWidget(self.side_menu_title_frame)
        self.side_menu_content_frame = QtWidgets.QFrame(SideMenu)
        self.side_menu_content_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.side_menu_content_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.side_menu_content_frame.setObjectName("side_menu_content_frame")
        self.content_frame_layout = QtWidgets.QVBoxLayout(self.side_menu_content_frame)
        self.content_frame_layout.setContentsMargins(0, 0, 9, 0)
        self.content_frame_layout.setSpacing(4)
        self.content_frame_layout.setObjectName("content_frame_layout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.content_frame_layout.addItem(spacerItem)
        self.main_layout.addWidget(self.side_menu_content_frame)

        self.retranslateUi(SideMenu)
        QtCore.QMetaObject.connectSlotsByName(SideMenu)

    def retranslateUi(self, SideMenu):
        _translate = QtCore.QCoreApplication.translate
        SideMenu.setWindowTitle(_translate("SideMenu", "Form"))
        self.side_menu_title_label.setText(_translate("SideMenu", "TextLabel"))
