import platform
import subprocess
from pathlib import Path
from typing import Optional

import conan_app_launcher.app as app
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.core.system import escape_venv
from conan_app_launcher.ui.common import get_themed_asset_image
from conan_app_launcher.ui.widgets import RoundedMenu
from conans.client.cache.remote_registry import Remote
from PyQt5.QtCore import Qt, pyqtBoundSignal, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QDialog, QWidget, QMessageBox

from .conan_conf_ui import Ui_Form
from .dialogs import RemoteEditDialog, RemoteLoginDialog
from .model import ProfilesModel
from .controller import ConanRemoteController

class ConanConfigView(QDialog):

    load_signal = pyqtSignal()

    def __init__(self, parent: Optional[QWidget], conan_remotes_updated: Optional[pyqtBoundSignal] = None):
        # Add minimize and maximize buttons
        super().__init__(parent,  Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.config_file_path = Path("Unknown")
        self.profiles_path = Path("Unknown")
        self._remotes_controller = ConanRemoteController(self._ui.remotes_tree_view, conan_remotes_updated)
        self._init_remotes_tab()
        self._init_profiles_tab()
        self.load_signal.connect(self.__load)

    def __load(self):
        self.config_file_path = Path(app.conan_api.client_cache.conan_conf_path)
        self.profiles_path = Path(str(app.conan_api.client_cache.default_profile_path)).parent
        self._load_info_tab()
        self._load_remotes_tab()
        self._load_profiles_tab()
        self._load_config_file_tab()
        self._load_settings_yml_tab()

        # always show first tab on start
        self._ui.config_tab_widget.tabBar().setCurrentIndex(0)

    def _load_info_tab(self):
        self._ui.conan_cur_version_value_label.setText(app.conan_api.client_version)

        # setup system version outside of own venv
        with escape_venv():
            try:  # move to conan?
                out = subprocess.check_output("conan --version", shell=True).decode("utf-8")
                conan_sys_version = out.lower().split("version ")[1].rstrip()
            except Exception:
                Logger().debug("Conan version unknown...")
                conan_sys_version = "Unknown"
            try:  # move to conan?
                python_exe_name = "python"
                if platform.system() == "Linux":
                    python_exe_name = "python3"
                out = subprocess.check_output(f"{python_exe_name} --version", shell=True).decode("utf-8")
                python_sys_version = out.lower().split("python ")[1].rstrip()
            except Exception:
                python_sys_version = "Unknown"

        self._ui.python_cur_version_value_label.setText(platform.python_version())
        self._ui.revision_enabled_checkbox.setChecked(app.conan_api.client_cache.config.revisions_enabled)
        self._ui.conan_sys_version_value_label.setText(conan_sys_version)
        self._ui.python_sys_version_value_label.setText(python_sys_version)
        self._ui.conan_usr_home_value_label.setText(app.conan_api.client_cache.cache_folder)
        self._ui.conan_usr_cache_value_label.setText(str(app.conan_api.get_short_path_root()))
        self._ui.conan_storage_path_value_label.setText(str(app.conan_api.client_cache.store))

    def _load_settings_yml_tab(self):
        try:
            self._ui.settings_file_text_browser.setText(Path(app.conan_api.client_cache.settings_path).read_text())
        except Exception:
            Logger().error("Cannot read settings.yaml file!")

    def _load_config_file_tab(self):
        try:
            self._ui.config_file_text_browser.setText(self.config_file_path.read_text())
            self._ui.save_config_file_button.clicked.connect(self.save_config_file)
        except Exception:
            Logger().error("Cannot read Conan config file!")

    def _init_profiles_tab(self):
        self._ui.profiles_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.profiles_list_view.customContextMenuRequested.connect(
            self.on_profile_context_menu_requested)
        self._init_profile_context_menu()
        self._ui.save_profile_button.clicked.connect(self.save_profile_file)

    def _load_profiles_tab(self):
        profiles_model = ProfilesModel()
        self._ui.profiles_list_view.setModel(profiles_model)
        self._ui.profiles_list_view.selectionModel().selectionChanged.connect(self.on_profile_selected)

    def _init_profile_context_menu(self):
        self.profiles_cntx_menu = RoundedMenu()
        self._copy_profile_action = QAction("Copy profile name", self)
        self._copy_profile_action.setIcon(QIcon(get_themed_asset_image("icons/copy_link.png")))
        self.profiles_cntx_menu.addAction(self._copy_profile_action)
        self._copy_profile_action.triggered.connect(self.on_copy_profile_requested)

    def resizeEvent(self, a0):  # override
        """ Resize remote view columns automatically if window size changes """
        super().resizeEvent(a0)
        self._remotes_controller.resize_remote_columns()

    def apply_theme(self):
        self._init_profile_context_menu()
        self._init_remote_context_menu()

# Profile

    def on_copy_profile_requested(self):
        view_index = self._ui.profiles_list_view.selectedIndexes()[0]
        profile_name = view_index.data()
        QApplication.clipboard().setText(profile_name)

    def on_profile_selected(self):
        view_index = self._ui.profiles_list_view.selectedIndexes()[0]
        profile_name = view_index.data()
        try:
            profile_content = (self.profiles_path / profile_name).read_text()
        except Exception:
            profile_content = ""
        self._ui.profiles_text_browser.setText(profile_content)

    def on_profile_context_menu_requested(self, position):
        self.profiles_cntx_menu.exec_(self._ui.profiles_list_view.mapToGlobal(position))

    def save_profile_file(self):
        view_index = self._ui.profiles_list_view.selectedIndexes()[0]
        profile_name = view_index.data(0)
        text = self._ui.profiles_text_browser.toPlainText()
        (self.profiles_path / profile_name).write_text(text)

# Remote

    def _load_remotes_tab(self):
        
        self._remotes_controller.update() # TODO update once on show

    def _init_remotes_tab(self):
        self._ui.remote_refresh_button.clicked.connect(self._remotes_controller.update)
        self._ui.remote_move_down_button.setIcon(QIcon(get_themed_asset_image("icons/arrow_down.png")))
        self._ui.remote_login.clicked.connect(self.on_remotes_login)
        self._ui.remote_login.setIcon(QIcon(get_themed_asset_image("icons/login.png")))
        self._ui.remote_toggle_disabled.clicked.connect(self.on_remote_disable)
        self._ui.remote_toggle_disabled.setIcon(QIcon(get_themed_asset_image("icons/hide.png")))
        self._ui.remote_add.clicked.connect(self.on_remote_add)
        self._ui.remote_add.setIcon(QIcon(get_themed_asset_image("icons/plus_rounded.png")))
        self._ui.remote_remove.clicked.connect(self.on_remote_remove)
        self._ui.remote_remove.setIcon(QIcon(get_themed_asset_image("icons/minus_rounded.png")))

        self._ui.remotes_tree_view.doubleClicked.connect(self.on_remote_edit)
        self._ui.remotes_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.remotes_tree_view.customContextMenuRequested.connect(
            self.on_remote_context_menu_requested)
        self._ui.remote_refresh_button.setIcon(QIcon(get_themed_asset_image("icons/refresh.png")))
        self._ui.remote_move_up_button.setIcon(QIcon(get_themed_asset_image("icons/arrow_up.png")))
        self._ui.remote_move_down_button.clicked.connect(self._remotes_controller.move_down)
        self._ui.remote_move_up_button.clicked.connect(self._remotes_controller.move_up)

        self._init_remote_context_menu()

    def on_remote_context_menu_requested(self, position):
        self._remotes_cntx_menu.exec_(self._ui.remotes_tree_view.mapToGlobal(position))

    def _init_remote_context_menu(self):
        self._remotes_cntx_menu = RoundedMenu()
        self._copy_remote_action = QAction("Copy remote name", self)
        self._copy_remote_action.setIcon(QIcon(get_themed_asset_image("icons/copy_link.png")))
        self._remotes_cntx_menu.addAction(self._copy_remote_action)
        self._copy_remote_action.triggered.connect(self.on_copy_remote_name_requested)

        self._edit_remote_action = QAction("Edit remote", self)
        self._edit_remote_action.setIcon(QIcon(get_themed_asset_image("icons/edit.png")))
        self._remotes_cntx_menu.addAction(self._edit_remote_action)
        self._edit_remote_action.triggered.connect(self.on_remote_edit)

        self._add_remote_action = QAction("Add new remote", self)
        self._add_remote_action.setIcon(QIcon(get_themed_asset_image("icons/plus_rounded.png")))
        self._remotes_cntx_menu.addAction(self._add_remote_action)
        self._add_remote_action.triggered.connect(self.on_remote_add)

        self._remove_remote_action = QAction("Remove remote", self)
        self._remove_remote_action.setIcon(QIcon(get_themed_asset_image("icons/minus_rounded.png")))
        self._remotes_cntx_menu.addAction(self._remove_remote_action)
        self._remove_remote_action.triggered.connect(self.on_remote_remove)

        self._disable_profile_action = QAction("Disable/Enable remote", self)
        self._disable_profile_action.setIcon(QIcon(get_themed_asset_image("icons/hide.png")))
        self._remotes_cntx_menu.addAction(self._disable_profile_action)
        self._disable_profile_action.triggered.connect(self.on_remote_disable)

        self._login_remotes_action = QAction("(Multi)Login to remote", self)
        self._login_remotes_action.setIcon(QIcon(get_themed_asset_image("icons/login.png")))
        self._remotes_cntx_menu.addAction(self._login_remotes_action)
        self._login_remotes_action.triggered.connect(self.on_remotes_login)

    def on_remote_edit(self, model_index):
        remote_item = self._remotes_controller.get_selected_remote()
        if not remote_item:
            return
        self.remote_edit_dialog = RemoteEditDialog(remote_item.remote, False, self)
        reply = self.remote_edit_dialog.exec_()
        if reply == QDialog.Accepted:
            self._remotes_controller.update()

    def on_remotes_login(self):
        remote_item = self._remotes_controller.get_selected_remote()
        if not remote_item:
            return
        remotes = self._remotes_controller.get_remotes_from_same_server(remote_item.remote)
        if not remotes:
            return
        self.remote_login_dialog = RemoteLoginDialog(remotes, self)
        reply = self.remote_login_dialog.exec_()
        if reply == QDialog.Accepted:
                self._remotes_controller.update()

    def on_remote_add(self, model_index):
        new_remote = Remote("New", "", True, False)
        self.remote_edit_dialog = RemoteEditDialog(new_remote, True, self)
        reply = self.remote_edit_dialog.exec_()
        if reply == QDialog.Accepted:
            self._remotes_controller.update()

    def on_remote_remove(self, model_index):
        remote_item = self._remotes_controller.get_selected_remote()
        if not remote_item:
            return
        message_box = QMessageBox(parent=self)  # self.parentWidget())
        message_box.setWindowTitle("Delete Remove")
        message_box.setText(f"Are you sure, you want to delete the remote {remote_item.remote.name}?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setIcon(QMessageBox.Question)
        reply = message_box.exec_()
        if reply == QMessageBox.Yes:
            app.conan_api.conan.remote_remove(remote_item.remote.name)
            self._remotes_controller.update()

    def on_remote_disable(self, model_index):
        self._remotes_controller.remote_disable(model_index)

    def on_copy_remote_name_requested(self):
        self._remotes_controller.copy_remote_name()

# Conan Config 

    def save_config_file(self):
        self.config_file_path.write_text(self._ui.config_file_text_browser.toPlainText())


