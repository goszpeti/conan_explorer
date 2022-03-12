from pathlib import Path
from typing import TYPE_CHECKING, List

from conan_app_launcher.ui.common.icon import get_themed_asset_image
from conan_app_launcher.ui.data import UiAppLinkConfig, UiTabConfig
from .model import UiAppLinkModel, UiTabModel
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QInputDialog, QMenu, QAction, QMessageBox

from .tab import TabGrid



if TYPE_CHECKING:  # pragma: no cover
    from conan_app_launcher.ui.main_window import MainWindow
    from conan_app_launcher.ui.views.app_grid.model import UiAppGridModel


class AppGridView(QWidget):

    def __init__(self, main_window: "MainWindow", model: "UiAppGridModel"):
        super().__init__(main_window)

        self._main_window = main_window
        current_dir = Path(__file__).parent
        self._ui = uic.loadUi(current_dir / "app_grid.ui", baseinstance=self)

        self.model = model
        self.conan_pkg_installed = main_window.conan_pkg_installed
        self.conan_pkg_installed.connect(self.update_conan_info)

        self._ui.tab_bar.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.tab_bar.tabBar().customContextMenuRequested.connect(self.on_tab_context_menu_requested)

        self._ui.tab_bar.setMovable(True)
        self._ui.tab_bar.tabBar().tabMoved.connect(self.on_tab_move)
        if self._ui.tab_bar.count() > 0:  # remove the default tab
            self._ui.tab_bar.removeTab(0)

    def re_init(self, model: "UiAppGridModel"):
        """ To be called, when a new config file is loaded """
        self.model = model
        # delete all tabs
        tab_count = self._ui.tab_bar.count()
        for i in range(tab_count, 0, -1):
            self._ui.tab_bar.removeTab(i-1)
        self.load()

    def re_init_all_app_links(self):
        for tab in self.get_tabs():
            tab.redraw_grid(force=True)

    def open_new_app_link_dialog(self):
        # call tab on_app_link_add
        current_tab = self._ui.tab_bar.widget(self._ui.tab_bar.currentIndex())
        current_tab.open_app_link_add_dialog()

    def on_tab_move(self):
        """ Refresh backend info when tabs are reordered"""
        reordered_tabs = []
        for i in range(self._ui.tab_bar.count()):
            reordered_tabs.append(self._ui.tab_bar.widget(i).model)
        self.model.tabs = reordered_tabs
        self.model.save()

    def on_tab_context_menu_requested(self, position):
        index = self._ui.tab_bar.tabBar().tabAt(position)
        menu = QMenu()
        self.menu = menu

        rename_action = QAction("Rename", self._main_window)
        rename_action.setIcon(QIcon(get_themed_asset_image("icons/rename.png")))
        menu.addAction(rename_action)
        rename_action.triggered.connect(lambda: self.on_tab_rename(index))

        remove_action = QAction("Remove", self._main_window)
        remove_action.setIcon(QIcon(get_themed_asset_image("icons/delete.png")))
        menu.addAction(remove_action)
        remove_action.triggered.connect(lambda: self.on_tab_remove(index))

        new_tab_action = QAction("Add new tab", self._main_window)
        new_tab_action.setIcon(QIcon(get_themed_asset_image("icons/plus.png")))
        menu.addAction(new_tab_action)
        new_tab_action.triggered.connect(self.on_new_tab)

        menu.exec_(self._ui.tab_bar.tabBar().mapToGlobal(position))
        return self.menu  # for testing

    def on_new_tab(self):
        # call tab on_app_link_add
        new_tab_dialog = QInputDialog(self._main_window)
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
            tab = TabGrid(self._ui.tab_bar, model=tab_model)
            tab.load()
            self._ui.tab_bar.addTab(tab, text)

    def on_tab_rename(self, index):
        tab: TabGrid = self._ui.tab_bar.widget(index)

        rename_tab_dialog = QInputDialog(self._main_window)
        text, accepted = rename_tab_dialog.getText(self._main_window, 'Rename tab',
                                                   'Enter new name:', text=tab.model.name)
        if accepted:
            tab.model.name = text
            self._ui.tab_bar.setTabText(index, text)
            tab.model.save()

    def on_tab_remove(self, index):
        # last tab can't be deleted! # TODO dialog
        if len(self.model.tabs) == 1:
            return
        msg = QMessageBox(parent=self._main_window)
        msg.setWindowTitle("Delete tab")
        msg.setText("Are you sure, you want to delete this tab\t")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.setIcon(QMessageBox.Question)
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            self._ui.tab_bar.removeTab(index)
            self.model.tabs.remove(self.model.tabs[index])
            self.model.save()

    def get_tabs(self) -> List[TabGrid]:
        return self._ui.tab_bar.findChildren(TabGrid)

    def load(self):
        """ Creates new layout """
        for tab_config in self.model.tabs:

            # need to save object locally, otherwise it can be destroyed in the underlying C++ layer
            tab = TabGrid(parent=self._ui.tab_bar, model=tab_config)
            self._ui.tab_bar.addTab(tab, tab_config.name)
            tab.load()

        # always show the first tab first
        self._ui.tab_bar.setCurrentIndex(0)
        # needed, because the resizeEvent is only called for the active (first) tab
        self.re_init_all_app_links()

    def open_new_app_dialog_from_extern(self, app_config: UiAppLinkConfig):
        """ Called from pacakge explorer, where tab is unknown"""
        dialog = QInputDialog(self._main_window)
        tab_list = list(item.name for item in self.model.tabs)
        model = UiAppLinkModel()
        dialog.setLabelText("Choose a tab for the new AppLink!")
        dialog.setComboBoxItems(tab_list)
        dialog.setWindowTitle("New AppLink")
        if dialog.exec_() == QInputDialog.Accepted:
            answer = dialog.textValue()
            for tab in self.get_tabs():
                if answer == tab.model.name:
                    tab.open_app_link_add_dialog(model.load(app_config, tab.model))

    def update_conan_info(self, conan_ref: str, pkg_id: str):
        if self._main_window.isHidden():  # the gui is about to shut down
            return
        # call update on every entry which has this ref
        for tab in self.get_tabs():
            for app in tab.app_links:
                app.model.update_from_cache()
                app.update_with_conan_info()
