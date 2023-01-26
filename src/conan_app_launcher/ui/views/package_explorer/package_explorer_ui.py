# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'package_explorer.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QLayout,
    QLineEdit, QPushButton, QSizePolicy, QSplitter,
    QTreeView, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(716, 573)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
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
        self.package_path_label = QLabel(self.splitter_filter)
        self.package_path_label.setObjectName(u"package_path_label")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(5)
        sizePolicy4.setVerticalStretch(1)
        sizePolicy4.setHeightForWidth(self.package_path_label.sizePolicy().hasHeightForWidth())
        self.package_path_label.setSizePolicy(sizePolicy4)
        self.package_path_label.setMinimumSize(QSize(300, 32))
        self.package_path_label.setMaximumSize(QSize(16777215, 32))
        self.package_path_label.setBaseSize(QSize(500, 0))
        self.package_path_label.setScaledContents(True)
        self.package_path_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.package_path_label.setWordWrap(False)
        self.package_path_label.setOpenExternalLinks(True)
        self.package_path_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)
        self.splitter_filter.addWidget(self.package_path_label)

        self.local_packages_bar_layout.addWidget(self.splitter_filter)


        self.verticalLayout.addLayout(self.local_packages_bar_layout)

        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy5)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.package_select_view = QTreeView(self.splitter)
        self.package_select_view.setObjectName(u"package_select_view")
        sizePolicy6 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy6.setHorizontalStretch(1)
        sizePolicy6.setVerticalStretch(1)
        sizePolicy6.setHeightForWidth(self.package_select_view.sizePolicy().hasHeightForWidth())
        self.package_select_view.setSizePolicy(sizePolicy6)
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
        sizePolicy7 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy7.setHorizontalStretch(2)
        sizePolicy7.setVerticalStretch(1)
        sizePolicy7.setHeightForWidth(self.package_file_view.sizePolicy().hasHeightForWidth())
        self.package_file_view.setSizePolicy(sizePolicy7)
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
        self.package_path_label.setText("")
    # retranslateUi

