# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'remote_login_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.5.3
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QAbstractScrollArea, QApplication,
    QDialog, QDialogButtonBox, QGridLayout, QLabel,
    QLayout, QLineEdit, QListView, QListWidget,
    QListWidgetItem, QSizePolicy, QVBoxLayout, QWidget)

from conan_explorer.ui.widgets.password_line_edit import PasswordLineEdit

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(429, 273)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setModal(True)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, 0, 0)
        self.edit_grid = QGridLayout()
        self.edit_grid.setObjectName(u"edit_grid")
        self.edit_grid.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.edit_grid.setContentsMargins(-1, -1, 4, -1)
        self.password_label = QLabel(Dialog)
        self.password_label.setObjectName(u"password_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.password_label.sizePolicy().hasHeightForWidth())
        self.password_label.setSizePolicy(sizePolicy1)
        self.password_label.setMinimumSize(QSize(0, 0))
        self.password_label.setWordWrap(True)

        self.edit_grid.addWidget(self.password_label, 2, 0, 1, 1)

        self.name_label = QLabel(Dialog)
        self.name_label.setObjectName(u"name_label")
        self.name_label.setWordWrap(True)

        self.edit_grid.addWidget(self.name_label, 1, 0, 1, 1)

        self.name_line_edit = QLineEdit(Dialog)
        self.name_line_edit.setObjectName(u"name_line_edit")

        self.edit_grid.addWidget(self.name_line_edit, 1, 1, 1, 1)

        self.password_line_edit = PasswordLineEdit(Dialog)
        self.password_line_edit.setObjectName(u"password_line_edit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.password_line_edit.sizePolicy().hasHeightForWidth())
        self.password_line_edit.setSizePolicy(sizePolicy2)
        self.password_line_edit.setMinimumSize(QSize(0, 0))
        self.password_line_edit.setFrame(True)
        self.password_line_edit.setEchoMode(QLineEdit.Password)
        self.password_line_edit.setClearButtonEnabled(False)

        self.edit_grid.addWidget(self.password_line_edit, 2, 1, 1, 1)

        self.remote_list = QListWidget(Dialog)
        self.remote_list.setObjectName(u"remote_list")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.remote_list.sizePolicy().hasHeightForWidth())
        self.remote_list.setSizePolicy(sizePolicy3)
        self.remote_list.setMinimumSize(QSize(0, 40))
        self.remote_list.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.remote_list.setSelectionMode(QAbstractItemView.NoSelection)
        self.remote_list.setMovement(QListView.Static)
        self.remote_list.setFlow(QListView.TopToBottom)
        self.remote_list.setProperty("isWrapping", False)
        self.remote_list.setResizeMode(QListView.Adjust)
        self.remote_list.setUniformItemSizes(True)
        self.remote_list.setWordWrap(True)
        self.remote_list.setSelectionRectVisible(True)
        self.remote_list.setSortingEnabled(False)

        self.edit_grid.addWidget(self.remote_list, 0, 0, 1, 2)


        self.verticalLayout.addLayout(self.edit_grid)

        self.note_label = QLabel(Dialog)
        self.note_label.setObjectName(u"note_label")

        self.verticalLayout.addWidget(self.note_label)

        self.button_box = QDialogButtonBox(Dialog)
        self.button_box.setObjectName(u"button_box")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(1)
        sizePolicy4.setHeightForWidth(self.button_box.sizePolicy().hasHeightForWidth())
        self.button_box.setSizePolicy(sizePolicy4)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.button_box)

        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(Dialog)
        self.button_box.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Login to Remote", None))
        self.password_label.setText(QCoreApplication.translate("Dialog", u"Password", None))
        self.name_label.setText(QCoreApplication.translate("Dialog", u"Name", None))
        self.note_label.setText("")
    # retranslateUi

