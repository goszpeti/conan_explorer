# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'example.ui'
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
from PySide6.QtWidgets import (QApplication, QHeaderView, QLabel, QPushButton,
    QSizePolicy, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(466, 359)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tree_widget = QTreeWidget(Dialog)
        __qtreewidgetitem = QTreeWidgetItem(self.tree_widget)
        QTreeWidgetItem(__qtreewidgetitem)
        self.tree_widget.setObjectName(u"tree_widget")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree_widget.sizePolicy().hasHeightForWidth())
        self.tree_widget.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.tree_widget)

        self.icon_label = QLabel(Dialog)
        self.icon_label.setObjectName(u"icon_label")

        self.verticalLayout.addWidget(self.icon_label)

        self.push_button = QPushButton(Dialog)
        self.push_button.setObjectName(u"push_button")

        self.verticalLayout.addWidget(self.push_button)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        ___qtreewidgetitem = self.tree_widget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("Dialog", u"Coloumn2", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Dialog", u"Coloumn1", None));

        __sortingEnabled = self.tree_widget.isSortingEnabled()
        self.tree_widget.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.tree_widget.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("Dialog", u"Element1", None));
        ___qtreewidgetitem2 = ___qtreewidgetitem1.child(0)
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("Dialog", u"Element2", None));
        self.tree_widget.setSortingEnabled(__sortingEnabled)

        self.icon_label.setText(QCoreApplication.translate("Dialog", u"Icon", None))
        self.push_button.setText(QCoreApplication.translate("Dialog", u"Do Something", None))
    # retranslateUi

