# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'remote_edit_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QLabel, QLayout, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget)

from conan_explorer.ui.widgets import AnimatedToggle

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(776, 146)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setModal(True)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.edit_grid = QGridLayout()
        self.edit_grid.setObjectName(u"edit_grid")
        self.edit_grid.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.verify_ssl_checkbox = AnimatedToggle(Dialog)
        self.verify_ssl_checkbox.setObjectName(u"verify_ssl_checkbox")

        self.edit_grid.addWidget(self.verify_ssl_checkbox, 2, 1, 1, 1)

        self.url_label = QLabel(Dialog)
        self.url_label.setObjectName(u"url_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.url_label.sizePolicy().hasHeightForWidth())
        self.url_label.setSizePolicy(sizePolicy1)
        self.url_label.setMinimumSize(QSize(0, 0))
        self.url_label.setWordWrap(True)

        self.edit_grid.addWidget(self.url_label, 1, 0, 1, 1)

        self.url_line_edit = QLineEdit(Dialog)
        self.url_line_edit.setObjectName(u"url_line_edit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.url_line_edit.sizePolicy().hasHeightForWidth())
        self.url_line_edit.setSizePolicy(sizePolicy2)
        self.url_line_edit.setMinimumSize(QSize(0, 0))
        self.url_line_edit.setFrame(True)

        self.edit_grid.addWidget(self.url_line_edit, 1, 1, 1, 1)

        self.name_line_edit = QLineEdit(Dialog)
        self.name_line_edit.setObjectName(u"name_line_edit")

        self.edit_grid.addWidget(self.name_line_edit, 0, 1, 1, 1)

        self.name_label = QLabel(Dialog)
        self.name_label.setObjectName(u"name_label")
        self.name_label.setWordWrap(True)

        self.edit_grid.addWidget(self.name_label, 0, 0, 1, 1)

        self.verify_ssl_label = QLabel(Dialog)
        self.verify_ssl_label.setObjectName(u"verify_ssl_label")

        self.edit_grid.addWidget(self.verify_ssl_label, 2, 0, 1, 1)

        self.edit_grid.setRowStretch(0, 1)

        self.verticalLayout.addLayout(self.edit_grid)

        self.button_box = QDialogButtonBox(Dialog)
        self.button_box.setObjectName(u"button_box")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.button_box.sizePolicy().hasHeightForWidth())
        self.button_box.setSizePolicy(sizePolicy3)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(Dialog)
        self.button_box.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Edit Remote", None))
        self.verify_ssl_checkbox.setText("")
        self.url_label.setText(QCoreApplication.translate("Dialog", u"URL", None))
        self.name_label.setText(QCoreApplication.translate("Dialog", u"Name", None))
        self.verify_ssl_label.setText(QCoreApplication.translate("Dialog", u"Verify SSL", None))
    # retranslateUi

