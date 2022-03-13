# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Repos\app_grid_conan\src\conan_app_launcher\ui\fluent_window_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def __init__(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(851, 795)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(400, 400))
        MainWindow.setAcceptDrops(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(1, 0, 2, 1)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_frame = QtWidgets.QFrame(self.centralwidget)
        self.main_frame.setStyleSheet("")
        self.main_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.main_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_frame.setLineWidth(0)
        self.main_frame.setObjectName("main_frame")
        self.gridLayout = QtWidgets.QGridLayout(self.main_frame)
        self.gridLayout.setContentsMargins(3, 2, 2, 2)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.top_frame = QtWidgets.QFrame(self.main_frame)
        self.top_frame.setMinimumSize(QtCore.QSize(0, 50))
        self.top_frame.setMaximumSize(QtCore.QSize(16777215, 65))
        self.top_frame.setStyleSheet("")
        self.top_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.top_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.top_frame.setLineWidth(0)
        self.top_frame.setObjectName("top_frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.top_frame)
        self.horizontalLayout_3.setContentsMargins(1, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.top_center_frame = QtWidgets.QFrame(self.top_frame)
        self.top_center_frame.setMaximumSize(QtCore.QSize(16777215, 70))
        self.top_center_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.top_center_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.top_center_frame.setObjectName("top_center_frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.top_center_frame)
        self.horizontalLayout_2.setContentsMargins(5, 5, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.page_title = QtWidgets.QLabel(self.top_center_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page_title.sizePolicy().hasHeightForWidth())
        self.page_title.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.page_title.setFont(font)
        self.page_title.setObjectName("page_title")
        self.horizontalLayout_2.addWidget(self.page_title)
        self.top_center_right_frame = QtWidgets.QFrame(self.top_center_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.top_center_right_frame.sizePolicy().hasHeightForWidth())
        self.top_center_right_frame.setSizePolicy(sizePolicy)
        self.top_center_right_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.top_center_right_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.top_center_right_frame.setObjectName("top_center_right_frame")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.top_center_right_frame)
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.window_btns_frame = QtWidgets.QFrame(self.top_center_right_frame)
        self.window_btns_frame.setMinimumSize(QtCore.QSize(0, 35))
        self.window_btns_frame.setMaximumSize(QtCore.QSize(135, 45))
        self.window_btns_frame.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.window_btns_frame.setStyleSheet("")
        self.window_btns_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.window_btns_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.window_btns_frame.setObjectName("window_btns_frame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.window_btns_frame)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.close_button = QtWidgets.QPushButton(self.window_btns_frame)
        self.close_button.setMinimumSize(QtCore.QSize(45, 30))
        self.close_button.setStyleSheet("")
        self.close_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("c:\\Repos\\app_grid_conan\\src\\conan_app_launcher\\ui\\../assets/icons/close.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.close_button.setIcon(icon1)
        self.close_button.setFlat(True)
        self.close_button.setObjectName("close_button")
        self.horizontalLayout_4.addWidget(self.close_button)
        self.restore_max_button = QtWidgets.QPushButton(self.window_btns_frame)
        self.restore_max_button.setMinimumSize(QtCore.QSize(45, 30))
        self.restore_max_button.setStyleSheet("")
        self.restore_max_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("c:\\Repos\\app_grid_conan\\src\\conan_app_launcher\\ui\\../assets/icons/restore.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.restore_max_button.setIcon(icon2)
        self.restore_max_button.setObjectName("restore_max_button")
        self.horizontalLayout_4.addWidget(self.restore_max_button)
        self.minimize_button = QtWidgets.QPushButton(self.window_btns_frame)
        self.minimize_button.setMinimumSize(QtCore.QSize(45, 30))
        self.minimize_button.setStyleSheet("")
        self.minimize_button.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("c:\\Repos\\app_grid_conan\\src\\conan_app_launcher\\ui\\../assets/icons/minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.minimize_button.setIcon(icon3)
        self.minimize_button.setObjectName("minimize_button")
        self.horizontalLayout_4.addWidget(self.minimize_button)
        self.verticalLayout_10.addWidget(self.window_btns_frame)
        self.page_info_label = QtWidgets.QLabel(self.top_center_right_frame)
        self.page_info_label.setObjectName("page_info_label")
        self.verticalLayout_10.addWidget(self.page_info_label)
        self.horizontalLayout_2.addWidget(self.top_center_right_frame)
        self.horizontalLayout_3.addWidget(self.top_center_frame)
        self.gridLayout.addWidget(self.top_frame, 0, 1, 1, 1)
        self.center_frame = QtWidgets.QFrame(self.main_frame)
        self.center_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.center_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.center_frame.setObjectName("center_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.center_frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 1)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.page_frame = QtWidgets.QFrame(self.center_frame)
        self.page_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.page_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.page_frame.setObjectName("page_frame")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.page_frame)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 1)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.content_footer_splitter = QtWidgets.QSplitter(self.page_frame)
        self.content_footer_splitter.setOrientation(QtCore.Qt.Vertical)
        self.content_footer_splitter.setChildrenCollapsible(False)
        self.content_footer_splitter.setObjectName("content_footer_splitter")
        self.content_frame = QtWidgets.QFrame(self.content_footer_splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.content_frame.sizePolicy().hasHeightForWidth())
        self.content_frame.setSizePolicy(sizePolicy)
        self.content_frame.setMinimumSize(QtCore.QSize(0, 300))
        self.content_frame.setStyleSheet("border-radius: 7px;\n"
"")
        self.content_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.content_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.content_frame.setObjectName("content_frame")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.content_frame)
        self.verticalLayout_4.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.verticalLayout_4.setContentsMargins(0, 5, 0, 5)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.page_stacked_widget = QtWidgets.QStackedWidget(self.content_frame)
        self.page_stacked_widget.setObjectName("page_stacked_widget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout_8.setContentsMargins(2, 0, 0, 0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.page_stacked_widget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.page_stacked_widget.addWidget(self.page_2)
        self.verticalLayout_4.addWidget(self.page_stacked_widget)
        self.page_footer = QtWidgets.QFrame(self.content_footer_splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page_footer.sizePolicy().hasHeightForWidth())
        self.page_footer.setSizePolicy(sizePolicy)
        self.page_footer.setMinimumSize(QtCore.QSize(0, 150))
        self.page_footer.setMaximumSize(QtCore.QSize(16777215, 500))
        self.page_footer.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-bottom-right-radius: 7px;\n"
"")
        self.page_footer.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.page_footer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.page_footer.setObjectName("page_footer")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.page_footer)
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.verticalLayout_3.setContentsMargins(0, 0, 2, 2)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.console = QtWidgets.QTextBrowser(self.page_footer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.console.sizePolicy().hasHeightForWidth())
        self.console.setSizePolicy(sizePolicy)
        self.console.setMinimumSize(QtCore.QSize(100, 0))
        self.console.setBaseSize(QtCore.QSize(832, 200))
        self.console.setStyleSheet("")
        self.console.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.console.setFrameShadow(QtWidgets.QFrame.Raised)
        self.console.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.console.setAutoFormatting(QtWidgets.QTextEdit.AutoAll)
        self.console.setReadOnly(True)
        self.console.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.875pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>")
        self.console.setTabStopWidth(200)
        self.console.setOpenExternalLinks(True)
        self.console.setObjectName("console")
        self.verticalLayout_3.addWidget(self.console)
        self.verticalLayout_6.addWidget(self.content_footer_splitter)
        self.horizontalLayout.addWidget(self.page_frame)
        self.right_menu_frame = QtWidgets.QFrame(self.center_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.right_menu_frame.sizePolicy().hasHeightForWidth())
        self.right_menu_frame.setSizePolicy(sizePolicy)
        self.right_menu_frame.setMinimumSize(QtCore.QSize(0, 0))
        self.right_menu_frame.setMaximumSize(QtCore.QSize(0, 16777215))
        self.right_menu_frame.setStyleSheet("QFrame{\n"
"background-color:  #d3d3d3;\n"
"}")
        self.right_menu_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.right_menu_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.right_menu_frame.setObjectName("right_menu_frame")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.right_menu_frame)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.right_menu_top_frame = QtWidgets.QFrame(self.right_menu_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.right_menu_top_frame.sizePolicy().hasHeightForWidth())
        self.right_menu_top_frame.setSizePolicy(sizePolicy)
        self.right_menu_top_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.right_menu_top_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.right_menu_top_frame.setObjectName("right_menu_top_frame")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.right_menu_top_frame)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.right_menu_top_title_frame = QtWidgets.QFrame(self.right_menu_top_frame)
        self.right_menu_top_title_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.right_menu_top_title_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.right_menu_top_title_frame.setObjectName("right_menu_top_title_frame")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.right_menu_top_title_frame)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.right_menu_top_back_button = QtWidgets.QPushButton(self.right_menu_top_title_frame)
        self.right_menu_top_back_button.setMinimumSize(QtCore.QSize(32, 32))
        self.right_menu_top_back_button.setMaximumSize(QtCore.QSize(32, 32))
        self.right_menu_top_back_button.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("c:\\Repos\\app_grid_conan\\src\\conan_app_launcher\\ui\\../assets/icons/back.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.right_menu_top_back_button.setIcon(icon4)
        self.right_menu_top_back_button.setFlat(True)
        self.right_menu_top_back_button.setObjectName("right_menu_top_back_button")
        self.horizontalLayout_5.addWidget(self.right_menu_top_back_button)
        self.right_menu_top_title_label = QtWidgets.QLabel(self.right_menu_top_title_frame)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.right_menu_top_title_label.setFont(font)
        self.right_menu_top_title_label.setObjectName("right_menu_top_title_label")
        self.horizontalLayout_5.addWidget(self.right_menu_top_title_label)
        self.verticalLayout_15.addWidget(self.right_menu_top_title_frame)
        self.right_menu_top_content_sw = QtWidgets.QStackedWidget(self.right_menu_top_frame)
        self.right_menu_top_content_sw.setObjectName("right_menu_top_content_sw")
        self.main_top_settings_page = QtWidgets.QWidget()
        self.main_top_settings_page.setObjectName("main_top_settings_page")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.main_top_settings_page)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.right_menu_top_content_sw.addWidget(self.main_top_settings_page)
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setObjectName("page_4")
        self.right_menu_top_content_sw.addWidget(self.page_4)
        self.verticalLayout_15.addWidget(self.right_menu_top_content_sw)
        self.verticalLayout_5.addWidget(self.right_menu_top_frame)
        self.right_menu_bottom_frame = QtWidgets.QFrame(self.right_menu_frame)
        self.right_menu_bottom_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.right_menu_bottom_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.right_menu_bottom_frame.setObjectName("right_menu_bottom_frame")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.right_menu_bottom_frame)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.right_menu_bottom_title_frame = QtWidgets.QFrame(self.right_menu_bottom_frame)
        self.right_menu_bottom_title_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.right_menu_bottom_title_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.right_menu_bottom_title_frame.setObjectName("right_menu_bottom_title_frame")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.right_menu_bottom_title_frame)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.right_menu_bottom_back_button = QtWidgets.QPushButton(self.right_menu_bottom_title_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.right_menu_bottom_back_button.sizePolicy().hasHeightForWidth())
        self.right_menu_bottom_back_button.setSizePolicy(sizePolicy)
        self.right_menu_bottom_back_button.setMinimumSize(QtCore.QSize(0, 32))
        self.right_menu_bottom_back_button.setMaximumSize(QtCore.QSize(32, 32))
        self.right_menu_bottom_back_button.setText("")
        self.right_menu_bottom_back_button.setIcon(icon4)
        self.right_menu_bottom_back_button.setFlat(True)
        self.right_menu_bottom_back_button.setObjectName("right_menu_bottom_back_button")
        self.horizontalLayout_6.addWidget(self.right_menu_bottom_back_button)
        self.right_menu_bottom_title_label = QtWidgets.QLabel(self.right_menu_bottom_title_frame)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.right_menu_bottom_title_label.setFont(font)
        self.right_menu_bottom_title_label.setObjectName("right_menu_bottom_title_label")
        self.horizontalLayout_6.addWidget(self.right_menu_bottom_title_label)
        self.verticalLayout_7.addWidget(self.right_menu_bottom_title_frame)
        self.right_menu_bottom_content_sw = QtWidgets.QStackedWidget(self.right_menu_bottom_frame)
        self.right_menu_bottom_content_sw.setMinimumSize(QtCore.QSize(0, 100))
        self.right_menu_bottom_content_sw.setObjectName("right_menu_bottom_content_sw")
        self.main_settings_page = QtWidgets.QWidget()
        self.main_settings_page.setObjectName("main_settings_page")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.main_settings_page)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_14.addItem(spacerItem)
        self.right_menu_bottom_content_sw.addWidget(self.main_settings_page)
        self.page_6 = QtWidgets.QWidget()
        self.page_6.setObjectName("page_6")
        self.right_menu_bottom_content_sw.addWidget(self.page_6)
        self.verticalLayout_7.addWidget(self.right_menu_bottom_content_sw)
        self.verticalLayout_5.addWidget(self.right_menu_bottom_frame)
        self.horizontalLayout.addWidget(self.right_menu_frame)
        self.gridLayout.addWidget(self.center_frame, 1, 1, 1, 1)
        self.left_menu_frame = QtWidgets.QFrame(self.main_frame)
        self.left_menu_frame.setMinimumSize(QtCore.QSize(70, 0))
        self.left_menu_frame.setMaximumSize(QtCore.QSize(70, 16777215))
        self.left_menu_frame.setStyleSheet("QFrame{\n"
"background-color:  #d3d3d3;\n"
"border-bottom-left-radius: 5px;\n"
"border-top-left-radius: 5px;\n"
"}")
        self.left_menu_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.left_menu_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.left_menu_frame.setObjectName("left_menu_frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.left_menu_frame)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.left_menu_top_subframe = QtWidgets.QFrame(self.left_menu_frame)
        self.left_menu_top_subframe.setStyleSheet("")
        self.left_menu_top_subframe.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.left_menu_top_subframe.setFrameShadow(QtWidgets.QFrame.Raised)
        self.left_menu_top_subframe.setObjectName("left_menu_top_subframe")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.left_menu_top_subframe)
        self.verticalLayout_12.setContentsMargins(3, 7, 3, 0)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.title_label = QtWidgets.QLabel(self.left_menu_top_subframe)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.title_label.setFont(font)
        self.title_label.setText("")
        self.title_label.setIndent(3)
        self.title_label.setObjectName("title_label")
        self.verticalLayout_12.addWidget(self.title_label)
        self.toggle_left_menu_button = QtWidgets.QPushButton(self.left_menu_top_subframe)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toggle_left_menu_button.sizePolicy().hasHeightForWidth())
        self.toggle_left_menu_button.setSizePolicy(sizePolicy)
        self.toggle_left_menu_button.setMinimumSize(QtCore.QSize(64, 45))
        self.toggle_left_menu_button.setMaximumSize(QtCore.QSize(60, 45))
        self.toggle_left_menu_button.setStyleSheet("")
        self.toggle_left_menu_button.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("c:\\Repos\\app_grid_conan\\src\\conan_app_launcher\\ui\\../assets/icons/menu_stripes.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toggle_left_menu_button.setIcon(icon5)
        self.toggle_left_menu_button.setIconSize(QtCore.QSize(32, 32))
        self.toggle_left_menu_button.setCheckable(False)
        self.toggle_left_menu_button.setDefault(False)
        self.toggle_left_menu_button.setFlat(True)
        self.toggle_left_menu_button.setObjectName("toggle_left_menu_button")
        self.verticalLayout_12.addWidget(self.toggle_left_menu_button)
        self.verticalLayout_2.addWidget(self.left_menu_top_subframe)
        self.left_menu_middle_subframe = QtWidgets.QFrame(self.left_menu_frame)
        self.left_menu_middle_subframe.setMinimumSize(QtCore.QSize(0, 0))
        self.left_menu_middle_subframe.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.left_menu_middle_subframe.setFrameShadow(QtWidgets.QFrame.Raised)
        self.left_menu_middle_subframe.setObjectName("left_menu_middle_subframe")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.left_menu_middle_subframe)
        self.verticalLayout_11.setContentsMargins(3, -1, 3, 0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.verticalLayout_2.addWidget(self.left_menu_middle_subframe)
        self.left_menu_bottom_subframe = QtWidgets.QFrame(self.left_menu_frame)
        self.left_menu_bottom_subframe.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.left_menu_bottom_subframe.setFrameShadow(QtWidgets.QFrame.Raised)
        self.left_menu_bottom_subframe.setObjectName("left_menu_bottom_subframe")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.left_menu_bottom_subframe)
        self.verticalLayout_9.setContentsMargins(3, 0, 3, 10)
        self.verticalLayout_9.setSpacing(5)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_9.addItem(spacerItem1)
        self.settings_button = QtWidgets.QPushButton(self.left_menu_bottom_subframe)
        self.settings_button.setMinimumSize(QtCore.QSize(64, 50))
        self.settings_button.setMaximumSize(QtCore.QSize(64, 16777215))
        self.settings_button.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("c:\\Repos\\app_grid_conan\\src\\conan_app_launcher\\ui\\../assets/icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.settings_button.setIcon(icon6)
        self.settings_button.setIconSize(QtCore.QSize(32, 32))
        self.settings_button.setCheckable(True)
        self.settings_button.setChecked(False)
        self.settings_button.setObjectName("settings_button")
        self.verticalLayout_9.addWidget(self.settings_button)
        self.verticalLayout_2.addWidget(self.left_menu_bottom_subframe)
        self.gridLayout.addWidget(self.left_menu_frame, 0, 0, 2, 1)
        self.verticalLayout.addWidget(self.main_frame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menu_about_action = QtWidgets.QAction(MainWindow)
        self.menu_about_action.setObjectName("menu_about_action")
        self.menu_open_config_file = QtWidgets.QAction(MainWindow)
        self.menu_open_config_file.setObjectName("menu_open_config_file")
        self.menu_toggle_display_versions = QtWidgets.QAction(MainWindow)
        self.menu_toggle_display_versions.setCheckable(True)
        self.menu_toggle_display_versions.setChecked(True)
        self.menu_toggle_display_versions.setObjectName("menu_toggle_display_versions")
        self.menu_toggle_display_channels = QtWidgets.QAction(MainWindow)
        self.menu_toggle_display_channels.setCheckable(True)
        self.menu_toggle_display_channels.setChecked(True)
        self.menu_toggle_display_channels.setObjectName("menu_toggle_display_channels")
        self.menu_settings = QtWidgets.QAction(MainWindow)
        self.menu_settings.setObjectName("menu_settings")
        self.menu_auto_install = QtWidgets.QAction(MainWindow)
        self.menu_auto_install.setObjectName("menu_auto_install")
        self.menu_cleanup_cache = QtWidgets.QAction(MainWindow)
        self.menu_cleanup_cache.setObjectName("menu_cleanup_cache")
        self.menu_toggle_display_users = QtWidgets.QAction(MainWindow)
        self.menu_toggle_display_users.setCheckable(True)
        self.menu_toggle_display_users.setChecked(False)
        self.menu_toggle_display_users.setObjectName("menu_toggle_display_users")
        self.menu_remove_locks = QtWidgets.QAction(MainWindow)
        self.menu_remove_locks.setObjectName("menu_remove_locks")
        self.menu_search_in_remotes = QtWidgets.QAction(MainWindow)
        self.menu_search_in_remotes.setObjectName("menu_search_in_remotes")
        self.actionConan_Settings = QtWidgets.QAction(MainWindow)
        self.actionConan_Settings.setObjectName("actionConan_Settings")
        self.menu_enable_dark_mode = QtWidgets.QAction(MainWindow)
        self.menu_enable_dark_mode.setCheckable(True)
        self.menu_enable_dark_mode.setObjectName("menu_enable_dark_mode")
        self.menu_increase_font_size = QtWidgets.QAction(MainWindow)
        self.menu_increase_font_size.setObjectName("menu_increase_font_size")
        self.menu_decrease_font_size = QtWidgets.QAction(MainWindow)
        self.menu_decrease_font_size.setObjectName("menu_decrease_font_size")

        self.retranslateUi(MainWindow)
        self.page_stacked_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Conan App Launcher"))
        self.page_title.setText(_translate("MainWindow", "Page Title"))
        self.page_info_label.setText(_translate("MainWindow", "Page Info"))
        self.right_menu_top_title_label.setText(_translate("MainWindow", "Page Settings"))
        self.right_menu_bottom_title_label.setText(_translate("MainWindow", "Settings"))
        self.menu_about_action.setText(_translate("MainWindow", "About"))
        self.menu_open_config_file.setText(_translate("MainWindow", "Open Config File"))
        self.menu_toggle_display_versions.setText(_translate("MainWindow", "Display versions for AppLinks"))
        self.menu_toggle_display_channels.setText(_translate("MainWindow", "Display channels for AppLinks"))
        self.menu_settings.setText(_translate("MainWindow", "Settings"))
        self.menu_auto_install.setText(_translate("MainWindow", "Auto Install"))
        self.menu_cleanup_cache.setText(_translate("MainWindow", "Clean Local Cache"))
        self.menu_toggle_display_users.setText(_translate("MainWindow", "Display users for AppLinks"))
        self.menu_remove_locks.setText(_translate("MainWindow", "Remove Locks"))
        self.menu_search_in_remotes.setText(_translate("MainWindow", "Search in Remotes"))
        self.actionConan_Settings.setText(_translate("MainWindow", "Conan Settings"))
        self.menu_enable_dark_mode.setText(_translate("MainWindow", "Enable Dark Mode"))
        self.menu_increase_font_size.setText(_translate("MainWindow", "Increase Font Size"))
        self.menu_decrease_font_size.setText(_translate("MainWindow", "Decrease Font Size"))
