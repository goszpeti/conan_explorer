# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'conan_install.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QCheckBox,
    QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QFrame, QHeaderView, QLabel, QLineEdit,
    QSizePolicy, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

from conan_app_launcher.ui.widgets.conan_line_edit import ConanRefLineEdit

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(406, 343)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QSize(400, 100))
        Dialog.setSizeIncrement(QSize(0, 0))
        Dialog.setModal(False)
        self.verticalLayout_2 = QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.main_frame = QFrame(Dialog)
        self.main_frame.setObjectName(u"main_frame")
        self.main_frame.setFrameShape(QFrame.StyledPanel)
        self.main_frame.setFrameShadow(QFrame.Raised)
        self.formLayout = QFormLayout(self.main_frame)
        self.formLayout.setObjectName(u"formLayout")
        self.conan_ref_line_edit = ConanRefLineEdit(self.main_frame)
        self.conan_ref_line_edit.setObjectName(u"conan_ref_line_edit")
        sizePolicy.setHeightForWidth(self.conan_ref_line_edit.sizePolicy().hasHeightForWidth())
        self.conan_ref_line_edit.setSizePolicy(sizePolicy)
        self.conan_ref_line_edit.setMinimumSize(QSize(0, 0))
        self.conan_ref_line_edit.setMaximumSize(QSize(1024, 16777215))
        self.conan_ref_line_edit.setMaxLength(1024)
        self.conan_ref_line_edit.setFrame(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.conan_ref_line_edit)

        self.profile_label = QLabel(self.main_frame)
        self.profile_label.setObjectName(u"profile_label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.profile_label)

        self.profile_cbox = QComboBox(self.main_frame)
        self.profile_cbox.setObjectName(u"profile_cbox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.profile_cbox)

        self.conan_opts_label = QLabel(self.main_frame)
        self.conan_opts_label.setObjectName(u"conan_opts_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.conan_opts_label.sizePolicy().hasHeightForWidth())
        self.conan_opts_label.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.conan_opts_label)

        self.options_widget = QTreeWidget(self.main_frame)
        self.options_widget.setObjectName(u"options_widget")
        self.options_widget.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.options_widget.setSortingEnabled(True)
        self.options_widget.setWordWrap(True)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.options_widget)

        self.add_args_label = QLabel(self.main_frame)
        self.add_args_label.setObjectName(u"add_args_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.add_args_label)

        self.additional_args_line_edit = QLineEdit(self.main_frame)
        self.additional_args_line_edit.setObjectName(u"additional_args_line_edit")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.additional_args_line_edit)


        self.verticalLayout_2.addWidget(self.main_frame)

        self.bottom_frame = QFrame(Dialog)
        self.bottom_frame.setObjectName(u"bottom_frame")
        self.bottom_frame.setFrameShape(QFrame.StyledPanel)
        self.bottom_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.bottom_frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.update_check_box = QCheckBox(self.bottom_frame)
        self.update_check_box.setObjectName(u"update_check_box")
        sizePolicy.setHeightForWidth(self.update_check_box.sizePolicy().hasHeightForWidth())
        self.update_check_box.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.update_check_box)

        self.line = QFrame(self.bottom_frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.auto_install_check_box = QCheckBox(self.bottom_frame)
        self.auto_install_check_box.setObjectName(u"auto_install_check_box")
        sizePolicy.setHeightForWidth(self.auto_install_check_box.sizePolicy().hasHeightForWidth())
        self.auto_install_check_box.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.auto_install_check_box)

        self.button_box = QDialogButtonBox(self.bottom_frame)
        self.button_box.setObjectName(u"button_box")
        sizePolicy.setHeightForWidth(self.button_box.sizePolicy().hasHeightForWidth())
        self.button_box.setSizePolicy(sizePolicy)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.button_box.setCenterButtons(False)

        self.verticalLayout.addWidget(self.button_box)


        self.verticalLayout_2.addWidget(self.bottom_frame)


        self.retranslateUi(Dialog)
        self.button_box.accepted.connect(Dialog.accept)
        self.button_box.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Conan Install", None))
        self.conan_ref_line_edit.setText("")
        self.profile_label.setText(QCoreApplication.translate("Dialog", u"Profile", None))
        self.conan_opts_label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Conan Options</p></body></html>", None))
        ___qtreewidgetitem = self.options_widget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("Dialog", u"Value", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Dialog", u"Name", None));
        self.add_args_label.setText(QCoreApplication.translate("Dialog", u"Additional args", None))
        self.update_check_box.setText(QCoreApplication.translate("Dialog", u"Update (-u)", None))
        self.auto_install_check_box.setText(QCoreApplication.translate("Dialog", u"Automatically determine best matching package", None))
    # retranslateUi

