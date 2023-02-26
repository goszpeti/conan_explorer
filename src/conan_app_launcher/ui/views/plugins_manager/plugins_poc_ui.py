# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plugins_poc.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHeaderView,
    QPushButton, QSizePolicy, QSpacerItem, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(645, 454)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.treeWidget = QTreeWidget(Form)
        icon = QIcon()
        icon.addFile(u"../../assets/icons/about.svg", QSize(), QIcon.Normal, QIcon.On)
        __qtreewidgetitem = QTreeWidgetItem(self.treeWidget)
        __qtreewidgetitem1 = QTreeWidgetItem(__qtreewidgetitem)
        __qtreewidgetitem1.setIcon(0, icon);
        self.treeWidget.setObjectName(u"treeWidget")

        self.gridLayout.addWidget(self.treeWidget, 0, 0, 1, 1)

        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButton = QPushButton(self.frame)
        self.pushButton.setObjectName(u"pushButton")
        icon1 = QIcon()
        icon1.addFile(u"../../assets/icons/plus_rounded.svg", QSize(), QIcon.Normal, QIcon.On)
        self.pushButton.setIcon(icon1)

        self.verticalLayout.addWidget(self.pushButton)

        self.pushButton_3 = QPushButton(self.frame)
        self.pushButton_3.setObjectName(u"pushButton_3")
        icon2 = QIcon()
        icon2.addFile(u"../../assets/icons/hide.svg", QSize(), QIcon.Normal, QIcon.On)
        self.pushButton_3.setIcon(icon2)

        self.verticalLayout.addWidget(self.pushButton_3)

        self.pushButton_2 = QPushButton(self.frame)
        self.pushButton_2.setObjectName(u"pushButton_2")
        icon3 = QIcon()
        icon3.addFile(u"../../assets/icons/minus_rounded.svg", QSize(), QIcon.Normal, QIcon.On)
        self.pushButton_2.setIcon(icon3)

        self.verticalLayout.addWidget(self.pushButton_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout.addWidget(self.frame, 0, 1, 2, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(4, QCoreApplication.translate("Form", u"Description", None));
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("Form", u"Author", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("Form", u"Version", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("Form", u"Name", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Form", u"Path", None));

        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.treeWidget.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("Form", u"dir/plugins.ini", None));
        ___qtreewidgetitem2 = ___qtreewidgetitem1.child(0)
        ___qtreewidgetitem2.setText(3, QCoreApplication.translate("Form", u"Myself", None));
        ___qtreewidgetitem2.setText(2, QCoreApplication.translate("Form", u"0.1.1", None));
        ___qtreewidgetitem2.setText(1, QCoreApplication.translate("Form", u"MY Plugin", None));
        self.treeWidget.setSortingEnabled(__sortingEnabled)

        self.pushButton.setText(QCoreApplication.translate("Form", u"Add new Plugin", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"Enable / Disable", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"Remove Plugin", None))
    # retranslateUi

