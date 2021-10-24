from pathlib import Path
from shutil import rmtree

import conan_app_launcher as this
from conan_app_launcher.base import Logger
from conan_app_launcher.components import (AppConfigEntry, ConanApi,
                                           write_config_file)
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_VERSIONS,
                                         LAST_CONFIG_FILE)
from conan_app_launcher.ui.about_dialog import AboutDialog
from conan_app_launcher.ui.app_grid import AppGrid
from conan_app_launcher.ui.package_explorer import LocalConanPackageExplorer
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot

Qt = QtCore.Qt


class MainUi(QtWidgets.QMainWindow):
    """ Instantiates MainWindow and holds all UI objects """
    TOOLBOX_GRID_ITEM = 0
    TOOLBOX_PACKAGES_ITEM = 1

    display_versions_updated = QtCore.pyqtSignal(bool)
    display_channels_updated = QtCore.pyqtSignal(bool)
    new_message_logged = QtCore.pyqtSignal(str)  # str arg is the message

    def __init__(self):
        super().__init__()
        self._icons_path = this.asset_path / "icons"

        self.ui = uic.loadUi(this.base_path / "ui" / "main.ui", baseinstance=self)
        self._about_dialog = AboutDialog(self)

        if this.ADD_APP_LINK_BUTTON:
            self.ui.add_app_link_button = QtWidgets.QPushButton(self)
            self.ui.add_app_link_button.setGeometry(765, 452, 44, 44)
            self.ui.add_app_link_button.setIconSize(QtCore.QSize(44, 44))
            self.ui.add_app_link_button.clicked.connect(self.open_new_app_link_dialog)
        if this.ADD_TAB_BUTTON:
            self.ui.add_tab_button = QtWidgets.QPushButton(self)
            self.ui.add_tab_button.setGeometry(802, 50, 28, 28)
            self.ui.add_tab_button.setIconSize(QtCore.QSize(28, 28))
            self.ui.add_tab_button.clicked.connect(self.open_new_tab_dialog)

        self.load_icons()

        # connect logger to console widget to log possible errors at init
        Logger.init_qt_logger(self)
        self.ui.console.setFontPointSize(10)

        #self.config_changed.connect(self.save_config)
        self.new_message_logged.connect(self.write_log)

        # load app grid
        self._app_grid = AppGrid(self)
        self._local_package_explorer = LocalConanPackageExplorer(self)

        self.ui.menu_about_action.triggered.connect(self._about_dialog.show)
        self.ui.menu_open_config_file.triggered.connect(self.open_config_file_dialog)
        self.ui.menu_set_display_versions.triggered.connect(self.toggle_display_versions)
        self.ui.menu_set_display_channels.triggered.connect(self.toogle_display_channels)
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

    def start_app_grid(self):
        self._app_grid.load_tabs()

    # Menu callbacks #

    @pyqtSlot()
    def on_main_view_changed(self):
        """ Change between main views (grid and package explorer) """
        if self.ui.main_toolbox.currentIndex() == 1:  # package view
            # hide floating grid buttons
            if this.ADD_APP_LINK_BUTTON:
                self.ui.add_app_link_button.hide()
            if this.ADD_TAB_BUTTON:
                self.ui.add_tab_button.hide()
        elif self.ui.main_toolbox.currentIndex() == 0:  # grid view
            # show floating buttons
            if this.ADD_APP_LINK_BUTTON:
                self.ui.add_app_link_button.show()
            if this.ADD_TAB_BUTTON:
                self.ui.add_tab_button.show()

    @ pyqtSlot()
    def open_cleanup_cache_dialog(self):
        """ Open the message box to confirm deletion of invalid cache folders """
        conan = ConanApi()
        paths = conan.get_cleanup_cache_paths()
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
        dialog_path = Path.home()
        config_file_path = Path(this.settings.get_string(LAST_CONFIG_FILE))
        if config_file_path.exists():
            dialog_path = config_file_path.parent
        dialog = QtWidgets.QFileDialog(parent=self, caption="Select JSON Config File",
                                       directory=str(dialog_path), filter="JSON files (*.json)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            this.settings.set(LAST_CONFIG_FILE, dialog.selectedFiles()[0])
            self._app_grid.re_init()

    @ pyqtSlot()
    def toggle_display_versions(self):
        """ Reads the current menu setting, sevaes it and updates the gui """
        version_status = self.ui.menu_set_display_versions.isChecked()
        this.settings.set(DISPLAY_APP_VERSIONS, version_status)
        self.display_versions_updated.emit(version_status)

    @ pyqtSlot()
    def toogle_display_channels(self):
        """ Reads the current menu setting, sevaes it and updates the gui """
        channel_status = self.ui.menu_set_display_channels.isChecked()
        this.settings.set(DISPLAY_APP_CHANNELS, channel_status)
        self.display_channels_updated.emit(channel_status)

    @pyqtSlot()
    def open_new_app_link_dialog(self):
        # call tab on_app_link_add
        current_tab = self.ui.tab_bar.widget(self.ui.tab_bar.currentIndex())
        current_tab.open_app_link_add_dialog()

    @ pyqtSlot(str)
    def write_log(self, text):
        """ Write the text signaled by the logger """
        self.ui.console.append(text)

    def save_config(self):
        """ Update without cleaning up. Ungrey entries and set correct icon and add hover text """
        write_config_file(Path(this.settings.get_string(LAST_CONFIG_FILE)), this.tab_configs)

    def load_icons(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(str(self._icons_path / "grid.png")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.main_toolbox.setItemIcon(self.TOOLBOX_GRID_ITEM, icon)

        icon.addPixmap(QtGui.QPixmap(str(self._icons_path / "search_packages.png")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.main_toolbox.setItemIcon(self.TOOLBOX_PACKAGES_ITEM, icon)
        if this.ADD_APP_LINK_BUTTON:
            self.ui.add_app_link_button.setIcon(QtGui.QIcon(str(self._icons_path / "add_link.png")))
        if this.ADD_TAB_BUTTON:
            self.ui.add_tab_button.setIcon(QtGui.QIcon(str(self._icons_path / "plus.png")))
        # menu
        self.ui.refresh_button.setIcon(QtGui.QIcon(str(self._icons_path / "refresh.png")))
        self.ui.menu_cleanup_cache.setIcon(QtGui.QIcon(str(self._icons_path / "cleanup.png")))
        self.ui.menu_about_action.setIcon(QtGui.QIcon(str(self._icons_path / "about.png")))

    def open_new_app_dialog_from_extern(self, config_data = AppConfigEntry()):
        """ Called from pacakge explorer, where tab is unknown"""
        dialog = QtWidgets.QInputDialog(self)
        tab_list = list(item.name for item in this.tab_configs)

        dialog.setComboBoxItems(tab_list)
        dialog.setWindowTitle("Choose a tab!")
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            answer = dialog.textValue()
            tabs = self._app_grid.get_tabs()
            for tab in tabs:
                if answer == tab.config_data.name:
                    tab.open_app_link_add_dialog(config_data)
