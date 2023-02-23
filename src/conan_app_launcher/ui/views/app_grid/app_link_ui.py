# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app_link.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLayout, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

from conan_app_launcher.ui.widgets import ClickableIcon

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1179, 146)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QSize(0, 140))
        Form.setMaximumSize(QSize(800000, 159))
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.left_frame = QFrame(Form)
        self.left_frame.setObjectName(u"left_frame")
        self.left_frame.setMinimumSize(QSize(0, 0))
        self.left_frame.setFrameShape(QFrame.StyledPanel)
        self.left_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.left_frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.verticalLayout_2.setContentsMargins(-1, 6, -1, -1)
        self.app_button = ClickableIcon(self.left_frame)
        self.app_button.setObjectName(u"app_button")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.app_button.sizePolicy().hasHeightForWidth())
        self.app_button.setSizePolicy(sizePolicy1)
        self.app_button.setMinimumSize(QSize(150, 120))
        self.app_button.setMaximumSize(QSize(200, 120))

        self.verticalLayout_2.addWidget(self.app_button)

        self.app_name = QLabel(self.left_frame)
        self.app_name.setObjectName(u"app_name")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.app_name.sizePolicy().hasHeightForWidth())
        self.app_name.setSizePolicy(sizePolicy2)
        self.app_name.setMinimumSize(QSize(200, 0))
        self.app_name.setAlignment(Qt.AlignCenter)
        self.app_name.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.app_name)


        self.horizontalLayout.addWidget(self.left_frame)

        self.central_frame = QFrame(Form)
        self.central_frame.setObjectName(u"central_frame")
        sizePolicy3 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.central_frame.sizePolicy().hasHeightForWidth())
        self.central_frame.setSizePolicy(sizePolicy3)
        self.central_frame.setMinimumSize(QSize(500, 0))
        self.central_frame.setFrameShape(QFrame.StyledPanel)
        self.central_frame.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.central_frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.gridLayout.setContentsMargins(-1, 4, -1, 0)
        self.conan_ref_label = QLabel(self.central_frame)
        self.conan_ref_label.setObjectName(u"conan_ref_label")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.conan_ref_label.sizePolicy().hasHeightForWidth())
        self.conan_ref_label.setSizePolicy(sizePolicy4)
        self.conan_ref_label.setMinimumSize(QSize(200, 0))
        self.conan_ref_label.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.conan_ref_label, 0, 0, 1, 1)

        self.line = QFrame(self.central_frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 1, 2, 1, 1)

        self.line_2 = QFrame(self.central_frame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_2, 0, 2, 1, 1)

        self.arguments_label = QLabel(self.central_frame)
        self.arguments_label.setObjectName(u"arguments_label")
        sizePolicy3.setHeightForWidth(self.arguments_label.sizePolicy().hasHeightForWidth())
        self.arguments_label.setSizePolicy(sizePolicy3)
        self.arguments_label.setMinimumSize(QSize(80, 0))

        self.gridLayout.addWidget(self.arguments_label, 1, 4, 1, 2)

        self.arguments_value_label = QLabel(self.central_frame)
        self.arguments_value_label.setObjectName(u"arguments_value_label")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.arguments_value_label.sizePolicy().hasHeightForWidth())
        self.arguments_value_label.setSizePolicy(sizePolicy5)
        self.arguments_value_label.setMinimumSize(QSize(160, 0))
        self.arguments_value_label.setMaximumSize(QSize(480, 16777215))
        self.arguments_value_label.setWordWrap(False)

        self.gridLayout.addWidget(self.arguments_value_label, 1, 6, 1, 1)

        self.label = QLabel(self.central_frame)
        self.label.setObjectName(u"label")
        sizePolicy3.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.open_shell_checkbox = QCheckBox(self.central_frame)
        self.open_shell_checkbox.setObjectName(u"open_shell_checkbox")
        self.open_shell_checkbox.setEnabled(False)
        sizePolicy5.setHeightForWidth(self.open_shell_checkbox.sizePolicy().hasHeightForWidth())
        self.open_shell_checkbox.setSizePolicy(sizePolicy5)
        self.open_shell_checkbox.setMaximumSize(QSize(16777215, 35))
        self.open_shell_checkbox.setStyleSheet(u"margin-top:50%; margin-bottom:50%;margin-left: 10%;")

        self.gridLayout.addWidget(self.open_shell_checkbox, 1, 1, 1, 1)

        self.gridLayout.setColumnStretch(5, 1)

        self.horizontalLayout.addWidget(self.central_frame)

        self.right_frame = QFrame(Form)
        self.right_frame.setObjectName(u"right_frame")
        self.right_frame.setMinimumSize(QSize(100, 0))
        self.right_frame.setFrameShape(QFrame.StyledPanel)
        self.right_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.right_frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.verticalLayout.setContentsMargins(-1, 0, -1, 0)
        self.edit_button = QPushButton(self.right_frame)
        self.edit_button.setObjectName(u"edit_button")
        sizePolicy5.setHeightForWidth(self.edit_button.sizePolicy().hasHeightForWidth())
        self.edit_button.setSizePolicy(sizePolicy5)
        self.edit_button.setMinimumSize(QSize(80, 0))

        self.verticalLayout.addWidget(self.edit_button)

        self.remove_button = QPushButton(self.right_frame)
        self.remove_button.setObjectName(u"remove_button")
        sizePolicy1.setHeightForWidth(self.remove_button.sizePolicy().hasHeightForWidth())
        self.remove_button.setSizePolicy(sizePolicy1)
        self.remove_button.setMinimumSize(QSize(80, 0))

        self.verticalLayout.addWidget(self.remove_button)


        self.horizontalLayout.addWidget(self.right_frame)

        self.horizontalLayout.setStretch(1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.app_button.setText("")
        self.app_name.setText(QCoreApplication.translate("Form", u"Name", None))
        self.conan_ref_label.setText(QCoreApplication.translate("Form", u"example/9.9.9@user/channel", None))
        self.arguments_label.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-weight:700;\">Arguments:</span></p></body></html>", None))
        self.arguments_value_label.setText(QCoreApplication.translate("Form", u"-f silver_output -d C:Reposfep_interface_silver3exampledemo_simplesilver_example.description -t standard_data -s fepifsilver_default_system", None))
        self.label.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-weight:700;\">Open terminal:</span></p></body></html>", None))
        self.open_shell_checkbox.setText("")
        self.edit_button.setText(QCoreApplication.translate("Form", u"Edit", None))
        self.remove_button.setText(QCoreApplication.translate("Form", u"Remove", None))
    # retranslateUi

