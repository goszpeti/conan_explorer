# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'conan_install.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QLineEdit, QSizePolicy,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from conan_app_launcher.ui.widgets.conan_line_edit import ConanRefLineEdit

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(452, 419)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QSize(200, 100))
        Dialog.setSizeIncrement(QSize(0, 0))
        Dialog.setModal(False)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.install_icon = QLabel(Dialog)
        self.install_icon.setObjectName(u"install_icon")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.install_icon.sizePolicy().hasHeightForWidth())
        self.install_icon.setSizePolicy(sizePolicy1)
        self.install_icon.setMinimumSize(QSize(30, 0))
        self.install_icon.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout.addWidget(self.install_icon)

        self.conan_ref_line_edit = ConanRefLineEdit(Dialog)
        self.conan_ref_line_edit.setObjectName(u"conan_ref_line_edit")
        sizePolicy.setHeightForWidth(self.conan_ref_line_edit.sizePolicy().hasHeightForWidth())
        self.conan_ref_line_edit.setSizePolicy(sizePolicy)
        self.conan_ref_line_edit.setMinimumSize(QSize(0, 0))
        self.conan_ref_line_edit.setMaximumSize(QSize(1024, 16777215))
        self.conan_ref_line_edit.setMaxLength(1024)
        self.conan_ref_line_edit.setFrame(True)

        self.horizontalLayout.addWidget(self.conan_ref_line_edit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout_4.addWidget(self.label)

        self.profile_cbox = QComboBox(Dialog)
        self.profile_cbox.setObjectName(u"profile_cbox")

        self.horizontalLayout_4.addWidget(self.profile_cbox)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.conan_opts_label = QLabel(Dialog)
        self.conan_opts_label.setObjectName(u"conan_opts_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.conan_opts_label.sizePolicy().hasHeightForWidth())
        self.conan_opts_label.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.conan_opts_label)

        self.options_widget = QTreeWidget(Dialog)
        QTreeWidgetItem(self.options_widget)
        self.options_widget.setObjectName(u"options_widget")

        self.horizontalLayout_2.addWidget(self.options_widget)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.lineEdit = QLineEdit(Dialog)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout_3.addWidget(self.lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.auto_install_check_box = QCheckBox(Dialog)
        self.auto_install_check_box.setObjectName(u"auto_install_check_box")
        sizePolicy.setHeightForWidth(self.auto_install_check_box.sizePolicy().hasHeightForWidth())
        self.auto_install_check_box.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.auto_install_check_box)

        self.update_check_box = QCheckBox(Dialog)
        self.update_check_box.setObjectName(u"update_check_box")
        sizePolicy.setHeightForWidth(self.update_check_box.sizePolicy().hasHeightForWidth())
        self.update_check_box.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.update_check_box)

        self.button_box = QDialogButtonBox(Dialog)
        self.button_box.setObjectName(u"button_box")
        sizePolicy.setHeightForWidth(self.button_box.sizePolicy().hasHeightForWidth())
        self.button_box.setSizePolicy(sizePolicy)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(Dialog)
        self.button_box.accepted.connect(Dialog.accept)
        self.button_box.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Conan Install", None))
        self.install_icon.setText(QCoreApplication.translate("Dialog", u"Icon", None))
        self.conan_ref_line_edit.setText("")
        self.label.setText(QCoreApplication.translate("Dialog", u"Profile", None))
        self.conan_opts_label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Conan Options</p><p>using format: </p><p>name1=val1</p><p>name2=val2</p></body></html>", None))
        ___qtreewidgetitem = self.options_widget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("Dialog", u"value", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Dialog", u"name", None));

        __sortingEnabled = self.options_widget.isSortingEnabled()
        self.options_widget.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.options_widget.topLevelItem(0)
        ___qtreewidgetitem1.setText(1, QCoreApplication.translate("Dialog", u"1", None));
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("Dialog", u"Option1", None));
        self.options_widget.setSortingEnabled(__sortingEnabled)

        self.label_2.setText(QCoreApplication.translate("Dialog", u"Additional args", None))
        self.auto_install_check_box.setText(QCoreApplication.translate("Dialog", u"Automatically determine best matching package", None))
        self.update_check_box.setText(QCoreApplication.translate("Dialog", u"Update (-u)", None))
    # retranslateUi

