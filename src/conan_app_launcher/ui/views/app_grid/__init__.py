from typing import TYPE_CHECKING, List, Type, TypeVar, Union

import conan_app_launcher.app as app
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.settings import APPLIST_ENABLED  # using global module pattern
from conan_app_launcher.ui.common.icon import get_themed_asset_image
from conan_app_launcher.ui.config import UiAppLinkConfig, UiTabConfig
from conan_app_launcher.ui.fluent_window import FluentWindow
from conan_app_launcher.ui.widgets import RoundedMenu
from conan_app_launcher.core.conan import ConanFileReference, PackageReference

from PySide6.QtCore import Qt, SignalInstance, Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QInputDialog, QMessageBox, QTabWidget,
                             QVBoxLayout, QWidget)

from .model import UiAppLinkModel, UiTabModel
from .tab import TabBase, TabGrid, TabList

if TYPE_CHECKING:
    from conan_app_launcher.ui.views.app_grid.model import UiAppGridModel


class AppGridView(QWidget):
    load_signal = Signal()

    def __init__(self, parent, model: "UiAppGridModel", conan_pkg_installed: SignalInstance, page_widgets: FluentWindow.PageStore):
        super().__init__(parent)
        self.page_widgets = page_widgets
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setContentsMargins(0, 0, 0, 0)
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideLeft)
        self.tab_widget.setUsesScrollButtons(True)
        self.layout().addWidget(self.tab_widget)

        self.model = model
        conan_pkg_installed.connect(self.update_conan_info)

        self.tab_widget.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_widget.tabBar().setContentsMargins(0, 0, 0, 0)
        self.tab_widget.tabBar().customContextMenuRequested.connect(self.on_tab_context_menu_requested)

        self.tab_widget.setMovable(True)
        self.tab_widget.tabBar().tabMoved.connect(self.on_tab_move)
        if self.tab_widget.count() > 0:  # remove the default tab
            self.tab_widget.removeTab(0)
        self.load_signal.connect(self.load)

    def reload_themed_icons(self):
        self.re_init(self.model)

    T = TypeVar('T')
    def findChildren(self, type: Type[T]) -> List[T]:
        return super().findChildren(type) # type: ignore

    def re_init(self, model: "UiAppGridModel", offset=0):
        """ To be called, when a new config file is loaded """
        self.model = model
        # clear all tabs and flag them for later deletion
        self.tab_widget.clear()
        for tab in self.get_tabs():
            tab.deleteLater()
        self.load(offset)

    def re_init_all_app_links(self, force=False):
        for tab in self.get_tabs():
            tab.redraw(force)

    def open_new_app_link_dialog(self):
        # call tab on_app_link_add
        current_tab: TabBase = self.tab_widget.widget(self.tab_widget.currentIndex()) # type: ignore
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
        menu = RoundedMenu()
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

        menu.exec(self.tab_widget.tabBar().mapToGlobal(position))
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
            tab = self.get_tab_type()(self.tab_widget, model=tab_model)
            tab.load()
            self.tab_widget.addTab(tab, text)

    def on_tab_rename(self, index):
        tab: TabBase = self.tab_widget.widget(index)

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
        msg.setText("Are you sure, you want to delete this tab?\t")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        msg.setIcon(QMessageBox.Icon.Question)
        reply = msg.exec()
        if reply == QMessageBox.StandardButton.Yes:
            self.tab_widget.removeTab(index)
            self.model.tabs.remove(self.model.tabs[index])
            self.model.save()

    def get_tabs(self) -> List[Union[TabGrid, TabList]]:
        return self.findChildren(self.get_tab_type())

    def load(self, offset=0):
        """ Creates new layout """
        for tab_config in self.model.tabs:
            # need to save object locally, otherwise it can be destroyed in the underlying C++ layer
            tab = self.get_tab_type()(parent=self.tab_widget, model=tab_config)
            self.tab_widget.addTab(tab, tab_config.name)
            tab.load(offset)

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
        if dialog.exec() == QInputDialog.DialogCode.Accepted:
            answer = dialog.textValue()
            for tab in self.get_tabs():
                if answer == tab.model.name:
                    tab.open_app_link_add_dialog(model.load(app_config, tab.model))
                    break

    def update_conan_info(self, conan_ref: str, pkg_id: str):
        if not self.isEnabled():  # the gui is about to shut down
            return
        try:
            for tab in self.get_tabs():
                for app_link in tab.app_links:
                    # Catch shutdown
                    if not self.isEnabled():
                        return
                    if not conan_ref: # unspecific reload
                        app_link.model.load_from_cache()

                    if app_link.model.conan_ref == conan_ref:
                        # reverse lookup - don't update an icon with other options
                        pkg_info = app.conan_api.get_local_pkg_from_id(PackageReference.loads(conan_ref + ":" + pkg_id))
                        if app_link.model.conan_options: # only compare options, if user explicitly set them
                            # user options should be a subset of full pkg options
                            if not app_link.model.conan_options.items() <= pkg_info.get("options", {}).items():
                                continue
                        if pkg_id:
                            app_link.model.set_package_folder(app.conan_api.get_package_folder(ConanFileReference.loads(conan_ref), pkg_id))
                        app_link.model.load_from_cache()
                    app_link.apply_conan_info()

        except Exception as e:
            Logger().error(f"Can't update AppGrid with conan info {str(e)}")


    @classmethod
    def get_tab_type(cls):
        if app.active_settings.get_bool(APPLIST_ENABLED):
            return TabList
        else:
            return TabGrid


