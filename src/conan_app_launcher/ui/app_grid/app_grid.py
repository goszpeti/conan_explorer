from pathlib import Path
from typing import TYPE_CHECKING, List

import conan_app_launcher as this
from conan_app_launcher.components import TabConfigEntry, parse_config_file
from conan_app_launcher.settings import (GRID_COLUMNS, GRID_ROWS,
                                         LAST_CONFIG_FILE)
from PyQt5 import QtCore, QtGui, QtWidgets

from .tab_app_grid import TabAppGrid

Qt = QtCore.Qt

if TYPE_CHECKING:
    from conan_app_launcher.ui.main_window import MainUi


class AppGrid():

    def __init__(self, main_window: "MainUi"):
        self._main_window = main_window
        self._icons_path = this.asset_path / "icons"

        self._main_window.ui.tab_bar.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self._main_window.ui.tab_bar.tabBar().customContextMenuRequested.connect(self.on_tab_context_menu_requested)

        self._main_window.ui.tab_bar.setMovable(True)
        self._main_window.ui.tab_bar.tabBar().tabMoved.connect(self.on_tab_move)
        if self._main_window.ui.tab_bar.count() > 0:  # remove the default tab
            self._main_window.ui.tab_bar.removeTab(0)

    def re_init(self):
        """ To be called, when a new config file is loaded """
        tab_count = self._main_window.ui.tab_bar.count()
        for i in range(tab_count, 0, -1):  # delete all tabs
            self._main_window.ui.tab_bar.removeTab(i-1)

        if this.conan_worker:
            this.conan_worker.finish_working(3)

        config_file_path = Path(this.settings.get_string(LAST_CONFIG_FILE))

        if config_file_path.is_file():  # escape error log on first opening
            this.tab_configs = parse_config_file(config_file_path)
        else:
            this.tab_configs = []

        # update conan info
        if this.conan_worker:
            this.conan_worker.update_all_info()

        self.load_tabs()

    def on_tab_move(self):
        """ Refresh backend info when tabs are reordered"""
        new_list = []
        for i in range(self._main_window.ui.tab_bar.count()):
            new_list.append(self._main_window.ui.tab_bar.widget(i).config_data)
        this.tab_configs = new_list
        self._main_window.save_config()

    def on_tab_context_menu_requested(self, position):
        index = self._main_window.ui.tab_bar.tabBar().tabAt(position)
        menu = QtWidgets.QMenu()
        self.menu = menu

        rename_action = QtWidgets.QAction("Rename", self._main_window)
        rename_action.setIcon(QtGui.QIcon(str(self._icons_path / "rename.png")))
        menu.addAction(rename_action)
        rename_action.triggered.connect(lambda: self.on_tab_rename(index))

        remove_action = QtWidgets.QAction("Remove", self._main_window)
        remove_action.setIcon(QtGui.QIcon(str(self._icons_path / "delete.png")))
        menu.addAction(remove_action)
        remove_action.triggered.connect(lambda: self.on_tab_remove(index))

        new_tab_action = QtWidgets.QAction("Add new tab", self._main_window)
        new_tab_action.setIcon(QtGui.QIcon(str(self._icons_path / "plus.png")))
        menu.addAction(new_tab_action)
        new_tab_action.triggered.connect(self.on_new_tab)

        menu.exec_(self._main_window.ui.tab_bar.tabBar().mapToGlobal(position))
        self.menu = None

    def on_new_tab(self):
        # call tab on_app_link_add
        new_tab_dialog = QtWidgets.QInputDialog(self._main_window)
        text, accepted = new_tab_dialog.getText(self._main_window, 'Add tab',
                                                'Enter name:')
        if accepted:
            # do nothing on empty text
            if not text:
                return
            # add tab
            tab_config = TabConfigEntry(text)
            this.tab_configs.append(tab_config)

            tab = TabAppGrid(self._main_window.ui.tab_bar, tab_config,
                             max_columns=this.settings.get_int(GRID_COLUMNS),
                             max_rows=this.settings.get_int(GRID_ROWS))
            self._main_window.ui.tab_bar.addTab(tab, text)
            self._main_window.ui.save_config()

    def on_tab_rename(self, index):
        tab: TabAppGrid = self._main_window.ui.tab_bar.widget(index)

        rename_tab_dialog = QtWidgets.QInputDialog(self._main_window)
        text, accepted = rename_tab_dialog.getText(self._main_window, 'Rename tab',
                                                   'Enter new name:', text=tab.config_data.name)
        if accepted:
            tab.config_data.name = text
            self._main_window.ui.tab_bar.setTabText(index, text)
            self._main_window.save_config()

    def on_tab_remove(self, index):
        tab: TabAppGrid = self._main_window.ui.tab_bar.widget(index)

        msg = QtWidgets.QMessageBox(parent=self._main_window)
        msg.setWindowTitle("Delete tab")
        msg.setText("Are you sure, you want to delete this tab\t")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        reply = msg.exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            this.tab_configs.remove(tab.config_data)
            self._main_window.ui.tab_bar.removeTab(index)
            self._main_window.save_config()

    def get_tabs(self) -> List[TabAppGrid]:
        return self._main_window.ui.tab_bar.findChildren(TabAppGrid)

    def load_tabs(self):
        """ Creates new layout """
        for config_data in this.tab_configs:
            # need to save object locally, otherwise it can be destroyed in the underlying C++ layer
            tab = TabAppGrid(parent=self._main_window.ui.tab_bar, config_data=config_data,
                             max_columns=this.settings.get_int(GRID_COLUMNS), max_rows=this.settings.get_int(GRID_ROWS))
            self._main_window.ui.tab_bar.addTab(tab, config_data.name)

        # always show the first tab first
        self._main_window.ui.tab_bar.setCurrentIndex(0)
