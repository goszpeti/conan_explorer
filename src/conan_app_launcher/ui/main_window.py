from pathlib import Path
from shutil import rmtree
from typing import Optional

import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher import (ADD_APP_LINK_BUTTON, ADD_TAB_BUTTON, PathLike,
                                asset_path, base_path, user_save_path)
from conan_app_launcher.logger import Logger
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_USERS,
                                         DISPLAY_APP_VERSIONS,
                                         LAST_CONFIG_FILE)
from conan_app_launcher.ui.model import UiApplicationModel
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot

from .modules.about_dialog import AboutDialog
from .modules.app_grid import AppGridView
from .modules.package_explorer import LocalConanPackageExplorer

Qt = QtCore.Qt


class MainWindow(QtWidgets.QMainWindow):
    """ Instantiates MainWindow and holds all UI objects """
    TOOLBOX_GRID_ITEM = 0
    TOOLBOX_PACKAGES_ITEM = 1

    display_versions_changed = QtCore.pyqtSignal()
    display_channels_changed = QtCore.pyqtSignal()
    display_users_changed = QtCore.pyqtSignal()

    new_message_logged = QtCore.pyqtSignal(str)  # str arg is the message

    def __init__(self):
        super().__init__()
        self.model = UiApplicationModel()
        self.ui = uic.loadUi(base_path / "ui" / "main.ui", baseinstance=self)

        self._icons_path = asset_path / "icons"
        self._about_dialog = AboutDialog(self)

        self.load_icons()

        # connect logger to console widget to log possible errors at init
        Logger.init_qt_logger(self.new_message_logged)
        self.ui.console.setFontPointSize(10)
        self.new_message_logged.connect(self.write_log)

        # load app grid
        self.app_grid = AppGridView(self, self.model)
        self.local_package_explorer = LocalConanPackageExplorer(self)

        # initialize view user settings
        self.ui.menu_toggle_display_versions.setChecked(app.active_settings.get_bool(DISPLAY_APP_VERSIONS))
        self.ui.menu_toggle_display_users.setChecked(app.active_settings.get_bool(DISPLAY_APP_USERS))
        self.ui.menu_toggle_display_channels.setChecked(app.active_settings.get_bool(DISPLAY_APP_CHANNELS))

        self.ui.menu_about_action.triggered.connect(self._about_dialog.show)
        self.ui.menu_open_config_file.triggered.connect(self.open_config_file_dialog)
        self.ui.menu_toggle_display_versions.triggered.connect(self.display_versions_setting_toggled)
        self.ui.menu_toggle_display_users.triggered.connect(self.apply_display_users_setting_toggled)
        self.ui.menu_toggle_display_channels.triggered.connect(self.display_channels_setting_toggled)
        self.ui.menu_cleanup_cache.triggered.connect(self.open_cleanup_cache_dialog)
        self.ui.menu_remove_locks.triggered.connect(app.conan_api.remove_locks)
        self.ui.main_toolbox.currentChanged.connect(self.on_main_view_changed)

    def closeEvent(self, event):  # override QMainWindow
        """ Remove qt logger, so it doesn't log into a non existant object """
        try:
            self.new_message_logged.disconnect(self.write_log)
        except Exception:
            # Sometimes the closeEvent is called twice and disconnect errors.
            pass
        Logger.remove_qt_logger()
        super().closeEvent(event)

    def load(self, config_source: Optional[PathLike]=None):
        config_source_str = str(config_source)
        if not config_source:
           config_source_str = app.active_settings.get_string(LAST_CONFIG_FILE)

        # model loads incrementally
        self.model.loadf(config_source_str)

        # conan works, model can be loaded
        self.app_grid.load()
        self.apply_view_settings()

    def apply_view_settings(self):
        self.display_versions_setting_toggled()
        self.apply_display_users_setting_toggled()
        self.display_channels_setting_toggled()

    # Menu callbacks #

    @pyqtSlot()
    def on_main_view_changed(self):
        """ Change between main views (grid and package explorer) """
        if self.ui.main_toolbox.currentIndex() == 1:  # package view
            # hide floating grid buttons
            if ADD_APP_LINK_BUTTON:
                self.ui.add_app_link_button.hide()
            if ADD_TAB_BUTTON:
                self.ui.add_tab_button.hide()
        elif self.ui.main_toolbox.currentIndex() == 0:  # grid view
            # show floating buttons
            if ADD_APP_LINK_BUTTON:
                self.ui.add_app_link_button.show()
            if ADD_TAB_BUTTON:
                self.ui.add_tab_button.show()

    @ pyqtSlot()
    def open_cleanup_cache_dialog(self):
        """ Open the message box to confirm deletion of invalid cache folders """
        paths = app.conan_api.get_cleanup_cache_paths()
        if not paths:
            self.write_log("INFO: Nothing found in cache to clean up.")
            return
        if len(paths) > 1:
            path_list = "\n".join(paths)
        else:
            path_list = paths[0]

        msg = QtWidgets.QMessageBox(parent=self)
        msg.setWindowTitle("Delete folders")
        msg.setText("Are you sure, you want to delete the found folders?\t")
        msg.setDetailedText(path_list)
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        reply = msg.exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            for path in paths:
                rmtree(str(path), ignore_errors=True)

    @ pyqtSlot()
    def open_config_file_dialog(self):
        """" Open File Dialog and load config file """
        dialog_path = user_save_path
        config_file_path = Path(app.active_settings.get_string(LAST_CONFIG_FILE))
        if config_file_path.exists():
            dialog_path = config_file_path.parent
        dialog = QtWidgets.QFileDialog(parent=self, caption="Select JSON Config File",
                                       directory=str(dialog_path), filter="JSON files (*.json)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_file = dialog.selectedFiles()[0]
            app.active_settings.set(LAST_CONFIG_FILE, new_file)
            # model loads incrementally
            self.model.loadf(new_file)

            # conan works, model can be loaded
            self.app_grid.re_init(self.model)  # loads tabs
            self.apply_view_settings()  # now view settings can be applied

    @pyqtSlot()
    def display_versions_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_versions.isChecked()
        app.active_settings.set(DISPLAY_APP_VERSIONS, status)
        self.app_grid.re_init_all_app_links()

    @pyqtSlot()
    def apply_display_users_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_users.isChecked()
        app.active_settings.set(DISPLAY_APP_USERS, status)
        self.app_grid.re_init_all_app_links()

    @pyqtSlot()
    def display_channels_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_channels.isChecked()
        app.active_settings.set(DISPLAY_APP_CHANNELS, status)
        self.app_grid.re_init_all_app_links()


    @pyqtSlot(str)
    def write_log(self, text):
        """ Write the text signaled by the logger """
        self.ui.console.append(text)

    def load_icons(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(str(self._icons_path / "grid.png")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.main_toolbox.setItemIcon(self.TOOLBOX_GRID_ITEM, icon)

        icon.addPixmap(QtGui.QPixmap(str(self._icons_path / "search_packages.png")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.main_toolbox.setItemIcon(self.TOOLBOX_PACKAGES_ITEM, icon)

        # menu
        self.ui.refresh_button.setIcon(QtGui.QIcon(str(self._icons_path / "refresh.png")))
        self.ui.menu_cleanup_cache.setIcon(QtGui.QIcon(str(self._icons_path / "cleanup.png")))
        self.ui.menu_about_action.setIcon(QtGui.QIcon(str(self._icons_path / "about.png")))
        self.ui.menu_remove_locks.setIcon(QtGui.QIcon(str(self._icons_path / "remove-lock.png")))
