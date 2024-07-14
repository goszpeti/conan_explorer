# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'conan_search.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
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
    QListView, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QSplitter, QTextBrowser, QToolButton,
    QTreeView, QVBoxLayout, QWidget)

from conan_explorer.ui.widgets.conan_line_edit import ConanRefLineEdit

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(432, 391)
        Form.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 1, 1, 2)
        self.search_text_button_layout = QHBoxLayout()
        self.search_text_button_layout.setObjectName(u"search_text_button_layout")
        self.search_text_button_layout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.search_line = ConanRefLineEdit(Form)
        self.search_line.setObjectName(u"search_line")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_line.sizePolicy().hasHeightForWidth())
        self.search_line.setSizePolicy(sizePolicy)
        self.search_line.setMinimumSize(QSize(100, 0))
        self.search_line.setMaximumSize(QSize(16777215, 16777215))
        self.search_line.setSizeIncrement(QSize(0, 0))
        self.search_line.setBaseSize(QSize(500, 0))
        self.search_line.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.search_line.setClearButtonEnabled(True)

        self.search_text_button_layout.addWidget(self.search_line)

        self.search_button = QPushButton(Form)
        self.search_button.setObjectName(u"search_button")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.search_button.sizePolicy().hasHeightForWidth())
        self.search_button.setSizePolicy(sizePolicy1)
        self.search_button.setMinimumSize(QSize(150, 0))
        self.search_button.setMaximumSize(QSize(150, 16777215))
        icon = QIcon()
        icon.addFile(u"../../../assets/icons/search_packages.png", QSize(), QIcon.Normal, QIcon.Off)
        self.search_button.setIcon(icon)

        self.search_text_button_layout.addWidget(self.search_button)

        self.install_button = QPushButton(Form)
        self.install_button.setObjectName(u"install_button")
        sizePolicy1.setHeightForWidth(self.install_button.sizePolicy().hasHeightForWidth())
        self.install_button.setSizePolicy(sizePolicy1)
        self.install_button.setMinimumSize(QSize(150, 0))
        self.install_button.setMaximumSize(QSize(150, 16777215))
        icon1 = QIcon()
        icon1.addFile(u"../../../assets/icons/download_pkg.png", QSize(), QIcon.Normal, QIcon.Off)
        self.install_button.setIcon(icon1)

        self.search_text_button_layout.addWidget(self.install_button)

        self.search_text_button_layout.setStretch(0, 1)
        self.search_text_button_layout.setStretch(1, 1)
        self.search_text_button_layout.setStretch(2, 1)

        self.verticalLayout.addLayout(self.search_text_button_layout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.remote_toggle_button = QToolButton(Form)
        self.remote_toggle_button.setObjectName(u"remote_toggle_button")
        self.remote_toggle_button.setStyleSheet(u" border: none; ")
        self.remote_toggle_button.setCheckable(True)
        self.remote_toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.remote_toggle_button.setArrowType(Qt.ArrowType.RightArrow)

        self.horizontalLayout.addWidget(self.remote_toggle_button)

        self.remote_hline = QFrame(Form)
        self.remote_hline.setObjectName(u"remote_hline")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.remote_hline.sizePolicy().hasHeightForWidth())
        self.remote_hline.setSizePolicy(sizePolicy2)
        self.remote_hline.setStyleSheet(u"")
        self.remote_hline.setFrameShape(QFrame.Shape.HLine)
        self.remote_hline.setFrameShadow(QFrame.Shadow.Sunken)
        self.remote_hline.setLineWidth(2)

        self.horizontalLayout.addWidget(self.remote_hline)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.select_all_widget = QListWidget(self.frame)
        __qlistwidgetitem = QListWidgetItem(self.select_all_widget)
        __qlistwidgetitem.setCheckState(Qt.Checked);
        __qlistwidgetitem.setFlags(Qt.ItemIsSelectable|Qt.ItemIsDragEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled|Qt.ItemIsAutoTristate);
        self.select_all_widget.setObjectName(u"select_all_widget")
        sizePolicy1.setHeightForWidth(self.select_all_widget.sizePolicy().hasHeightForWidth())
        self.select_all_widget.setSizePolicy(sizePolicy1)
        self.select_all_widget.setMaximumSize(QSize(16777215, 30))
        self.select_all_widget.setFrameShape(QFrame.Shape.NoFrame)
        self.select_all_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.select_all_widget.setResizeMode(QListView.ResizeMode.Fixed)
        self.select_all_widget.setUniformItemSizes(True)

        self.verticalLayout_2.addWidget(self.select_all_widget)

        self.remote_list = QListWidget(self.frame)
        self.remote_list.setObjectName(u"remote_list")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.remote_list.sizePolicy().hasHeightForWidth())
        self.remote_list.setSizePolicy(sizePolicy3)
        self.remote_list.setMinimumSize(QSize(0, 0))
        self.remote_list.setMaximumSize(QSize(16777215, 16777215))
        self.remote_list.setFrameShape(QFrame.Shape.NoFrame)
        self.remote_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.remote_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.remote_list.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.remote_list.setAutoScroll(False)
        self.remote_list.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        self.remote_list.setMovement(QListView.Movement.Snap)
        self.remote_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.remote_list.setLayoutMode(QListView.LayoutMode.Batched)
        self.remote_list.setUniformItemSizes(True)
        self.remote_list.setSelectionRectVisible(False)
        self.remote_list.setSortingEnabled(True)

        self.verticalLayout_2.addWidget(self.remote_list)

        self.verticalLayout_2.setStretch(1, 1)

        self.verticalLayout.addWidget(self.frame)

        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.layoutWidget_2 = QWidget(self.splitter)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.results_layout = QVBoxLayout(self.layoutWidget_2)
        self.results_layout.setObjectName(u"results_layout")
        self.results_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.results_layout.setContentsMargins(2, 0, 0, 0)
        self.results_label = QLabel(self.layoutWidget_2)
        self.results_label.setObjectName(u"results_label")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.results_label.sizePolicy().hasHeightForWidth())
        self.results_label.setSizePolicy(sizePolicy4)
        font = QFont()
        font.setBold(True)
        self.results_label.setFont(font)

        self.results_layout.addWidget(self.results_label)

        self.search_results_tree_view = QTreeView(self.layoutWidget_2)
        self.search_results_tree_view.setObjectName(u"search_results_tree_view")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.search_results_tree_view.sizePolicy().hasHeightForWidth())
        self.search_results_tree_view.setSizePolicy(sizePolicy5)
        self.search_results_tree_view.setFrameShape(QFrame.Shape.NoFrame)
        self.search_results_tree_view.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.search_results_tree_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.search_results_tree_view.setSortingEnabled(True)
        self.search_results_tree_view.setAnimated(True)

        self.results_layout.addWidget(self.search_results_tree_view)

        self.splitter.addWidget(self.layoutWidget_2)
        self.layoutWidget_3 = QWidget(self.splitter)
        self.layoutWidget_3.setObjectName(u"layoutWidget_3")
        self.pkg_info_layout = QVBoxLayout(self.layoutWidget_3)
        self.pkg_info_layout.setObjectName(u"pkg_info_layout")
        self.pkg_info_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.pkg_info_layout.setContentsMargins(4, 0, 0, 0)
        self.package_info_label = QLabel(self.layoutWidget_3)
        self.package_info_label.setObjectName(u"package_info_label")
        sizePolicy4.setHeightForWidth(self.package_info_label.sizePolicy().hasHeightForWidth())
        self.package_info_label.setSizePolicy(sizePolicy4)
        self.package_info_label.setMinimumSize(QSize(20, 0))
        self.package_info_label.setBaseSize(QSize(20, 0))
        self.package_info_label.setFont(font)

        self.pkg_info_layout.addWidget(self.package_info_label)

        self.package_info_text = QTextBrowser(self.layoutWidget_3)
        self.package_info_text.setObjectName(u"package_info_text")
        sizePolicy5.setHeightForWidth(self.package_info_text.sizePolicy().hasHeightForWidth())
        self.package_info_text.setSizePolicy(sizePolicy5)
        self.package_info_text.setMinimumSize(QSize(200, 20))
        self.package_info_text.setFrameShape(QFrame.Shape.NoFrame)
        self.package_info_text.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.pkg_info_layout.addWidget(self.package_info_text)

        self.splitter.addWidget(self.layoutWidget_3)

        self.verticalLayout.addWidget(self.splitter)

        QWidget.setTabOrder(self.search_line, self.search_button)
        QWidget.setTabOrder(self.search_button, self.install_button)
        QWidget.setTabOrder(self.install_button, self.remote_toggle_button)
        QWidget.setTabOrder(self.remote_toggle_button, self.search_results_tree_view)
        QWidget.setTabOrder(self.search_results_tree_view, self.package_info_text)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Conan Search", None))
        self.search_line.setText("")
        self.search_line.setPlaceholderText(QCoreApplication.translate("Form", u"*", None))
        self.search_button.setText(QCoreApplication.translate("Form", u"Search", None))
        self.install_button.setText(QCoreApplication.translate("Form", u"Install", None))
        self.remote_toggle_button.setText(QCoreApplication.translate("Form", u"Remotes", None))

        __sortingEnabled = self.select_all_widget.isSortingEnabled()
        self.select_all_widget.setSortingEnabled(False)
        ___qlistwidgetitem = self.select_all_widget.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("Form", u"Select/Deselect All", None));
        self.select_all_widget.setSortingEnabled(__sortingEnabled)

        self.results_label.setText(QCoreApplication.translate("Form", u"Results", None))
        self.package_info_label.setText(QCoreApplication.translate("Form", u"Package Info", None))
    # retranslateUi

