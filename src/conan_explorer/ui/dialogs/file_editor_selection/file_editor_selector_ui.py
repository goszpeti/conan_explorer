# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'file_editor_selector.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialogButtonBox, QFrame,
    QGridLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(671, 239)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.description_label = QLabel(Form)
        self.description_label.setObjectName(u"description_label")
        self.description_label.setTextFormat(Qt.RichText)
        self.description_label.setWordWrap(True)

        self.verticalLayout.addWidget(self.description_label)

        self.edit_frame = QFrame(Form)
        self.edit_frame.setObjectName(u"edit_frame")
        self.edit_frame.setFrameShape(QFrame.StyledPanel)
        self.edit_frame.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.edit_frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.file_edit = QLineEdit(self.edit_frame)
        self.file_edit.setObjectName(u"file_edit")

        self.gridLayout.addWidget(self.file_edit, 0, 0, 1, 1)

        self.browse_button = QPushButton(self.edit_frame)
        self.browse_button.setObjectName(u"browse_button")

        self.gridLayout.addWidget(self.browse_button, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.edit_frame)

        self.button_box = QDialogButtonBox(Form)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.description_label.setText(QCoreApplication.translate("Form", u"<html><head/><body><p>Select editor executable to use with right click &quot;Edit File&quot; option. </p><p>Most editors will work, though they have to support on the commandline the following calling convention: '&lt;editor_executable&gt; &lt;file_name&gt;'.</p></body></html>", None))
        self.browse_button.setText(QCoreApplication.translate("Form", u"Browse", None))
    # retranslateUi

