# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'editable_edit_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QLabel, QLayout, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

from conan_explorer.ui.widgets.conan_line_edit import ConanRefLineEdit

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(645, 146)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
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
        self.output_folder_label = QLabel(Dialog)
        self.output_folder_label.setObjectName(u"output_folder_label")

        self.edit_grid.addWidget(self.output_folder_label, 2, 0, 1, 1)

        self.path_browse_button = QPushButton(Dialog)
        self.path_browse_button.setObjectName(u"path_browse_button")
        self.path_browse_button.setMaximumSize(QSize(50, 16777215))

        self.edit_grid.addWidget(self.path_browse_button, 1, 2, 1, 1)

        self.name_label = QLabel(Dialog)
        self.name_label.setObjectName(u"name_label")
        self.name_label.setWordWrap(True)

        self.edit_grid.addWidget(self.name_label, 0, 0, 1, 1)

        self.path_line_edit = QLineEdit(Dialog)
        self.path_line_edit.setObjectName(u"path_line_edit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.path_line_edit.sizePolicy().hasHeightForWidth())
        self.path_line_edit.setSizePolicy(sizePolicy1)
        self.path_line_edit.setMinimumSize(QSize(0, 0))
        self.path_line_edit.setFrame(True)

        self.edit_grid.addWidget(self.path_line_edit, 1, 1, 1, 1)

        self.path_label = QLabel(Dialog)
        self.path_label.setObjectName(u"path_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.path_label.sizePolicy().hasHeightForWidth())
        self.path_label.setSizePolicy(sizePolicy2)
        self.path_label.setMinimumSize(QSize(0, 0))
        self.path_label.setWordWrap(True)

        self.edit_grid.addWidget(self.path_label, 1, 0, 1, 1)

        self.name_line_edit = ConanRefLineEdit(Dialog)
        self.name_line_edit.setObjectName(u"name_line_edit")

        self.edit_grid.addWidget(self.name_line_edit, 0, 1, 1, 1)

        self.output_folder_line_edit = QLineEdit(Dialog)
        self.output_folder_line_edit.setObjectName(u"output_folder_line_edit")

        self.edit_grid.addWidget(self.output_folder_line_edit, 2, 1, 1, 1)

        self.output_folder_browse_button = QPushButton(Dialog)
        self.output_folder_browse_button.setObjectName(u"output_folder_browse_button")
        self.output_folder_browse_button.setMaximumSize(QSize(50, 16777215))

        self.edit_grid.addWidget(self.output_folder_browse_button, 2, 2, 1, 1)

        self.edit_grid.setRowStretch(0, 1)

        self.verticalLayout.addLayout(self.edit_grid)

        self.button_box = QDialogButtonBox(Dialog)
        self.button_box.setObjectName(u"button_box")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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
        self.output_folder_label.setText(QCoreApplication.translate("Dialog", u"Output Folder", None))
        self.path_browse_button.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.name_label.setText(QCoreApplication.translate("Dialog", u"Reference", None))
        self.path_label.setText(QCoreApplication.translate("Dialog", u"Path", None))
        self.output_folder_browse_button.setText(QCoreApplication.translate("Dialog", u"...", None))
    # retranslateUi

