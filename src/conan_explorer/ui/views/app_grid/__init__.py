from pathlib import Path
from typing import TYPE_CHECKING, List, Type, TypeVar

import conan_explorer.app as app
from conan_explorer import AUTHOR, BUILT_IN_PLUGIN, user_save_path
from conan_explorer.app.logger import Logger
# using global module pattern
from conan_explorer.ui.common import get_themed_asset_icon
from conan_explorer.settings import AUTO_INSTALL_QUICKLAUNCH_REFS, LAST_CONFIG_FILE  # using global module pattern
from conan_explorer.ui.fluent_window import FluentWindow
from conan_explorer.ui.plugin import PluginInterfaceV1
from conan_explorer.ui.plugin.types import PluginDescription
from conan_explorer.ui.widgets import RoundedMenu, AnimatedToggle
from conan_explorer.conan_wrapper.types import ConanRef, ConanPkgRef

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QInputDialog, QMessageBox, QTabWidget, QFileDialog, QVBoxLayout)

from .model import UiAppLinkModel, UiTabModel
from .config import UiAppLinkConfig, UiTabConfig
from .tab import TabList, TabList  # TabGrid

if TYPE_CHECKING:
    from conan_explorer.ui.views.app_grid.model import UiAppGridModel
    from conan_explorer.ui.main_window import BaseSignals


class AppGridView(PluginInterfaceV1):
    load_signal = Signal() # type: ignore

    def __init__(self, parent, model: "UiAppGridModel", base_signals: "BaseSignals", page_widgets: FluentWindow.PageStore):
        plugin_descr = PluginDescription("Conan Quicklaunch", BUILT_IN_PLUGIN, AUTHOR, "", "", "", " ", False, "")
        super().__init__(parent, plugin_descr, base_signals, page_widgets) # TODO

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setContentsMargins(0, 0, 0, 0)
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideLeft)
        self.tab_widget.setUsesScrollButtons(True)
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.tab_widget)

        self.model = model
        base_signals.conan_pkg_installed.connect(self.update_conan_info)

        self.tab_widget.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_widget.tabBar().setContentsMargins(0, 0, 0, 0)
        self.tab_widget.tabBar().customContextMenuRequested.connect(self.on_tab_context_menu_requested)

        self.tab_widget.setMovable(True)
        self.tab_widget.tabBar().tabMoved.connect(self.on_tab_move)
        if self.tab_widget.count() > 0:  # remove the default tab
            self.tab_widget.removeTab(0)
        self.load_signal.connect(self.load)

    def load(self, offset=0):
        """ Creates new layout """
        self._init_right_menu()
        for tab_config in self.model.tabs:
            # need to save object locally, otherwise it can be destroyed in the underlying C++ layer
            tab = TabList(parent=self.tab_widget, model=tab_config)
            self.tab_widget.addTab(tab, tab_config.name)
            tab.load(offset)

        # always show the first tab first
        self.tab_widget.setCurrentIndex(0)

    def _init_right_menu(self):
        # Right Settings menu
        assert self._page_widgets
        quicklaunch_submenu = self._page_widgets.get_side_menu_by_type(type(self))
        assert quicklaunch_submenu
        quicklaunch_submenu.reset_widgets()
        quicklaunch_submenu.add_button_menu_entry(
            "Open Layout File", self.open_config_file_dialog, "icons/opened_folder.svg")
        quicklaunch_submenu.add_button_menu_entry(
            "Add AppLink", self.on_add_link, "icons/add_link.svg")
        quicklaunch_submenu.add_button_menu_entry(
            "Reorder AppLinks", self.on_reorder, "icons/rearrange.svg")
        quicklaunch_submenu.add_menu_line()

        quicklaunch_submenu.add_toggle_menu_entry(
            "Auto-install quicklaunch packages", self.on_toggle_auto_install, app.active_settings.get_bool(AUTO_INSTALL_QUICKLAUNCH_REFS))

    def reload_themed_icons(self):
        self.re_init(self.model)

    T = TypeVar('T')
    def findChildren(self, type: Type[T]) -> List[T]:
        return super().findChildren(type)  # type: ignore

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
        current_tab: TabList = self.tab_widget.widget(self.tab_widget.currentIndex())  # type: ignore
        current_tab.open_app_link_add_dialog()

    def on_tab_move(self):
        """ Refresh backend info when tabs are reordered"""
        reordered_tabs = []
        for i in range(self.tab_widget.count()):
            tab: TabList = self.tab_widget.widget(i) # type: ignore
            reordered_tabs.append(tab.model)
        self.model.tabs = reordered_tabs
        self.model.save()

    def on_tab_context_menu_requested(self, position):
        index = self.tab_widget.tabBar().tabAt(position)
        menu = RoundedMenu()
        self.menu = menu

        rename_action = QAction("Rename", self)
        rename_action.setIcon(QIcon(get_themed_asset_icon("icons/rename.svg")))
        menu.addAction(rename_action)
        rename_action.triggered.connect(lambda: self.on_tab_rename(index))

        remove_action = QAction("Remove", self)
        remove_action.setIcon(QIcon(get_themed_asset_icon("icons/delete.svg")))
        menu.addAction(remove_action)
        remove_action.triggered.connect(lambda: self.on_tab_remove(index))

        new_tab_action = QAction("Add new tab", self)
        new_tab_action.setIcon(QIcon(get_themed_asset_icon("icons/plus.svg")))
        menu.addAction(new_tab_action)
        new_tab_action.triggered.connect(self.on_new_tab)

        menu.exec(self.tab_widget.tabBar().mapToGlobal(position))
        return self.menu  # for testing

    def on_new_tab(self):
        # call tab on_app_link_add
        new_tab_dialog = QInputDialog(self)
        text, accepted = new_tab_dialog.getText(self, 'Add tab', 'Enter name:')
        if accepted:
            # do nothing on empty text
            if not text:
                return
            # update model
            tab_model = UiTabModel().load(UiTabConfig(text, apps=[UiAppLinkConfig()]), self.model)
            self.model.tabs.append(tab_model)
            self.model.save()
            # add tab in ui
            tab = TabList(self.tab_widget, model=tab_model)
            tab.load()
            self.tab_widget.addTab(tab, text)

    def on_tab_rename(self, index):
        tab: TabList = self.tab_widget.widget(index) # type: ignore

        rename_tab_dialog = QInputDialog(self)
        text, accepted = rename_tab_dialog.getText(self, 'Rename tab', 'Enter new name:', text=tab.model.name)
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

    def get_tabs(self) -> List[TabList]:
        return self.findChildren(TabList)

    def on_toggle_auto_install(self):
        sender_toggle: AnimatedToggle = self.sender()  # type: ignore
        status = sender_toggle.isChecked()
        app.active_settings.set(AUTO_INSTALL_QUICKLAUNCH_REFS, status)
        # model loads incrementally
        self.model.parent.loadf(app.active_settings.get_string(LAST_CONFIG_FILE))
        sender_toggle.wait_for_anim_finish()

        self.re_init(self.model)

    def open_config_file_dialog(self):
        """" Open File Dialog and load config file """
        dialog_path = user_save_path
        config_file_path = Path(app.active_settings.get_string(LAST_CONFIG_FILE))
        if config_file_path.exists():
            dialog_path = config_file_path.parent
        dialog = QFileDialog(parent=self, caption="Select JSON Config File",
                             directory=str(dialog_path), filter="JSON files (*.json)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            new_file = dialog.selectedFiles()[0]
            app.active_settings.set(LAST_CONFIG_FILE, new_file)
            # model loads incrementally
            self.model.parent.loadf(new_file)
            # conan works, model can be loaded
            self.re_init(self.model)  # loads tabs

    def on_add_link(self):
        tab: TabList = self.tab_widget.currentWidget()  # type: ignore
        tab.open_app_link_add_dialog()

    def on_reorder(self):
        tab: TabList = self.tab_widget.currentWidget()  # type: ignore
        tab.app_links[0].on_move()

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
                    if not conan_ref:  # unspecific reload
                        app_link.model.load_from_cache()

                    if app_link.model.conan_ref == conan_ref:
                        # reverse lookup - don't update an icon with other options
                        pkg_info = app.conan_api.get_local_pkg_from_id(ConanPkgRef.loads(conan_ref + ":" + pkg_id))
                        if app_link.model.conan_options:  # only compare options, if user explicitly set them
                            # user options should be a subset of full pkg options
                            if not app_link.model.conan_options.items() <= pkg_info.get("options", {}).items():
                                continue
                        if pkg_id:
                            app_link.model.set_package_folder(app.conan_api.get_package_folder(
                                ConanRef.loads(conan_ref), pkg_id))
                        else:
                            app_link.model.load_from_cache()
                    app_link.apply_conan_info()

        except Exception as e:
            Logger().error(f"Can't update AppGrid with conan info {str(e)}")

