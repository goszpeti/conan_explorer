# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app_link.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QLayout, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

from conan_explorer.ui.widgets import (AnimatedToggle, ClickableIcon)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(882, 140)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QSize(0, 140))
        self.horizontalLayout_3 = QHBoxLayout(Form)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 2, 0, 2)
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
        self.app_button.setMinimumSize(QSize(150, 100))
        self.app_button.setMaximumSize(QSize(150, 100))

        self.verticalLayout_2.addWidget(self.app_button)

        self.app_name_label = QLabel(self.left_frame)
        self.app_name_label.setObjectName(u"app_name_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.app_name_label.sizePolicy().hasHeightForWidth())
        self.app_name_label.setSizePolicy(sizePolicy2)
        self.app_name_label.setMinimumSize(QSize(0, 0))
        self.app_name_label.setMaximumSize(QSize(180, 16777215))
        self.app_name_label.setAlignment(Qt.AlignCenter)
        self.app_name_label.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.app_name_label)


        self.horizontalLayout_3.addWidget(self.left_frame)

        self.central_frame = QFrame(Form)
        self.central_frame.setObjectName(u"central_frame")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.central_frame.sizePolicy().hasHeightForWidth())
        self.central_frame.setSizePolicy(sizePolicy3)
        self.central_frame.setMinimumSize(QSize(0, 0))
        self.central_frame.setFrameShape(QFrame.StyledPanel)
        self.central_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.central_frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.central_left_frame = QFrame(self.central_frame)
        self.central_left_frame.setObjectName(u"central_left_frame")
        sizePolicy2.setHeightForWidth(self.central_left_frame.sizePolicy().hasHeightForWidth())
        self.central_left_frame.setSizePolicy(sizePolicy2)
        self.central_left_frame.setFrameShape(QFrame.StyledPanel)
        self.central_left_frame.setFrameShadow(QFrame.Raised)
        self.formLayout = QFormLayout(self.central_left_frame)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(-1, -1, 0, -1)
        self.open_shell_checkbox = AnimatedToggle(self.central_left_frame)
        self.open_shell_checkbox.setObjectName(u"open_shell_checkbox")
        self.open_shell_checkbox.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.open_shell_checkbox.sizePolicy().hasHeightForWidth())
        self.open_shell_checkbox.setSizePolicy(sizePolicy1)
        self.open_shell_checkbox.setMaximumSize(QSize(16777215, 35))
        self.open_shell_checkbox.setStyleSheet(u"margin-top:50%; margin-bottom:50%;margin-left: 10%;")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.open_shell_checkbox)

        self.open_shell_label = QLabel(self.central_left_frame)
        self.open_shell_label.setObjectName(u"open_shell_label")
        sizePolicy3.setHeightForWidth(self.open_shell_label.sizePolicy().hasHeightForWidth())
        self.open_shell_label.setSizePolicy(sizePolicy3)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.open_shell_label)

        self.executable_name_label = QLabel(self.central_left_frame)
        self.executable_name_label.setObjectName(u"executable_name_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.executable_name_label)

        self.executable_value_label = QLabel(self.central_left_frame)
        self.executable_value_label.setObjectName(u"executable_value_label")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.executable_value_label)

        self.conan_ref_name_label = QLabel(self.central_left_frame)
        self.conan_ref_name_label.setObjectName(u"conan_ref_name_label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.conan_ref_name_label)

        self.conan_ref_value_label = QLabel(self.central_left_frame)
        self.conan_ref_value_label.setObjectName(u"conan_ref_value_label")
        sizePolicy3.setHeightForWidth(self.conan_ref_value_label.sizePolicy().hasHeightForWidth())
        self.conan_ref_value_label.setSizePolicy(sizePolicy3)
        self.conan_ref_value_label.setMaximumSize(QSize(16777215, 16777215))

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.conan_ref_value_label)


        self.horizontalLayout_2.addWidget(self.central_left_frame)

        self.central_right_frame = QFrame(self.central_frame)
        self.central_right_frame.setObjectName(u"central_right_frame")
        self.central_right_frame.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.central_right_frame.sizePolicy().hasHeightForWidth())
        self.central_right_frame.setSizePolicy(sizePolicy2)
        self.central_right_frame.setMaximumSize(QSize(16777215, 16777215))
        self.central_right_frame.setFrameShape(QFrame.StyledPanel)
        self.central_right_frame.setFrameShadow(QFrame.Raised)
        self.formLayout_2 = QFormLayout(self.central_right_frame)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.formLayout_2.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.arguments_name_label = QLabel(self.central_right_frame)
        self.arguments_name_label.setObjectName(u"arguments_name_label")
        sizePolicy2.setHeightForWidth(self.arguments_name_label.sizePolicy().hasHeightForWidth())
        self.arguments_name_label.setSizePolicy(sizePolicy2)
        self.arguments_name_label.setMinimumSize(QSize(0, 0))
        self.arguments_name_label.setMaximumSize(QSize(2000, 16777215))
        self.arguments_name_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.arguments_name_label)

        self.arguments_value_label = QLabel(self.central_right_frame)
        self.arguments_value_label.setObjectName(u"arguments_value_label")
        sizePolicy2.setHeightForWidth(self.arguments_value_label.sizePolicy().hasHeightForWidth())
        self.arguments_value_label.setSizePolicy(sizePolicy2)
        self.arguments_value_label.setMinimumSize(QSize(0, 0))
        self.arguments_value_label.setMaximumSize(QSize(100, 16777215))
        self.arguments_value_label.setScaledContents(False)
        self.arguments_value_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.arguments_value_label.setWordWrap(True)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.arguments_value_label)


        self.horizontalLayout_2.addWidget(self.central_right_frame)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 2)

        self.horizontalLayout_3.addWidget(self.central_frame)

        self.right_frame = QFrame(Form)
        self.right_frame.setObjectName(u"right_frame")
        self.right_frame.setMinimumSize(QSize(100, 0))
        self.right_frame.setFrameShape(QFrame.StyledPanel)
        self.right_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.right_frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.verticalLayout.setContentsMargins(6, 0, -1, 0)
        self.edit_button = QPushButton(self.right_frame)
        self.edit_button.setObjectName(u"edit_button")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.edit_button.sizePolicy().hasHeightForWidth())
        self.edit_button.setSizePolicy(sizePolicy4)
        self.edit_button.setMinimumSize(QSize(150, 0))
        self.edit_button.setMaximumSize(QSize(150, 16777215))

        self.verticalLayout.addWidget(self.edit_button)

        self.remove_button = QPushButton(self.right_frame)
        self.remove_button.setObjectName(u"remove_button")
        sizePolicy4.setHeightForWidth(self.remove_button.sizePolicy().hasHeightForWidth())
        self.remove_button.setSizePolicy(sizePolicy4)
        self.remove_button.setMinimumSize(QSize(150, 0))
        self.remove_button.setMaximumSize(QSize(150, 16777215))

        self.verticalLayout.addWidget(self.remove_button)


        self.horizontalLayout_3.addWidget(self.right_frame)

        self.horizontalLayout_3.setStretch(1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.app_button.setText("")
        self.app_name_label.setText(QCoreApplication.translate("Form", u"Name", None))
        self.open_shell_checkbox.setText("")
        self.open_shell_label.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-weight:700;\">Use terminal:</span></p></body></html>", None))
        self.executable_name_label.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-weight:700;\">Executable:</span></p></body></html>", None))
        self.executable_value_label.setText(QCoreApplication.translate("Form", u"bin/python.exe", None))
        self.conan_ref_name_label.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-weight:700;\">Reference:</span></p></body></html>", None))
        self.conan_ref_value_label.setText(QCoreApplication.translate("Form", u"example/9.9.9@user/channel", None))
        self.arguments_name_label.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-weight:700;\">Arguments:</span></p></body></html>", None))
        self.arguments_value_label.setText(QCoreApplication.translate("Form", u"-f silver_output -d C:Reposfep_interface_silver3exampledemo_simplesilver_example.description -t standard_data -s fepifsilver_default_system", None))
        self.edit_button.setText(QCoreApplication.translate("Form", u"Edit ", None))
        self.remove_button.setText(QCoreApplication.translate("Form", u"Remove ", None))
    # retranslateUi

