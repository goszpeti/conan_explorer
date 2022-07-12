# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\repos\conan_app_launcher\src\conan_app_launcher\ui\views\conan_conf\conan_conf.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


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
        self.info_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.info_scroll_area.setWidgetResizable(True)
        self.info_scroll_area.setObjectName("info_scroll_area")
        self.info_contents = QtWidgets.QWidget()
        self.info_contents.setGeometry(QtCore.QRect(0, 0, 608, 434))
        self.info_contents.setObjectName("info_contents")
        self.formLayout = QtWidgets.QFormLayout(self.info_contents)
        self.formLayout.setObjectName("formLayout")
        self.conan_cur_version_name_label = QtWidgets.QLabel(self.info_contents)
        self.conan_cur_version_name_label.setObjectName("conan_cur_version_name_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.conan_cur_version_name_label)
        self.conan_cur_version_value_label = QtWidgets.QLabel(self.info_contents)
        self.conan_cur_version_value_label.setText("")
        self.conan_cur_version_value_label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.conan_cur_version_value_label.setObjectName("conan_cur_version_value_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.conan_cur_version_value_label)
        self.conan_sys_version_name_label = QtWidgets.QLabel(self.info_contents)
        self.conan_sys_version_name_label.setObjectName("conan_sys_version_name_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.conan_sys_version_name_label)
        self.conan_sys_version_value_label = QtWidgets.QLabel(self.info_contents)
        self.conan_sys_version_value_label.setText("")
        self.conan_sys_version_value_label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.conan_sys_version_value_label.setObjectName("conan_sys_version_value_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.conan_sys_version_value_label)
        self.conan_usr_home_name_label = QtWidgets.QLabel(self.info_contents)
        self.conan_usr_home_name_label.setObjectName("conan_usr_home_name_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.conan_usr_home_name_label)
        self.conan_usr_cache_name_label = QtWidgets.QLabel(self.info_contents)
        self.conan_usr_cache_name_label.setObjectName("conan_usr_cache_name_label")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.conan_usr_cache_name_label)
        self.conan_usr_home_value_label = QtWidgets.QLabel(self.info_contents)
        self.conan_usr_home_value_label.setText("")
        self.conan_usr_home_value_label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.conan_usr_home_value_label.setObjectName("conan_usr_home_value_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.conan_usr_home_value_label)
        self.conan_usr_cache_value_label = QtWidgets.QLabel(self.info_contents)
        self.conan_usr_cache_value_label.setText("")
        self.conan_usr_cache_value_label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.conan_usr_cache_value_label.setObjectName("conan_usr_cache_value_label")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.conan_usr_cache_value_label)
        self.conan_storage_path_name_label = QtWidgets.QLabel(self.info_contents)
        self.conan_storage_path_name_label.setObjectName("conan_storage_path_name_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.conan_storage_path_name_label)
        self.conan_storage_path_value_label = QtWidgets.QLabel(self.info_contents)
        self.conan_storage_path_value_label.setText("")
        self.conan_storage_path_value_label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.conan_storage_path_value_label.setObjectName("conan_storage_path_value_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.conan_storage_path_value_label)
        self.info_scroll_area.setWidget(self.info_contents)
        self.verticalLayout_2.addWidget(self.info_scroll_area)
        self.config_tab_widget.addTab(self.info_widget, "")
        self.remotes = QtWidgets.QWidget()
        self.remotes.setObjectName("remotes")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.remotes)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.remotes_tree_view = QtWidgets.QTreeView(self.remotes)
        self.remotes_tree_view.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.remotes_tree_view.setDragEnabled(True)
        self.remotes_tree_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.remotes_tree_view.setSortingEnabled(False)
        self.remotes_tree_view.setObjectName("remotes_tree_view")
        self.verticalLayout_4.addWidget(self.remotes_tree_view)
        self.config_tab_widget.addTab(self.remotes, "")
        self.profiles = QtWidgets.QWidget()
        self.profiles.setObjectName("profiles")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.profiles)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.splitter = QtWidgets.QSplitter(self.profiles)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.profiles_list_view = QtWidgets.QListView(self.splitter)
        self.profiles_list_view.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.profiles_list_view.setMovement(QtWidgets.QListView.Free)
        self.profiles_list_view.setUniformItemSizes(True)
        self.profiles_list_view.setObjectName("profiles_list_view")
        self.profiles_text_browser = QtWidgets.QTextBrowser(self.splitter)
        self.profiles_text_browser.setReadOnly(False)
        self.profiles_text_browser.setObjectName("profiles_text_browser")
        self.verticalLayout_5.addWidget(self.splitter)
        self.frame_2 = QtWidgets.QFrame(self.profiles)
        self.frame_2.setMinimumSize(QtCore.QSize(0, 0))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.save_profile_button = QtWidgets.QPushButton(self.frame_2)
        self.save_profile_button.setObjectName("save_profile_button")
        self.horizontalLayout_2.addWidget(self.save_profile_button)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
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
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.save_config_file_button = QtWidgets.QPushButton(self.frame)
        self.save_config_file_button.setObjectName("save_config_file_button")
        self.horizontalLayout.addWidget(self.save_config_file_button)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
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
        self.conan_cur_version_name_label.setText(_translate("Form", "App Launcher Conan Version:"))
        self.conan_sys_version_name_label.setText(_translate("Form", "System Conan Version:"))
        self.conan_usr_home_name_label.setText(_translate("Form", "Conan User Home:"))
        self.conan_usr_cache_name_label.setText(_translate("Form", "Conan Short Path Cache:"))
        self.conan_storage_path_name_label.setText(_translate("Form", "Conan Storage Path:"))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.info_widget), _translate("Form", "Info"))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.remotes), _translate("Form", "Remotes"))
        self.save_profile_button.setText(_translate("Form", "Save"))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.profiles), _translate("Form", "Profiles"))
        self.save_config_file_button.setText(_translate("Form", "Save"))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.config), _translate("Form", "Config File"))
        self.config_tab_widget.setTabText(self.config_tab_widget.indexOf(self.settings_file), _translate("Form", "Settings YML File"))
