from typing import TYPE_CHECKING, List

from conan_app_launcher.ui.fluent_window import FluentWindow
from conan_app_launcher.ui.common.icon import get_themed_asset_image
from conan_app_launcher.ui.data import UiAppLinkConfig, UiTabConfig
from .model import UiAppLinkModel, UiTabModel
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtBoundSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QInputDialog, QMenu, QAction, QMessageBox, QTabWidget, QVBoxLayout

from .tab import TabGrid



if TYPE_CHECKING:  # pragma: no cover
    from conan_app_launcher.ui.main_window import MainWindow
    from conan_app_launcher.ui.views.app_grid.model import UiAppGridModel


class AppGridView(QWidget):

    def __init__(self, parent, model: "UiAppGridModel", conan_pkg_installed: pyqtBoundSignal, page_widgets: FluentWindow.PageStore):
        super().__init__(parent)
        self.page_widgets = page_widgets
        self.setLayout(QVBoxLayout(self))
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setElideMode(Qt.ElideLeft)
        self.tab_widget.setUsesScrollButtons(True)
        self.layout().addWidget(self.tab_widget)
        self.layout().setContentsMargins(2, 0, 2, 0)

        self.model = model
        conan_pkg_installed.connect(self.update_conan_info)

        self.tab_widget.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.tabBar().customContextMenuRequested.connect(self.on_tab_context_menu_requested)

        self.tab_widget.setMovable(True)
        self.tab_widget.tabBar().tabMoved.connect(self.on_tab_move)
        if self.tab_widget.count() > 0:  # remove the default tab
            self.tab_widget.removeTab(0)

    def re_init(self, model: "UiAppGridModel"):
        """ To be called, when a new config file is loaded """
        self.model = model
        # delete all tabs
        tab_count = self.tab_widget.count()
        for i in range(tab_count, 0, -1):
            self.tab_widget.removeTab(i-1)
        self.load()

    def re_init_all_app_links(self, force=False):
        for tab in self.get_tabs():
            tab.redraw_grid(force)

    def open_new_app_link_dialog(self):
        # call tab on_app_link_add
        current_tab = self.tab_widget.widget(self.tab_widget.currentIndex())
        current_tab.open_app_link_add_dialog()

    def on_tab_move(self):
        """ Refresh backend info when tabs are reordered"""
        reordered_tabs = []
        for i in range(self.tab_widget.count()):
            reordered_tabs.append(self.tab_widget.widget(i).model)
        self.model.tabs = reordered_tabs
        self.model.save()

    def on_tab_context_menu_requested(self, position):
        index = self.tab_widget.tabBar().tabAt(position)
        menu = QMenu(self)
        self.menu = menu

        rename_action = QAction("Rename", self)
        rename_action.setIcon(QIcon(get_themed_asset_image("icons/rename.png")))
        menu.addAction(rename_action)
        rename_action.triggered.connect(lambda: self.on_tab_rename(index))

        remove_action = QAction("Remove", self)
        remove_action.setIcon(QIcon(get_themed_asset_image("icons/delete.png")))
        menu.addAction(remove_action)
        remove_action.triggered.connect(lambda: self.on_tab_remove(index))

        new_tab_action = QAction("Add new tab", self)
        new_tab_action.setIcon(QIcon(get_themed_asset_image("icons/plus.png")))
        menu.addAction(new_tab_action)
        new_tab_action.triggered.connect(self.on_new_tab)

        menu.exec_(self.tab_widget.tabBar().mapToGlobal(position))
        return self.menu  # for testing

    def on_new_tab(self):
        # call tab on_app_link_add
        new_tab_dialog = QInputDialog(self)
        text, accepted = new_tab_dialog.getText(self, 'Add tab',
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
            tab = TabGrid(self.tab_widget, model=tab_model)
            tab.load()
            self.tab_widget.addTab(tab, text)

    def on_tab_rename(self, index):
        tab: TabGrid = self.tab_widget.widget(index)

        rename_tab_dialog = QInputDialog(self)
        text, accepted = rename_tab_dialog.getText(self, 'Rename tab',
                                                   'Enter new name:', text=tab.model.name)
        if accepted:
            tab.model.name = text
            self.tab_widget.setTabText(index, text)
            tab.model.save()

    def on_tab_remove(self, index):
        # last tab can't be deleted! # TODO dialog
        if len(self.model.tabs) == 1:
            return
        msg = QMessageBox(parent=self)
        msg.setWindowTitle("Delete tab")
        msg.setText("Are you sure, you want to delete this tab\t")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.setIcon(QMessageBox.Question)
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            self.tab_widget.removeTab(index)
            self.model.tabs.remove(self.model.tabs[index])
            self.model.save()

    def get_tabs(self) -> List[TabGrid]:
        return self.tab_widget.findChildren(TabGrid)

    def load(self):
        """ Creates new layout """
        for tab_config in self.model.tabs:

            # need to save object locally, otherwise it can be destroyed in the underlying C++ layer
            tab = TabGrid(parent=self.tab_widget, model=tab_config)
            self.tab_widget.addTab(tab, tab_config.name)
            tab.load()

        # always show the first tab first
        self.tab_widget.setCurrentIndex(0)

    def open_new_app_dialog_from_extern(self, app_config: UiAppLinkConfig):
        """ Called from pacakge explorer, where tab is unknown"""
        dialog = QInputDialog(self)
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
        if self.isHidden():  # the gui is about to shut down
            return
        # call update on every entry which has this ref
        for tab in self.get_tabs():
            for app in tab.app_links:
                app.model.update_from_cache()
                app.update_with_conan_info()
