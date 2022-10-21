# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\repos\conan_app_launcher\src\conan_app_launcher\ui\views\conan_conf\dialogs\remote_login_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(429, 273)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(-1, -1, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.edit_grid = QtWidgets.QGridLayout()
        self.edit_grid.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.edit_grid.setContentsMargins(-1, -1, 4, -1)
        self.edit_grid.setObjectName("edit_grid")
        self.password_label = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.password_label.sizePolicy().hasHeightForWidth())
        self.password_label.setSizePolicy(sizePolicy)
        self.password_label.setMinimumSize(QtCore.QSize(0, 0))
        self.password_label.setWordWrap(True)
        self.password_label.setObjectName("password_label")
        self.edit_grid.addWidget(self.password_label, 2, 0, 1, 1)
        self.name_label = QtWidgets.QLabel(Dialog)
        self.name_label.setWordWrap(True)
        self.name_label.setObjectName("name_label")
        self.edit_grid.addWidget(self.name_label, 1, 0, 1, 1)
        self.name_line_edit = QtWidgets.QLineEdit(Dialog)
        self.name_line_edit.setObjectName("name_line_edit")
        self.edit_grid.addWidget(self.name_line_edit, 1, 1, 1, 1)
        self.password_line_edit = PasswordLineEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.password_line_edit.sizePolicy().hasHeightForWidth())
        self.password_line_edit.setSizePolicy(sizePolicy)
        self.password_line_edit.setMinimumSize(QtCore.QSize(0, 0))
        self.password_line_edit.setFrame(True)
        self.password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_line_edit.setClearButtonEnabled(False)
        self.password_line_edit.setObjectName("password_line_edit")
        self.edit_grid.addWidget(self.password_line_edit, 2, 1, 1, 1)
        self.remote_list = QtWidgets.QListWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.remote_list.sizePolicy().hasHeightForWidth())
        self.remote_list.setSizePolicy(sizePolicy)
        self.remote_list.setMinimumSize(QtCore.QSize(0, 40))
        self.remote_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.remote_list.setMovement(QtWidgets.QListView.Static)
        self.remote_list.setFlow(QtWidgets.QListView.TopToBottom)
        self.remote_list.setProperty("isWrapping", False)
        self.remote_list.setResizeMode(QtWidgets.QListView.Adjust)
        self.remote_list.setUniformItemSizes(True)
        self.remote_list.setWordWrap(True)
        self.remote_list.setSelectionRectVisible(True)
        self.remote_list.setObjectName("remote_list")
        self.edit_grid.addWidget(self.remote_list, 0, 0, 1, 2)
        self.verticalLayout.addLayout(self.edit_grid)
        self.note_label = QtWidgets.QLabel(Dialog)
        self.note_label.setText("")
        self.note_label.setObjectName("note_label")
        self.verticalLayout.addWidget(self.note_label)
        self.button_box = QtWidgets.QDialogButtonBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.button_box.sizePolicy().hasHeightForWidth())
        self.button_box.setSizePolicy(sizePolicy)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.verticalLayout.addWidget(self.button_box)
        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(Dialog)
        self.button_box.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Login to Remote"))
        self.password_label.setText(_translate("Dialog", "Password"))
        self.name_label.setText(_translate("Dialog", "Name"))
        self.remote_list.setSortingEnabled(False)
from conan_app_launcher.ui.widgets.password_line_edit import PasswordLineEdit
