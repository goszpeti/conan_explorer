from pathlib import Path
from shutil import rmtree

from conan_app_launcher import (ADD_APP_LINK_BUTTON, ADD_TAB_BUTTON,
                                DEFAULT_UI_CFG_FILE_NAME, base_path)
from conan_app_launcher.app import (active_settings, asset_path, conan_api,
                                    user_save_path)
from conan_app_launcher.logger import Logger
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_USERS,
                                         DISPLAY_APP_VERSIONS,
                                         LAST_CONFIG_FILE)
from conan_app_launcher.ui.data import UI_CONFIG_JSON_TYPE, UiConfigFactory
from conan_app_launcher.ui.model import UiApplicationModel
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot

from .modules.about_dialog import AboutDialog
from .modules.app_grid import AppGrid
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

        self._icons_path = asset_path / "icons"
        self.ui = uic.loadUi(base_path / "ui" / "main.ui", baseinstance=self)
        self._about_dialog = AboutDialog(self)

        if ADD_APP_LINK_BUTTON:
            self.ui.add_app_link_button = QtWidgets.QPushButton(self)
            self.ui.add_app_link_button.setGeometry(765, 452, 44, 44)
            self.ui.add_app_link_button.setIconSize(QtCore.QSize(44, 44))
            self.ui.add_app_link_button.clicked.connect(self.open_new_app_link_dialog)
        if ADD_TAB_BUTTON:
            self.ui.add_tab_button = QtWidgets.QPushButton(self)
            self.ui.add_tab_button.setGeometry(802, 50, 28, 28)
            self.ui.add_tab_button.setIconSize(QtCore.QSize(28, 28))
            self.ui.add_tab_button.clicked.connect(self.open_new_tab_dialog)

        self.load_icons()

        # connect logger to console widget to log possible errors at init
        Logger.init_qt_logger(self.new_message_logged)
        self.ui.console.setFontPointSize(10)

        self.new_message_logged.connect(self.write_log)

        # load app grid
        self._app_grid = AppGrid(self, self.model)
        self._local_package_explorer = LocalConanPackageExplorer(self)

        # initialize view user settings
        self.ui.menu_toggle_display_versions.setChecked(active_settings.get_bool(DISPLAY_APP_VERSIONS))
        self.ui.menu_toggle_display_users.setChecked(active_settings.get_bool(DISPLAY_APP_USERS))
        self.ui.menu_toggle_display_channels.setChecked(active_settings.get_bool(DISPLAY_APP_CHANNELS))

        self.ui.menu_about_action.triggered.connect(self._about_dialog.show)
        self.ui.menu_open_config_file.triggered.connect(self.open_config_file_dialog)
        self.ui.menu_toggle_display_versions.triggered.connect(self.apply_display_versions_setting)
        self.ui.menu_toggle_display_users.triggered.connect(self.apply_display_users_setting)
        self.ui.menu_toggle_display_channels.triggered.connect(self.apply_display_channels_setting)
        self.ui.menu_cleanup_cache.triggered.connect(self.open_cleanup_cache_dialog)
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

    def load(self, config_file_setting):
        # empty config, create it in user path
        default_config_file_path = user_save_path / DEFAULT_UI_CFG_FILE_NAME
        if not config_file_setting or not default_config_file_path.exists():
            config_file_setting = default_config_file_path
        active_settings.set(LAST_CONFIG_FILE, str(config_file_setting))

        # model loads incrementally
        self.model.loadf(config_file_setting)

        # conan works, model can be loaded
        self._app_grid.load_tabs()
        self.apply_view_settings()

    def apply_view_settings(self):
        self.apply_display_versions_setting()
        self.apply_display_users_setting()
        self.apply_display_channels_setting()

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
        paths = conan_api.get_cleanup_cache_paths()
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
        config_file_path = Path(active_settings.get_string(LAST_CONFIG_FILE))
        if config_file_path.exists():
            dialog_path = config_file_path.parent
        dialog = QtWidgets.QFileDialog(parent=self, caption="Select JSON Config File",
                                       directory=str(dialog_path), filter="JSON files (*.json)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            dialog.selectedFiles()[0]
            config_file_setting = active_settings.set(LAST_CONFIG_FILE, )
            # model loads incrementally
            self.model.loadf(config_file_setting)

            # conan works, model can be loaded
            self._app_grid.re_init(self.model)  # loads tabs
            self.apply_view_settings()  # now view settings can be applied

    @pyqtSlot()
    def apply_display_versions_setting(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_versions.isChecked()
        active_settings.set(DISPLAY_APP_VERSIONS, status)
        self.display_versions_changed.emit()

    @pyqtSlot()
    def apply_display_users_setting(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_users.isChecked()
        active_settings.set(DISPLAY_APP_USERS, status)
        self.display_users_changed.emit()

    @pyqtSlot()
    def apply_display_channels_setting(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_channels.isChecked()
        active_settings.set(DISPLAY_APP_CHANNELS, status)
        self.display_channels_changed.emit()

    @pyqtSlot()
    def open_new_app_link_dialog(self):
        # call tab on_app_link_add
        current_tab = self.ui.tab_bar.widget(self.ui.tab_bar.currentIndex())
        current_tab.open_app_link_add_dialog()

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
        if ADD_APP_LINK_BUTTON:
            self.ui.add_app_link_button.setIcon(QtGui.QIcon(str(self._icons_path / "add_link.png")))
        if ADD_TAB_BUTTON:
            self.ui.add_tab_button.setIcon(QtGui.QIcon(str(self._icons_path / "plus.png")))
        # menu
        self.ui.refresh_button.setIcon(QtGui.QIcon(str(self._icons_path / "refresh.png")))
        self.ui.menu_cleanup_cache.setIcon(QtGui.QIcon(str(self._icons_path / "cleanup.png")))
        self.ui.menu_about_action.setIcon(QtGui.QIcon(str(self._icons_path / "about.png")))

    def open_new_app_dialog_from_extern(self, config_data):
        """ Called from pacakge explorer, where tab is unknown"""
        dialog = QtWidgets.QInputDialog(self)
        tab_list = list(item.name for item in tab_configs)

        dialog.setComboBoxItems(tab_list)
        dialog.setWindowTitle("Choose a tab!")
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            answer = dialog.textValue()
            tabs = self._app_grid.get_tabs()
            for tab in tabs:
                if answer == tab.config_data.name:
                    tab.open_app_link_add_dialog(config_data)
