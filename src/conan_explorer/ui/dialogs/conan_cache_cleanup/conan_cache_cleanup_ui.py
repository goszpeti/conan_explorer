# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'conan_cache_cleanup.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
    QFrame, QHBoxLayout, QHeaderView, QLabel,
    QSizePolicy, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(524, 307)
        Dialog.setSizeGripEnabled(True)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.question_label = QLabel(self.frame)
        self.question_label.setObjectName(u"question_label")
        self.question_label.setLineWidth(0)

        self.horizontalLayout.addWidget(self.question_label)

        self.icon = QLabel(self.frame)
        self.icon.setObjectName(u"icon")

        self.horizontalLayout.addWidget(self.icon)

        self.horizontalLayout.setStretch(0, 1)

        self.verticalLayout.addWidget(self.frame)

        self.cleanup_tree_widget = QTreeWidget(Dialog)
        self.cleanup_tree_widget.setObjectName(u"cleanup_tree_widget")

        self.verticalLayout.addWidget(self.cleanup_tree_widget)

        self.button_box = QDialogButtonBox(Dialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(Dialog)
        self.button_box.accepted.connect(Dialog.accept)
        self.button_box.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Delete folders", None))
        self.question_label.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.icon.setText("")
        ___qtreewidgetitem = self.cleanup_tree_widget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("Dialog", u"Size", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Dialog", u"Conan Reference", None));
    # retranslateUi

