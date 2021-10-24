
import conan_app_launcher as this
from conan_app_launcher.components import (AppConfigEntry,
                                           open_in_file_manager, run_file)
from conan_app_launcher.ui.app_grid.app_button import AppButton
from conan_app_launcher.ui.app_grid.app_edit_dialog import EditAppDialog
from PyQt5 import QtCore, QtGui, QtWidgets

# from conan_app_launcher.ui.tab_app_grid import TabAppGrid


# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt

OFFICIAL_RELEASE_DISP_NAME = "<official release>"
OFFICIAL_USER_DISP_NAME = "<official user>"


class AppLink(QtWidgets.QVBoxLayout):

    def __init__(self, parent: QtWidgets.QWidget, app_config: AppConfigEntry):
        super().__init__(parent)
        self.parent_tab = parent # save parent - don't use qt signals ands solts
        self.config_data = app_config
        self.config_data.register_update_callback(self.update_with_conan_info)

        self.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)

        self._app_name_label = QtWidgets.QLabel(parent)
        self._app_version_cbox = QtWidgets.QComboBox(parent)
        self._app_channel_cbox = QtWidgets.QComboBox(parent)
        self._app_button = AppButton(parent)

        # size policies
        self.setSpacing(3)
        self.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                            QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self._app_button.setSizePolicy(size_policy)
        self._app_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self._app_button.customContextMenuRequested.connect(self.on_context_menu_requested)

        # add sub widgets
        self.addWidget(self._app_button)
        self._app_name_label.setAlignment(Qt.AlignCenter)
        self._app_name_label.setSizePolicy(size_policy)
        self._app_name_label.setText(app_config.name)

        self.addWidget(self._app_name_label)

        self._app_version_cbox.setDisabled(True)
        self._app_version_cbox.setDuplicatesEnabled(False)
        self._app_version_cbox.setSizePolicy(size_policy)
        self._app_version_cbox.setMaximumWidth(193)  # TODO should be used from a const

        self.addWidget(self._app_version_cbox)

        self._app_channel_cbox.setDisabled(True)
        self._app_channel_cbox.setDuplicatesEnabled(False)
        self._app_channel_cbox.setSizePolicy(size_policy)
        self._app_channel_cbox.setMaximumWidth(193)  # TODO should be used from a const

        self.addWidget(self._app_channel_cbox)

        # connect signals
        if this.main_window:
            this.main_window.display_versions_updated.connect(self.update_versions_cbox)
            this.main_window.display_channels_updated.connect(self.update_channels_cbox)
        self._app_button.clicked.connect(self.on_click)
        self._app_version_cbox.currentIndexChanged.connect(self.on_version_selected)
        self._app_channel_cbox.currentIndexChanged.connect(self.on_channel_selected)

        self._init_menu()
        self._apply_new_config()
        self.update_with_conan_info()

    def _init_menu(self):
        self.menu = QtWidgets.QMenu()
        icons_path = this.asset_path / "icons"

        self.open_fm_action = QtWidgets.QAction("Show in file manager", self)
        self.open_fm_action.setIcon(QtGui.QIcon(str(icons_path / "file-explorer.png")))
        self.menu.addAction(self.open_fm_action)
        self.open_fm_action.triggered.connect(self.on_open_in_file_manager)

        self.show_in_pkg_exp_action = QtWidgets.QAction("Show in Package Explorer", self)
        self.show_in_pkg_exp_action.setIcon(QtGui.QIcon(str(icons_path / "search_packages.png")))
        self.menu.addAction(self.show_in_pkg_exp_action)
        self.show_in_pkg_exp_action.setDisabled(True)  # TODO upcoming feature

        self.menu.addSeparator()

        self.add_action = QtWidgets.QAction("Add new app link", self)
        self.add_action.setIcon(QtGui.QIcon(str(icons_path / "add_link.png")))
        self.menu.addAction(self.add_action)
        self.add_action.triggered.connect(self.open_app_link_add_dialog)

        self.edit_action = QtWidgets.QAction("Edit", self)
        self.edit_action.setIcon(QtGui.QIcon(str(icons_path / "edit.png")))
        self.menu.addAction(self.edit_action)
        self.edit_action.triggered.connect(self.open_edit_dialog)

        self.remove_action = QtWidgets.QAction("Remove app link", self)
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
        self._app_name_label.deleteLater()
        self._app_version_cbox.hide()
        self._app_version_cbox.deleteLater()
        self._app_channel_cbox.hide()
        self._app_channel_cbox.deleteLater()
        self._app_button.hide()
        self._app_button.deleteLater()

    def on_context_menu_requested(self, position):
        self.menu.exec_(self._app_button.mapToGlobal(position))

    def on_open_in_file_manager(self):
        open_in_file_manager(self.config_data.executable.parent)

    def _apply_new_config(self):
        self._app_name_label.setText(self.config_data.name)
        self._app_button.setToolTip(str(self.config_data.conan_ref))
        self._app_button.set_icon(self.config_data.icon)

        self._app_channel_cbox.clear()
        channel = self.config_data.conan_ref.channel
        if not channel:
            channel = AppConfigEntry.OFFICIAL_RELEASE
        self._app_channel_cbox.addItem(channel)
        self._app_version_cbox.clear()
        self._app_version_cbox.addItem(self.config_data.conan_ref.version)

    def open_edit_dialog(self, config_data: AppConfigEntry = None):
        if config_data:
            self.config_data = config_data
        self._edit_app_dialog = EditAppDialog(self.config_data, parent=self.parentWidget())
        reply = self._edit_app_dialog.exec_()
        if reply == EditAppDialog.Accepted:
            self._edit_app_dialog.save_data()
            self._apply_new_config()
            self._app_button.grey_icon()
            if this.main_window:
                this.main_window.save_config()

    def open_app_link_add_dialog(self, config_data: AppConfigEntry = None):
        if not config_data:
            config_data = AppConfigEntry()
        # TODO save for testing
        self._edit_app_dialog = EditAppDialog(config_data, parent=self.parentWidget())
        reply = self._edit_app_dialog.exec_()
        if reply == EditAppDialog.Accepted:
            self._edit_app_dialog.save_data()
            config_data.update_from_cache() # instantly use local paths and pkgs
            app_link = AppLink(self.parent_tab, config_data)
            self.parent_tab.add_app_link_to_tab(app_link)
            if this.main_window:
                this.main_window.save_config()
            return app_link  # for testing
        return None

    def remove(self):
        # confirmation dialog
        message_box = QtWidgets.QMessageBox(parent=this.main_window)
        message_box.setWindowTitle("Delete app link")
        message_box.setText(f"Are you sure, you want to delete the link \"{self.config_data.name}?\"")
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message_box.setIcon(QtWidgets.QMessageBox.Question)
        reply = message_box.exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            self.delete()
            self.parent_tab.remove_app_link_from_tab(self)
            if this.main_window:
                this.main_window.save_config()

    def update_with_conan_info(self):
        # on changed values
        if len(self.config_data.versions) > 1 and self._app_version_cbox.count() != len(self.config_data.versions) or \
                len(self.config_data.channels) > 1 and self._app_channel_cbox.count() != len(self.config_data.channels):
            # signals the cbox callback that we do not sen new user values
            self._app_version_cbox.setEnabled(False)
            self._app_channel_cbox.setEnabled(False)
            # TODO callback from changing channel zeroes selection
            self._app_version_cbox.clear()
            self._app_channel_cbox.clear()
            self._app_version_cbox.addItems(self.config_data.versions)
            self._app_channel_cbox.addItems(self.config_data.channels)
            try:  # TODO
                self._app_version_cbox.setCurrentIndex(
                    self.config_data.versions.index(self.config_data.version))
                self._app_channel_cbox.setCurrentIndex(
                    self.config_data.channels.index(self.config_data.channel))
            except Exception:
                pass
            self._app_version_cbox.setDisabled(False)
            self._app_channel_cbox.setDisabled(False)

        # add tooltip for channels, in case it is too long
        for i in range(0, len(self.config_data.channels)):
            self._app_channel_cbox.setItemData(i, self.config_data.channels[i], Qt.ToolTipRole)
        if self.config_data.executable.is_file():
            self._app_button.set_icon(self.config_data.icon)
            self._app_button.ungrey_icon()

    def update_versions_cbox(self, show: bool):
        if show:
            self._app_version_cbox.show()
        else:
            self._app_version_cbox.hide()

    def update_channels_cbox(self, show: bool):
        if show:
            self._app_channel_cbox.show()
        else:
            self._app_channel_cbox.hide()

    def on_click(self):
        """ Callback for opening the executable on click """
        run_file(self.config_data.executable, self.config_data.is_console_application, self.config_data.args)

    def on_version_selected(self, index):
        if not self._app_version_cbox.isEnabled():
            return
        if index == -1:  # on clear
            return
        if self.config_data.version == self._app_version_cbox.currentText():  # no change
            return
        self._app_button.grey_icon()
        # update channels to match version
        self._app_channel_cbox.clear()  # reset cbox
        if len(self.config_data.channels) == 1:
            self._app_channel_cbox.addItems(self.config_data.channels)
        else:
            self._app_channel_cbox.addItems([self.config_data.INVALID_DESCR] + self.config_data.channels)
            self.config_data.channel = self.config_data.INVALID_DESCR
            # add tooltip for channels, in case it is too long
            for i in range(0, len(self.config_data.channels)):
                self._app_channel_cbox.setItemData(i+1, self.config_data.channels[i], Qt.ToolTipRole)
                self._app_channel_cbox.setDisabled(True)

        self._app_channel_cbox.setCurrentIndex(0)
        self.config_data.version = self._app_version_cbox.currentText()
        self._app_button.setToolTip(str(self.config_data.conan_ref))
        if this.main_window:
            this.main_window.save_config()

    def on_channel_selected(self, index):
        """ This is callback is also called on cbox_add_items, so a workaround is needed"""
        if not self._app_channel_cbox.isEnabled():
            return
        if index == -1:
            return
        if self.config_data.channel == self._app_channel_cbox.currentText():
            return

        self.config_data.channel = self._app_channel_cbox.currentText()
        self._app_button.setToolTip(str(self.config_data.conan_ref))
        self._app_button.set_icon(self.config_data.icon)
        if this.main_window:
            this.main_window.save_config()
