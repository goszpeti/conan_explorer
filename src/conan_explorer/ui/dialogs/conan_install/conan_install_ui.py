# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'conan_install.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QSizePolicy, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

from conan_explorer.ui.widgets import AnimatedToggle
from conan_explorer.ui.widgets.conan_line_edit import ConanRefLineEdit

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(406, 343)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QSize(400, 100))
        Dialog.setSizeIncrement(QSize(0, 0))
        Dialog.setModal(False)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
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

        self.set_default_install_profile_button = QPushButton(self.main_frame)
        self.set_default_install_profile_button.setObjectName(u"set_default_install_profile_button")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.set_default_install_profile_button)

        self.conan_opts_label = QLabel(self.main_frame)
        self.conan_opts_label.setObjectName(u"conan_opts_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.conan_opts_label.sizePolicy().hasHeightForWidth())
        self.conan_opts_label.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.conan_opts_label)

        self.options_widget = QTreeWidget(self.main_frame)
        self.options_widget.setObjectName(u"options_widget")
        self.options_widget.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.options_widget.setSortingEnabled(True)
        self.options_widget.setWordWrap(True)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.options_widget)

        self.label = QLabel(self.main_frame)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)


        self.gridLayout.addWidget(self.main_frame, 0, 0, 1, 1)

        self.bottom_frame = QFrame(Dialog)
        self.bottom_frame.setObjectName(u"bottom_frame")
        self.bottom_frame.setFrameShape(QFrame.StyledPanel)
        self.bottom_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.bottom_frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.update_check_box = AnimatedToggle(self.bottom_frame)
        self.update_check_box.setObjectName(u"update_check_box")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.update_check_box.sizePolicy().hasHeightForWidth())
        self.update_check_box.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.update_check_box)

        self.update_label = QLabel(self.bottom_frame)
        self.update_label.setObjectName(u"update_label")
        self.update_label.setLayoutDirection(Qt.RightToLeft)

        self.horizontalLayout.addWidget(self.update_label)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.line = QFrame(self.bottom_frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.auto_install_check_box = AnimatedToggle(self.bottom_frame)
        self.auto_install_check_box.setObjectName(u"auto_install_check_box")
        sizePolicy2.setHeightForWidth(self.auto_install_check_box.sizePolicy().hasHeightForWidth())
        self.auto_install_check_box.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.auto_install_check_box)

        self.auto_install_label = QLabel(self.bottom_frame)
        self.auto_install_label.setObjectName(u"auto_install_label")

        self.horizontalLayout_2.addWidget(self.auto_install_label)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.button_box = QDialogButtonBox(self.bottom_frame)
        self.button_box.setObjectName(u"button_box")
        sizePolicy.setHeightForWidth(self.button_box.sizePolicy().hasHeightForWidth())
        self.button_box.setSizePolicy(sizePolicy)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.button_box.setCenterButtons(False)

        self.verticalLayout.addWidget(self.button_box)


        self.gridLayout.addWidget(self.bottom_frame, 1, 0, 1, 1)


        self.retranslateUi(Dialog)
        self.button_box.accepted.connect(Dialog.accept)
        self.button_box.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Conan Install", None))
        self.conan_ref_line_edit.setText("")
        self.profile_label.setText(QCoreApplication.translate("Dialog", u"Profile", None))
        self.set_default_install_profile_button.setText(QCoreApplication.translate("Dialog", u"Set this as default install profile", None))
        self.conan_opts_label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Options</p></body></html>", None))
        ___qtreewidgetitem = self.options_widget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("Dialog", u"Value", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Dialog", u"Name", None));
        self.label.setText(QCoreApplication.translate("Dialog", u"Reference", None))
        self.update_check_box.setText("")
        self.update_label.setText(QCoreApplication.translate("Dialog", u"Update (-u)", None))
        self.auto_install_check_box.setText("")
        self.auto_install_label.setText(QCoreApplication.translate("Dialog", u"Automatically determine best matching package", None))
    # retranslateUi

