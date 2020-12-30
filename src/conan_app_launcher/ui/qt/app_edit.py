# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\sw-dev\product\app_grid_conan\src\conan_app_launcher\ui\qt\app_edit.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(372, 295)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 10, 371, 281))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.vertical_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.vertical_layout.setContentsMargins(3, 3, 3, 0)
        self.vertical_layout.setObjectName("vertical_layout")
        self.options_layout = QtWidgets.QFormLayout()
        self.options_layout.setObjectName("options_layout")
        self.name_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.name_label.setObjectName("name_label")
        self.options_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.name_label)
        self.name_line_edit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.name_line_edit.setObjectName("name_line_edit")
        self.options_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.name_line_edit)
        self.conan_ref_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.conan_ref_label.setObjectName("conan_ref_label")
        self.options_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.conan_ref_label)
        self.conan_ref_line_edit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.conan_ref_line_edit.setObjectName("conan_ref_line_edit")
        self.options_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.conan_ref_line_edit)
        self.exec_path_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.exec_path_label.setObjectName("exec_path_label")
        self.options_layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.exec_path_label)
        self.exec_path_line_edit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.exec_path_line_edit.setObjectName("exec_path_line_edit")
        self.options_layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.exec_path_line_edit)
        self.icon_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.icon_label.setObjectName("icon_label")
        self.options_layout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.icon_label)
        self.icon_line_edit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.icon_line_edit.setObjectName("icon_line_edit")
        self.options_layout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.icon_line_edit)
        self.is_console_app_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.is_console_app_label.setObjectName("is_console_app_label")
        self.options_layout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.is_console_app_label)
        self.is_console_app_checkbox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.is_console_app_checkbox.setText("")
        self.is_console_app_checkbox.setObjectName("is_console_app_checkbox")
        self.options_layout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.is_console_app_checkbox)
        self.args_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.args_label.setObjectName("args_label")
        self.options_layout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.args_label)
        self.args_line_edit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.args_line_edit.setObjectName("args_line_edit")
        self.options_layout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.args_line_edit)
        self.conan_opts_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.conan_opts_label.setObjectName("conan_opts_label")
        self.options_layout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.conan_opts_label)
        self.conan_opts_text_edit = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.conan_opts_text_edit.setAutoFormatting(QtWidgets.QTextEdit.AutoNone)
        self.conan_opts_text_edit.setObjectName("conan_opts_text_edit")
        self.options_layout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.conan_opts_text_edit)
        self.vertical_layout.addLayout(self.options_layout)
        self.button_box = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.vertical_layout.addWidget(self.button_box)

        self.retranslateUi(Dialog)
        self.button_box.accepted.connect(Dialog.accept)
        self.button_box.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.name_label.setText(_translate("Dialog", "Name"))
        self.conan_ref_label.setText(_translate("Dialog", "Conan Reference"))
        self.exec_path_label.setText(_translate("Dialog", "Executable path"))
        self.icon_label.setText(_translate("Dialog", "Icon"))
        self.is_console_app_label.setText(_translate("Dialog", "Console application"))
        self.args_label.setText(_translate("Dialog", "Arguments"))
        self.conan_opts_label.setText(_translate("Dialog", "Conan Options"))
        self.conan_opts_text_edit.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.875pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Shared=True</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">MyOpt=2</p></body></html>"))
