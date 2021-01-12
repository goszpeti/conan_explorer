
import time
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

    def __init__(self, parent: QtWidgets.QWidget, app: AppConfigEntry, app_link_added, app_link_removed, is_new_link=False):
        super().__init__(parent)
        self.config_data = app
        self.is_new_link = is_new_link
        self.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)

        self._app_name_label = QtWidgets.QLabel(parent)
        self._app_version_cbox = QtWidgets.QComboBox(parent)
        self._app_channel_cbox = QtWidgets.QComboBox(parent)
        self._app_button = AppButton(parent)
        self._app_link_added = app_link_added
        self._app_link_removed = app_link_removed

        #     self.init(parent)

    # def init(self, parent):
    #     app = self.config_data
        # self.setObjectName(parent.objectName() + app.name)  # to find it for tests

        # size policies
        self.setSpacing(3)
        self.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                            QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self._app_button.setSizePolicy(size_policy)
        #self._app_button.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # add sub widgets
        self.addWidget(self._app_button)
        # self._app_name_label.setSizePolicy(size_policy)
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
        this.main_window.conan_info_updated.connect(self.update_with_conan_info)
        this.main_window.display_versions_updated.connect(self.update_versions_cbox)
        this.main_window.display_channels_updated.connect(self.update_channels_cbox)
        self._app_button.clicked.connect(self.on_click)
        self._app_version_cbox.currentIndexChanged.connect(self.version_selected)
        self._app_channel_cbox.currentIndexChanged.connect(self.channel_selected)

        # add right click context menu actions
        if not self.is_new_link:
            self._app_button.setContextMenuPolicy(Qt.ActionsContextMenu)
            add_action = QtWidgets.QAction("Add new app", self)
            self._app_button.addAction(add_action)
            add_action.triggered.connect(self.open_edit_dialog)
            add_action.setIcon(QtGui.QIcon(str(this.asset_path / "icons" / "new_app_icon.png")))
            edit_action = QtWidgets.QAction("Edit", self)
            self._app_button.addAction(edit_action)
            edit_action.triggered.connect(self.open_edit_dialog)
            remove_action = QtWidgets.QAction("Remove", self)
            self._app_button.addAction(remove_action)
            remove_action.triggered.connect(self.remove)
        else:
            self._app_button.ungrey_icon()
        # move_r = QtWidgets.QAction("Move Right", self)
        # self._app_button.addAction(move_r)
        # move_l = QtWidgets.QAction("Move Left", self)
        # self._app_button.addAction(move_l)
        self._apply_config()

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
        if self.is_new_link:  # new app link
            self.is_new_link = False
            self._app_button.grey_icon()
            self._app_link_added.emit(self.config_data)
            # self._tab.config_data.add_app_entry(self.config_data)
            # self._tab.display_new_app_link()
        else:
            self._apply_config()
        # this.main_window.config_changed.emit()

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
        if self.is_new_link:
            self.open_edit_dialog()
        else:
            run_file(self.config_data.executable, self.config_data.is_console_application, self.config_data.args)

    def version_selected(self, index):
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

    def channel_selected(self, index):
        if not self._app_channel_cbox.isEnabled():
            return
        if index == -1:
            return
        if self.config_data.channel == self._app_channel_cbox.currentText():
            return
        self._app_button.grey_icon()
        self.config_data.channel = self._app_channel_cbox.currentText()
