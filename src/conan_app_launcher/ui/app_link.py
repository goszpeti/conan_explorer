
import time
import os
import platform
import conan_app_launcher as this

from conan_app_launcher.components import AppConfigEntry, run_file
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_VERSIONS, Settings)
from conan_app_launcher.ui.qt.app_button import AppButton
# from conan_app_launcher.ui.tab_app_grid import TabAppGrid

from PyQt5 import QtCore, QtWidgets, QtGui
from conan_app_launcher.ui.edit_app import EditAppDialog

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
        self.addWidget(self._app_version_cbox)

        # self._app_channel_cbox.addItem(app.conan_ref.channel)
        self._app_channel_cbox.setDisabled(True)
        self._app_channel_cbox.setDuplicatesEnabled(False)
        self._app_channel_cbox.setSizePolicy(size_policy)
        self.addWidget(self._app_channel_cbox)

        # connect signals
        self.app_link_edited.connect(self.on_accept_edit_dialog)
        self.conan_info_updated.connect(self.update_with_conan_info)
        this.main_window.display_versions_updated.connect(self.update_versions_cbox)
        this.main_window.display_channels_updated.connect(self.update_channels_cbox)
        self._app_button.clicked.connect(self.on_click)
        self._app_version_cbox.currentIndexChanged.connect(self.on_version_selected)
        self._app_channel_cbox.currentIndexChanged.connect(self.on_channel_selected)

        # self._app_button.add_action.triggered.connect(self.open_edit_dialog)

        self._app_button.edit_action.triggered.connect(self.open_edit_dialog)

        self._app_button.remove_action.triggered.connect(self.remove)

        # move_r = QtWidgets.QAction("Move Right", self)
        # self._app_button.addAction(move_r)
        # move_l = QtWidgets.QAction("Move Left", self)
        # self._app_button.addAction(move_l)
        self._apply_config()
        self._app_button.open_fm_action.triggered.connect(self.open_in_file_manager)

    def open_in_file_manager(self):
        if platform.system() == "Linux":
            os.system("xdg-open " + str(self.config_data.executable.parent))
        elif platform.system() == "Windows":
            os.system("explorer " + str(self.config_data.executable.parent))

    def _apply_config(self):
        self._app_button.setToolTip(str(self.config_data.conan_ref))
        self._app_button.set_icon(self.config_data.icon)
        self._app_channel_cbox.clear()
        self._app_channel_cbox.addItem(self.config_data.conan_ref.channel)
        self._app_version_cbox.clear()
        self._app_channel_cbox.addItem(self.config_data.conan_ref.version)

    def open_edit_dialog(self):
        self._edit_app_dialog = EditAppDialog(
            self.config_data, parent=self.parentWidget(), app_link_edited=self.app_link_edited)

    def remove(self):
        # self._tab.remove_app_link(self)
        self._app_link_removed.emit(self)
        # this.main_window.config_changed.emit()

    def on_accept_edit_dialog(self):
        self._app_button.grey_icon()
        self._app_link_added.emit(self)
        self._apply_config()

    def update_with_conan_info(self):
        # set icon and ungrey if package is available
        if self.config_data.executable.is_file():
            self._app_button.set_icon(self.config_data.icon)
            self._app_button.ungrey_icon()

        if len(self.config_data.versions) > 0 and self._app_version_cbox.count() != len(self.config_data.versions):  # on nums changed
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
        self._app_channel_cbox.setCurrentIndex(0)

        self.config_data.channel = self.config_data.INVALID_DESCR
        self.config_data.version = self._app_version_cbox.currentText()

    def on_channel_selected(self, index):
        if not self._app_channel_cbox.isEnabled():
            return
        if index == -1:
            return
        if self.config_data.channel == self._app_channel_cbox.currentText():
            return
        self._app_button.grey_icon()
        self.config_data.channel = self._app_channel_cbox.currentText()
