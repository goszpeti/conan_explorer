# Form implementation generated from reading ui file 'c:\repos\conan_app_launcher\src\conan_app_launcher\ui\views\plugins.ui'
#
# Created by: PyQt6 UI code generator 6.3.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(645, 454)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.treeWidget = QtWidgets.QTreeWidget(Form)
        self.treeWidget.setObjectName("treeWidget")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("c:\\repos\\conan_app_launcher\\src\\conan_app_launcher\\ui\\views\\../../assets/icons/about.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
        item_1.setIcon(0, icon)
        self.gridLayout.addWidget(self.treeWidget, 0, 0, 1, 1)
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton = QtWidgets.QPushButton(self.frame)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("c:\\repos\\conan_app_launcher\\src\\conan_app_launcher\\ui\\views\\../../assets/icons/plus_rounded.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
        self.pushButton.setIcon(icon1)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.pushButton_3 = QtWidgets.QPushButton(self.frame)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("c:\\repos\\conan_app_launcher\\src\\conan_app_launcher\\ui\\views\\../../assets/icons/hide.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
        self.pushButton_3.setIcon(icon2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("c:\\repos\\conan_app_launcher\\src\\conan_app_launcher\\ui\\views\\../../assets/icons/minus_rounded.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
        self.pushButton_2.setIcon(icon3)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout.addWidget(self.frame, 0, 1, 2, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.treeWidget.headerItem().setText(0, _translate("Form", "Path"))
        self.treeWidget.headerItem().setText(1, _translate("Form", "Name"))
        self.treeWidget.headerItem().setText(2, _translate("Form", "Version"))
        self.treeWidget.headerItem().setText(3, _translate("Form", "Author"))
        self.treeWidget.headerItem().setText(4, _translate("Form", "Description"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(0, _translate("Form", "dir/plugins.ini"))
        self.treeWidget.topLevelItem(0).child(0).setText(1, _translate("Form", "MY Plugin"))
        self.treeWidget.topLevelItem(0).child(0).setText(2, _translate("Form", "0.1.1"))
        self.treeWidget.topLevelItem(0).child(0).setText(3, _translate("Form", "Myself"))
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.pushButton.setText(_translate("Form", "Add new Plugin"))
        self.pushButton_3.setText(_translate("Form", "Enable / Disable"))
        self.pushButton_2.setText(_translate("Form", "Remove Plugin"))