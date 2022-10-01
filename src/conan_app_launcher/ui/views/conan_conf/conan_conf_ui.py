# Form implementation generated from reading ui file 'c:\repos\conan_app_launcher\src\conan_app_launcher\ui\views\conan_conf\conan_conf.ui'
#
# Created by: PyQt6 UI code generator 6.3.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(617, 464)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(1, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.config_tab_widget = QtWidgets.QTabWidget(Form)
        self.config_tab_widget.setStyleSheet("")
        self.config_tab_widget.setObjectName("config_tab_widget")
        self.info_widget = QtWidgets.QWidget()
        self.info_widget.setStyleSheet("")
        self.info_widget.setObjectName("info_widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.info_widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.info_scroll_area = QtWidgets.QScrollArea(self.info_widget)
        self.info_scroll_area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.info_scroll_area.setWidgetResizable(True)
        self.info_scroll_area.setObjectName("info_scroll_area")
        self.info_contents = QtWidgets.QWidget()
        self.info_contents.setGeometry(QtCore.QRect(0, 0, 608, 434))
        self.info_contents.setObjectName("info_contents")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.info_contents)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.groupBox = QtWidgets.QGroupBox(self.info_contents)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.conan_cur_version_label = QtWidgets.QLabel(self.groupBox)
        self.conan_cur_version_label.setObjectName("conan_cur_version_label")
        self.gridLayout_2.addWidget(self.conan_cur_version_label, 0, 0, 1, 1)
        self.conan_cur_version_value_label = QtWidgets.QLabel(self.groupBox)
        self.conan_cur_version_value_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse|QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard|QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.conan_cur_version_value_label.setObjectName("conan_cur_version_value_label")
        self.gridLayout_2.addWidget(self.conan_cur_version_value_label, 0, 1, 1, 1)
        self.python_cur_version_label = QtWidgets.QLabel(self.groupBox)
        self.python_cur_version_label.setObjectName("python_cur_version_label")
        self.gridLayout_2.addWidget(self.python_cur_version_label, 1, 0, 1, 1)
        self.conan_sys_version_value_label = QtWidgets.QLabel(self.groupBox)
        self.conan_sys_version_value_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse|QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard|QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.conan_sys_version_value_label.setObjectName("conan_sys_version_value_label")
        self.gridLayout_2.addWidget(self.conan_sys_version_value_label, 2, 1, 1, 1)
        self.conan_sys_version_label = QtWidgets.QLabel(self.groupBox)
        self.conan_sys_version_label.setObjectName("conan_sys_version_label")
        self.gridLayout_2.addWidget(self.conan_sys_version_label, 2, 0, 1, 1)
        self.python_cur_version_value_label = QtWidgets.QLabel(self.groupBox)
        self.python_cur_version_value_label.setObjectName("python_cur_version_value_label")
        self.gridLayout_2.addWidget(self.python_cur_version_value_label, 1, 1, 1, 1)
        self.python_sys_version_label = QtWidgets.QLabel(self.groupBox)
        self.python_sys_version_label.setObjectName("python_sys_version_label")
        self.gridLayout_2.addWidget(self.python_sys_version_label, 3, 0, 1, 1)
        self.python_sys_version_value_label = QtWidgets.QLabel(self.groupBox)
        self.python_sys_version_value_label.setObjectName("python_sys_version_value_label")
        self.gridLayout_2.addWidget(self.python_sys_version_value_label, 3, 1, 1, 1)
        self.verticalLayout_7.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.info_contents)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.conan_usr_home_label = QtWidgets.QLabel(self.groupBox_2)
        self.conan_usr_home_label.setObjectName("conan_usr_home_label")
        self.gridLayout.addWidget(self.conan_usr_home_label, 0, 0, 1, 1)
        self.conan_usr_home_value_label = QtWidgets.QLabel(self.groupBox_2)
        self.conan_usr_home_value_label.setText("")
        self.conan_usr_home_value_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse|QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard|QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.conan_usr_home_value_label.setObjectName("conan_usr_home_value_label")
        self.gridLayout.addWidget(self.conan_usr_home_value_label, 0, 1, 1, 1)
        self.conan_storage_path_label = QtWidgets.QLabel(self.groupBox_2)
        self.conan_storage_path_label.setObjectName("conan_storage_path_label")
        self.gridLayout.addWidget(self.conan_storage_path_label, 1, 0, 1, 1)
        self.conan_storage_path_value_label = QtWidgets.QLabel(self.groupBox_2)
        self.conan_storage_path_value_label.setText("")
        self.conan_storage_path_value_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse|QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard|QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.conan_storage_path_value_label.setObjectName("conan_storage_path_value_label")
        self.gridLayout.addWidget(self.conan_storage_path_value_label, 1, 1, 1, 1)
        self.conan_usr_cache_label = QtWidgets.QLabel(self.groupBox_2)
        self.conan_usr_cache_label.setObjectName("conan_usr_cache_label")
        self.gridLayout.addWidget(self.conan_usr_cache_label, 2, 0, 1, 1)
        self.conan_usr_cache_value_label = QtWidgets.QLabel(self.groupBox_2)
        self.conan_usr_cache_value_label.setText("")
        self.conan_usr_cache_value_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse|QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard|QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.conan_usr_cache_value_label.setObjectName("conan_usr_cache_value_label")
        self.gridLayout.addWidget(self.conan_usr_cache_value_label, 2, 1, 1, 1)
        self.verticalLayout_7.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.info_contents)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.revision_enabled_label = QtWidgets.QLabel(self.groupBox_3)
        self.revision_enabled_label.setObjectName("revision_enabled_label")
        self.gridLayout_3.addWidget(self.revision_enabled_label, 0, 0, 1, 1)
        self.revision_enabled_checkbox = QtWidgets.QCheckBox(self.groupBox_3)
        self.revision_enabled_checkbox.setEnabled(False)
        self.revision_enabled_checkbox.setText("")
        self.revision_enabled_checkbox.setCheckable(True)
        self.revision_enabled_checkbox.setObjectName("revision_enabled_checkbox")
        self.gridLayout_3.addWidget(self.revision_enabled_checkbox, 0, 1, 1, 1)
        self.verticalLayout_7.addWidget(self.groupBox_3)
        spacerItem = QtWidgets.QSpacerItem(20, 800, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_7.addItem(spacerItem)
        self.info_scroll_area.setWidget(self.info_contents)
        self.verticalLayout_2.addWidget(self.info_scroll_area)
        self.config_tab_widget.addTab(self.info_widget, "")
        self.remotes = QtWidgets.QWidget()
        self.remotes.setObjectName("remotes")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.remotes)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.frame_3 = QtWidgets.QFrame(self.remotes)
        self.frame_3.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.frame_3)
        self.gridLayout_4.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.remotes_tree_view = QtWidgets.QTreeView(self.frame_3)
        self.remotes_tree_view.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.remotes_tree_view.setDragEnabled(True)
        self.remotes_tree_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.remotes_tree_view.setSortingEnabled(False)
        self.remotes_tree_view.setObjectName("remotes_tree_view")
        self.gridLayout_4.addWidget(self.remotes_tree_view, 0, 0, 1, 1)
        self.frame_4 = QtWidgets.QFrame(self.frame_3)
        self.frame_4.setStyleSheet("QPushButton {Text-align:left}")
        self.frame_4.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_8.setContentsMargins(0, -1, 0, -1)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.remote_refresh_button = QtWidgets.QPushButton(self.frame_4)
        self.remote_refresh_button.setObjectName("remote_refresh_button")
        self.verticalLayout_8.addWidget(self.remote_refresh_button)
        self.remote_move_up_button = QtWidgets.QPushButton(self.frame_4)
        self.remote_move_up_button.setObjectName("remote_move_up_button")
        self.verticalLayout_8.addWidget(self.remote_move_up_button)
        self.remote_move_down_button = QtWidgets.QPushButton(self.frame_4)
        self.remote_move_down_button.setObjectName("remote_move_down_button")
        self.verticalLayout_8.addWidget(self.remote_move_down_button)
        self.remote_login = QtWidgets.QPushButton(self.frame_4)
        self.remote_login.setObjectName("remote_login")
        self.verticalLayout_8.addWidget(self.remote_login)
        self.remote_toggle_disabled = QtWidgets.QPushButton(self.frame_4)
        self.remote_toggle_disabled.setObjectName("remote_toggle_disabled")
        self.verticalLayout_8.addWidget(self.remote_toggle_disabled)
        self.remote_add = QtWidgets.QPushButton(self.frame_4)
        self.remote_add.setObjectName("remote_add")
        self.verticalLayout_8.addWidget(self.remote_add)
        self.remote_remove = QtWidgets.QPushButton(self.frame_4)
        self.remote_remove.setObjectName("remote_remove")
        self.verticalLayout_8.addWidget(self.remote_remove)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_8.addItem(spacerItem1)
        self.gridLayout_4.addWidget(self.frame_4, 0, 1, 1, 1)
        self.verticalLayout_4.addWidget(self.frame_3)
        self.config_tab_widget.addTab(self.remotes, "")
        self.profiles = QtWidgets.QWidget()
        self.profiles.setObjectName("profiles")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.profiles)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.splitter = QtWidgets.QSplitter(self.profiles)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.splitter.setObjectName("splitter")
        self.profiles_list_view = QtWidgets.QListView(self.splitter)
        self.profiles_list_view.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.profiles_list_view.setMovement(QtWidgets.QListView.Movement.Free)
        self.profiles_list_view.setUniformItemSizes(True)
        self.profiles_list_view.setObjectName("profiles_list_view")
        self.profiles_text_browser = QtWidgets.QTextBrowser(self.splitter)
        self.profiles_text_browser.setReadOnly(False)
        self.profiles_text_browser.setObjectName("profiles_text_browser")
        self.verticalLayout_5.addWidget(self.splitter)
        self.frame_2 = QtWidgets.QFrame(self.profiles)
        self.frame_2.setMinimumSize(QtCore.QSize(0, 0))
        self.frame_2.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.save_profile_button = QtWidgets.QPushButton(self.frame_2)
        self.save_profile_button.setObjectName("save_profile_button")
        self.horizontalLayout_2.addWidget(self.save_profile_button)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout_5.addWidget(self.frame_2)
        self.config_tab_widget.addTab(self.profiles, "")
        self.config = QtWidgets.QWidget()
        self.config.setObjectName("config")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.config)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.config_file_text_browser = QtWidgets.QTextBrowser(self.config)
        self.config_file_text_browser.setTabChangesFocus(False)
        self.config_file_text_browser.setReadOnly(False)
        self.config_file_text_browser.setObjectName("config_file_text_browser")
        self.verticalLayout_3.addWidget(self.config_file_text_browser)
        self.frame = QtWidgets.QFrame(self.config)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.save_config_file_button = QtWidgets.QPushButton(self.frame)
        self.save_config_file_button.setObjectName("save_config_file_button")
        self.horizontalLayout.addWidget(self.save_config_file_button)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout_3.addWidget(self.frame)
        self.config_tab_widget.addTab(self.config, "")
        self.settings_file = QtWidgets.QWidget()
        self.settings_file.setObjectName("settings_file")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.settings_file)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.settings_file_text_browser = QtWidgets.QTextBrowser(self.settings_file)
        self.settings_file_text_browser.setObjectName("settings_file_text_browser")
        self.verticalLayout_6.addWidget(self.settings_file_text_browser)
        self.config_tab_widget.addTab(self.settings_file, "")
        self.verticalLayout.addWidget(self.config_tab_widget)

        self.retranslateUi(Form)
        self.config_tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Versions"))
        self.conan_cur_version_label.setText(_translate("Form", "Current Conan Version:"))
        self.conan_cur_version_value_label.setText(_translate("Form", "Unknown"))
        self.python_cur_version_label.setText(_translate("Form", "Current Python Version:"))
        self.conan_sys_version_value_label.setText(_translate("Form", "Unknown"))
        self.conan_sys_version_label.setText(_translate("Form", "System Conan Version:"))
        self.python_cur_version_value_label.setText(_translate("Form", "Unknown"))
        self.python_sys_version_label.setText(_translate("Form", "System Python Version:"))
        self.python_sys_version_value_label.setText(_translate("Form", "Unknown"))
        self.groupBox_2.setTitle(_translate("Form", "Paths"))
        self.conan_usr_home_label.setText(_translate("Form", "Conan User Home:"))
        self.conan_storage_path_label.setText(_translate("Form", "Conan Storage Path:"))
        self.conan_usr_cache_label.setText(_translate("Form", "Conan Short Path Cache:"))
        self.groupBox_3.setTitle(_translate("Form", "Features"))
        self.revision_enabled_label.setText(_translate("Form", "Revisions enabled:"))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.info_widget), _translate("Form", "Info"))
        self.remote_refresh_button.setText(_translate("Form", "Refresh list"))
        self.remote_move_up_button.setText(_translate("Form", "Move Up"))
        self.remote_move_down_button.setText(_translate("Form", "Move Down"))
        self.remote_login.setText(_translate("Form", "(Multi)Login"))
        self.remote_toggle_disabled.setText(_translate("Form", "Enable/Disable"))
        self.remote_add.setText(_translate("Form", "Add"))
        self.remote_remove.setText(_translate("Form", "Remove"))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.remotes), _translate("Form", "Remotes"))
        self.save_profile_button.setText(_translate("Form", "Save"))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.profiles), _translate("Form", "Profiles"))
        self.save_config_file_button.setText(_translate("Form", "Save"))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.config), _translate("Form", "Config File"))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.settings_file), _translate("Form", "Settings YML File"))
