# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'conan_conf.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QListView, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QSplitter, QTabWidget, QTreeView,
    QVBoxLayout, QWidget)

from conan_explorer.ui.widgets import (AnimatedToggle, PlainTextPasteBrowser)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(495, 464)
        Form.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(1, 2, 2, 2)
        self.config_tab_widget = QTabWidget(Form)
        self.config_tab_widget.setObjectName(u"config_tab_widget")
        self.config_tab_widget.setStyleSheet(u"QPushButton {Text-align:left}")
        self.info_widget = QWidget()
        self.info_widget.setObjectName(u"info_widget")
        self.info_widget.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.info_widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.info_scroll_area = QScrollArea(self.info_widget)
        self.info_scroll_area.setObjectName(u"info_scroll_area")
        self.info_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.info_scroll_area.setWidgetResizable(True)
        self.info_contents = QWidget()
        self.info_contents.setObjectName(u"info_contents")
        self.info_contents.setGeometry(QRect(0, 0, 486, 431))
        self.verticalLayout_7 = QVBoxLayout(self.info_contents)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.versions_box = QGroupBox(self.info_contents)
        self.versions_box.setObjectName(u"versions_box")
        self.gridLayout = QGridLayout(self.versions_box)
        self.gridLayout.setObjectName(u"gridLayout")
        self.python_exe_label = QLabel(self.versions_box)
        self.python_exe_label.setObjectName(u"python_exe_label")

        self.gridLayout.addWidget(self.python_exe_label, 2, 0, 1, 1)

        self.python_exe_value_label = QLabel(self.versions_box)
        self.python_exe_value_label.setObjectName(u"python_exe_value_label")
        self.python_exe_value_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout.addWidget(self.python_exe_value_label, 2, 1, 1, 1)

        self.conan_cur_version_label = QLabel(self.versions_box)
        self.conan_cur_version_label.setObjectName(u"conan_cur_version_label")

        self.gridLayout.addWidget(self.conan_cur_version_label, 0, 0, 1, 1)

        self.python_cur_version_value_label = QLabel(self.versions_box)
        self.python_cur_version_value_label.setObjectName(u"python_cur_version_value_label")

        self.gridLayout.addWidget(self.python_cur_version_value_label, 1, 1, 1, 1)

        self.conan_cur_version_value_label = QLabel(self.versions_box)
        self.conan_cur_version_value_label.setObjectName(u"conan_cur_version_value_label")
        self.conan_cur_version_value_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout.addWidget(self.conan_cur_version_value_label, 0, 1, 1, 1)

        self.python_cur_version_label = QLabel(self.versions_box)
        self.python_cur_version_label.setObjectName(u"python_cur_version_label")

        self.gridLayout.addWidget(self.python_cur_version_label, 1, 0, 1, 1)

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
        self.conan_usr_home_value_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_2.addWidget(self.conan_usr_home_value_label, 0, 1, 1, 1)

        self.conan_storage_path_label = QLabel(self.paths_box)
        self.conan_storage_path_label.setObjectName(u"conan_storage_path_label")

        self.gridLayout_2.addWidget(self.conan_storage_path_label, 1, 0, 1, 1)

        self.conan_storage_path_value_label = QLabel(self.paths_box)
        self.conan_storage_path_value_label.setObjectName(u"conan_storage_path_value_label")
        self.conan_storage_path_value_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_2.addWidget(self.conan_storage_path_value_label, 1, 1, 1, 1)

        self.conan_usr_cache_label = QLabel(self.paths_box)
        self.conan_usr_cache_label.setObjectName(u"conan_usr_cache_label")

        self.gridLayout_2.addWidget(self.conan_usr_cache_label, 2, 0, 1, 1)

        self.conan_usr_cache_value_label = QLabel(self.paths_box)
        self.conan_usr_cache_value_label.setObjectName(u"conan_usr_cache_value_label")
        self.conan_usr_cache_value_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_2.addWidget(self.conan_usr_cache_value_label, 2, 1, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 2)

        self.verticalLayout_7.addWidget(self.paths_box)

        self.features_box = QGroupBox(self.info_contents)
        self.features_box.setObjectName(u"features_box")
        self.features_box.setFlat(False)
        self.features_box.setCheckable(False)
        self.gridLayout_3 = QGridLayout(self.features_box)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.revision_enabled_label = QLabel(self.features_box)
        self.revision_enabled_label.setObjectName(u"revision_enabled_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
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
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.revision_enabled_checkbox.sizePolicy().hasHeightForWidth())
        self.revision_enabled_checkbox.setSizePolicy(sizePolicy1)
        self.revision_enabled_checkbox.setCheckable(True)

        self.gridLayout_3.addWidget(self.revision_enabled_checkbox, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 1)
        self.gridLayout_3.setColumnStretch(2, 2)

        self.verticalLayout_7.addWidget(self.features_box)

        self.verticalSpacer = QSpacerItem(20, 800, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer)

        self.info_scroll_area.setWidget(self.info_contents)

        self.verticalLayout_2.addWidget(self.info_scroll_area)

        self.config_tab_widget.addTab(self.info_widget, "")
        self.remotes = QWidget()
        self.remotes.setObjectName(u"remotes")
        self.verticalLayout_4 = QVBoxLayout(self.remotes)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.remotes_frame = QFrame(self.remotes)
        self.remotes_frame.setObjectName(u"remotes_frame")
        self.remotes_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.remotes_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_4 = QGridLayout(self.remotes_frame)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, -1, 0, -1)
        self.remotes_buttons_frame = QFrame(self.remotes_frame)
        self.remotes_buttons_frame.setObjectName(u"remotes_buttons_frame")
        self.remotes_buttons_frame.setStyleSheet(u"QPushButton {Text-align:left}")
        self.remotes_buttons_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.remotes_buttons_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.remotes_buttons_frame)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, -1, 0, -1)
        self.remote_refresh_button = QPushButton(self.remotes_buttons_frame)
        self.remote_refresh_button.setObjectName(u"remote_refresh_button")

        self.verticalLayout_8.addWidget(self.remote_refresh_button)

        self.remote_move_top_button = QPushButton(self.remotes_buttons_frame)
        self.remote_move_top_button.setObjectName(u"remote_move_top_button")

        self.verticalLayout_8.addWidget(self.remote_move_top_button)

        self.remote_move_up_button = QPushButton(self.remotes_buttons_frame)
        self.remote_move_up_button.setObjectName(u"remote_move_up_button")

        self.verticalLayout_8.addWidget(self.remote_move_up_button)

        self.remote_move_down_button = QPushButton(self.remotes_buttons_frame)
        self.remote_move_down_button.setObjectName(u"remote_move_down_button")

        self.verticalLayout_8.addWidget(self.remote_move_down_button)

        self.remote_move_bottom_button = QPushButton(self.remotes_buttons_frame)
        self.remote_move_bottom_button.setObjectName(u"remote_move_bottom_button")

        self.verticalLayout_8.addWidget(self.remote_move_bottom_button)

        self.remote_login_button = QPushButton(self.remotes_buttons_frame)
        self.remote_login_button.setObjectName(u"remote_login_button")

        self.verticalLayout_8.addWidget(self.remote_login_button)

        self.remote_toggle_disabled_button = QPushButton(self.remotes_buttons_frame)
        self.remote_toggle_disabled_button.setObjectName(u"remote_toggle_disabled_button")

        self.verticalLayout_8.addWidget(self.remote_toggle_disabled_button)

        self.remote_add_button = QPushButton(self.remotes_buttons_frame)
        self.remote_add_button.setObjectName(u"remote_add_button")

        self.verticalLayout_8.addWidget(self.remote_add_button)

        self.remote_remove_button = QPushButton(self.remotes_buttons_frame)
        self.remote_remove_button.setObjectName(u"remote_remove_button")

        self.verticalLayout_8.addWidget(self.remote_remove_button)

        self.remotes_edit_button = QPushButton(self.remotes_buttons_frame)
        self.remotes_edit_button.setObjectName(u"remotes_edit_button")

        self.verticalLayout_8.addWidget(self.remotes_edit_button)

        self.remotes_btns_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.remotes_btns_spacer)


        self.gridLayout_4.addWidget(self.remotes_buttons_frame, 0, 1, 1, 1)

        self.remotes_tree_view = QTreeView(self.remotes_frame)
        self.remotes_tree_view.setObjectName(u"remotes_tree_view")
        self.remotes_tree_view.setFrameShape(QFrame.Shape.NoFrame)
        self.remotes_tree_view.setDragEnabled(True)
        self.remotes_tree_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.remotes_tree_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.remotes_tree_view.setSortingEnabled(False)

        self.gridLayout_4.addWidget(self.remotes_tree_view, 0, 0, 1, 1)


        self.verticalLayout_4.addWidget(self.remotes_frame)

        self.config_tab_widget.addTab(self.remotes, "")
        self.profiles = QWidget()
        self.profiles.setObjectName(u"profiles")
        self.verticalLayout_11 = QVBoxLayout(self.profiles)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.profiles_grid_layout = QGridLayout()
        self.profiles_grid_layout.setObjectName(u"profiles_grid_layout")
        self.splitter = QSplitter(self.profiles)
        self.splitter.setObjectName(u"splitter")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy2)
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.profiles_list_view = QListView(self.splitter)
        self.profiles_list_view.setObjectName(u"profiles_list_view")
        self.profiles_list_view.setFrameShape(QFrame.Shape.NoFrame)
        self.profiles_list_view.setMovement(QListView.Movement.Free)
        self.profiles_list_view.setUniformItemSizes(True)
        self.splitter.addWidget(self.profiles_list_view)
        self.profiles_text_browser = PlainTextPasteBrowser(self.splitter)
        self.profiles_text_browser.setObjectName(u"profiles_text_browser")
        self.profiles_text_browser.setUndoRedoEnabled(True)
        self.profiles_text_browser.setReadOnly(False)
        self.splitter.addWidget(self.profiles_text_browser)

        self.profiles_grid_layout.addWidget(self.splitter, 0, 0, 1, 1)

        self.profiles_buttons_frame = QFrame(self.profiles)
        self.profiles_buttons_frame.setObjectName(u"profiles_buttons_frame")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.profiles_buttons_frame.sizePolicy().hasHeightForWidth())
        self.profiles_buttons_frame.setSizePolicy(sizePolicy3)
        self.profiles_buttons_frame.setStyleSheet(u"QPushButton {Text-align:left}")
        self.profiles_buttons_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.profiles_buttons_frame.setFrameShadow(QFrame.Shadow.Raised)
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

        self.profile_rename_button = QPushButton(self.profiles_buttons_frame)
        self.profile_rename_button.setObjectName(u"profile_rename_button")

        self.verticalLayout_9.addWidget(self.profile_rename_button)

        self.profile_save_button = QPushButton(self.profiles_buttons_frame)
        self.profile_save_button.setObjectName(u"profile_save_button")

        self.verticalLayout_9.addWidget(self.profile_save_button)

        self.profiles_copy_name_button = QPushButton(self.profiles_buttons_frame)
        self.profiles_copy_name_button.setObjectName(u"profiles_copy_name_button")

        self.verticalLayout_9.addWidget(self.profiles_copy_name_button)

        self.profiles_btns_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_9.addItem(self.profiles_btns_spacer)


        self.profiles_grid_layout.addWidget(self.profiles_buttons_frame, 0, 1, 1, 1)


        self.verticalLayout_11.addLayout(self.profiles_grid_layout)

        self.config_tab_widget.addTab(self.profiles, "")
        self.editables = QWidget()
        self.editables.setObjectName(u"editables")
        self.verticalLayout_5 = QVBoxLayout(self.editables)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.editables_grid_layout = QGridLayout()
        self.editables_grid_layout.setObjectName(u"editables_grid_layout")
        self.editables_splitter = QSplitter(self.editables)
        self.editables_splitter.setObjectName(u"editables_splitter")
        sizePolicy2.setHeightForWidth(self.editables_splitter.sizePolicy().hasHeightForWidth())
        self.editables_splitter.setSizePolicy(sizePolicy2)
        self.editables_splitter.setOrientation(Qt.Orientation.Vertical)
        self.editables_ref_view = QTreeView(self.editables_splitter)
        self.editables_ref_view.setObjectName(u"editables_ref_view")
        self.editables_ref_view.setFrameShape(QFrame.Shape.NoFrame)
        self.editables_splitter.addWidget(self.editables_ref_view)

        self.editables_grid_layout.addWidget(self.editables_splitter, 0, 0, 1, 1)

        self.editables_button_frame = QFrame(self.editables)
        self.editables_button_frame.setObjectName(u"editables_button_frame")
        self.editables_button_frame.setStyleSheet(u"QPushButton {Text-align:left}")
        self.editables_button_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.editables_button_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.editables_button_frame)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, -1, 0, -1)
        self.editables_refresh_button = QPushButton(self.editables_button_frame)
        self.editables_refresh_button.setObjectName(u"editables_refresh_button")

        self.verticalLayout_10.addWidget(self.editables_refresh_button)

        self.editables_add_button = QPushButton(self.editables_button_frame)
        self.editables_add_button.setObjectName(u"editables_add_button")

        self.verticalLayout_10.addWidget(self.editables_add_button)

        self.editables_remove_button = QPushButton(self.editables_button_frame)
        self.editables_remove_button.setObjectName(u"editables_remove_button")

        self.verticalLayout_10.addWidget(self.editables_remove_button)

        self.editables_edit_button = QPushButton(self.editables_button_frame)
        self.editables_edit_button.setObjectName(u"editables_edit_button")

        self.verticalLayout_10.addWidget(self.editables_edit_button)

        self.editables_button_vspacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.editables_button_vspacer)


        self.editables_grid_layout.addWidget(self.editables_button_frame, 0, 1, 1, 1)


        self.verticalLayout_5.addLayout(self.editables_grid_layout)

        self.config_tab_widget.addTab(self.editables, "")
        self.config = QWidget()
        self.config.setObjectName(u"config")
        self.verticalLayout_3 = QVBoxLayout(self.config)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.config_file_text_browser = PlainTextPasteBrowser(self.config)
        self.config_file_text_browser.setObjectName(u"config_file_text_browser")
        self.config_file_text_browser.setTabChangesFocus(False)
        self.config_file_text_browser.setUndoRedoEnabled(True)
        self.config_file_text_browser.setReadOnly(False)

        self.verticalLayout_3.addWidget(self.config_file_text_browser)

        self.config_btns_frame = QFrame(self.config)
        self.config_btns_frame.setObjectName(u"config_btns_frame")
        self.config_btns_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.config_btns_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.config_btns_frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.config_file_save_button = QPushButton(self.config_btns_frame)
        self.config_file_save_button.setObjectName(u"config_file_save_button")

        self.horizontalLayout.addWidget(self.config_file_save_button)

        self.config_btns_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.config_btns_spacer)


        self.verticalLayout_3.addWidget(self.config_btns_frame)

        self.config_tab_widget.addTab(self.config, "")
        self.settings_file = QWidget()
        self.settings_file.setObjectName(u"settings_file")
        self.verticalLayout_6 = QVBoxLayout(self.settings_file)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.settings_file_text_browser = PlainTextPasteBrowser(self.settings_file)
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
        self.python_exe_label.setText(QCoreApplication.translate("Form", u"Current Python Executable:", None))
        self.python_exe_value_label.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.conan_cur_version_label.setText(QCoreApplication.translate("Form", u"Current Conan Version:", None))
        self.python_cur_version_value_label.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.conan_cur_version_value_label.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.python_cur_version_label.setText(QCoreApplication.translate("Form", u"Current Python Version:", None))
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
        self.remote_move_top_button.setText(QCoreApplication.translate("Form", u"Move to Top", None))
        self.remote_move_up_button.setText(QCoreApplication.translate("Form", u"Move Up", None))
        self.remote_move_down_button.setText(QCoreApplication.translate("Form", u"Move Down", None))
        self.remote_move_bottom_button.setText(QCoreApplication.translate("Form", u"Move to Bottom", None))
        self.remote_login_button.setText(QCoreApplication.translate("Form", u"(Multi)Login", None))
        self.remote_toggle_disabled_button.setText(QCoreApplication.translate("Form", u"Enable/Disable", None))
        self.remote_add_button.setText(QCoreApplication.translate("Form", u"Add", None))
        self.remote_remove_button.setText(QCoreApplication.translate("Form", u"Remove", None))
        self.remotes_edit_button.setText(QCoreApplication.translate("Form", u"Edit", None))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.remotes), QCoreApplication.translate("Form", u"Remotes", None))
        self.profile_refresh_button.setText(QCoreApplication.translate("Form", u"Refresh List", None))
        self.profile_add_button.setText(QCoreApplication.translate("Form", u"Add", None))
        self.profile_remove_button.setText(QCoreApplication.translate("Form", u"Remove", None))
        self.profile_rename_button.setText(QCoreApplication.translate("Form", u"Rename", None))
        self.profile_save_button.setText(QCoreApplication.translate("Form", u"Save", None))
        self.profiles_copy_name_button.setText(QCoreApplication.translate("Form", u"Copy Name", None))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.profiles), QCoreApplication.translate("Form", u"Profiles", None))
        self.editables_refresh_button.setText(QCoreApplication.translate("Form", u"Refresh List", None))
        self.editables_add_button.setText(QCoreApplication.translate("Form", u"Add", None))
        self.editables_remove_button.setText(QCoreApplication.translate("Form", u"Remove", None))
        self.editables_edit_button.setText(QCoreApplication.translate("Form", u"Edit", None))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.editables), QCoreApplication.translate("Form", u"Editables", None))
        self.config_file_save_button.setText(QCoreApplication.translate("Form", u"Save", None))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.config), QCoreApplication.translate("Form", u"Config File", None))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.settings_file), QCoreApplication.translate("Form", u"Settings YML File", None))
    # retranslateUi

