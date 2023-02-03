# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fluent_window.ui'
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
    QGridLayout, QHBoxLayout, QLabel, QLayout,
    QListView, QMainWindow, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSplitter, QStackedWidget,
    QTextBrowser, QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(859, 824)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(400, 400))
        palette = QPalette()
        brush = QBrush(QColor(160, 160, 160, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Highlight, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Highlight, brush)
        brush1 = QBrush(QColor(0, 120, 215, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Highlight, brush1)
        MainWindow.setPalette(palette)
        MainWindow.setAcceptDrops(True)
        icon = QIcon()
        icon.addFile(u":/icons/icon.ico", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.central_widget = QWidget(MainWindow)
        self.central_widget.setObjectName(u"central_widget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.central_widget.sizePolicy().hasHeightForWidth())
        self.central_widget.setSizePolicy(sizePolicy1)
        self.central_widget_layout = QVBoxLayout(self.central_widget)
        self.central_widget_layout.setSpacing(0)
        self.central_widget_layout.setObjectName(u"central_widget_layout")
        self.central_widget_layout.setContentsMargins(2, 1, 1, 1)
        self.main_frame = QFrame(self.central_widget)
        self.main_frame.setObjectName(u"main_frame")
        self.main_frame.setFrameShape(QFrame.NoFrame)
        self.main_frame.setFrameShadow(QFrame.Raised)
        self.main_frame.setLineWidth(0)
        self.main_frame_layout = QGridLayout(self.main_frame)
        self.main_frame_layout.setSpacing(0)
        self.main_frame_layout.setObjectName(u"main_frame_layout")
        self.main_frame_layout.setContentsMargins(0, 0, 3, 1)
        self.top_frame = QFrame(self.main_frame)
        self.top_frame.setObjectName(u"top_frame")
        self.top_frame.setMinimumSize(QSize(0, 55))
        self.top_frame.setMaximumSize(QSize(16777215, 70))
        self.top_frame.setLineWidth(0)
        self.top_frame_layout = QHBoxLayout(self.top_frame)
        self.top_frame_layout.setSpacing(0)
        self.top_frame_layout.setObjectName(u"top_frame_layout")
        self.top_frame_layout.setContentsMargins(1, 0, 0, 0)
        self.top_center_frame = QFrame(self.top_frame)
        self.top_center_frame.setObjectName(u"top_center_frame")
        self.top_center_frame.setMinimumSize(QSize(55, 0))
        self.top_center_frame.setMaximumSize(QSize(16777214, 100))
        self.top_center_frame_layout = QHBoxLayout(self.top_center_frame)
        self.top_center_frame_layout.setObjectName(u"top_center_frame_layout")
        self.top_center_frame_layout.setContentsMargins(5, 3, 0, 2)
        self.page_title = QLabel(self.top_center_frame)
        self.page_title.setObjectName(u"page_title")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.page_title.sizePolicy().hasHeightForWidth())
        self.page_title.setSizePolicy(sizePolicy2)
        font = QFont()
        font.setPointSize(24)
        self.page_title.setFont(font)

        self.top_center_frame_layout.addWidget(self.page_title)

        self.top_center_right_frame = QFrame(self.top_center_frame)
        self.top_center_right_frame.setObjectName(u"top_center_right_frame")
        sizePolicy3 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.top_center_right_frame.sizePolicy().hasHeightForWidth())
        self.top_center_right_frame.setSizePolicy(sizePolicy3)
        self.top_center_right_frame.setMinimumSize(QSize(0, 0))
        self.verticalLayout_10 = QVBoxLayout(self.top_center_right_frame)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(9, 0, 3, 0)
        self.window_btns_frame = QFrame(self.top_center_right_frame)
        self.window_btns_frame.setObjectName(u"window_btns_frame")
        self.window_btns_frame.setMinimumSize(QSize(0, 35))
        self.window_btns_frame.setMaximumSize(QSize(150, 60))
        self.window_btns_frame.setLayoutDirection(Qt.RightToLeft)
        self.window_btns_frame.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_4 = QHBoxLayout(self.window_btns_frame)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.close_button = QPushButton(self.window_btns_frame)
        self.close_button.setObjectName(u"close_button")
        self.close_button.setMinimumSize(QSize(50, 60))
        icon1 = QIcon()
        icon1.addFile(u"../../assets/icons/close.png", QSize(), QIcon.Normal, QIcon.On)
        self.close_button.setIcon(icon1)
        self.close_button.setFlat(True)

        self.horizontalLayout_4.addWidget(self.close_button)

        self.restore_max_button = QPushButton(self.window_btns_frame)
        self.restore_max_button.setObjectName(u"restore_max_button")
        self.restore_max_button.setMinimumSize(QSize(50, 60))
        icon2 = QIcon()
        icon2.addFile(u"../../assets/icons/restore.png", QSize(), QIcon.Normal, QIcon.On)
        self.restore_max_button.setIcon(icon2)
        self.restore_max_button.setFlat(True)

        self.horizontalLayout_4.addWidget(self.restore_max_button)

        self.minimize_button = QPushButton(self.window_btns_frame)
        self.minimize_button.setObjectName(u"minimize_button")
        self.minimize_button.setMinimumSize(QSize(50, 60))
        icon3 = QIcon()
        icon3.addFile(u"../../assets/icons/minus.png", QSize(), QIcon.Normal, QIcon.On)
        self.minimize_button.setIcon(icon3)
        self.minimize_button.setFlat(True)

        self.horizontalLayout_4.addWidget(self.minimize_button)


        self.verticalLayout_10.addWidget(self.window_btns_frame)


        self.top_center_frame_layout.addWidget(self.top_center_right_frame)


        self.top_frame_layout.addWidget(self.top_center_frame)


        self.main_frame_layout.addWidget(self.top_frame, 0, 1, 1, 1)

        self.center_frame = QFrame(self.main_frame)
        self.center_frame.setObjectName(u"center_frame")
        self.center_frame.setFrameShape(QFrame.NoFrame)
        self.center_frame.setFrameShadow(QFrame.Raised)
        self.center_frame_layout = QHBoxLayout(self.center_frame)
        self.center_frame_layout.setSpacing(0)
        self.center_frame_layout.setObjectName(u"center_frame_layout")
        self.center_frame_layout.setSizeConstraint(QLayout.SetNoConstraint)
        self.center_frame_layout.setContentsMargins(0, 0, 2, 0)
        self.page_frame = QFrame(self.center_frame)
        self.page_frame.setObjectName(u"page_frame")
        self.page_frame.setFrameShape(QFrame.NoFrame)
        self.page_frame.setFrameShadow(QFrame.Raised)
        self.page_frame_layout = QVBoxLayout(self.page_frame)
        self.page_frame_layout.setSpacing(0)
        self.page_frame_layout.setObjectName(u"page_frame_layout")
        self.page_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.content_footer_splitter = QSplitter(self.page_frame)
        self.content_footer_splitter.setObjectName(u"content_footer_splitter")
        self.content_footer_splitter.setOrientation(Qt.Vertical)
        self.content_footer_splitter.setChildrenCollapsible(False)
        self.content_frame = QFrame(self.content_footer_splitter)
        self.content_frame.setObjectName(u"content_frame")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.content_frame.sizePolicy().hasHeightForWidth())
        self.content_frame.setSizePolicy(sizePolicy4)
        self.content_frame.setMinimumSize(QSize(0, 300))
        self.content_frame.setFrameShape(QFrame.NoFrame)
        self.content_frame.setFrameShadow(QFrame.Raised)
        self.content_frame_layout = QVBoxLayout(self.content_frame)
        self.content_frame_layout.setSpacing(0)
        self.content_frame_layout.setObjectName(u"content_frame_layout")
        self.content_frame_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.content_frame_layout.setContentsMargins(2, 0, 0, 5)
        self.page_stacked_widget = QStackedWidget(self.content_frame)
        self.page_stacked_widget.setObjectName(u"page_stacked_widget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page_layout = QVBoxLayout(self.page)
        self.page_layout.setObjectName(u"page_layout")
        self.page_layout.setContentsMargins(2, 0, 0, 0)
        self.listView_2 = QListView(self.page)
        self.listView_2.setObjectName(u"listView_2")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.listView_2.sizePolicy().hasHeightForWidth())
        self.listView_2.setSizePolicy(sizePolicy5)
        self.listView_2.setMinimumSize(QSize(0, 400))
        self.listView_2.setFrameShape(QFrame.NoFrame)
        self.listView_2.setFrameShadow(QFrame.Plain)
        self.listView_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.listView_2.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.page_layout.addWidget(self.listView_2)

        self.page_stacked_widget.addWidget(self.page)

        self.content_frame_layout.addWidget(self.page_stacked_widget)

        self.content_footer_splitter.addWidget(self.content_frame)
        self.page_footer = QFrame(self.content_footer_splitter)
        self.page_footer.setObjectName(u"page_footer")
        sizePolicy6 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.page_footer.sizePolicy().hasHeightForWidth())
        self.page_footer.setSizePolicy(sizePolicy6)
        self.page_footer.setMinimumSize(QSize(0, 150))
        self.page_footer.setMaximumSize(QSize(16777215, 500))
        self.page_footer.setFrameShape(QFrame.NoFrame)
        self.page_footer.setFrameShadow(QFrame.Raised)
        self.page_footer_layout = QVBoxLayout(self.page_footer)
        self.page_footer_layout.setSpacing(0)
        self.page_footer_layout.setObjectName(u"page_footer_layout")
        self.page_footer_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.page_footer_layout.setContentsMargins(0, 0, 0, 1)
        self.console = QTextBrowser(self.page_footer)
        self.console.setObjectName(u"console")
        sizePolicy7 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.MinimumExpanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.console.sizePolicy().hasHeightForWidth())
        self.console.setSizePolicy(sizePolicy7)
        self.console.setBaseSize(QSize(832, 200))
        self.console.setStyleSheet(u"")
        self.console.setFrameShape(QFrame.NoFrame)
        self.console.setFrameShadow(QFrame.Raised)
        self.console.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.console.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.console.setAutoFormatting(QTextEdit.AutoAll)
        self.console.setTabChangesFocus(True)
        self.console.setReadOnly(True)
        self.console.setHtml(u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:7.875pt;\"><br /></p></body></html>")
        self.console.setOpenExternalLinks(True)

        self.page_footer_layout.addWidget(self.console)

        self.content_footer_splitter.addWidget(self.page_footer)

        self.page_frame_layout.addWidget(self.content_footer_splitter)


        self.center_frame_layout.addWidget(self.page_frame)

        self.right_menu_frame = QFrame(self.center_frame)
        self.right_menu_frame.setObjectName(u"right_menu_frame")
        sizePolicy8 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.right_menu_frame.sizePolicy().hasHeightForWidth())
        self.right_menu_frame.setSizePolicy(sizePolicy8)
        self.right_menu_frame.setMinimumSize(QSize(0, 0))
        self.right_menu_frame.setMaximumSize(QSize(0, 16777215))
        self.right_menu_frame.setBaseSize(QSize(0, 0))
        self.right_menu_frame.setFrameShape(QFrame.NoFrame)
        self.right_menu_frame.setFrameShadow(QFrame.Raised)
        self.right_menu_frame_layout = QVBoxLayout(self.right_menu_frame)
        self.right_menu_frame_layout.setObjectName(u"right_menu_frame_layout")
        self.right_menu_frame_layout.setContentsMargins(0, 0, 4, 5)
        self.right_menu_scroll_area = QScrollArea(self.right_menu_frame)
        self.right_menu_scroll_area.setObjectName(u"right_menu_scroll_area")
        sizePolicy9 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.right_menu_scroll_area.sizePolicy().hasHeightForWidth())
        self.right_menu_scroll_area.setSizePolicy(sizePolicy9)
        self.right_menu_scroll_area.setMinimumSize(QSize(0, 0))
        self.right_menu_scroll_area.setFrameShape(QFrame.NoFrame)
        self.right_menu_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.right_menu_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.right_menu_scroll_area.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.right_menu_scroll_area.setWidgetResizable(True)
        self.right_menu_scroll_area_widgets = QWidget()
        self.right_menu_scroll_area_widgets.setObjectName(u"right_menu_scroll_area_widgets")
        self.right_menu_scroll_area_widgets.setGeometry(QRect(0, 0, 93, 751))
        self.right_menu_scroll_area_widgets.setMinimumSize(QSize(0, 0))
        self.right_menu_scroll_area_widgets_layout = QVBoxLayout(self.right_menu_scroll_area_widgets)
        self.right_menu_scroll_area_widgets_layout.setSpacing(2)
        self.right_menu_scroll_area_widgets_layout.setObjectName(u"right_menu_scroll_area_widgets_layout")
        self.right_menu_scroll_area_widgets_layout.setContentsMargins(0, 2, 0, 0)
        self.right_menu_content_frame = QFrame(self.right_menu_scroll_area_widgets)
        self.right_menu_content_frame.setObjectName(u"right_menu_content_frame")
        sizePolicy10 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(self.right_menu_content_frame.sizePolicy().hasHeightForWidth())
        self.right_menu_content_frame.setSizePolicy(sizePolicy10)
        self.right_menu_content_frame.setFrameShadow(QFrame.Raised)
        self.right_menu_content_frame_layout = QVBoxLayout(self.right_menu_content_frame)
        self.right_menu_content_frame_layout.setSpacing(0)
        self.right_menu_content_frame_layout.setObjectName(u"right_menu_content_frame_layout")
        self.right_menu_content_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.right_menu_top_content_sw = QStackedWidget(self.right_menu_content_frame)
        self.right_menu_top_content_sw.setObjectName(u"right_menu_top_content_sw")
        sizePolicy10.setHeightForWidth(self.right_menu_top_content_sw.sizePolicy().hasHeightForWidth())
        self.right_menu_top_content_sw.setSizePolicy(sizePolicy10)
        self.right_menu_top_content_sw.setMinimumSize(QSize(0, 100))
        self.dummy_page_t = QWidget()
        self.dummy_page_t.setObjectName(u"dummy_page_t")
        sizePolicy10.setHeightForWidth(self.dummy_page_t.sizePolicy().hasHeightForWidth())
        self.dummy_page_t.setSizePolicy(sizePolicy10)
        self.dummy_layout2 = QVBoxLayout(self.dummy_page_t)
        self.dummy_layout2.setObjectName(u"dummy_layout2")
        self.pushButton_6 = QPushButton(self.dummy_page_t)
        self.pushButton_6.setObjectName(u"pushButton_6")

        self.dummy_layout2.addWidget(self.pushButton_6)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.dummy_layout2.addItem(self.verticalSpacer_2)

        self.right_menu_top_content_sw.addWidget(self.dummy_page_t)

        self.right_menu_content_frame_layout.addWidget(self.right_menu_top_content_sw)

        self.right_menu_bottom_content_sw = QStackedWidget(self.right_menu_content_frame)
        self.right_menu_bottom_content_sw.setObjectName(u"right_menu_bottom_content_sw")
        sizePolicy10.setHeightForWidth(self.right_menu_bottom_content_sw.sizePolicy().hasHeightForWidth())
        self.right_menu_bottom_content_sw.setSizePolicy(sizePolicy10)
        self.right_menu_bottom_content_sw.setMinimumSize(QSize(0, 100))
        self.dummy_page_b = QWidget()
        self.dummy_page_b.setObjectName(u"dummy_page_b")
        sizePolicy10.setHeightForWidth(self.dummy_page_b.sizePolicy().hasHeightForWidth())
        self.dummy_page_b.setSizePolicy(sizePolicy10)
        self.dummy_page_b.setStyleSheet(u"")
        self.dummy_layout = QVBoxLayout(self.dummy_page_b)
        self.dummy_layout.setObjectName(u"dummy_layout")
        self.pushButton = QPushButton(self.dummy_page_b)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy11 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy11.setHorizontalStretch(0)
        sizePolicy11.setVerticalStretch(0)
        sizePolicy11.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy11)
        self.pushButton.setMinimumSize(QSize(0, 50))

        self.dummy_layout.addWidget(self.pushButton)

        self.verticalSpacer = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.dummy_layout.addItem(self.verticalSpacer)

        self.right_menu_bottom_content_sw.addWidget(self.dummy_page_b)

        self.right_menu_content_frame_layout.addWidget(self.right_menu_bottom_content_sw)


        self.right_menu_scroll_area_widgets_layout.addWidget(self.right_menu_content_frame)

        self.right_menu_scroll_area.setWidget(self.right_menu_scroll_area_widgets)

        self.right_menu_frame_layout.addWidget(self.right_menu_scroll_area)


        self.center_frame_layout.addWidget(self.right_menu_frame)

        self.center_frame_layout.setStretch(1, 1)

        self.main_frame_layout.addWidget(self.center_frame, 1, 1, 1, 1)

        self.left_menu_frame = QFrame(self.main_frame)
        self.left_menu_frame.setObjectName(u"left_menu_frame")
        self.left_menu_frame.setMinimumSize(QSize(75, 0))
        self.left_menu_frame.setMaximumSize(QSize(75, 16777215))
        self.left_menu_frame.setStyleSheet(u"")
        self.left_menu_frame.setFrameShape(QFrame.NoFrame)
        self.left_menu_frame.setFrameShadow(QFrame.Raised)
        self.left_menu_frame_layout = QVBoxLayout(self.left_menu_frame)
        self.left_menu_frame_layout.setSpacing(0)
        self.left_menu_frame_layout.setObjectName(u"left_menu_frame_layout")
        self.left_menu_frame_layout.setContentsMargins(3, 0, 0, 0)
        self.left_menu_top_subframe = QFrame(self.left_menu_frame)
        self.left_menu_top_subframe.setObjectName(u"left_menu_top_subframe")
        self.left_menu_top_subframe.setFrameShape(QFrame.NoFrame)
        self.left_menu_top_subframe.setFrameShadow(QFrame.Raised)
        self.left_menu_top_subframe_layout = QVBoxLayout(self.left_menu_top_subframe)
        self.left_menu_top_subframe_layout.setSpacing(15)
        self.left_menu_top_subframe_layout.setObjectName(u"left_menu_top_subframe_layout")
        self.left_menu_top_subframe_layout.setContentsMargins(3, 5, 3, 0)
        self.title_label = QLabel(self.left_menu_top_subframe)
        self.title_label.setObjectName(u"title_label")
        self.title_label.setMinimumSize(QSize(0, 30))
        font1 = QFont()
        font1.setBold(True)
        font1.setItalic(False)
        self.title_label.setFont(font1)
        self.title_label.setStyleSheet(u"font: bold")
        self.title_label.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)
        self.title_label.setMargin(0)
        self.title_label.setIndent(5)

        self.left_menu_top_subframe_layout.addWidget(self.title_label)

        self.toggle_left_menu_button = QPushButton(self.left_menu_top_subframe)
        self.toggle_left_menu_button.setObjectName(u"toggle_left_menu_button")
        sizePolicy11.setHeightForWidth(self.toggle_left_menu_button.sizePolicy().hasHeightForWidth())
        self.toggle_left_menu_button.setSizePolicy(sizePolicy11)
        self.toggle_left_menu_button.setMinimumSize(QSize(64, 45))
        self.toggle_left_menu_button.setMaximumSize(QSize(64, 45))
        icon4 = QIcon()
        icon4.addFile(u"../../../../../../Users/peter/.designer/assets/icons/menu_stripes.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toggle_left_menu_button.setIcon(icon4)
        self.toggle_left_menu_button.setIconSize(QSize(32, 32))
        self.toggle_left_menu_button.setCheckable(False)
        self.toggle_left_menu_button.setFlat(True)

        self.left_menu_top_subframe_layout.addWidget(self.toggle_left_menu_button)


        self.left_menu_frame_layout.addWidget(self.left_menu_top_subframe)

        self.left_menu_middle_subframe = QFrame(self.left_menu_frame)
        self.left_menu_middle_subframe.setObjectName(u"left_menu_middle_subframe")
        self.left_menu_middle_subframe.setMinimumSize(QSize(0, 0))
        self.left_menu_middle_subframe.setFrameShape(QFrame.NoFrame)
        self.left_menu_middle_subframe.setFrameShadow(QFrame.Raised)
        self.left_menu_middle_subframe_layout = QVBoxLayout(self.left_menu_middle_subframe)
        self.left_menu_middle_subframe_layout.setObjectName(u"left_menu_middle_subframe_layout")
        self.left_menu_middle_subframe_layout.setContentsMargins(3, -1, 3, 0)

        self.left_menu_frame_layout.addWidget(self.left_menu_middle_subframe)

        self.left_menu_bottom_subframe = QFrame(self.left_menu_frame)
        self.left_menu_bottom_subframe.setObjectName(u"left_menu_bottom_subframe")
        self.left_menu_bottom_subframe.setFrameShape(QFrame.NoFrame)
        self.left_menu_bottom_subframe.setFrameShadow(QFrame.Raised)
        self.left_menu_bottom_subframe_layout = QVBoxLayout(self.left_menu_bottom_subframe)
        self.left_menu_bottom_subframe_layout.setSpacing(5)
        self.left_menu_bottom_subframe_layout.setObjectName(u"left_menu_bottom_subframe_layout")
        self.left_menu_bottom_subframe_layout.setContentsMargins(3, 0, 3, 10)
        self.left_menu_bottom_vspacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.left_menu_bottom_subframe_layout.addItem(self.left_menu_bottom_vspacer)

        self.settings_button = QPushButton(self.left_menu_bottom_subframe)
        self.settings_button.setObjectName(u"settings_button")
        self.settings_button.setMinimumSize(QSize(64, 50))
        self.settings_button.setMaximumSize(QSize(64, 16777215))
        icon5 = QIcon()
        icon5.addFile(u"../../../../../../Users/peter/.designer/assets/icons/settings.png", QSize(), QIcon.Normal, QIcon.On)
        self.settings_button.setIcon(icon5)
        self.settings_button.setIconSize(QSize(32, 32))
        self.settings_button.setCheckable(True)
        self.settings_button.setChecked(False)
        self.settings_button.setFlat(True)

        self.left_menu_bottom_subframe_layout.addWidget(self.settings_button)


        self.left_menu_frame_layout.addWidget(self.left_menu_bottom_subframe)


        self.main_frame_layout.addWidget(self.left_menu_frame, 0, 0, 2, 1)


        self.central_widget_layout.addWidget(self.main_frame)

        MainWindow.setCentralWidget(self.central_widget)

        self.retranslateUi(MainWindow)

        self.page_stacked_widget.setCurrentIndex(0)
        self.toggle_left_menu_button.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Conan App Launcher", None))
        self.page_title.setText(QCoreApplication.translate("MainWindow", u"Page Title", None))
        self.close_button.setText("")
        self.restore_max_button.setText("")
        self.minimize_button.setText("")
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.title_label.setText(QCoreApplication.translate("MainWindow", u"App Title", None))
#if QT_CONFIG(tooltip)
        self.toggle_left_menu_button.setToolTip(QCoreApplication.translate("MainWindow", u"Expand/Collapse Menu", None))
#endif // QT_CONFIG(tooltip)
        self.toggle_left_menu_button.setText("")
#if QT_CONFIG(tooltip)
        self.settings_button.setToolTip(QCoreApplication.translate("MainWindow", u"Show Settings Menu", None))
#endif // QT_CONFIG(tooltip)
        self.settings_button.setText("")
    # retranslateUi

