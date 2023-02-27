# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'conan_conf.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QListView, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTabWidget, QTextBrowser, QTreeView,
    QVBoxLayout, QWidget)

from conan_app_launcher.ui.widgets import AnimatedToggle

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(617, 464)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(1, 2, 2, 2)
        self.config_tab_widget = QTabWidget(Form)
        self.config_tab_widget.setObjectName(u"config_tab_widget")
        self.config_tab_widget.setStyleSheet(u"")
        self.info_widget = QWidget()
        self.info_widget.setObjectName(u"info_widget")
        self.info_widget.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.info_widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.info_scroll_area = QScrollArea(self.info_widget)
        self.info_scroll_area.setObjectName(u"info_scroll_area")
        self.info_scroll_area.setFrameShape(QFrame.NoFrame)
        self.info_scroll_area.setWidgetResizable(True)
        self.info_contents = QWidget()
        self.info_contents.setObjectName(u"info_contents")
        self.info_contents.setGeometry(QRect(0, 0, 608, 431))
        self.verticalLayout_7 = QVBoxLayout(self.info_contents)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.versions_box = QGroupBox(self.info_contents)
        self.versions_box.setObjectName(u"versions_box")
        self.gridLayout = QGridLayout(self.versions_box)
        self.gridLayout.setObjectName(u"gridLayout")
        self.conan_cur_version_label = QLabel(self.versions_box)
        self.conan_cur_version_label.setObjectName(u"conan_cur_version_label")

        self.gridLayout.addWidget(self.conan_cur_version_label, 0, 0, 1, 1)

        self.conan_cur_version_value_label = QLabel(self.versions_box)
        self.conan_cur_version_value_label.setObjectName(u"conan_cur_version_value_label")
        self.conan_cur_version_value_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.conan_cur_version_value_label, 0, 1, 1, 1)

        self.python_cur_version_label = QLabel(self.versions_box)
        self.python_cur_version_label.setObjectName(u"python_cur_version_label")

        self.gridLayout.addWidget(self.python_cur_version_label, 1, 0, 1, 1)

        self.python_cur_version_value_label = QLabel(self.versions_box)
        self.python_cur_version_value_label.setObjectName(u"python_cur_version_value_label")

        self.gridLayout.addWidget(self.python_cur_version_value_label, 1, 1, 1, 1)

        self.conan_sys_version_label = QLabel(self.versions_box)
        self.conan_sys_version_label.setObjectName(u"conan_sys_version_label")

        self.gridLayout.addWidget(self.conan_sys_version_label, 2, 0, 1, 1)

        self.conan_sys_version_value_label = QLabel(self.versions_box)
        self.conan_sys_version_value_label.setObjectName(u"conan_sys_version_value_label")
        self.conan_sys_version_value_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.conan_sys_version_value_label, 2, 1, 1, 1)

        self.python_sys_version_label = QLabel(self.versions_box)
        self.python_sys_version_label.setObjectName(u"python_sys_version_label")

        self.gridLayout.addWidget(self.python_sys_version_label, 3, 0, 1, 1)

        self.python_sys_version_value_label = QLabel(self.versions_box)
        self.python_sys_version_value_label.setObjectName(u"python_sys_version_value_label")

        self.gridLayout.addWidget(self.python_sys_version_value_label, 3, 1, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)

        self.verticalLayout_7.addWidget(self.versions_box)

        self.paths_box = QGroupBox(self.info_contents)
        self.paths_box.setObjectName(u"paths_box")
        self.gridLayout_2 = QGridLayout(self.paths_box)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.conan_usr_home_label = QLabel(self.paths_box)
        self.conan_usr_home_label.setObjectName(u"conan_usr_home_label")

        self.gridLayout_2.addWidget(self.conan_usr_home_label, 0, 0, 1, 1)

        self.conan_usr_home_value_label = QLabel(self.paths_box)
        self.conan_usr_home_value_label.setObjectName(u"conan_usr_home_value_label")
        self.conan_usr_home_value_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.gridLayout_2.addWidget(self.conan_usr_home_value_label, 0, 1, 1, 1)

        self.conan_storage_path_label = QLabel(self.paths_box)
        self.conan_storage_path_label.setObjectName(u"conan_storage_path_label")

        self.gridLayout_2.addWidget(self.conan_storage_path_label, 1, 0, 1, 1)

        self.conan_storage_path_value_label = QLabel(self.paths_box)
        self.conan_storage_path_value_label.setObjectName(u"conan_storage_path_value_label")
        self.conan_storage_path_value_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.gridLayout_2.addWidget(self.conan_storage_path_value_label, 1, 1, 1, 1)

        self.conan_usr_cache_label = QLabel(self.paths_box)
        self.conan_usr_cache_label.setObjectName(u"conan_usr_cache_label")

        self.gridLayout_2.addWidget(self.conan_usr_cache_label, 2, 0, 1, 1)

        self.conan_usr_cache_value_label = QLabel(self.paths_box)
        self.conan_usr_cache_value_label.setObjectName(u"conan_usr_cache_value_label")
        self.conan_usr_cache_value_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.gridLayout_2.addWidget(self.conan_usr_cache_value_label, 2, 1, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 2)

        self.verticalLayout_7.addWidget(self.paths_box)

        self.features_box = QGroupBox(self.info_contents)
        self.features_box.setObjectName(u"features_box")
        self.gridLayout_3 = QGridLayout(self.features_box)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.revision_enabled_label = QLabel(self.features_box)
        self.revision_enabled_label.setObjectName(u"revision_enabled_label")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.revision_enabled_label.sizePolicy().hasHeightForWidth())
        self.revision_enabled_label.setSizePolicy(sizePolicy)
        self.revision_enabled_label.setMaximumSize(QSize(16777215, 16777215))
        self.revision_enabled_label.setMidLineWidth(0)

        self.gridLayout_3.addWidget(self.revision_enabled_label, 0, 0, 1, 1)

        self.revision_enabled_checkbox = AnimatedToggle(self.features_box)
        self.revision_enabled_checkbox.setObjectName(u"revision_enabled_checkbox")
        self.revision_enabled_checkbox.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.revision_enabled_checkbox.sizePolicy().hasHeightForWidth())
        self.revision_enabled_checkbox.setSizePolicy(sizePolicy1)
        self.revision_enabled_checkbox.setCheckable(True)

        self.gridLayout_3.addWidget(self.revision_enabled_checkbox, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 1)
        self.gridLayout_3.setColumnStretch(2, 2)

        self.verticalLayout_7.addWidget(self.features_box)

        self.verticalSpacer = QSpacerItem(20, 800, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer)

        self.info_scroll_area.setWidget(self.info_contents)

        self.verticalLayout_2.addWidget(self.info_scroll_area)

        self.config_tab_widget.addTab(self.info_widget, "")
        self.remotes = QWidget()
        self.remotes.setObjectName(u"remotes")
        self.verticalLayout_4 = QVBoxLayout(self.remotes)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.remotes_frame = QFrame(self.remotes)
        self.remotes_frame.setObjectName(u"remotes_frame")
        self.remotes_frame.setFrameShape(QFrame.StyledPanel)
        self.remotes_frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_4 = QGridLayout(self.remotes_frame)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, -1, 0, -1)
        self.remotes_buttons_frame = QFrame(self.remotes_frame)
        self.remotes_buttons_frame.setObjectName(u"remotes_buttons_frame")
        self.remotes_buttons_frame.setStyleSheet(u"QPushButton {Text-align:left}")
        self.remotes_buttons_frame.setFrameShape(QFrame.StyledPanel)
        self.remotes_buttons_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.remotes_buttons_frame)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, -1, 0, -1)
        self.remote_refresh_button = QPushButton(self.remotes_buttons_frame)
        self.remote_refresh_button.setObjectName(u"remote_refresh_button")

        self.verticalLayout_8.addWidget(self.remote_refresh_button)

        self.remote_move_up_button = QPushButton(self.remotes_buttons_frame)
        self.remote_move_up_button.setObjectName(u"remote_move_up_button")

        self.verticalLayout_8.addWidget(self.remote_move_up_button)

        self.remote_move_down_button = QPushButton(self.remotes_buttons_frame)
        self.remote_move_down_button.setObjectName(u"remote_move_down_button")

        self.verticalLayout_8.addWidget(self.remote_move_down_button)

        self.remote_login = QPushButton(self.remotes_buttons_frame)
        self.remote_login.setObjectName(u"remote_login")

        self.verticalLayout_8.addWidget(self.remote_login)

        self.remote_toggle_disabled = QPushButton(self.remotes_buttons_frame)
        self.remote_toggle_disabled.setObjectName(u"remote_toggle_disabled")

        self.verticalLayout_8.addWidget(self.remote_toggle_disabled)

        self.remote_add = QPushButton(self.remotes_buttons_frame)
        self.remote_add.setObjectName(u"remote_add")

        self.verticalLayout_8.addWidget(self.remote_add)

        self.remote_remove = QPushButton(self.remotes_buttons_frame)
        self.remote_remove.setObjectName(u"remote_remove")

        self.verticalLayout_8.addWidget(self.remote_remove)

        self.remotes_btns_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_8.addItem(self.remotes_btns_spacer)


        self.gridLayout_4.addWidget(self.remotes_buttons_frame, 0, 1, 1, 1)

        self.remotes_tree_view = QTreeView(self.remotes_frame)
        self.remotes_tree_view.setObjectName(u"remotes_tree_view")
        self.remotes_tree_view.setFrameShape(QFrame.NoFrame)
        self.remotes_tree_view.setDragEnabled(True)
        self.remotes_tree_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.remotes_tree_view.setSortingEnabled(False)

        self.gridLayout_4.addWidget(self.remotes_tree_view, 0, 0, 1, 1)


        self.verticalLayout_4.addWidget(self.remotes_frame)

        self.config_tab_widget.addTab(self.remotes, "")
        self.profiles = QWidget()
        self.profiles.setObjectName(u"profiles")
        self.verticalLayout_5 = QVBoxLayout(self.profiles)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.profiles_layout = QGridLayout()
        self.profiles_layout.setObjectName(u"profiles_layout")
        self.profiles_list_view = QListView(self.profiles)
        self.profiles_list_view.setObjectName(u"profiles_list_view")
        self.profiles_list_view.setFrameShape(QFrame.NoFrame)
        self.profiles_list_view.setMovement(QListView.Free)
        self.profiles_list_view.setUniformItemSizes(True)

        self.profiles_layout.addWidget(self.profiles_list_view, 0, 0, 1, 1)

        self.profiles_buttons_frame = QFrame(self.profiles)
        self.profiles_buttons_frame.setObjectName(u"profiles_buttons_frame")
        self.profiles_buttons_frame.setStyleSheet(u"QPushButton {Text-align:left}")
        self.profiles_buttons_frame.setFrameShape(QFrame.StyledPanel)
        self.profiles_buttons_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.profiles_buttons_frame)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, -1, 0, -1)
        self.profile_refresh_button = QPushButton(self.profiles_buttons_frame)
        self.profile_refresh_button.setObjectName(u"profile_refresh_button")

        self.verticalLayout_9.addWidget(self.profile_refresh_button)

        self.profile_add_button = QPushButton(self.profiles_buttons_frame)
        self.profile_add_button.setObjectName(u"profile_add_button")

        self.verticalLayout_9.addWidget(self.profile_add_button)

        self.profile_remove_button = QPushButton(self.profiles_buttons_frame)
        self.profile_remove_button.setObjectName(u"profile_remove_button")

        self.verticalLayout_9.addWidget(self.profile_remove_button)

        self.profile_save_button = QPushButton(self.profiles_buttons_frame)
        self.profile_save_button.setObjectName(u"profile_save_button")

        self.verticalLayout_9.addWidget(self.profile_save_button)

        self.profiles_btns_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_9.addItem(self.profiles_btns_spacer)


        self.profiles_layout.addWidget(self.profiles_buttons_frame, 0, 1, 2, 1)

        self.profiles_text_browser = QTextBrowser(self.profiles)
        self.profiles_text_browser.setObjectName(u"profiles_text_browser")
        self.profiles_text_browser.setReadOnly(False)

        self.profiles_layout.addWidget(self.profiles_text_browser, 1, 0, 1, 1)


        self.verticalLayout_5.addLayout(self.profiles_layout)

        self.config_tab_widget.addTab(self.profiles, "")
        self.config = QWidget()
        self.config.setObjectName(u"config")
        self.verticalLayout_3 = QVBoxLayout(self.config)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.config_file_text_browser = QTextBrowser(self.config)
        self.config_file_text_browser.setObjectName(u"config_file_text_browser")
        self.config_file_text_browser.setTabChangesFocus(False)
        self.config_file_text_browser.setReadOnly(False)

        self.verticalLayout_3.addWidget(self.config_file_text_browser)

        self.config_btns_frame = QFrame(self.config)
        self.config_btns_frame.setObjectName(u"config_btns_frame")
        self.config_btns_frame.setFrameShape(QFrame.StyledPanel)
        self.config_btns_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.config_btns_frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.config_file_save_button = QPushButton(self.config_btns_frame)
        self.config_file_save_button.setObjectName(u"config_file_save_button")

        self.horizontalLayout.addWidget(self.config_file_save_button)

        self.config_btns_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.config_btns_spacer)


        self.verticalLayout_3.addWidget(self.config_btns_frame)

        self.config_tab_widget.addTab(self.config, "")
        self.settings_file = QWidget()
        self.settings_file.setObjectName(u"settings_file")
        self.verticalLayout_6 = QVBoxLayout(self.settings_file)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.settings_file_text_browser = QTextBrowser(self.settings_file)
        self.settings_file_text_browser.setObjectName(u"settings_file_text_browser")

        self.verticalLayout_6.addWidget(self.settings_file_text_browser)

        self.config_tab_widget.addTab(self.settings_file, "")

        self.verticalLayout.addWidget(self.config_tab_widget)


        self.retranslateUi(Form)

        self.config_tab_widget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.versions_box.setTitle(QCoreApplication.translate("Form", u"Versions", None))
        self.conan_cur_version_label.setText(QCoreApplication.translate("Form", u"Current Conan Version:", None))
        self.conan_cur_version_value_label.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.python_cur_version_label.setText(QCoreApplication.translate("Form", u"Current Python Version:", None))
        self.python_cur_version_value_label.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.conan_sys_version_label.setText(QCoreApplication.translate("Form", u"System Conan Version:", None))
        self.conan_sys_version_value_label.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.python_sys_version_label.setText(QCoreApplication.translate("Form", u"System Python Version:", None))
        self.python_sys_version_value_label.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.paths_box.setTitle(QCoreApplication.translate("Form", u"Paths", None))
        self.conan_usr_home_label.setText(QCoreApplication.translate("Form", u"Conan User Home:", None))
        self.conan_usr_home_value_label.setText("")
        self.conan_storage_path_label.setText(QCoreApplication.translate("Form", u"Conan Storage Path:", None))
        self.conan_storage_path_value_label.setText("")
        self.conan_usr_cache_label.setText(QCoreApplication.translate("Form", u"Conan Short Path Cache:", None))
        self.conan_usr_cache_value_label.setText("")
        self.features_box.setTitle(QCoreApplication.translate("Form", u"Features", None))
        self.revision_enabled_label.setText(QCoreApplication.translate("Form", u"Revisions enabled:", None))
        self.revision_enabled_checkbox.setText("")
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.info_widget), QCoreApplication.translate("Form", u"Info", None))
        self.remote_refresh_button.setText(QCoreApplication.translate("Form", u"Refresh list", None))
        self.remote_move_up_button.setText(QCoreApplication.translate("Form", u"Move Up", None))
        self.remote_move_down_button.setText(QCoreApplication.translate("Form", u"Move Down", None))
        self.remote_login.setText(QCoreApplication.translate("Form", u"(Multi)Login", None))
        self.remote_toggle_disabled.setText(QCoreApplication.translate("Form", u"Enable/Disable", None))
        self.remote_add.setText(QCoreApplication.translate("Form", u"Add", None))
        self.remote_remove.setText(QCoreApplication.translate("Form", u"Remove", None))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.remotes), QCoreApplication.translate("Form", u"Remotes", None))
        self.profile_refresh_button.setText(QCoreApplication.translate("Form", u"Refresh list", None))
        self.profile_add_button.setText(QCoreApplication.translate("Form", u"Add", None))
        self.profile_remove_button.setText(QCoreApplication.translate("Form", u"Remove", None))
        self.profile_save_button.setText(QCoreApplication.translate("Form", u"Save", None))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.profiles), QCoreApplication.translate("Form", u"Profiles", None))
        self.config_file_save_button.setText(QCoreApplication.translate("Form", u"Save", None))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.config), QCoreApplication.translate("Form", u"Config File", None))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.settings_file), QCoreApplication.translate("Form", u"Settings YML File", None))
    # retranslateUi

