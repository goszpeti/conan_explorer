
from typing import TYPE_CHECKING
from pathlib import Path
import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher import INVALID_CONAN_REF, asset_path
from conan_app_launcher.logger import Logger
from conan_app_launcher.components import (
    open_in_file_manager, run_file)
from conan_app_launcher.settings import DISPLAY_APP_CHANNELS, DISPLAY_APP_USERS, DISPLAY_APP_VERSIONS
from conan_app_launcher.ui.modules.app_grid.model import UiAppLinkModel
from .common.app_button import AppButton
from .common.app_edit_dialog import EditAppDialog
from .common.move_dialog import MoveAppLinksDialog

from PyQt5 import QtCore, QtGui, QtWidgets

if TYPE_CHECKING:
    from.tab import TabGrid


# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt

OFFICIAL_RELEASE_DISP_NAME = "<official release>"
OFFICIAL_USER_DISP_NAME = "<official user>"

current_dir = Path(__file__).parent


class AppLink(QtWidgets.QVBoxLayout):
    MAX_WIDTH = 190

    def __init__(self, parent: "TabGrid", model: UiAppLinkModel):
        super().__init__()
        self._parent_tab = parent  # save parent - don't use qt signals ands slots
        self.model = model
        self._lock_cboxes = False
        self._init_app_link()

    def _init_app_link(self):
        self._app_name_label = QtWidgets.QLabel(self._parent_tab)
        self._app_version_cbox = QtWidgets.QComboBox(self._parent_tab)
        self._app_user_cbox = QtWidgets.QComboBox(self._parent_tab)
        self._app_channel_cbox = QtWidgets.QComboBox(self._parent_tab)
        self._app_button = AppButton(self._parent_tab, asset_path / "icons" / "app.png")

        # size policies
        self.setSpacing(3)
        self.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                            QtWidgets.QSizePolicy.Fixed)
        # add sub widgets

        self._app_button.setSizePolicy(size_policy)
        self._app_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self._app_button.customContextMenuRequested.connect(self.on_context_menu_requested)
        self.addWidget(self._app_button)

        self._app_name_label.setAlignment(Qt.AlignCenter)
        self._app_name_label.setSizePolicy(size_policy)
        self._app_name_label.setText(self.model.name)
        self.addWidget(self._app_name_label)

        self._app_version_cbox.setDisabled(True)
        self._app_version_cbox.setDuplicatesEnabled(False)
        self._app_version_cbox.setSizePolicy(size_policy)
        self._app_version_cbox.setMaximumWidth(self.MAX_WIDTH)
        self.addWidget(self._app_version_cbox)

        self._app_user_cbox.setDisabled(True)
        self._app_user_cbox.setDuplicatesEnabled(False)
        self._app_user_cbox.setSizePolicy(size_policy)
        self._app_user_cbox.setMaximumWidth(self.MAX_WIDTH)
        self.addWidget(self._app_user_cbox)

        self._app_channel_cbox.setDisabled(True)
        self._app_channel_cbox.setDuplicatesEnabled(False)
        self._app_channel_cbox.setSizePolicy(size_policy)
        self._app_channel_cbox.setMaximumWidth(self.MAX_WIDTH)
        self.addWidget(self._app_channel_cbox)

        self._v_spacer = QtWidgets.QSpacerItem(
            20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.addSpacerItem(self._v_spacer)

        # connect signals
        self._app_button.clicked.connect(self.on_click)
        self._app_version_cbox.currentIndexChanged.connect(self.on_ref_cbox_selected)
        self._app_user_cbox.currentIndexChanged.connect(self.on_ref_cbox_selected)
        self._app_channel_cbox.currentIndexChanged.connect(self.on_ref_cbox_selected)

        self._init_menu()

    def load(self):
        self.model.register_update_callback(self.update_with_conan_info)
        self._apply_new_config()
        self.update_with_conan_info()

    def _init_menu(self):
        self.menu = QtWidgets.QMenu()
        icons_path = asset_path / "icons"

        self.open_fm_action = QtWidgets.QAction("Show in File Manager", self)
        self.open_fm_action.setIcon(QtGui.QIcon(str(icons_path / "file-explorer.png")))
        self.menu.addAction(self.open_fm_action)
        self.open_fm_action.triggered.connect(self.on_open_in_file_manager)

        self.show_in_pkg_exp_action = QtWidgets.QAction("Show in Package Explorer", self)
        self.show_in_pkg_exp_action.setIcon(QtGui.QIcon(str(icons_path / "search_packages.png")))
        self.menu.addAction(self.show_in_pkg_exp_action)
        self.show_in_pkg_exp_action.setDisabled(True)  # TODO upcoming feature

        self.menu.addSeparator()

        self.add_action = QtWidgets.QAction("Add new App Link", self)
        self.add_action.setIcon(QtGui.QIcon(str(icons_path / "add_link.png")))
        self.menu.addAction(self.add_action)
        self.add_action.triggered.connect(self.open_app_link_add_dialog)

        self.edit_action = QtWidgets.QAction("Edit", self)
        self.edit_action.setIcon(QtGui.QIcon(str(icons_path / "edit.png")))
        self.menu.addAction(self.edit_action)
        self.edit_action.triggered.connect(self.open_edit_dialog)

        self.remove_action = QtWidgets.QAction("Remove App Link", self)
        self.remove_action.setIcon(QtGui.QIcon(str(icons_path / "delete.png")))
        self.menu.addAction(self.remove_action)
        self.remove_action.triggered.connect(self.remove)

        self.menu.addSeparator()

        self.rearrange_action = QtWidgets.QAction("Rearrange App Links", self)
        self.rearrange_action.setIcon(QtGui.QIcon(str(icons_path / "rearrange.png")))
        self.rearrange_action.triggered.connect(self.on_move)

        self.menu.addAction(self.rearrange_action)

    def on_move(self):
        move_dialog = MoveAppLinksDialog(parent=self.parentWidget(), tab_ui_model=self.model.parent)
        ret = move_dialog.exec()
        if ret == QtWidgets.QDialog.Accepted:
            move_dialog.save()
            self._parent_tab.remove_all_app_links()
            self._parent_tab.load_apps_from_model()

    def delete(self):
        self._app_name_label.hide()
        self._app_version_cbox.hide()
        self._app_user_cbox.hide()
        self._app_channel_cbox.hide()
        self._app_button.hide()

    def on_context_menu_requested(self, position):
        self.menu.exec_(self._app_button.mapToGlobal(position))

    def on_open_in_file_manager(self):
        open_in_file_manager(self.model.get_executable_path().parent)

    def _apply_new_config(self):
        self._app_name_label.setText(self.model.name)
        self._app_button.setToolTip(self.model.conan_ref)
        self._app_button.set_icon(self.model.get_icon())

        self._lock_cboxes = True
        self._app_channel_cbox.clear()
        self._app_channel_cbox.addItem(self.model.channel)
        self._app_version_cbox.clear()
        self._app_version_cbox.addItem(self.model.version)
        self._app_user_cbox.clear()
        self._app_user_cbox.addItem(self.model.user)
        self._lock_cboxes = False

        self.update_versions_cbox_visible()
        self.update_users_cbox_visible()
        self.update_channels_cbox_visible()

    def open_app_link_add_dialog(self):
        self._parent_tab.open_app_link_add_dialog()

    def open_edit_dialog(self, model: UiAppLinkModel = None):
        if model:
            self.model = model
        edit_app_dialog = EditAppDialog(self.model, parent=self.parentWidget())
        reply = edit_app_dialog.exec_()
        if reply == EditAppDialog.Accepted:
            edit_app_dialog.save_data()
            # grey icon, so update from cache can ungrey it, if the path is correct
            self._app_button.grey_icon()
            self.model.update_from_cache()
            # now apply gui config with resolved paths
            self._apply_new_config()
        del edit_app_dialog # call delete manually for faster thread cleanup

    def remove(self):
        # last link can't be deleted!
        if len(self.model.parent.apps) == 1:
            msg = QtWidgets.QMessageBox(parent=self._parent_tab)
            msg.setWindowTitle("Info")
            msg.setText("Can't delete the last link!")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.exec_()
            return

        # confirmation dialog
        message_box = QtWidgets.QMessageBox(parent=self.parentWidget())
        message_box.setWindowTitle("Delete app link")
        message_box.setText(f"Are you sure, you want to delete the link \"{self.model.name}?\"")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setIcon(QtWidgets.QMessageBox.Question)
        reply = message_box.exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            self.delete()
            self.model.parent.apps.remove(self.model)
            self.model.save()

    def update_with_conan_info(self):
        if self._lock_cboxes == True:
            return
        if self._app_channel_cbox.itemText(0) != self.model.INVALID_DESCR and \
                len(self.model.versions) > 1 and self._app_version_cbox.count() < len(self.model.versions) or \
                len(self.model.channels) > 1 and self._app_channel_cbox.count() < len(self.model.channels):
            # signals the cbox callback that we do not set new user values
            self._lock_cboxes = True
            self._app_version_cbox.clear()
            self._app_user_cbox.clear()
            self._app_channel_cbox.clear()

            self._app_version_cbox.addItems(self.model.versions)
            self._app_user_cbox.addItems(self.model.users)
            self._app_channel_cbox.addItems(self.model.channels)
            try:  # try to set updated values
                self._app_version_cbox.setCurrentIndex(
                    self.model.versions.index(self.model.version))
                self._app_user_cbox.setCurrentIndex(
                    self.model.users.index(self.model.user))
                self._app_channel_cbox.setCurrentIndex(
                    self.model.channels.index(self.model.channel))
            except Exception:
                pass
            # on first show
            self._app_version_cbox.setEnabled(True)
            self._app_user_cbox.setEnabled(True)
            self._app_channel_cbox.setEnabled(True)

            self._lock_cboxes = False

        # add tooltip for channels, in case it is too long
        for i in range(0, len(self.model.channels)):
            self._app_channel_cbox.setItemData(i, self.model.channels[i], Qt.ToolTipRole)
        self.update_icon()

    def update_icon(self):
        if self.model.get_executable_path().is_file():
            self._app_button.set_icon(self.model.get_icon())
            self._app_button.ungrey_icon()

    def update_versions_cbox_visible(self):
        if app.active_settings.get(DISPLAY_APP_VERSIONS):
            self._app_version_cbox.show()
        else:
            self._app_version_cbox.hide()

    def update_users_cbox_visible(self):
        if app.active_settings.get(DISPLAY_APP_USERS):
            self._app_user_cbox.show()
        else:
            self._app_user_cbox.hide()

    def update_channels_cbox_visible(self):
        if app.active_settings.get(DISPLAY_APP_CHANNELS):
            self._app_channel_cbox.show()
        else:
            self._app_channel_cbox.hide()

    def on_click(self):
        """ Callback for opening the executable on click """
        if not self.model.get_executable_path().is_file():
            Logger().error(
                f"Can't find file in package {self.model.conan_ref}:\n    {str(self.model.get_executable_path())}")
        run_file(self.model.get_executable_path(), self.model.is_console_application, self.model.args)

    def on_ref_cbox_selected(self, index: int):
        if self._lock_cboxes:
            return
        if index == -1:  # on clear
            return
        self._lock_cboxes = True
        re_eval_channel = False
        self._app_button.grey_icon()
        if self.model.version != self._app_version_cbox.currentText():
            self.model.lock_changes = True
            self.model.version = self._app_version_cbox.currentText()
            self.model.user = self.model.INVALID_DESCR  # invalidate, must be evaluated again for new version
        if self.model.user != self._app_user_cbox.currentText():
            self.model.lock_changes = True
            if self.model.user == self.model.INVALID_DESCR:
                self.model.update_from_cache()
                # update user to match version
                self._app_user_cbox.clear()  # reset cbox
                users = self.model.users
                if not users:
                    users = self.model.INVALID_DESCR
                self._app_user_cbox.addItems(users)
            re_eval_channel = True  # re-eval channel. can't use INVALID_DESCR, since it is also a valid user choice
            self.model.user = self._app_user_cbox.currentText()
        if self.model.channel != self._app_channel_cbox.currentText() or re_eval_channel:
            self.model.lock_changes = True
            if re_eval_channel:
                self.model.channel = self.model.INVALID_DESCR  # eval for channels
                # update channels to match version
                self._app_channel_cbox.clear()  # reset cbox
                self._app_channel_cbox.addItems(self.model.channels)
                # add tooltip for channels, in case it is too long
                for i in range(0, len(self.model.channels)):
                    self._app_channel_cbox.setItemData(i+1, self.model.channels[i], Qt.ToolTipRole)
                self._app_channel_cbox.setCurrentIndex(0)
            else:
                # remove entry NA after setting something other - NA should always have index 0
                if self._app_channel_cbox.itemText(0) == self.model.INVALID_DESCR:
                    self._app_channel_cbox.removeItem(0)
                # normal switch
                self.model.lock_changes = False
                self.model.channel = self._app_channel_cbox.currentText()
                self._app_button.setToolTip(self.model.conan_ref)
                self._app_button.set_icon(self.model.get_icon())
                # self.model.trigger_conan_update()
                self._app_button.setToolTip(self.model.conan_ref)
        self.update_icon()
        self.model.save()
        self.model.lock_changes = False
        self._lock_cboxes = False
