from pathlib import Path
from typing import TYPE_CHECKING, List

from conan_app_launcher import asset_path
import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher.settings import (GRID_COLUMNS, GRID_ROWS)
from conan_app_launcher.ui.data import UiTabConfig

from PyQt5 import QtCore, QtGui, QtWidgets

from conan_app_launcher.ui.modules.app_grid.model import UiTabModel

Qt = QtCore.Qt

from .tab import TabAppGrid

if TYPE_CHECKING:  # pragma: no cover
    from conan_app_launcher.ui.main_window import MainWindow
    from conan_app_launcher.ui.modules.app_grid.model import UiApplicationModel

class AppGrid():

    def __init__(self, main_window: "MainWindow", model: "UiApplicationModel"):
        self._main_window = main_window
        self.model = model
        self._icons_path = asset_path / "icons"

        self._main_window.ui.tab_bar.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self._main_window.ui.tab_bar.tabBar().customContextMenuRequested.connect(self.on_tab_context_menu_requested)

        self._main_window.ui.tab_bar.setMovable(True)
        self._main_window.ui.tab_bar.tabBar().tabMoved.connect(self.on_tab_move)
        if self._main_window.ui.tab_bar.count() > 0:  # remove the default tab
            self._main_window.ui.tab_bar.removeTab(0)

    def re_init(self, model):
        """ To be called, when a new config file is loaded """
        self.model = model
        # delete all tabs
        tab_count = self._main_window.ui.tab_bar.count()
        for i in range(tab_count, 0, -1): 
            self._main_window.ui.tab_bar.removeTab(i-1)

        # update conan info
        if app.conan_worker:
            app.conan_worker.finish_working(3)
            app.conan_worker.update_all_info(self.model.get_all_conan_refs())

        self.load_tabs()

    def on_tab_move(self):
        """ Refresh backend info when tabs are reordered"""
        reordered_tabs = []
        for i in range(self._main_window.ui.tab_bar.count()):
            reordered_tabs.append(self._main_window.ui.tab_bar.widget(i).model)
        self.model.tabs = reordered_tabs
        self.model.save()

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
            # TODO add to model (move to extra function in model?)
            tab_model = UiTabModel().load(UiTabConfig(text), self.model)
            self.model.tabs.append(tab_model)
            self.model.save()
            # add tab
            tab = TabAppGrid(self._main_window.ui.tab_bar,
                             max_columns=app.active_settings.get_int(GRID_COLUMNS),
                             max_rows=app.active_settings.get_int(GRID_ROWS), model=tab_model)
            self._main_window.ui.tab_bar.addTab(tab, text)


    def on_tab_rename(self, index):
        tab: TabAppGrid = self._main_window.ui.tab_bar.widget(index)

        rename_tab_dialog = QtWidgets.QInputDialog(self._main_window)
        text, accepted = rename_tab_dialog.getText(self._main_window, 'Rename tab',
                                                   'Enter new name:', text=tab.model.name)
        if accepted:
            tab.model.name = text
            self._main_window.ui.tab_bar.setTabText(index, text)
            tab.model.save()

    def on_tab_remove(self, index):
        #tab: TabAppGrid = self._main_window.ui.tab_bar.widget(index)

        msg = QtWidgets.QMessageBox(parent=self._main_window)
        msg.setWindowTitle("Delete tab")
        msg.setText("Are you sure, you want to delete this tab\t")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        reply = msg.exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            self._main_window.ui.tab_bar.removeTab(index)
            self.model.tabs.remove(self.model.tabs[index])
            self.model.save()

    def get_tabs(self) -> List[TabAppGrid]:
        return self._main_window.ui.tab_bar.findChildren(TabAppGrid)

    def load_tabs(self):
        """ Creates new layout """
        for tab_config in self.model.tabs:
            
            # need to save object locally, otherwise it can be destroyed in the underlying C++ layer
            tab = TabAppGrid(parent=self._main_window.ui.tab_bar, max_columns=app.active_settings.get_int(GRID_COLUMNS),
                             max_rows=app.active_settings.get_int(GRID_ROWS), model=tab_config)
            self._main_window.ui.tab_bar.addTab(tab, tab_config.name)
            tab.load()

        # always show the first tab first
        self._main_window.ui.tab_bar.setCurrentIndex(0)
