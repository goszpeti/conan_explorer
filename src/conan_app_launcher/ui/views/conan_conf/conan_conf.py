from pathlib import Path
from typing import List, Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.ui.common import get_themed_asset_image
from conan_app_launcher.ui.common.model import re_register_signal
from conan_app_launcher.ui.widgets import RoundedMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QDialog, QWidget
import subprocess

from .model import ProfilesModel, RemotesModel, RemotesModelItem
from .dialogs import RemoteEditDialog
from .conan_conf_ui import Ui_Form

# app.conan_api.get_remotes()
from conans.client.cache.remote_registry import Remote


class ConanConfigView(QDialog):

    def __init__(self, parent: Optional[QWidget]):
        # Add minimize and maximize buttons
        super().__init__(parent,  Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        #self.page_widgets = page_widgets
        #self.conan_pkg_installed = conan_pkg_installed
        #self.conan_pkg_removed = conan_pkg_removed
        self._ui = Ui_Form()
        self._ui.setupUi(self)

        self.config_file_path = Path(app.conan_api.client_cache.conan_conf_path)
        self.profiles_path = Path(app.conan_api.client_cache.default_profile_path).parent
        
        self._init_info_tab()
        self._init_remotes_tab()
        self._init_profiles_tab()
        self._init_config_file_tab()
        self._init_settings_yml_tab()
        
        app.conan_api.conan.remote_list_pref

    def _init_info_tab(self):
        self._ui.conan_cur_version_value_label.setText(app.conan_api.client_version)

        # setup system version:
        try: # TODO move to conan?
            out = subprocess.check_output("conan --version").decode("utf-8")  # TODO
            conan_sys_version = out.split("version ")[1].rstrip()
        except:
            conan_sys_version = "Unknown"

        self._ui.conan_sys_version_value_label.setText(conan_sys_version)
        self._ui.conan_usr_home_value_label.setText(app.conan_api.client_cache.cache_folder)
        self._ui.conan_usr_cache_value_label.setText(str(app.conan_api.get_short_path_root()))
        self._ui.conan_storage_path_value_label.setText(app.conan_api.conan.app.cache.store)

    def _init_settings_yml_tab(self):
        self._ui.settings_file_text_browser.setText(Path(app.conan_api.conan.app.cache.settings_path).read_text())

    def _init_config_file_tab(self):
        self._ui.config_file_text_browser.setText(self.config_file_path.read_text())
        self._ui.save_config_file_button.clicked.connect(self.save_config_file)

    def _init_profiles_tab(self):
        profiles_model = ProfilesModel()
        self.profiles_cntx_menu = RoundedMenu()

        self._ui.profiles_list_view.setModel(profiles_model)
        self._ui.profiles_list_view.selectionModel().selectionChanged.connect(self.on_profile_selected)
        self._ui.profiles_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.profiles_list_view.customContextMenuRequested.connect(
            self.on_profile_context_menu_requested)
        self._init_profile_context_menu()
        self._ui.save_profile_button.clicked.connect(self.save_profile_file)

    def _init_remotes_tab(self):
        remotes_model = RemotesModel()
        self.remotes_cntx_menu = RoundedMenu()

        remotes_model.setup_model_data()
        self._ui.remotes_tree_view.setModel(remotes_model)
        self._ui.remotes_tree_view.resizeColumnToContents(0)
        self._ui.remotes_tree_view.resizeColumnToContents(1)
        self._ui.remotes_tree_view.resizeColumnToContents(3)
        self._ui.remotes_tree_view.doubleClicked.connect(self.edit_remote)
        # re_register_signal(self._ui.remotes_tree_view.doubleClicked,
        #                    self.edit_remote)
        self._ui.remotes_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.remotes_tree_view.customContextMenuRequested.connect(
            self.on_remote_context_menu_requested)
        self._init_remote_context_menu()
        
    def _init_profile_context_menu(self):
        self.copy_profile_action = QAction("Copy profile name", self)
        self.copy_profile_action.setIcon(QIcon(get_themed_asset_image("icons/copy_link.png")))
        self.profiles_cntx_menu.addAction(self.copy_profile_action)
        self.copy_profile_action.triggered.connect(self.on_copy_profile_requested)

    def on_copy_profile_requested(self):
        view_index = self._ui.profiles_list_view.selectedIndexes()[0]
        profile_name = view_index.data()
        QApplication.clipboard().setText(profile_name)

    def on_profile_selected(self):
        view_index = self._ui.profiles_list_view.selectedIndexes()[0]
        profile_name = view_index.data()
        try:
            profile_content = (self.profiles_path / profile_name).read_text()
        except:
            profile_content = ""
        self._ui.profiles_text_browser.setText(profile_content)

    def on_profile_context_menu_requested(self, position):
        self.profiles_cntx_menu.exec_(self._ui.profiles_list_view.mapToGlobal(position))

    def on_remote_context_menu_requested(self, position):
        self.remotes_cntx_menu.exec_(self._ui.remotes_tree_view.mapToGlobal(position))

    def edit_remote(self, model_index):
        self.remote_dialog = RemoteEditDialog(self)
        self.remote_dialog.show()
        
    def add_remote(self, model_index):
        print("HALLO")
        
    def remove_remote(self, model_index):
        print("HALLO")

    def _init_remote_context_menu(self):
        self.copy_profile_action = QAction("Copy remote name", self)
        self.copy_profile_action.setIcon(QIcon(get_themed_asset_image("icons/copy_link.png")))
        self.remotes_cntx_menu.addAction(self.copy_profile_action)
        self.copy_profile_action.triggered.connect(self.on_copy_remote_name_requested)

        self.copy_profile_action = QAction("Edit remote", self)
        self.copy_profile_action.setIcon(QIcon(get_themed_asset_image("icons/edit.png")))
        self.remotes_cntx_menu.addAction(self.copy_profile_action)
        self.copy_profile_action.triggered.connect(self.edit_remote)

        self.copy_profile_action = QAction("Add new remote", self)
        self.copy_profile_action.setIcon(QIcon(get_themed_asset_image("icons/plus_rounded.png")))
        self.remotes_cntx_menu.addAction(self.copy_profile_action)
        self.copy_profile_action.triggered.connect(self.on_copy_remote_name_requested)

        self.copy_profile_action = QAction("Remove remote", self)
        self.copy_profile_action.setIcon(QIcon(get_themed_asset_image("icons/minus_rounded.png")))
        self.remotes_cntx_menu.addAction(self.copy_profile_action)
        self.copy_profile_action.triggered.connect(self.on_copy_remote_name_requested)

    def on_copy_remote_name_requested(self):
        view_index = self._ui.remotes_tree_view.selectedIndexes()[0]
        name = view_index.data(0)
        QApplication.clipboard().setText(name)

    def save_profile_file(self):
        view_index = self._ui.profiles_list_view.selectedIndexes()[0]
        profile_name = view_index.data(0)
        text = self._ui.profiles_text_browser.toPlainText()
        (self.profiles_path / profile_name).write_text(text)

    def save_config_file(self):
        self.config_file_path.write_text(self._ui.config_file_text_browser.toPlainText())
