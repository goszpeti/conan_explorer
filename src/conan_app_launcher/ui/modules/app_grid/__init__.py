from typing import TYPE_CHECKING, List

from conan_app_launcher import ADD_APP_LINK_BUTTON, ADD_TAB_BUTTON, asset_path
from conan_app_launcher.ui.data import UiAppLinkConfig, UiTabConfig
from conan_app_launcher.ui.modules.app_grid.model import (UiAppLinkModel,
                                                          UiTabModel)
from PyQt5 import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt

from .tab import TabGrid

if TYPE_CHECKING:  # pragma: no cover
    from conan_app_launcher.ui.main_window import MainWindow
    from conan_app_launcher.ui.modules.app_grid.model import UiApplicationModel

class AppGridView():

    def __init__(self, main_window: "MainWindow", model: "UiApplicationModel"):
        self._main_window = main_window
        self.model = model
        self._icons_path = asset_path / "icons"
        self.model.conan_info_updated.connect(self.update_conan_info)

        if ADD_APP_LINK_BUTTON:
            self._main_window.ui.add_app_link_button = QtWidgets.QPushButton(self._main_window)
            self._main_window.ui.add_app_link_button.setGeometry(765, 452, 44, 44)
            self._main_window.ui.add_app_link_button.setIconSize(QtCore.QSize(44, 44))
            self._main_window.ui.add_app_link_button.clicked.connect(self.open_new_app_link_dialog)
            self._main_window.ui.add_app_link_button.setIcon(QtGui.QIcon(str(self._icons_path / "add_link.png")))

        if ADD_TAB_BUTTON:
            self._main_window.ui.add_tab_button = QtWidgets.QPushButton(self._main_window)
            self._main_window.ui.add_tab_button.setGeometry(802, 50, 28, 28)
            self._main_window.ui.add_tab_button.setIconSize(QtCore.QSize(28, 28))
            self._main_window.ui.add_tab_button.clicked.connect(self.on_new_tab)
            self._main_window.ui.add_tab_button.setIcon(QtGui.QIcon(str(self._icons_path / "plus.png")))

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
        self.load()

    def re_init_all_app_links(self):
        for tab in self.get_tabs():
            tab.redraw_grid()


    def open_new_app_link_dialog(self):
        # call tab on_app_link_add
        current_tab = self._main_window.ui.tab_bar.widget(self._main_window.ui.tab_bar.currentIndex())
        current_tab.open_app_link_add_dialog()

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
        return self.menu # for testing

    def on_new_tab(self):
        # call tab on_app_link_add
        new_tab_dialog = QtWidgets.QInputDialog(self._main_window)
        text, accepted = new_tab_dialog.getText(self._main_window, 'Add tab',
                                                'Enter name:')
        if accepted:
            # do nothing on empty text
            if not text:
                return
            # update model
            tab_model = UiTabModel().load(UiTabConfig(text, apps=[UiAppLinkConfig()]), self.model)
            self.model.tabs.append(tab_model)
            self.model.save()
            # add tab in ui
            tab = TabGrid(self._main_window.ui.tab_bar, model=tab_model)
            tab.load()
            self._main_window.ui.tab_bar.addTab(tab, text)


    def on_tab_rename(self, index):
        tab: TabGrid = self._main_window.ui.tab_bar.widget(index)

        rename_tab_dialog = QtWidgets.QInputDialog(self._main_window)
        text, accepted = rename_tab_dialog.getText(self._main_window, 'Rename tab',
                                                   'Enter new name:', text=tab.model.name)
        if accepted:
            tab.model.name = text
            self._main_window.ui.tab_bar.setTabText(index, text)
            tab.model.save()

    def on_tab_remove(self, index):
        # last tab can't be deleted! # TODO dialog
        if len(self.model.tabs) == 1:
            return
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

    def get_tabs(self) -> List[TabGrid]:
        return self._main_window.ui.tab_bar.findChildren(TabGrid)

    def load(self):
        """ Creates new layout """
            
        for tab_config in self.model.tabs:
            
            # need to save object locally, otherwise it can be destroyed in the underlying C++ layer
            tab = TabGrid(parent=self._main_window.ui.tab_bar, model=tab_config)
            self._main_window.ui.tab_bar.addTab(tab, tab_config.name)
            tab.load()

        # always show the first tab first
        self._main_window.ui.tab_bar.setCurrentIndex(0)

    def open_new_app_dialog_from_extern(self, app_config: UiAppLinkConfig):
        """ Called from pacakge explorer, where tab is unknown"""
        dialog = QtWidgets.QInputDialog(self._main_window)
        tab_list = list(item.name for item in self.model.tabs)
        model = UiAppLinkModel()
        dialog.setComboBoxItems(tab_list)
        dialog.setWindowTitle("Choose a tab!")
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            answer = dialog.textValue()
            for tab in self.get_tabs():
                if answer == tab.model.name:
                    tab.open_app_link_add_dialog(model.load(app_config, tab.model))

    def update_conan_info(self, conan_ref: str):
        # call update on every entry which has this ref
        for tab in self.get_tabs():
            for app in tab.app_links:
                app.model.update_from_cache()
                app.update_with_conan_info()
