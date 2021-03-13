
import os
import platform
import conan_app_launcher as this

from conan_app_launcher.base import Logger
from conan_app_launcher.components import AppConfigEntry, run_file
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_VERSIONS, Settings)
from conan_app_launcher.ui.app_grid.app_button import AppButton
# from conan_app_launcher.ui.tab_app_grid import TabAppGrid

from PyQt5 import QtCore, QtWidgets, QtGui
from conan_app_launcher.ui.app_grid.app_edit_dialog import EditAppDialog

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class AppLink(QtWidgets.QVBoxLayout):
    app_link_edited = QtCore.pyqtSignal(AppConfigEntry)
    conan_info_updated = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QWidget, app: AppConfigEntry, app_link_added, app_link_removed):
        super().__init__(parent)
        self.config_data = app
        self.config_data.gui_update_signal = self.conan_info_updated
        self.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)

        self._app_name_label = QtWidgets.QLabel(parent)
        self._app_version_cbox = QtWidgets.QComboBox(parent)
        self._app_channel_cbox = QtWidgets.QComboBox(parent)
        self._app_button = AppButton(parent)
        self._app_link_added = app_link_added
        self._app_link_removed = app_link_removed

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
        self._app_name_label.setText(app.name)

        self.addWidget(self._app_name_label)

        # self._app_version_cbox.addItem(app.conan_ref.version)
        self._app_version_cbox.setDisabled(True)
        self._app_version_cbox.setDuplicatesEnabled(False)
        self._app_version_cbox.setSizePolicy(size_policy)
        self._app_version_cbox.setMaximumWidth(193)  # TODO should be used from a const

        self.addWidget(self._app_version_cbox)

        # self._app_channel_cbox.addItem(app.conan_ref.channel)
        self._app_channel_cbox.setDisabled(True)
        self._app_channel_cbox.setDuplicatesEnabled(False)
        self._app_channel_cbox.setSizePolicy(size_policy)
        self._app_channel_cbox.setMaximumWidth(193)  # TODO should be used from a const

        self.addWidget(self._app_channel_cbox)

        # connect signals
        self.app_link_edited.connect(self.on_accept_edit_dialog)
        self.conan_info_updated.connect(self.update_with_conan_info)
        if this.main_window:
            this.main_window.display_versions_updated.connect(self.update_versions_cbox)
            this.main_window.display_channels_updated.connect(self.update_channels_cbox)
        self._app_button.clicked.connect(self.on_click)
        self._app_version_cbox.currentIndexChanged.connect(self.on_version_selected)
        self._app_channel_cbox.currentIndexChanged.connect(self.on_channel_selected)

        self.menu = QtWidgets.QMenu()
        icons_path = this.asset_path / "icons"

        self.open_fm_action = QtWidgets.QAction("Open in file manager", self)
        self.open_fm_action.setIcon(QtGui.QIcon(str(icons_path / "file-explorer.png")))
        self.menu.addAction(self.open_fm_action)

        self.menu.addSeparator()

        self.add_action = QtWidgets.QAction("Add new app link", self)
        self.add_action.setIcon(QtGui.QIcon(str(icons_path / "add_link.png")))
        self.menu.addAction(self.add_action)

        self.edit_action = QtWidgets.QAction("Edit", self)
        self.edit_action.setIcon(QtGui.QIcon(str(icons_path / "edit.png")))
        self.menu.addAction(self.edit_action)

        self.remove_action = QtWidgets.QAction("Remove app link", self)
        self.remove_action.setIcon(QtGui.QIcon(str(icons_path / "delete.png")))
        self.menu.addAction(self.remove_action)

        self.menu.addSeparator()

        self.move_r = QtWidgets.QAction("Move Right", self)
        self.move_r.setDisabled(True)  # TODO upcomng feature
        self.menu.addAction(self.move_r)

        self.move_l = QtWidgets.QAction("Move Left", self)
        self.move_l.setDisabled(True)  # TODO upcoming feature
        self.menu.addAction(self.move_l)

        self.add_action.triggered.connect(self.open_edit_dialog)
        self.open_fm_action.triggered.connect(self.open_in_file_manager)
        self.edit_action.triggered.connect(self.open_edit_dialog)
        self.remove_action.triggered.connect(self.remove)

        self._apply_new_config()
        self.update_with_conan_info()

    def __del__(self):
        self._app_name_label.deleteLater()
        self._app_version_cbox.deleteLater()
        self._app_channel_cbox.deleteLater()
        self._app_button.deleteLater()

    def on_context_menu_requested(self, position):
        self.menu.exec_(self._app_button.mapToGlobal(position))

    def open_in_file_manager(self):
        if platform.system() == "Linux":
            os.system("xdg-open " + str(self.config_data.executable.parent))
        elif platform.system() == "Windows":
            os.system("explorer " + str(self.config_data.executable.parent))

    def _apply_new_config(self):
        self._app_button.setToolTip(str(self.config_data.conan_ref))
        self._app_button.set_icon(self.config_data.icon)

        self._app_channel_cbox.clear()
        self._app_channel_cbox.addItem(self.config_data.conan_ref.channel)
        self._app_version_cbox.clear()
        self._app_version_cbox.addItem(self.config_data.conan_ref.version)

    def open_edit_dialog(self):
        self._edit_app_dialog = EditAppDialog(
            self.config_data, parent=self.parentWidget(), app_link_edited=self.app_link_edited)

    def remove(self):
        # confirmation dialog
        msg = QtWidgets.QMessageBox(parent=this.main_window)
        msg.setWindowTitle("Delete app link")
        msg.setText(f"Are you sure, you want to delete the link \"{self.config_data.name}?\"")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        reply = msg.exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            self._app_link_removed.emit(self)
            this.main_window.config_changed.emit()

    def on_accept_edit_dialog(self):
        self._app_button.grey_icon()
        self._app_link_added.emit(self)
        self._apply_new_config()
        this.main_window.config_changed.emit()

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
        self._app_channel_cbox.addItems([self.config_data.INVALID_DESCR] + self.config_data.channels)
        # add tooltip for channels, in case it is too long
        for i in range(0, len(self.config_data.channels)):
            self._app_channel_cbox.setItemData(i+1, self.config_data.channels[i], Qt.ToolTipRole)
        self._app_channel_cbox.setCurrentIndex(0)

        self.config_data.channel = self.config_data.INVALID_DESCR
        self.config_data.version = self._app_version_cbox.currentText()
        this.main_window.config_changed.emit()

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
        this.main_window.config_changed.emit()