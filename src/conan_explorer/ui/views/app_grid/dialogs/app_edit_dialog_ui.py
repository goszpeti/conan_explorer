# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app_edit_dialog.ui'
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
    QPushButton, QSizePolicy, QTextEdit, QToolButton,
    QVBoxLayout, QWidget)

from conan_explorer.ui.widgets import AnimatedToggle
from conan_explorer.ui.widgets.conan_line_edit import ConanRefLineEdit

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(769, 568)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
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
        self.edit_grid.setVerticalSpacing(8)
        self.conan_ref_line_edit = ConanRefLineEdit(Dialog)
        self.conan_ref_line_edit.setObjectName(u"conan_ref_line_edit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.conan_ref_line_edit.sizePolicy().hasHeightForWidth())
        self.conan_ref_line_edit.setSizePolicy(sizePolicy1)
        self.conan_ref_line_edit.setMinimumSize(QSize(400, 0))

        self.edit_grid.addWidget(self.conan_ref_line_edit, 1, 1, 1, 1)

        self.icon_line_edit = QLineEdit(Dialog)
        self.icon_line_edit.setObjectName(u"icon_line_edit")

        self.edit_grid.addWidget(self.icon_line_edit, 6, 1, 1, 1)

        self.args_line_edit = QLineEdit(Dialog)
        self.args_line_edit.setObjectName(u"args_line_edit")
        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.args_line_edit.sizePolicy().hasHeightForWidth())
        self.args_line_edit.setSizePolicy(sizePolicy2)

        self.edit_grid.addWidget(self.args_line_edit, 4, 1, 1, 1)

        self.execpath_line_edit = QLineEdit(Dialog)
        self.execpath_line_edit.setObjectName(u"execpath_line_edit")

        self.edit_grid.addWidget(self.execpath_line_edit, 3, 1, 1, 1)

        self.execpath_label = QLabel(Dialog)
        self.execpath_label.setObjectName(u"execpath_label")
        self.execpath_label.setWordWrap(True)

        self.edit_grid.addWidget(self.execpath_label, 3, 0, 1, 1)

        self.conan_opts_text_edit = QTextEdit(Dialog)
        self.conan_opts_text_edit.setObjectName(u"conan_opts_text_edit")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.conan_opts_text_edit.sizePolicy().hasHeightForWidth())
        self.conan_opts_text_edit.setSizePolicy(sizePolicy3)
        self.conan_opts_text_edit.setMinimumSize(QSize(600, 0))
        self.conan_opts_text_edit.setAutoFormatting(QTextEdit.AutoNone)

        self.edit_grid.addWidget(self.conan_opts_text_edit, 2, 1, 1, 1)

        self.name_line_edit = QLineEdit(Dialog)
        self.name_line_edit.setObjectName(u"name_line_edit")
        self.name_line_edit.setMinimumSize(QSize(500, 0))

        self.edit_grid.addWidget(self.name_line_edit, 0, 1, 1, 1)

        self.icon_label = QLabel(Dialog)
        self.icon_label.setObjectName(u"icon_label")
        self.icon_label.setTextFormat(Qt.RichText)
        self.icon_label.setWordWrap(True)

        self.edit_grid.addWidget(self.icon_label, 6, 0, 1, 1)

        self.icon_browse_button = QToolButton(Dialog)
        self.icon_browse_button.setObjectName(u"icon_browse_button")
        sizePolicy2.setHeightForWidth(self.icon_browse_button.sizePolicy().hasHeightForWidth())
        self.icon_browse_button.setSizePolicy(sizePolicy2)

        self.edit_grid.addWidget(self.icon_browse_button, 6, 2, 1, 1)

        self.conan_opts_label = QLabel(Dialog)
        self.conan_opts_label.setObjectName(u"conan_opts_label")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.conan_opts_label.sizePolicy().hasHeightForWidth())
        self.conan_opts_label.setSizePolicy(sizePolicy4)

        self.edit_grid.addWidget(self.conan_opts_label, 2, 0, 1, 1)

        self.args_label = QLabel(Dialog)
        self.args_label.setObjectName(u"args_label")

        self.edit_grid.addWidget(self.args_label, 4, 0, 1, 1)

        self.is_console_app_label = QLabel(Dialog)
        self.is_console_app_label.setObjectName(u"is_console_app_label")

        self.edit_grid.addWidget(self.is_console_app_label, 5, 0, 1, 1)

        self.executable_browse_button = QToolButton(Dialog)
        self.executable_browse_button.setObjectName(u"executable_browse_button")
        sizePolicy2.setHeightForWidth(self.executable_browse_button.sizePolicy().hasHeightForWidth())
        self.executable_browse_button.setSizePolicy(sizePolicy2)
        self.executable_browse_button.setLayoutDirection(Qt.LeftToRight)

        self.edit_grid.addWidget(self.executable_browse_button, 3, 2, 1, 1)

        self.conan_ref_label = QLabel(Dialog)
        self.conan_ref_label.setObjectName(u"conan_ref_label")
        sizePolicy3.setHeightForWidth(self.conan_ref_label.sizePolicy().hasHeightForWidth())
        self.conan_ref_label.setSizePolicy(sizePolicy3)
        self.conan_ref_label.setMinimumSize(QSize(0, 40))
        self.conan_ref_label.setWordWrap(True)

        self.edit_grid.addWidget(self.conan_ref_label, 1, 0, 1, 1)

        self.is_console_app_checkbox = AnimatedToggle(Dialog)
        self.is_console_app_checkbox.setObjectName(u"is_console_app_checkbox")

        self.edit_grid.addWidget(self.is_console_app_checkbox, 5, 1, 1, 1)

        self.name_label = QLabel(Dialog)
        self.name_label.setObjectName(u"name_label")
        self.name_label.setWordWrap(True)

        self.edit_grid.addWidget(self.name_label, 0, 0, 1, 1)

        self.install_button = QPushButton(Dialog)
        self.install_button.setObjectName(u"install_button")
        sizePolicy5 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.install_button.sizePolicy().hasHeightForWidth())
        self.install_button.setSizePolicy(sizePolicy5)
        self.install_button.setFlat(False)

        self.edit_grid.addWidget(self.install_button, 7, 1, 1, 1)

        self.edit_grid.setRowStretch(0, 1)
        self.edit_grid.setRowStretch(1, 1)
        self.edit_grid.setColumnStretch(1, 1)

        self.verticalLayout.addLayout(self.edit_grid)

        self.note_label = QLabel(Dialog)
        self.note_label.setObjectName(u"note_label")

        self.verticalLayout.addWidget(self.note_label)

        self.button_box = QDialogButtonBox(Dialog)
        self.button_box.setObjectName(u"button_box")
        sizePolicy6 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(1)
        sizePolicy6.setVerticalStretch(1)
        sizePolicy6.setHeightForWidth(self.button_box.sizePolicy().hasHeightForWidth())
        self.button_box.setSizePolicy(sizePolicy6)
        self.button_box.setMinimumSize(QSize(0, 0))
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(Dialog)
        self.button_box.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Edit App Link", None))
        self.args_line_edit.setText("")
        self.execpath_label.setText(QCoreApplication.translate("Dialog", u"Relative path of file to open", None))
        self.conan_opts_text_edit.setHtml(QCoreApplication.translate("Dialog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:7.875pt;\"><br /></p></body></html>", None))
        self.icon_label.setText(QCoreApplication.translate("Dialog", u"Icon path (relative or absoulte)", None))
        self.icon_browse_button.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.conan_opts_label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Conan Options</p><p>using format: </p><p>name1=val1</p><p>name2=val2</p></body></html>", None))
        self.args_label.setText(QCoreApplication.translate("Dialog", u"Launch arguments", None))
        self.is_console_app_label.setText(QCoreApplication.translate("Dialog", u"Start in new console", None))
        self.executable_browse_button.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.conan_ref_label.setText(QCoreApplication.translate("Dialog", u"Conan Reference", None))
        self.is_console_app_checkbox.setText("")
        self.name_label.setText(QCoreApplication.translate("Dialog", u"Link Name", None))
        self.install_button.setText(QCoreApplication.translate("Dialog", u"Install package", None))
        self.note_label.setText(QCoreApplication.translate("Dialog", u"All relative paths resolve to the Conan package!", None))
    # retranslateUi

