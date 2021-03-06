from pathlib import Path
from shutil import rmtree

from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtCore import pyqtSlot

import conan_app_launcher as this
from conan_app_launcher.base import Logger
from conan_app_launcher.components import parse_config_file, write_config_file, TabConfigEntry, ConanApi
from conan_app_launcher.settings import (
    LAST_CONFIG_FILE, DISPLAY_APP_VERSIONS, DISPLAY_APP_CHANNELS, GRID_COLUMNS, GRID_ROWS)
from conan_app_launcher.ui.app_grid.tab_app_grid import TabAppGrid
from conan_app_launcher.ui.package_explorer.local_packages import CustomProxyModel
# from conan_app_launcher.ui.add_remove_apps import AddRemoveAppsDialog
# from conan_app_launcher.ui.edit_app import EditAppDialog
from conan_app_launcher.ui.about_dialog import AboutDialog

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

    def __init__(self):
        super().__init__()
        self._icons_path = this.asset_path / "icons"

        self._ui = uic.loadUi(this.base_path / "ui" / "main.ui", baseinstance=self)
        self._about_dialog = AboutDialog(self)
        # self._new_tab = QtWidgets.QTabWidget() TODO do i need this?

        if this.ADD_APP_LINK_BUTTON:
            self._ui.add_app_link_button = QtWidgets.QPushButton(self)
            self._ui.add_app_link_button.setGeometry(765, 452, 44, 44)
            self._ui.add_app_link_button.setIconSize(QtCore.QSize(44, 44))
            self._ui.add_app_link_button.clicked.connect(self.open_new_app_link_dialog)
        if this.ADD_TAB_BUTTON:
            self._ui.add_tab_button = QtWidgets.QPushButton(self)
            self._ui.add_tab_button.setGeometry(802, 50, 28, 28)
            self._ui.add_tab_button.setIconSize(QtCore.QSize(28, 28))
            self._ui.add_tab_button.clicked.connect(self.open_new_tab_dialog)

        self._ui.tab_bar.setMovable(True)
        self._ui.tab_bar.tabBar().tabMoved.connect(self.on_tab_move)

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
        self._ui.menu_cleanup_cache.triggered.connect(self.open_cleanup_cache_dialog)
        self._ui.tab_bar.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.tab_bar.tabBar().customContextMenuRequested.connect(self.on_tab_context_menu_requested)
        self._ui.main_toolbox.currentChanged.connect(self.on_main_view_changed)
        # self.load_tabs()

        # TODO display conaninfo.txt on the right
        # self.model = QtWidgets.QFileSystemModel()
        # self.model.setRootPath(r"C:\Users\goszp\.conan\data")

        # dirModel -> setFilter(QDir: : NoDotAndDotDot |
        #                       QDir:: AllDirs);
        self.proxy = CustomProxyModel()
        storage_path = Path(ConanApi().conan.config_get("storage.path"))

        self.proxy.setRootPath(str(storage_path))

        # self.proxy.setSourceModel(self.model)
        # self.model_index = self.model.index(self.model.rootDirectory().absolutePath())
        # print(self.model.rootDirectory().absolutePath())
        # self.proxy_index = self.proxy.mapFromSource(self.model_index)
        self._ui.package_view.setModel(self.proxy)
        self._ui.package_view.setRootIndex(self.proxy.index(self.proxy.rootDirectory().absolutePath()))

        # self._ui.package_view.clicked.connect(self.on_click)
        self._ui.package_view.setColumnHidden(1, True)
        self._ui.package_view.setColumnHidden(2, True)
        self._ui.package_view.setColumnWidth(0, 310)
        # self._ui.package_view.setRootIsDecorated(False)
        # self._ui.package_view.setItemsExpandable(False)
        self._ui.package_view.selectionModel().selectionChanged.connect(
            self.on_selection_change)

        if self._ui.tab_bar.count() > 0:  # remove the default tab
            self._ui.tab_bar.removeTab(0)

    def closeEvent(self, event):  # override QMainWindow
        """ Remove qt logger, so it doesn't log into a non existant object """
        try:
            self.new_message_logged.disconnect(self.write_log)
        except Exception:
            # Sometimes the closeEvent is called twice and disconnect errors.
            pass
        Logger.remove_qt_logger()
        super().closeEvent(event)

    # Menu callbacks #

    @pyqtSlot()
    def on_main_view_changed(self):
        """ Change between main views (grid and package explorer) """
        if self._ui.main_toolbox.currentIndex() == 1:  # package view
            # hide floating grid buttons
            if this.ADD_APP_LINK_BUTTON:
                self._ui.add_app_link_button.hide()
            if this.ADD_TAB_BUTTON:
                self._ui.add_tab_button.hide()
        elif self._ui.main_toolbox.currentIndex() == 0:  # grid view
            # show floating buttons
            if this.ADD_APP_LINK_BUTTON:
                self._ui.add_app_link_button.show()
            if this.ADD_TAB_BUTTON:
                self._ui.add_tab_button.show()

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
        config_file_path = Path(this.settings.get(LAST_CONFIG_FILE))
        if config_file_path.exists():
            dialog_path = config_file_path.parent
        dialog = QtWidgets.QFileDialog(parent=self, caption="Select JSON Config File",
                                       directory=str(dialog_path), filter="JSON files (*.json)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            this.settings.set(LAST_CONFIG_FILE, dialog.selectedFiles()[0])
            self._re_init()

    @ pyqtSlot()
    def toggle_display_versions(self):
        """ Reads the current menu setting, sevaes it and updates the gui """
        version_status = self._ui.menu_set_display_versions.isChecked()
        this.settings.set(DISPLAY_APP_VERSIONS, version_status)
        self.display_versions_updated.emit(version_status)

    @ pyqtSlot()
    def toogle_display_channels(self):
        """ Reads the current menu setting, sevaes it and updates the gui """
        channel_status = self._ui.menu_set_display_channels.isChecked()
        this.settings.set(DISPLAY_APP_CHANNELS, channel_status)
        self.display_channels_updated.emit(channel_status)

    @pyqtSlot()
    def open_new_app_link_dialog(self):
        # call tab on_app_link_add
        current_tab = self._ui.tab_bar.widget(self._ui.tab_bar.currentIndex())
        current_tab.open_app_link_add_dialog()

    @ pyqtSlot()
    def on_config_change(self):
        """ Update without cleaning up. Ungrey entries and set correct icon and add hover text """
        write_config_file(Path(this.settings.get(LAST_CONFIG_FILE)), this.tab_configs)

    @ pyqtSlot(str)
    def write_log(self, text):
        """ Write the text signaled by the logger """
        self._ui.console.append(text)

    def load_icons(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(str(self._icons_path / "grid.png")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._ui.main_toolbox.setItemIcon(self.TOOLBOX_GRID_ITEM, icon)

        icon.addPixmap(QtGui.QPixmap(str(self._icons_path / "search_packages.png")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._ui.main_toolbox.setItemIcon(self.TOOLBOX_PACKAGES_ITEM, icon)
        if this.ADD_APP_LINK_BUTTON:
            self._ui.add_app_link_button.setIcon(QtGui.QIcon(str(self._icons_path / "add_link.png")))
        if this.ADD_TAB_BUTTON:
            self._ui.add_tab_button.setIcon(QtGui.QIcon(str(self._icons_path / "plus.png")))
        # menu
        self._ui.menu_cleanup_cache.setIcon(QtGui.QIcon(str(self._icons_path / "cleanup.png")))
        self._ui.menu_about_action.setIcon(QtGui.QIcon(str(self._icons_path / "about.png")))

    # Tab callbacks #

    @pyqtSlot()
    def on_tab_move(self):
        """ Refresh backend info when tabs are reordered"""
        new_list = []
        for i in range(self._ui.tab_bar.count()):
            new_list.append(self._ui.tab_bar.widget(i).config_data)
        this.tab_configs = new_list
        self.on_config_change()

    @pyqtSlot()
    def on_tab_context_menu_requested(self, position):
        index = self._ui.tab_bar.tabBar().tabAt(position)
        menu = QtWidgets.QMenu()

        rename_action = QtWidgets.QAction("Rename", self)
        rename_action.setIcon(QtGui.QIcon(str(self._icons_path / "rename.png")))
        menu.addAction(rename_action)
        rename_action.triggered.connect(lambda: self.open_tab_rename_dialog(index))

        remove_action = QtWidgets.QAction("Remove", self)
        remove_action.setIcon(QtGui.QIcon(str(self._icons_path / "delete.png")))
        menu.addAction(remove_action)
        remove_action.triggered.connect(lambda: self.on_tab_remove(index))

        new_tab_action = QtWidgets.QAction("Add new tab", self)
        new_tab_action.setIcon(QtGui.QIcon(str(self._icons_path / "plus.png")))
        menu.addAction(new_tab_action)
        new_tab_action.triggered.connect(self.open_new_tab_dialog)

        menu.exec_(self.tab_bar.tabBar().mapToGlobal(position))

    @pyqtSlot()
    def open_new_tab_dialog(self):
        # call tab on_app_link_add
        new_tab_dialog = QtWidgets.QInputDialog(self)
        text, accepted = new_tab_dialog.getText(self, 'Add tab',
                                                'Enter name:')
        if accepted:
            # do nothing on empty text
            if not text:
                return
            # add tab
            tab_config = TabConfigEntry(text)
            this.tab_configs.append(tab_config)

            tab = TabAppGrid(self, tab_config, max_columns=this.settings.get(
                GRID_COLUMNS), max_rows=this.settings.get(GRID_ROWS))
            self._ui.tab_bar.addTab(tab, text)
            self.on_config_change()

    @pyqtSlot(int)
    def open_tab_rename_dialog(self, index):
        tab: TabAppGrid = self._ui.tab_bar.widget(index)

        rename_tab_dialog = QtWidgets.QInputDialog(self)
        text, accepted = rename_tab_dialog.getText(self, 'Rename tab',
                                                   'Enter new name:', text=tab.config_data.name)
        if accepted:
            tab.config_data.name = text
            self._ui.tab_bar.setTabText(index, text)
            self.on_config_change()

    @ pyqtSlot(int)
    def on_tab_remove(self, index):
        tab: TabAppGrid = self._ui.tab_bar.widget(index)

        msg = QtWidgets.QMessageBox(parent=self)
        msg.setWindowTitle("Delete tab")
        msg.setText("Are you sure, you want to delete this tab\t")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        reply = msg.exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            this.tab_configs.remove(tab.config_data)
            self._ui.tab_bar.removeTab(index)

    def load_tabs(self):
        """ Creates new layout """
        for config_data in this.tab_configs:
            # need to save object locally, otherwise it can be destroyed in the underlying C++ layer
            tab = TabAppGrid(parent=self, config_data=config_data,
                             max_columns=this.settings.get(GRID_COLUMNS), max_rows=this.settings.get(GRID_ROWS))
            self._ui.tab_bar.addTab(tab, config_data.name)

        # always show the first tab first
        self._ui.tab_bar.setCurrentIndex(0)

    # @pyqtSlot(int)
    def on_selection_change(self):  # , index: int):
        # change folder in file view
        view_index = self._ui.package_view.selectionModel().selectedIndexes()[0]
        # proxy_index = self.proxy.mapToSource(view_index)
        # item_name = self.model.fileName(proxy_index)
        # # TODO discover upstream, if in package
        # path = self.model.fileInfo(proxy_index).absoluteFilePath()
        # c_p = Path(path) / "conaninfo.txt"
        # if c_p.is_file():
        #     text = ""
        #     with open(c_p, "r") as fp:
        #         text = fp.read()
        #     self.package_info.setText(text)

    def _re_init(self):
        """ To be called, when a new config file is loaded """
        tab_count = self._ui.tab_bar.count()
        for i in range(tab_count, 0, -1):  # delete all tabs
            self._ui.tab_bar.removeTab(i-1)
        this.conan_worker.finish_working(3)

        config_file_path = Path(this.settings.get(LAST_CONFIG_FILE))

        if config_file_path.is_file():  # escape error log on first opening
            this.tab_configs = parse_config_file(config_file_path)
        else:
            this.tab_configs = []

        # update conan info
        this.conan_worker.update_all_info()

        self.load_tabs()
