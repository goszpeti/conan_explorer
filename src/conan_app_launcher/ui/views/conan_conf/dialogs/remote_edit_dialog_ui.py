# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\repos\conan_app_launcher\src\conan_app_launcher\ui\views\conan_conf\dialogs\remote_edit_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(562, 163)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.edit_grid = QtWidgets.QGridLayout()
        self.edit_grid.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.edit_grid.setObjectName("edit_grid")
        self.verify_ssl_checkbox = QtWidgets.QCheckBox(Dialog)
        self.verify_ssl_checkbox.setText("")
        self.verify_ssl_checkbox.setObjectName("verify_ssl_checkbox")
        self.edit_grid.addWidget(self.verify_ssl_checkbox, 2, 1, 1, 1)
        self.url_label = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.url_label.sizePolicy().hasHeightForWidth())
        self.url_label.setSizePolicy(sizePolicy)
        self.url_label.setMinimumSize(QtCore.QSize(0, 0))
        self.url_label.setWordWrap(True)
        self.url_label.setObjectName("url_label")
        self.edit_grid.addWidget(self.url_label, 1, 0, 1, 1)
        self.url_line_edit = QtWidgets.QLineEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.url_line_edit.sizePolicy().hasHeightForWidth())
        self.url_line_edit.setSizePolicy(sizePolicy)
        self.url_line_edit.setMinimumSize(QtCore.QSize(0, 0))
        self.url_line_edit.setFrame(True)
        self.url_line_edit.setObjectName("url_line_edit")
        self.edit_grid.addWidget(self.url_line_edit, 1, 1, 1, 1)
        self.name_line_edit = QtWidgets.QLineEdit(Dialog)
        self.name_line_edit.setObjectName("name_line_edit")
        self.edit_grid.addWidget(self.name_line_edit, 0, 1, 1, 1)
        self.name_label = QtWidgets.QLabel(Dialog)
        self.name_label.setWordWrap(True)
        self.name_label.setObjectName("name_label")
        self.edit_grid.addWidget(self.name_label, 0, 0, 1, 1)
        self.verify_ssl_label = QtWidgets.QLabel(Dialog)
        self.verify_ssl_label.setObjectName("verify_ssl_label")
        self.edit_grid.addWidget(self.verify_ssl_label, 2, 0, 1, 1)
        self.edit_grid.setRowStretch(0, 1)
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

        self.retranslateUi(Dialog)
        self.button_box.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Edit Remote"))
        self.url_label.setText(_translate("Dialog", "URL"))
        self.name_label.setText(_translate("Dialog", "Name"))
        self.verify_ssl_label.setText(_translate("Dialog", "Verify SSL"))
