import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox, QWidget, QMenu
from typing_extensions import override

import conan_explorer.app as app
from conan_explorer import conan_version
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import delete_path
from conan_explorer.ui.common import ConfigHighlighter, get_themed_asset_icon
from conan_explorer.ui.plugin import PluginDescription, PluginInterfaceV1

from .dialogs import EditableEditDialog, RemoteEditDialog, RemoteLoginDialog
from .editable_controller import ConanEditableController
from .profiles_model import ProfilesModel
from .remotes_controller import ConanRemoteController

if TYPE_CHECKING:
    from conan_explorer.ui.fluent_window.fluent_window import FluentWindow
    from conan_explorer.ui.main_window import BaseSignals

class ConanConfigView(PluginInterfaceV1):

    load_signal = Signal()  # type: ignore

    def __init__(self, parent: QWidget, plugin_description: PluginDescription,
                 base_signals: "BaseSignals", 
                 page_widgets: Optional["FluentWindow.PageStore"] = None):
        super().__init__(parent, plugin_description, base_signals)
        from .conan_conf_ui import Ui_Form
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.load_signal.connect(self.load)
        self.profiles_path = Path("Unknown")
        self._edited_profile = ""

    def load(self):
        assert self._base_signals
        self._remotes_controller = ConanRemoteController(self._ui.remotes_tree_view, 
                                            self._base_signals.conan_remotes_updated)
        self._editable_controller = ConanEditableController(self._ui.editables_ref_view)
        self._init_remotes_tab()
        self._init_profiles_tab()

        self.config_file_path = app.conan_api.get_config_file_path()
        self.profiles_path = app.conan_api.get_profiles_path()
        self._load_info_tab()
        self._load_remotes_tab()
        self._load_profiles_tab()
        self._load_config_file_tab()
        self._load_settings_yml_tab()
        self._load_editables_tab()

        # always show first tab on start
        self._ui.config_tab_widget.tabBar().setCurrentIndex(0)
        self._conan_config_highlighter = ConfigHighlighter(
            self._ui.config_file_text_browser.document(), "ini")
        self._profile_highlighter = ConfigHighlighter(
            self._ui.profiles_text_browser.document(), "ini")
        self._settings_highlighter = ConfigHighlighter(
            self._ui.settings_file_text_browser.document(), "yaml")

    def _load_info_tab(self):
        self._ui.conan_cur_version_value_label.setText(str(conan_version))
        self._ui.python_exe_value_label.setText(str(Path(sys.executable).resolve()))
        self._ui.python_cur_version_value_label.setText(platform.python_version())
        self._ui.revision_enabled_checkbox.setChecked(
                                            app.conan_api.get_revisions_enabled())
        self._ui.conan_usr_home_value_label.setText(
            str(app.conan_api.get_user_home_path().resolve()))
        if conan_version.major == 2:
            self._ui.conan_usr_cache_value_label.setVisible(False)
            self._ui.conan_usr_cache_label.setVisible(False)
        else:
            self._ui.conan_usr_cache_value_label.setText(
                str(app.conan_api.get_short_path_root().resolve()))
        self._ui.conan_storage_path_value_label.setText(
            str(app.conan_api.get_storage_path().resolve()))

    def _load_settings_yml_tab(self):
        try:
            self._ui.settings_file_text_browser.setText(
                app.conan_api.get_settings_file_path().read_text())
        except Exception:
            Logger().error("Cannot read settings.yaml file!")

    @override
    def resizeEvent(self, a0):
        """ Resize remote view columns automatically if window size changes """
        super().resizeEvent(a0)
        self._remotes_controller.resize_remote_columns()

    def reload_themed_icons(self):
        super().reload_themed_icons()
        self._init_profile_context_menu()
        self._init_remote_context_menu()
        self._conan_config_highlighter = ConfigHighlighter(
            self._ui.config_file_text_browser.document(), "ini")
        self._profile_highlighter = ConfigHighlighter(
            self._ui.profiles_text_browser.document(), "ini")
        self._settings_highlighter = ConfigHighlighter(
            self._ui.settings_file_text_browser.document(), "yaml")

# Profile

    def _init_profiles_tab(self):
        self._ui.profiles_list_view.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self._ui.profiles_list_view.customContextMenuRequested.connect(
            self.on_profile_context_menu_requested)
        self._init_profile_context_menu()
        self._ui.profile_save_button.clicked.connect(self.on_profile_save_file)
        self._ui.profile_add_button.clicked.connect(self.on_profile_add)
        self._ui.profile_remove_button.clicked.connect(self.on_profile_remove)
        self._ui.profile_rename_button.clicked.connect(self.on_profile_rename)
        self._ui.profile_refresh_button.clicked.connect(self.on_profiles_refresh)
        self._ui.profiles_copy_name_button.clicked.connect(self.on_copy_profile_requested)

        self.set_themed_icon(self._ui.profile_save_button, "icons/save.svg")
        self.set_themed_icon(self._ui.profile_add_button, "icons/plus_rounded.svg")
        self.set_themed_icon(self._ui.profile_remove_button, "icons/delete.svg")
        self.set_themed_icon(self._ui.profile_refresh_button, "icons/refresh.svg")
        self.set_themed_icon(self._ui.profile_rename_button, "icons/rename.svg")
        self.set_themed_icon(self._ui.profiles_copy_name_button,
                             "icons/copy_to_clipboard.svg")

    def _init_profile_context_menu(self):
        self.profiles_cntx_menu = QMenu()
        self._copy_profile_action = QAction("Copy profile name", self)
        self._copy_profile_action.setIcon(
            QIcon(get_themed_asset_icon("icons/copy_link.svg")))
        self.profiles_cntx_menu.addAction(self._copy_profile_action)
        self._copy_profile_action.triggered.connect(self.on_copy_profile_requested)

    def _load_profiles_tab(self):
        profiles_model = ProfilesModel()
        self._ui.profiles_list_view.setModel(profiles_model)
        self._ui.profiles_list_view.selectionModel().selectionChanged.connect(self.on_profile_selected)

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
        profile_name: str = view_index.data()
        self._edited_profile = profile_name
        try:
            profile_content = (self.profiles_path / profile_name).read_text()
        except Exception:
            profile_content = ""
        self._ui.profiles_text_browser.setText(profile_content)

    def on_profile_context_menu_requested(self, position):
        self.profiles_cntx_menu.exec(self._ui.profiles_list_view.mapToGlobal(position))

    def on_profile_save_file(self):
        if not self._edited_profile:
            return
        profile_name = self._edited_profile
        text = self._ui.profiles_text_browser.toPlainText()
        (self.profiles_path / profile_name).write_text(text)

    def on_profile_add(self):
        new_profile_dialog = QInputDialog(self)
        profile_name, accepted = new_profile_dialog.getText(
            self, "New profile", 'Enter name:', text="")
        if accepted and profile_name:
            (self.profiles_path / profile_name).touch()
            self.on_profiles_refresh()

    def on_profile_rename(self):
        view_indexes = self._ui.profiles_list_view.selectedIndexes()
        if not view_indexes:
            return
        profile_name: str = view_indexes[0].data(0)
        rename_profile_dialog = QInputDialog(self)
        new_profile_name, accepted = rename_profile_dialog.getText(
            self, "Rename profile", 'Enter new name:', text=profile_name)
        if accepted and profile_name:
            try:
                (self.profiles_path / profile_name).rename(
                                                self.profiles_path / new_profile_name)
            except Exception as e:
                Logger().error(f"Can't rename {profile_name}: {e}")
            self.on_profiles_refresh()

    def on_profile_remove(self):
        view_indexes = self._ui.profiles_list_view.selectedIndexes()
        if not view_indexes:
            return
        profile_name: str = view_indexes[0].data(0)
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Remove profile")
        message_box.setText(
            f"Are you sure, you want to delete the profile {profile_name}?")
        message_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setIcon(QMessageBox.Icon.Question)
        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            delete_path(self.profiles_path / profile_name)
            self.on_profiles_refresh()

    def on_profiles_refresh(self):
        profile_model: ProfilesModel = self._ui.profiles_list_view.model() # type: ignore
        # clear selection, otherwise an old selection could remain active
        self._ui.profiles_list_view.selectionModel().clear()
        profile_model.setup_model_data()
        self._ui.profiles_list_view.repaint()

# Remote

    def _load_remotes_tab(self):
        self._remotes_controller.update()

    def _init_remotes_tab(self):
        self._ui.remote_refresh_button.clicked.connect(self._remotes_controller.update)
        self.set_themed_icon(self._ui.remote_refresh_button, "icons/refresh.svg")
        self._ui.remote_login_button.clicked.connect(self.on_remotes_login)
        self.set_themed_icon(self._ui.remote_login_button, "icons/login.svg")
        self._ui.remote_toggle_disabled_button.clicked.connect(
            self._remotes_controller.remote_disable)
        self.set_themed_icon(self._ui.remote_toggle_disabled_button, "icons/hide.svg")
        self._ui.remote_add_button.clicked.connect(self.on_remote_add)
        self.set_themed_icon(self._ui.remote_add_button, "icons/plus_rounded.svg")
        self._ui.remote_remove_button.clicked.connect(self.on_remote_remove)
        self.set_themed_icon(self._ui.remote_remove_button, "icons/delete.svg")

        self._ui.remote_move_up_button.clicked.connect(self._remotes_controller.move_up)
        self.set_themed_icon(self._ui.remote_move_up_button, "icons/arrow_up.svg")
        self._ui.remote_move_down_button.clicked.connect(
            self._remotes_controller.move_down)
        self.set_themed_icon(self._ui.remote_move_down_button, "icons/arrow_down.svg")

        self._ui.remote_move_top_button.clicked.connect(
            self._remotes_controller.move_to_top)
        self.set_themed_icon(self._ui.remote_move_top_button, "icons/expand_less.svg")
        self._ui.remote_move_bottom_button.clicked.connect(
            self._remotes_controller.move_to_bottom)
        self.set_themed_icon(self._ui.remote_move_bottom_button, "icons/expand.svg")

        self._ui.remotes_edit_button.clicked.connect(self.on_remote_edit)
        self.set_themed_icon(self._ui.remotes_edit_button, "icons/edit.svg")
        self._ui.remotes_tree_view.doubleClicked.connect(self.on_remote_edit)

        self._ui.remotes_tree_view.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self._ui.remotes_tree_view.customContextMenuRequested.connect(
            self.on_remote_context_menu_requested)
        self._init_remote_context_menu()

    def on_remote_context_menu_requested(self, position):
        self._remotes_cntx_menu.exec(self._ui.remotes_tree_view.mapToGlobal(position))

    def _init_remote_context_menu(self):
        self._remotes_cntx_menu = QMenu()
        self._copy_remote_action = QAction("Copy remote name", self)
        self._copy_remote_action.setIcon(
            QIcon(get_themed_asset_icon("icons/copy_link.svg")))
        self._remotes_cntx_menu.addAction(self._copy_remote_action)
        self._copy_remote_action.triggered.connect(self._remotes_controller.copy_remote_name)

        self._edit_remote_action = QAction("Edit remote", self)
        self._edit_remote_action.setIcon(QIcon(get_themed_asset_icon("icons/edit.svg")))
        self._remotes_cntx_menu.addAction(self._edit_remote_action)
        self._edit_remote_action.triggered.connect(self.on_remote_edit)

        self._add_remote_action = QAction("Add new remote", self)
        self._add_remote_action.setIcon(
            QIcon(get_themed_asset_icon("icons/plus_rounded.svg")))
        self._remotes_cntx_menu.addAction(self._add_remote_action)
        self._add_remote_action.triggered.connect(self.on_remote_add)

        self._remove_remote_action = QAction("Remove remote", self)
        self._remove_remote_action.setIcon(
            QIcon(get_themed_asset_icon("icons/delete.svg")))
        self._remotes_cntx_menu.addAction(self._remove_remote_action)
        self._remove_remote_action.triggered.connect(self.on_remote_remove)

        self._disable_profile_action = QAction("Disable/Enable remote", self)
        self._disable_profile_action.setIcon(
            QIcon(get_themed_asset_icon("icons/hide.svg")))
        self._remotes_cntx_menu.addAction(self._disable_profile_action)
        self._disable_profile_action.triggered.connect(
            self._remotes_controller.remote_disable)

        self._login_remotes_action = QAction("(Multi)Login to remote", self)
        self._login_remotes_action.setIcon(
            QIcon(get_themed_asset_icon("icons/login.svg")))
        self._remotes_cntx_menu.addAction(self._login_remotes_action)
        self._login_remotes_action.triggered.connect(self.on_remotes_login)

    def on_remote_edit(self, model_index):
        remote_item = self._remotes_controller.get_selected_remote()
        if not remote_item:
            return
        self.remote_edit_dialog = RemoteEditDialog(remote_item, self._remotes_controller, self)
        self.remote_edit_dialog.exec()

    def on_remotes_login(self):
        remote_item = self._remotes_controller.get_selected_remote()
        if not remote_item:
            return
        remotes = app.conan_api.get_remotes_from_same_server(remote_item)
        if not remotes:
            return
        self.remote_login_dialog = RemoteLoginDialog(remotes, self._remotes_controller, self)
        self.remote_login_dialog.exec()

    def on_remote_add(self, model_index):
        self.remote_edit_dialog = RemoteEditDialog(None, self._remotes_controller, self)
        self.remote_edit_dialog.exec()

    def on_remote_remove(self, model_index):
        remote_item = self._remotes_controller.get_selected_remote()
        if not remote_item:
            return
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Remove remote")
        message_box.setText(
            f"Are you sure, you want to delete the remote {remote_item.name}?")
        message_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setIcon(QMessageBox.Icon.Question)
        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            self._remotes_controller.remove(remote_item)

# Editables tab

    def _load_editables_tab(self):
        self._ui.editables_add_button.clicked.connect(self.on_editable_add)
        self._ui.editables_remove_button.clicked.connect(self.on_editable_remove)
        self._ui.editables_refresh_button.clicked.connect(self._editable_controller.update)
        self._ui.editables_edit_button.clicked.connect(self.on_editable_edit)
        self._ui.editables_ref_view.doubleClicked.connect(self.on_editable_edit)

        self.set_themed_icon(self._ui.editables_add_button, "icons/plus_rounded.svg")
        self.set_themed_icon(self._ui.editables_remove_button, "icons/delete.svg")
        self.set_themed_icon(self._ui.editables_refresh_button, "icons/refresh.svg")
        self.set_themed_icon(self._ui.editables_edit_button, "icons/edit.svg")

    def on_editable_add(self, model_index):
        self.remote_edit_dialog = EditableEditDialog(None, self._editable_controller, self)
        self.remote_edit_dialog.exec()

    def on_editable_edit(self, model_index):
        editable = self._editable_controller.get_selected_editable()
        if not editable:
            return
        self.remote_edit_dialog = EditableEditDialog(
            editable, self._editable_controller, self)
        self.remote_edit_dialog.exec()

    def on_editable_remove(self, model_index):
        editable_item = self._editable_controller.get_selected_editable()
        if not editable_item:
            return
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Remove editable")
        message_box.setText("Are you sure, you want to delete the editable" +
                             f"{editable_item.conan_ref}?")
        standard_button = QMessageBox.StandardButton
        message_box.setStandardButtons(standard_button.Yes | standard_button.No)
        message_box.setIcon(QMessageBox.Icon.Question)
        reply = message_box.exec()
        if reply == standard_button.Yes:
            self._editable_controller.remove(editable_item)

# Conan Config

    def _load_config_file_tab(self):
        self.set_themed_icon(self._ui.config_file_save_button, "icons/save.svg")
        try:
            self._ui.config_file_text_browser.setText(
                app.conan_api.get_config_file_path().read_text())
            self._ui.config_file_save_button.clicked.connect(self.on_save_config_file)
        except Exception:
            Logger().error("Cannot read Conan config file!")

    def on_save_config_file(self):
        app.conan_api.get_config_file_path().write_text(
            self._ui.config_file_text_browser.toPlainText())
        # restart conan api to apply changes internally
        app.conan_api.init_api()
        Logger().info("Applying Changes to Conan...")
        # re-init info tab to show the changes
        self._load_info_tab()
