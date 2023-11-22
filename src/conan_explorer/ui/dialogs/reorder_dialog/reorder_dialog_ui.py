# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'reorder_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFrame, QGridLayout, QLayout, QListView,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_rearrange_dialog(object):
    def setupUi(self, rearrange_dialog):
        if not rearrange_dialog.objectName():
            rearrange_dialog.setObjectName(u"rearrange_dialog")
        rearrange_dialog.resize(443, 331)
        self.gridLayout = QGridLayout(rearrange_dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.list_view = QListView(rearrange_dialog)
        self.list_view.setObjectName(u"list_view")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.list_view.sizePolicy().hasHeightForWidth())
        self.list_view.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.list_view, 0, 0, 1, 1)

        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.setObjectName(u"vertical_layout")
        self.move_up_button = QPushButton(rearrange_dialog)
        self.move_up_button.setObjectName(u"move_up_button")

        self.vertical_layout.addWidget(self.move_up_button)

        self.line = QFrame(rearrange_dialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.vertical_layout.addWidget(self.line)

        self.move_down_button = QPushButton(rearrange_dialog)
        self.move_down_button.setObjectName(u"move_down_button")

        self.vertical_layout.addWidget(self.move_down_button)

        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.vertical_layout.addItem(self.vertical_spacer)


        self.gridLayout.addLayout(self.vertical_layout, 0, 1, 1, 1)

        self.button_box = QDialogButtonBox(rearrange_dialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Ok)
        self.button_box.setCenterButtons(False)

        self.gridLayout.addWidget(self.button_box, 1, 0, 1, 1)


        self.retranslateUi(rearrange_dialog)
        self.button_box.accepted.connect(rearrange_dialog.accept)
        self.button_box.rejected.connect(rearrange_dialog.reject)

        QMetaObject.connectSlotsByName(rearrange_dialog)
    # setupUi

    def retranslateUi(self, rearrange_dialog):
        rearrange_dialog.setWindowTitle(QCoreApplication.translate("rearrange_dialog", u"Rearrange App Grid", None))
        self.move_up_button.setText(QCoreApplication.translate("rearrange_dialog", u"Move up", None))
        self.move_down_button.setText(QCoreApplication.translate("rearrange_dialog", u"Move down", None))
    # retranslateUi

