from pathlib import Path
from typing import List
from shutil import rmtree
from pathlib import Path

from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtCore import pyqtSlot

import conan_app_launcher as this
from conan_app_launcher.base import Logger
from conan_app_launcher.components import ConanWorker, parse_config_file, write_config_file, AppConfigEntry, ConanApi
from conan_app_launcher.settings import (
    LAST_CONFIG_FILE, DISPLAY_APP_VERSIONS, DISPLAY_APP_CHANNELS, GRID_COLUMNS, GRID_ROWS, Settings)
from conan_app_launcher.ui.app_link import AppLink
from conan_app_launcher.ui.tab_app_grid import TabAppGrid
# from conan_app_launcher.ui.add_remove_apps import AddRemoveAppsDialog
from conan_app_launcher.ui.edit_app import EditAppDialog
from conan_app_launcher.ui.about import AboutDialog

Qt = QtCore.Qt


class MainUi(QtWidgets.QMainWindow):
    """ Instantiates MainWindow and holds all UI objects """
    TOOLBOX_GRID_ITEM = 0
    TOOLBOX_PACKAGES_ITEM = 1

    conan_info_updated = QtCore.pyqtSignal()
    config_changed = QtCore.pyqtSignal()
    display_versions_updated = QtCore.pyqtSignal(bool)
    display_channels_updated = QtCore.pyqtSignal(bool)
    new_message_logged = QtCore.pyqtSignal(str)  # str arg is the message
    _icons_path = None

    def __init__(self, settings: Settings):
        super().__init__()
        self._icons_path = this.asset_path / "icons"

        self._ui = uic.loadUi(this.base_path / "ui" / "qt" / "app_grid.ui", baseinstance=self)
        self._settings = settings
        self._tabs_info: List[TabAppGrid] = []
        self._about_dialog = AboutDialog(self)
        self._new_tab = QtWidgets.QTabWidget()

        # add own widgets
        self._ui.add_app_link_button = QtWidgets.QPushButton(self)
        self._ui.add_app_link_button.setGeometry(765, 452, 44, 44)
        self._ui.add_app_link_button.setIconSize(QtCore.QSize(44, 44))

        self._ui.add_tab_button = QtWidgets.QPushButton(self)
        self._ui.add_tab_button.setGeometry(802, 50, 28, 28)
        self._ui.add_tab_button.setIconSize(QtCore.QSize(28, 28))

        self.load_icons()

        # connect logger to console widget to log possible errors at init
        Logger.init_qt_logger(self)
        self._ui.console.setFontPointSize(10)

        self.config_changed.connect(self.on_config_change)
        self.new_message_logged.connect(self.write_log)

        self._ui.menu_about_action.triggered.connect(self._about_dialog.show)
        self._ui.menu_open_config_file.triggered.connect(self.open_config_file_dialog)
        self._ui.menu_set_display_versions.triggered.connect(self.toggle_display_versions)
        self._ui.menu_set_display_channels.triggered.connect(self.toogle_display_channels)
        self._ui.menu_clean_cache.triggered.connect(self.open_cleanup_cache_dialog)
        self._ui.tab_bar.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.tab_bar.tabBar().customContextMenuRequested.connect(self.on_tab_context_menu_requested)
        self._ui.main_toolbox.currentChanged.connect(self.on_toolbox_changed)

    # def resizeEvent(self, event: "QResizeEvent"):  # override QMainWindow
        # TODO implement moving non layout buttons
    #    super().resizeEvent(event)

    def load_icons(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(str(self._icons_path / "grid.png")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._ui.main_toolbox.setItemIcon(self.TOOLBOX_GRID_ITEM, icon)

        icon.addPixmap(QtGui.QPixmap(str(self._icons_path / "search_packages.png")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._ui.main_toolbox.setItemIcon(self.TOOLBOX_PACKAGES_ITEM, icon)

        self._ui.add_app_link_button.setIcon(QtGui.QIcon(str(self._icons_path / "add_link.png")))
        self._ui.add_tab_button.setIcon(QtGui.QIcon(str(self._icons_path / "plus.png")))
        # menu
        self._ui.menu_clean_cache.setIcon(QtGui.QIcon(str(self._icons_path / "cleanup.png")))

    def on_toolbox_changed(self):
        if self._ui.main_toolbox.currentIndex() == 1:  # package view
            # hide floating grid buttons
            self._ui.add_app_link_button.hide()
            self._ui.add_tab_button.hide()
        elif self._ui.main_toolbox.currentIndex() == 0:  # grid view
            # show floating buttons
            self._ui.add_app_link_button.show()
            self._ui.add_tab_button.show()

    def closeEvent(self, event):  # override QMainWindow
        """ Remove qt logger, so it doesn't log into a non existant object """
        try:
            self.new_message_logged.disconnect(self.write_log)
        except Exception:
            # Sometimes the closeEvent is called twice and disconnect errors.
            pass
        Logger.remove_qt_logger()
        super().closeEvent(event)

    def on_tab_context_menu_requested(self, position):
        index = self._ui.tab_bar.tabBar().tabAt(position)
        menu = QtWidgets.QMenu()
        rename_action = QtWidgets.QAction("Rename", self)
        rename_action.setIcon()
        menu.addAction(rename_action)
        rename_action.triggered.connect(lambda: self.on_tab_rename(index))

        remove_action = QtWidgets.QAction("Remove", self)
        menu.addAction(remove_action)
        remove_action.triggered.connect(self.on_tab_remove)

        new_tab_action = QtWidgets.QAction("Add new tab", self)
        menu.addAction(new_tab_action)
        new_tab_action.triggered.connect(self.open_new_tab_dialog)
        menu.exec_(self.tab_bar.tabBar().mapToGlobal(position))

    @ pyqtSlot()
    def open_new_tab_dialog(self):
        self._new_tab_dialog = QtWidgets.QInputDialog(self)
        pass

    @ pyqtSlot(int)
    def on_tab_rename(self, index):
        tab: TabAppGrid = self._ui.tab_bar.widget(index)
        rename_tab_dialog = QtWidgets.QInputDialog(self)
        text, accepted = rename_tab_dialog.getText(self, 'Rename tab',
                                                   'Enter new name:', text=tab.config_data.name)
        if accepted:
            tab.config_data.name = text
            self._ui.tab_bar.setTabText(index, text)
            self.config_changed.emit()

    @ pyqtSlot()
    def on_tab_remove(self):
        pass
        # rename_tab_dialog = QtWidgets.QInputDialog(self)

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
        config_file_path = Path(self._settings.get(LAST_CONFIG_FILE))
        if config_file_path.exists():
            dialog_path = config_file_path.parent
        dialog = QtWidgets.QFileDialog(parent=self, caption="Select JSON Config File",
                                       directory=str(dialog_path), filter="JSON files (*.json)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self._settings.set(LAST_CONFIG_FILE, dialog.selectedFiles()[0])
            self._re_init()

    @ pyqtSlot()
    def toggle_display_versions(self):
        """ Reads the current menu setting, sevaes it and updates the gui """
        version_status = self._ui.menu_set_display_versions.isChecked()
        self._settings.set(DISPLAY_APP_VERSIONS, version_status)
        self.display_versions_updated.emit(version_status)

    @ pyqtSlot()
    def toogle_display_channels(self):
        """ Reads the current menu setting, sevaes it and updates the gui """
        channel_status = self._ui.menu_set_display_channels.isChecked()
        self._settings.set(DISPLAY_APP_CHANNELS, channel_status)
        self.display_channels_updated.emit(channel_status)

    def create_layout(self):
        """ Creates the tabs and app icons """
        self._ui.tab_bar.setMovable(True)

        for config_data in self._tabs_info:
            # need to save object locally, otherwise it can be destroyed in the underlying C++ layer
            tab = TabAppGrid(parent=self, config_data=config_data,
                             max_columns=self._settings.get(GRID_COLUMNS), max_rows=self._settings.get(GRID_ROWS))
            # self._tabs.append(tab)
            self._ui.tab_bar.addTab(tab, config_data.name)
        # self._ui.tab_bar.addTab(self._new_tab, "+")
        # self._ui.tab_bar.tabBarClicked.connect(self.open_new_tab_dialog)
        # add right click context menu actions
        # "New tab after this tab"

    @ pyqtSlot()
    def on_config_change(self):
        """ Update without cleaning up. Ungrey entries and set correct icon and add hover text """
        write_config_file(Path(self._settings.get(LAST_CONFIG_FILE)), self._tabs_info)

        # for tab in self._tabs:
        #     for app in tab.apps:
        #         app.update_entry(self._settings)
        # self.save_all_configs()

    def init_gui(self):
        """ Cleans up ui, reads config file and creates new layout """
        if self._ui.tab_bar.count() > 0:  # remove the default tab
            self._ui.tab_bar.removeTab(0)
        config_file_path = Path(self._settings.get(LAST_CONFIG_FILE))
        if config_file_path.is_file():  # escape error log on first opening
            self._tabs_info = parse_config_file(config_file_path)

        this.conan_worker = ConanWorker(self._tabs_info, self.conan_info_updated)
        self.create_layout()
        # always show the first tab first
        self._ui.tab_bar.setCurrentIndex(0)

    @ pyqtSlot(int)
    def on_selection_change(self, index: int):
        view_index = self._ui.treeView.selectionModel().selectedIndexes()[0]
        proxy_index = self.proxy.mapToSource(view_index)
        item_name = self.model.fileName(proxy_index)
        path = self.model.fileInfo(view_index).dir().absolutePath()
        self._ui.listView.setRootIndex(self.fileModel.setRootPath(path))
        print(item_name)

    def _re_init(self):
        """ To be called, when a new config file is loaded """
        this.conan_worker.finish_working(3)
        self.init_gui()

    @ pyqtSlot(str)
    def write_log(self, text):
        """ Write the text signaled by the logger """
        self._ui.console.append(text)
