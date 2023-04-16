from os import devnull
import platform
import subprocess
from pathlib import Path
import sys
from typing import Optional, TYPE_CHECKING

from conan_app_launcher import conan_version
import conan_app_launcher.app as app
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.app.system import delete_path
from conan_app_launcher.ui.common import get_themed_asset_icon
from conan_app_launcher.ui.common.syntax_highlighting import ConfigHighlighter
from conan_app_launcher.ui.plugin import PluginDescription, PluginInterfaceV1
from conan_app_launcher.ui.widgets import RoundedMenu
from conan_app_launcher.conan_wrapper.types import Remote
from PySide6.QtCore import Qt, Signal, QItemSelectionModel
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QDialog, QWidget, QMessageBox, QApplication, QInputDialog

from .dialogs import RemoteEditDialog, RemoteLoginDialog
from .model import ProfilesModel
from .controller import ConanRemoteController

if TYPE_CHECKING:
    from conan_app_launcher.ui.main_window import BaseSignals
    from conan_app_launcher.ui.fluent_window.fluent_window import FluentWindow


class ConanConfigView(PluginInterfaceV1):

    load_signal = Signal()  # type: ignore

    def __init__(self, parent: QWidget, plugin_description: PluginDescription,
                 base_signals: "BaseSignals", page_widgets: Optional["FluentWindow.PageStore"] = None):
        super().__init__(parent, plugin_description, base_signals)
        from .conan_conf_ui import Ui_Form
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.load_signal.connect(self.load)
        self.config_file_path = Path("Unknown")
        self.profiles_path = Path("Unknown")
        self._edited_profile = None

    def load(self):
        assert self._base_signals
        self._remotes_controller = ConanRemoteController(
            self._ui.remotes_tree_view, self._base_signals.conan_remotes_updated)
        self._init_remotes_tab()
        self._init_profiles_tab()
        self.set_themed_icon(self._ui.config_file_save_button, "icons/save.svg")

        self.config_file_path = Path(app.conan_api._client_cache.conan_conf_path)
        self.profiles_path = Path(str(app.conan_api._client_cache.default_profile_path)).parent
        self._load_info_tab()
        self._load_remotes_tab()
        self._load_profiles_tab()
        self._load_config_file_tab()
        self._load_settings_yml_tab()

        # always show first tab on start
        self._ui.config_tab_widget.tabBar().setCurrentIndex(0)
        self._conan_config_highlighter = ConfigHighlighter(self._ui.config_file_text_browser.document(), "ini")
        self._profile_highlighter = ConfigHighlighter(self._ui.profiles_text_browser.document(), "ini")
        self._settings_highlighter = ConfigHighlighter(self._ui.settings_file_text_browser.document(), "yaml")

    def _load_info_tab(self):
        self._ui.conan_cur_version_value_label.setText(conan_version)
        self._ui.python_exe_value_label.setText(sys.executable)
        self._ui.python_cur_version_value_label.setText(platform.python_version())
        self._ui.revision_enabled_checkbox.setChecked(app.conan_api._client_cache.config.revisions_enabled)
        self._ui.conan_usr_home_value_label.setText(app.conan_api._client_cache.cache_folder)
        self._ui.conan_usr_cache_value_label.setText(str(app.conan_api.get_short_path_root()))
        self._ui.conan_storage_path_value_label.setText(str(app.conan_api._client_cache.store))

    def _load_settings_yml_tab(self):
        try:
            self._ui.settings_file_text_browser.setText(Path(app.conan_api._client_cache.settings_path).read_text())
        except Exception:
            Logger().error("Cannot read settings.yaml file!")

    def _load_config_file_tab(self):
        try:
            self._ui.config_file_text_browser.setText(self.config_file_path.read_text())
            self._ui.config_file_save_button.clicked.connect(self.save_config_file)
        except Exception:
            Logger().error("Cannot read Conan config file!")

    def _init_profiles_tab(self):
        self._ui.profiles_list_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._ui.profiles_list_view.customContextMenuRequested.connect(
            self.on_profile_context_menu_requested)
        self._init_profile_context_menu()
        self._ui.profile_save_button.clicked.connect(self.on_save_profile_file)
        self._ui.profile_add_button.clicked.connect(self.on_add_profile)
        self._ui.profile_remove_button.clicked.connect(self.on_remove_profile)
        self._ui.profile_rename_button.clicked.connect(self.on_rename_profile)
        self._ui.profile_refresh_button.clicked.connect(self.on_refresh_profiles)

        self.set_themed_icon(self._ui.profile_save_button, "icons/save.svg")
        self.set_themed_icon(self._ui.profile_add_button, "icons/plus_rounded.svg")
        self.set_themed_icon(self._ui.profile_remove_button, "icons/delete.svg")
        self.set_themed_icon(self._ui.profile_refresh_button, "icons/refresh.svg")
        self.set_themed_icon(self._ui.profile_rename_button, "icons/rename.svg")
        
    def _load_profiles_tab(self):
        profiles_model = ProfilesModel()
        self._ui.profiles_list_view.setModel(profiles_model)
        self._ui.profiles_list_view.selectionModel().selectionChanged.connect(self.on_profile_selected)

    def _init_profile_context_menu(self):
        self.profiles_cntx_menu = RoundedMenu()
        self._copy_profile_action = QAction("Copy profile name", self)
        self._copy_profile_action.setIcon(QIcon(get_themed_asset_icon("icons/copy_link.svg")))
        self.profiles_cntx_menu.addAction(self._copy_profile_action)
        self._copy_profile_action.triggered.connect(self.on_copy_profile_requested)

    def resizeEvent(self, a0):  # override
        """ Resize remote view columns automatically if window size changes """
        super().resizeEvent(a0)

        self._remotes_controller.resize_remote_columns()
        # self._ui.conan_usr_cache_label.adjustSize()
        # self._ui.revision_enabled_label.setMaximumWidth(self._ui.conan_usr_cache_label.width())

    def reload_themed_icons(self):
        super().reload_themed_icons()
        self._init_profile_context_menu()
        self._init_remote_context_menu()
        self._conan_config_highlighter = ConfigHighlighter(self._ui.config_file_text_browser.document(),"ini")
        self._profile_highlighter = ConfigHighlighter(self._ui.profiles_text_browser.document(),"ini")
        self._settings_highlighter = ConfigHighlighter(self._ui.settings_file_text_browser.document(), "yaml")

# Profile

    def on_copy_profile_requested(self):
        view_indexes = self._ui.profiles_list_view.selectedIndexes()
        if not view_indexes:
            return
        view_index = view_indexes[0]
        profile_name = view_index.data()
        QApplication.clipboard().setText(profile_name)

    def on_profile_selected(self):
        view_indexes = self._ui.profiles_list_view.selectedIndexes()
        if not view_indexes:
            return
        view_index = view_indexes[0]
        profile_name = view_index.data()
        self._edited_profile = profile_name
        try:
            profile_content = (self.profiles_path / profile_name).read_text()
        except Exception:
            profile_content = ""
        self._ui.profiles_text_browser.setText(profile_content)

    def on_profile_context_menu_requested(self, position):
        self.profiles_cntx_menu.exec(self._ui.profiles_list_view.mapToGlobal(position))

    def on_save_profile_file(self):
        if not self._edited_profile:
            return
        profile_name = self._edited_profile
        text = self._ui.profiles_text_browser.toPlainText()
        (self.profiles_path / profile_name).write_text(text)

    def on_add_profile(self):
        new_profile_dialog = QInputDialog(self)
        profile_name, accepted = new_profile_dialog.getText(self, "New profile", 'Enter name:', text="")
        if accepted and profile_name:
            (self.profiles_path / profile_name).touch()
            self.on_refresh_profiles()

    def on_rename_profile(self):
        view_indexes = self._ui.profiles_list_view.selectedIndexes()
        if not view_indexes:
            return
        profile_name: str = view_indexes[0].data(0)
        rename_profile_dialog = QInputDialog(self)
        new_profile_name, accepted = rename_profile_dialog.getText(self, "Rename profile", 'Enter new name:', text=profile_name)
        if accepted and profile_name:
            try:
                (self.profiles_path / profile_name).rename(self.profiles_path / new_profile_name)
            except Exception as e:
                Logger().error(f"Can't rename {profile_name}: {e}")
            self.on_refresh_profiles()

    def on_remove_profile(self):
        view_indexes = self._ui.profiles_list_view.selectedIndexes()
        if not view_indexes:
            return
        profile_name: str = view_indexes[0].data(0)
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Remove profile")
        message_box.setText(f"Are you sure, you want to delete the profile {profile_name}?")
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setIcon(QMessageBox.Icon.Question)
        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            delete_path(self.profiles_path / profile_name)
            self.on_refresh_profiles()

    def on_refresh_profiles(self):
        profile_model: ProfilesModel = self._ui.profiles_list_view.model() # type: ignore
        # clear selection, otherwise an old selection could remain active in the profile content browser
        self._ui.profiles_list_view.selectionModel().clear()
        profile_model.update_profiles()

# Remote

    def _load_remotes_tab(self):
        self._remotes_controller.update()

    def _init_remotes_tab(self):
        self._ui.remote_refresh_button.clicked.connect(self._remotes_controller.update)
        self.set_themed_icon(self._ui.remote_refresh_button, "icons/refresh.svg")
        self._ui.remote_login.clicked.connect(self.on_remotes_login)
        self.set_themed_icon(self._ui.remote_login, "icons/login.svg")
        self._ui.remote_toggle_disabled.clicked.connect(self.on_remote_disable)
        self.set_themed_icon(self._ui.remote_toggle_disabled, "icons/hide.svg")
        self._ui.remote_add.clicked.connect(self.on_remote_add)
        self.set_themed_icon(self._ui.remote_add, "icons/plus_rounded.svg")
        self._ui.remote_remove.clicked.connect(self.on_remote_remove)
        self.set_themed_icon(self._ui.remote_remove, "icons/delete.svg")
        self._ui.remote_move_up_button.clicked.connect(self._remotes_controller.move_up)
        self.set_themed_icon(self._ui.remote_move_up_button, "icons/arrow_up.svg")
        self._ui.remote_move_down_button.clicked.connect(self._remotes_controller.move_down)
        self.set_themed_icon(self._ui.remote_move_down_button, "icons/arrow_down.svg")

        self._ui.remotes_tree_view.doubleClicked.connect(self.on_remote_edit)
        self._ui.remotes_tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._ui.remotes_tree_view.customContextMenuRequested.connect(self.on_remote_context_menu_requested)

        self._init_remote_context_menu()

    def on_remote_context_menu_requested(self, position):
        self._remotes_cntx_menu.exec(self._ui.remotes_tree_view.mapToGlobal(position))

    def _init_remote_context_menu(self):
        self._remotes_cntx_menu = RoundedMenu()
        self._copy_remote_action = QAction("Copy remote name", self)
        self._copy_remote_action.setIcon(QIcon(get_themed_asset_icon("icons/copy_link.svg")))
        self._remotes_cntx_menu.addAction(self._copy_remote_action)
        self._copy_remote_action.triggered.connect(self.on_copy_remote_name_requested)

        self._edit_remote_action = QAction("Edit remote", self)
        self._edit_remote_action.setIcon(QIcon(get_themed_asset_icon("icons/edit.svg")))
        self._remotes_cntx_menu.addAction(self._edit_remote_action)
        self._edit_remote_action.triggered.connect(self.on_remote_edit)

        self._add_remote_action = QAction("Add new remote", self)
        self._add_remote_action.setIcon(QIcon(get_themed_asset_icon("icons/plus_rounded.svg")))
        self._remotes_cntx_menu.addAction(self._add_remote_action)
        self._add_remote_action.triggered.connect(self.on_remote_add)

        self._remove_remote_action = QAction("Remove remote", self)
        self._remove_remote_action.setIcon(QIcon(get_themed_asset_icon("icons/delete.svg")))
        self._remotes_cntx_menu.addAction(self._remove_remote_action)
        self._remove_remote_action.triggered.connect(self.on_remote_remove)

        self._disable_profile_action = QAction("Disable/Enable remote", self)
        self._disable_profile_action.setIcon(QIcon(get_themed_asset_icon("icons/hide.svg")))
        self._remotes_cntx_menu.addAction(self._disable_profile_action)
        self._disable_profile_action.triggered.connect(self.on_remote_disable)

        self._login_remotes_action = QAction("(Multi)Login to remote", self)
        self._login_remotes_action.setIcon(QIcon(get_themed_asset_icon("icons/login.svg")))
        self._remotes_cntx_menu.addAction(self._login_remotes_action)
        self._login_remotes_action.triggered.connect(self.on_remotes_login)

    def on_remote_edit(self, model_index):
        remote_item = self._remotes_controller.get_selected_remote()
        if not remote_item:
            return
        self.remote_edit_dialog = RemoteEditDialog(remote_item.remote, False, self)
        reply = self.remote_edit_dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            self._remotes_controller.update()

    def on_remotes_login(self):
        remote_item = self._remotes_controller.get_selected_remote()
        if not remote_item:
            return
        remotes = self._remotes_controller.get_remotes_from_same_server(remote_item.remote)
        if not remotes:
            return
        self.remote_login_dialog = RemoteLoginDialog(remotes, self)
        reply = self.remote_login_dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            self._remotes_controller.update()

    def on_remote_add(self, model_index):
        new_remote = Remote("New", "", True, False)
        self.remote_edit_dialog = RemoteEditDialog(new_remote, True, self)
        reply = self.remote_edit_dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            self._remotes_controller.update()

    def on_remote_remove(self, model_index):
        remote_item = self._remotes_controller.get_selected_remote()
        if not remote_item:
            return
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Remove remote")
        message_box.setText(f"Are you sure, you want to delete the remote {remote_item.remote.name}?")
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setIcon(QMessageBox.Icon.Question)
        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            # TODO dedicated function
            app.conan_api._conan.remote_remove(remote_item.remote.name)
            self._remotes_controller.update()

    def on_remote_disable(self, model_index):
        self._remotes_controller.remote_disable(model_index)

    def on_copy_remote_name_requested(self):
        self._remotes_controller.copy_remote_name()

# Conan Config

    def save_config_file(self):
        self.config_file_path.write_text(self._ui.config_file_text_browser.toPlainText())
        # restart conan api to apply changes internally
        app.conan_api.init_api()
        Logger().info("Applying Changes to Conan...")
        # re-init info tab to show the changes
        self._load_info_tab()
