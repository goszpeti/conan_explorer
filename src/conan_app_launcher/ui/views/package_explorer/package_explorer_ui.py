# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'package_explorer.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QLayout,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QSplitter, QTextBrowser, QTextEdit, QTreeView,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(546, 330)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 3)
        self.local_packages_bar_layout = QHBoxLayout()
        self.local_packages_bar_layout.setObjectName(u"local_packages_bar_layout")
        self.local_packages_bar_layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.local_packages_bar_layout.setContentsMargins(-1, -1, 7, -1)
        self.refresh_button = QPushButton(Form)
        self.refresh_button.setObjectName(u"refresh_button")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.refresh_button.sizePolicy().hasHeightForWidth())
        self.refresh_button.setSizePolicy(sizePolicy)
        self.refresh_button.setMinimumSize(QSize(32, 32))
        self.refresh_button.setMaximumSize(QSize(32, 32))

        self.local_packages_bar_layout.addWidget(self.refresh_button)

        self.package_filter_label = QLabel(Form)
        self.package_filter_label.setObjectName(u"package_filter_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.package_filter_label.sizePolicy().hasHeightForWidth())
        self.package_filter_label.setSizePolicy(sizePolicy1)
        self.package_filter_label.setMinimumSize(QSize(0, 32))
        self.package_filter_label.setMaximumSize(QSize(16777215, 32))

        self.local_packages_bar_layout.addWidget(self.package_filter_label)

        self.splitter_filter = QSplitter(Form)
        self.splitter_filter.setObjectName(u"splitter_filter")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.splitter_filter.sizePolicy().hasHeightForWidth())
        self.splitter_filter.setSizePolicy(sizePolicy2)
        self.splitter_filter.setOrientation(Qt.Horizontal)
        self.splitter_filter.setChildrenCollapsible(False)
        self.package_filter_edit = QLineEdit(self.splitter_filter)
        self.package_filter_edit.setObjectName(u"package_filter_edit")
        self.package_filter_edit.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.package_filter_edit.sizePolicy().hasHeightForWidth())
        self.package_filter_edit.setSizePolicy(sizePolicy3)
        self.package_filter_edit.setMinimumSize(QSize(175, 32))
        self.package_filter_edit.setMaximumSize(QSize(400, 32))
        font = QFont()
        font.setPointSize(10)
        self.package_filter_edit.setFont(font)
        self.package_filter_edit.setInputMethodHints(Qt.ImhNone)
        self.package_filter_edit.setClearButtonEnabled(True)
        self.splitter_filter.addWidget(self.package_filter_edit)

        self.local_packages_bar_layout.addWidget(self.splitter_filter)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.local_packages_bar_layout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.local_packages_bar_layout)

        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy4)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.package_select_view = QTreeView(self.splitter)
        self.package_select_view.setObjectName(u"package_select_view")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy5.setHorizontalStretch(1)
        sizePolicy5.setVerticalStretch(1)
        sizePolicy5.setHeightForWidth(self.package_select_view.sizePolicy().hasHeightForWidth())
        self.package_select_view.setSizePolicy(sizePolicy5)
        self.package_select_view.setMinimumSize(QSize(100, 0))
        self.package_select_view.setFrameShape(QFrame.NoFrame)
        self.package_select_view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.package_select_view.setIndentation(15)
        self.package_select_view.setUniformRowHeights(True)
        self.package_select_view.setSortingEnabled(True)
        self.package_select_view.setAnimated(True)
        self.package_select_view.setHeaderHidden(False)
        self.splitter.addWidget(self.package_select_view)
        self.package_select_view.header().setVisible(True)
        self.package_file_view = QTreeView(self.splitter)
        self.package_file_view.setObjectName(u"package_file_view")
        sizePolicy6 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy6.setHorizontalStretch(2)
        sizePolicy6.setVerticalStretch(1)
        sizePolicy6.setHeightForWidth(self.package_file_view.sizePolicy().hasHeightForWidth())
        self.package_file_view.setSizePolicy(sizePolicy6)
        self.package_file_view.setMinimumSize(QSize(100, 0))
        self.package_file_view.setFrameShape(QFrame.NoFrame)
        self.package_file_view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.package_file_view.setDragDropMode(QAbstractItemView.DragDrop)
        self.package_file_view.setDefaultDropAction(Qt.TargetMoveAction)
        self.package_file_view.setIndentation(15)
        self.package_file_view.setUniformRowHeights(True)
        self.package_file_view.setItemsExpandable(True)
        self.package_file_view.setSortingEnabled(True)
        self.package_file_view.setAnimated(True)
        self.splitter.addWidget(self.package_file_view)

        self.verticalLayout.addWidget(self.splitter)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(4, -1, -1, -1)
        self.package_path_label_2 = QLabel(Form)
        self.package_path_label_2.setObjectName(u"package_path_label_2")

        self.horizontalLayout.addWidget(self.package_path_label_2)

        self.package_path_label = QTextBrowser(Form)
        self.package_path_label.setObjectName(u"package_path_label")
        sizePolicy7 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.package_path_label.sizePolicy().hasHeightForWidth())
        self.package_path_label.setSizePolicy(sizePolicy7)
        self.package_path_label.setMaximumSize(QSize(16777215, 32))
        self.package_path_label.setFrameShape(QFrame.NoFrame)
        self.package_path_label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.package_path_label.setLineWrapMode(QTextEdit.NoWrap)
        self.package_path_label.setOverwriteMode(False)

        self.horizontalLayout.addWidget(self.package_path_label)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.refresh_button.setToolTip(QCoreApplication.translate("Form", u"Refresh package list view", None))
#endif // QT_CONFIG(tooltip)
        self.refresh_button.setText("")
        self.package_filter_label.setText(QCoreApplication.translate("Form", u"Filter:", None))
        self.package_filter_edit.setPlaceholderText(QCoreApplication.translate("Form", u"*", None))
        self.package_path_label_2.setText(QCoreApplication.translate("Form", u"Package path:", None))
        self.package_path_label.setHtml(QCoreApplication.translate("Form", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
    # retranslateUi

