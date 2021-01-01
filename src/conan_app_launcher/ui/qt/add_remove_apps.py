# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\sw-dev\product\app_grid_conan\src\conan_app_launcher\ui\qt\add_remove_apps.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(211, 327)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 10, 211, 311))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.app_list_view = QtWidgets.QListView(self.verticalLayoutWidget)
        self.app_list_view.setObjectName("app_list_view")
        self.verticalLayout.addWidget(self.app_list_view)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.add_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.add_button.setObjectName("add_button")
        self.horizontalLayout.addWidget(self.add_button)
        self.remove_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.remove_button.setObjectName("remove_button")
        self.horizontalLayout.addWidget(self.remove_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.add_button.setText(_translate("Dialog", "Add"))
        self.remove_button.setText(_translate("Dialog", "Remove"))
