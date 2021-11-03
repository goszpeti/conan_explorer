
from conan_app_launcher.app import asset_path, active_settings
from conan_app_launcher.logger import Logger
from conan_app_launcher.components import (
                                           open_in_file_manager, run_file)
from conan_app_launcher.settings import DISPLAY_APP_CHANNELS, DISPLAY_APP_USERS, DISPLAY_APP_VERSIONS
from conan_app_launcher.ui.modules.app_grid.model import UiAppLinkModel
from conan_app_launcher.ui.data import UiAppLinkConfig
from .common.app_button import AppButton
from .common.app_edit_dialog import EditAppDialog
from PyQt5 import QtCore, QtGui, QtWidgets


# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt

OFFICIAL_RELEASE_DISP_NAME = "<official release>"
OFFICIAL_USER_DISP_NAME = "<official user>"


class AppLink(QtWidgets.QVBoxLayout):
    MAX_WIDTH = 193

    def __init__(self, parent: QtWidgets.QWidget, model: UiAppLinkModel):
        super().__init__()
        self._parent_tab = parent # save parent - don't use qt signals ands slots
        self.model = model
        self._init_app_link()


    def _init_app_link(self):
        self._app_name_label = QtWidgets.QLabel(self._parent_tab)
        self._app_version_cbox = QtWidgets.QComboBox(self._parent_tab)
        self._app_user_cbox = QtWidgets.QComboBox(self._parent_tab)
        self._app_channel_cbox = QtWidgets.QComboBox(self._parent_tab)
        self._app_button = AppButton(self._parent_tab)

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
        # if main_window:
        #     main_window.display_versions_changed.connect(self.update_versions_cbox)
        #     main_window.display_users_changed.connect(self.update_users_cbox)
        #     main_window.display_channels_changed.connect(self.update_channels_cbox)
        self._app_button.clicked.connect(self.on_click)
        self._app_version_cbox.currentIndexChanged.connect(self.on_version_selected)
        self._app_user_cbox.currentIndexChanged.connect(self.on_user_selected)
        self._app_channel_cbox.currentIndexChanged.connect(self.on_channel_selected)

        self._init_menu()
        #self.setObjectName("applink_" + self.model.name)


    def load(self):
        #self.model.load(ui_config, model_parent)
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

        self.move_r = QtWidgets.QAction("Move Right", self)
        self.move_r.setDisabled(True)  # TODO upcomng feature
        self.menu.addAction(self.move_r)

        self.move_l = QtWidgets.QAction("Move Left", self)
        self.move_l.setDisabled(True)  # TODO upcoming feature
        self.menu.addAction(self.move_l)

    def delete(self):
        self._app_name_label.hide()
        self._app_version_cbox.hide()
        self._app_channel_cbox.hide()
        self._app_button.hide()

    def on_context_menu_requested(self, position):
        self.menu.exec_(self._app_button.mapToGlobal(position))

    def on_open_in_file_manager(self):
        open_in_file_manager(self.model.get_executable_path().parent)

    def _apply_new_config(self):
        self._app_name_label.setText(self.model.name)
        self._app_button.setToolTip(str(self.model.conan_ref))
        self._app_button.set_icon(self.model.get_icon_path())

        self._app_channel_cbox.clear()
        self._app_channel_cbox.addItem(self.model.channel)
        self._app_version_cbox.clear()
        self._app_version_cbox.addItem(self.model.version)
        self._app_user_cbox.clear()
        self._app_user_cbox.addItem(self.model.user)
        self.update_versions_cbox()
        self.update_users_cbox()
        self.update_channels_cbox()


    def open_edit_dialog(self, model: UiAppLinkModel=None):
        if model:
            self.model = model
        self._edit_app_dialog = EditAppDialog(self.model, parent=self.parentWidget())
        reply = self._edit_app_dialog.exec_()
        if reply == EditAppDialog.Accepted:
            self._edit_app_dialog.save_data()
            self._apply_new_config()
            self._app_button.grey_icon()
            self.model.update_from_cache()

    def open_app_link_add_dialog(self, new_config = None):
        if not new_config:
            new_config = UiAppLinkConfig()
        # save for testing
        self._edit_app_dialog = EditAppDialog(new_config, parent=self.parentWidget())
        reply = self._edit_app_dialog.exec_()
        if reply == EditAppDialog.Accepted:
            self._edit_app_dialog.save_data()
            app_link = AppLink(self._parent_tab).load(new_config, self.model.parent)
            if self.model.parent:
                self.model.parent.apps.append(new_config)
            self._parent_tab.add_app_link_to_tab(app_link)
            self.model.save() # TODO this should happen on apps.append
            return app_link  # for testing
        return None

    def remove(self):
        # confirmation dialog
        message_box = QtWidgets.QMessageBox(parent=self.parentWidget())
        message_box.setWindowTitle("Delete app link")
        message_box.setText(f"Are you sure, you want to delete the link \"{self.model.name}?\"")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setIcon(QtWidgets.QMessageBox.Question)
        reply = message_box.exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            self.delete()
            self._parent_tab.remove_app_link_from_tab(self)
            self.model.save()

    def update_with_conan_info(self):
        if self._app_channel_cbox.itemText(0) != self.model.INVALID_DESCR and \
            len(self.model.versions) > 1 and self._app_version_cbox.count() != len(self.model.versions) or \
                    len(self.model.channels) > 1 and self._app_channel_cbox.count() != len(self.model.channels):
                # signals the cbox callback that we do not set new user values
                self._app_version_cbox.setDisabled(True)
                self._app_user_cbox.setDisabled(True)
                self._app_channel_cbox.setDisabled(True)
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
                self._app_version_cbox.setEnabled(True)
                self._app_user_cbox.setEnabled(True)
                self._app_channel_cbox.setEnabled(True)

        # add tooltip for channels, in case it is too long
        for i in range(0, len(self.model.channels)):
            self._app_channel_cbox.setItemData(i, self.model.channels[i], Qt.ToolTipRole)
        if self.model.get_executable_path().is_file():
            Logger().debug(f"Ungreying {str(self.model.__dict__)}")
            self._app_button.set_icon(self.model.get_icon_path())
            self._app_button.ungrey_icon()

    def update_versions_cbox(self):
        if active_settings and active_settings.get(DISPLAY_APP_VERSIONS):
            self._app_version_cbox.show()
        else:
            self._app_version_cbox.hide()


    def update_users_cbox(self):
        if active_settings and active_settings.get(DISPLAY_APP_USERS):
            self._app_user_cbox.show()
        else:
            self._app_user_cbox.hide()

    def update_channels_cbox(self):
        if active_settings and active_settings.get(DISPLAY_APP_CHANNELS):
            self._app_channel_cbox.show()
        else:
            self._app_channel_cbox.hide()

    def on_click(self):
        """ Callback for opening the executable on click """
        run_file(self.model.get_executable_path(), self.model.is_console_application, self.model.args)

    def on_version_selected(self, index):
        if not self._app_version_cbox.isEnabled():
            return
        if index == -1:  # on clear
            return
        if self.model.version == self._app_version_cbox.currentText():  # no change
            return
        self._app_button.grey_icon()
        self.model.version = self._app_version_cbox.currentText()

        # update channels to match version
        self._app_channel_cbox.clear()  # reset cbox
        if len(self.model.channels) == 1:
            self._app_channel_cbox.addItems(self.model.channels)
        else:
            self._app_channel_cbox.addItems([self.model.INVALID_DESCR] + self.model.channels)
            self.model.channel = self.model.INVALID_DESCR
            # add tooltip for channels, in case it is too long
            for i in range(0, len(self.model.channels)):
                self._app_channel_cbox.setItemData(i+1, self.model.channels[i], Qt.ToolTipRole)

        self._app_channel_cbox.setCurrentIndex(0)
        self._app_button.setToolTip(str(self.model.conan_ref))
        # if main_window:
        #     main_window.save_config()

    def on_user_selected(self, index):
        """ This is callback is also called on cbox_add_items, so a workaround is needed"""

        if not self._app_user_cbox.isEnabled():
            return
        if index == -1:
            return
        if self.model.user == self._app_user_cbox.currentText():
            return
        #self._app_channel_cbox.setDisabled(True)
        self._app_button.grey_icon()
        self.model.user = self._app_user_cbox.currentText()

        # update channels to match version
        self._app_channel_cbox.clear()  # reset cbox
        if len(self.model.channels) == 1:
            self._app_channel_cbox.addItems(self.model.channels)
        else:
            self._app_channel_cbox.addItems([self.model.INVALID_DESCR] + self.model.channels)
            self.model.channel = self.model.INVALID_DESCR
            # add tooltip for channels, in case it is too long
            for i in range(0, len(self.model.channels)):
                self._app_channel_cbox.setItemData(i+1, self.model.channels[i], Qt.ToolTipRole)

        self._app_channel_cbox.setCurrentIndex(0)
        self._app_button.setToolTip(str(self.model.conan_ref))
        self.model.save()

    def on_channel_selected(self, index):
        """ This is callback is also called on cbox_add_items, so a workaround is needed"""

        if not self._app_channel_cbox.isEnabled():
            return
        if index == -1:
            return
        if self.model.channel == self._app_channel_cbox.currentText():
            return
        self._app_button.grey_icon()
        # remove entry NA after setting something other
        if index != 0 and self._app_channel_cbox.itemText(0) == self.model.INVALID_DESCR:
           self._app_channel_cbox.removeItem(0)
        self.model.channel = self._app_channel_cbox.currentText()
        self._app_button.setToolTip(str(self.model.conan_ref))
        self._app_button.set_icon(self.model.get_icon_path())
        self.model.save()
