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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QCheckBox,
    QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLayout, QLineEdit, QSizePolicy, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget)

from conan_app_launcher.ui.widgets.conan_line_edit import ConanRefLineEdit

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(585, 343)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QSize(200, 100))
        Dialog.setSizeIncrement(QSize(0, 0))
        Dialog.setModal(False)
        self.verticalLayout_2 = QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame_2 = QFrame(Dialog)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.formLayout = QFormLayout(self.frame_2)
        self.formLayout.setObjectName(u"formLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        self.formLayout.setLayout(0, QFormLayout.LabelRole, self.horizontalLayout)

        self.conan_ref_line_edit = ConanRefLineEdit(self.frame_2)
        self.conan_ref_line_edit.setObjectName(u"conan_ref_line_edit")
        sizePolicy.setHeightForWidth(self.conan_ref_line_edit.sizePolicy().hasHeightForWidth())
        self.conan_ref_line_edit.setSizePolicy(sizePolicy)
        self.conan_ref_line_edit.setMinimumSize(QSize(0, 0))
        self.conan_ref_line_edit.setMaximumSize(QSize(1024, 16777215))
        self.conan_ref_line_edit.setMaxLength(1024)
        self.conan_ref_line_edit.setFrame(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.conan_ref_line_edit)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label = QLabel(self.frame_2)
        self.label.setObjectName(u"label")

        self.horizontalLayout_4.addWidget(self.label)


        self.formLayout.setLayout(1, QFormLayout.LabelRole, self.horizontalLayout_4)

        self.profile_cbox = QComboBox(self.frame_2)
        self.profile_cbox.setObjectName(u"profile_cbox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.profile_cbox)

        self.conan_opts_label = QLabel(self.frame_2)
        self.conan_opts_label.setObjectName(u"conan_opts_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.conan_opts_label.sizePolicy().hasHeightForWidth())
        self.conan_opts_label.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.conan_opts_label)

        self.options_widget = QTreeWidget(self.frame_2)
        self.options_widget.setObjectName(u"options_widget")
        self.options_widget.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.options_widget.setSortingEnabled(True)
        self.options_widget.setWordWrap(True)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.options_widget)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.formLayout.setLayout(3, QFormLayout.LabelRole, self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.frame_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)


        self.formLayout.setLayout(4, QFormLayout.LabelRole, self.horizontalLayout_3)

        self.lineEdit = QLineEdit(self.frame_2)
        self.lineEdit.setObjectName(u"lineEdit")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.lineEdit)


        self.verticalLayout_2.addWidget(self.frame_2)

        self.frame = QFrame(Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.auto_install_check_box = QCheckBox(self.frame)
        self.auto_install_check_box.setObjectName(u"auto_install_check_box")
        sizePolicy.setHeightForWidth(self.auto_install_check_box.sizePolicy().hasHeightForWidth())
        self.auto_install_check_box.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.auto_install_check_box)

        self.update_check_box = QCheckBox(self.frame)
        self.update_check_box.setObjectName(u"update_check_box")
        sizePolicy.setHeightForWidth(self.update_check_box.sizePolicy().hasHeightForWidth())
        self.update_check_box.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.update_check_box)

        self.button_box = QDialogButtonBox(self.frame)
        self.button_box.setObjectName(u"button_box")
        sizePolicy.setHeightForWidth(self.button_box.sizePolicy().hasHeightForWidth())
        self.button_box.setSizePolicy(sizePolicy)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.button_box.setCenterButtons(False)

        self.verticalLayout.addWidget(self.button_box)


        self.verticalLayout_2.addWidget(self.frame)


        self.retranslateUi(Dialog)
        self.button_box.accepted.connect(Dialog.accept)
        self.button_box.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Conan Install", None))
        self.conan_ref_line_edit.setText("")
        self.label.setText(QCoreApplication.translate("Dialog", u"Profile", None))
        self.conan_opts_label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Conan Options</p></body></html>", None))
        ___qtreewidgetitem = self.options_widget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("Dialog", u"Value", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Dialog", u"Name", None));
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Additional args", None))
        self.auto_install_check_box.setText(QCoreApplication.translate("Dialog", u"Automatically determine best matching package", None))
        self.update_check_box.setText(QCoreApplication.translate("Dialog", u"Update (-u)", None))
    # retranslateUi

