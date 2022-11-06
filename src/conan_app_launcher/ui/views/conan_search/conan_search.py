from typing import TYPE_CHECKING, Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.ui.common import get_themed_asset_image
from conan_app_launcher.ui.fluent_window.plugins import PluginInterface
from conan_app_launcher.ui.views import LocalConanPackageExplorer
from conan_app_launcher.ui.widgets import RoundedMenu
from PyQt6.QtCore import QPoint, Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QKeySequence, QAction
from PyQt6.QtWidgets import (QListWidgetItem, QWidget)

from .conan_search_ui import Ui_Form
from .controller import ConanSearchController


if TYPE_CHECKING:
    from conan_app_launcher.ui.fluent_window import FluentWindow
    from conan_app_launcher.ui.main_window import BaseSignals


class ConanSearchView(PluginInterface):

    def __init__(self, parent: QWidget, base_signals: Optional["BaseSignals"],
                 page_widgets: Optional["FluentWindow.PageStore"] = None):
        # Add minimize and maximize buttons
        super().__init__(parent, base_signals, page_widgets)

        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.load_signal.connect(self.load)

    def load(self):
        conan_pkg_installed = None
        conan_pkg_removed = None
        if self._base_signals:
            conan_pkg_installed = self._base_signals.conan_pkg_installed
            conan_pkg_removed = self._base_signals.conan_pkg_removed

        self._search_controller = ConanSearchController(
            self._ui.search_results_tree_view, self._ui.search_line, self._ui.search_button, self._ui.remote_list,
            self._ui.package_info_text, conan_pkg_installed, conan_pkg_removed)

        self._ui.search_button.clicked.connect(self._search_controller.on_search)
        self._ui.search_button.setEnabled(False)
        self._ui.search_line.validator_enabled = False
        self._ui.search_line.textChanged.connect(self._enable_search_button)
        self._ui.search_button.setShortcut(QKeySequence(Qt.Key.Key_Return))

        # init remotes list
        if self._base_signals:
            self._base_signals.conan_remotes_updated.connect(self._init_remotes)
        else:
            self._init_remotes()
        self._ui.search_results_tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._ui.search_results_tree_view.customContextMenuRequested.connect(self.on_pkg_context_menu_requested)
        self._init_pkg_context_menu()
        self.set_themed_icon(self._ui.search_icon, "icons/search_packages.png", size=(20, 20))

    def _init_remotes(self):
        remotes = app.conan_api.get_remotes()
        self._ui.remote_list.clear()
        for remote in remotes:
            item = QListWidgetItem(remote.name, self._ui.remote_list)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)

    def _enable_search_button(self):
        """ Enable search button from minimum 3 characters onwards"""
        if len(self._ui.search_line.text()) > 2:
            self._ui.search_button.setEnabled(True)
        else:
            self._ui.search_button.setEnabled(False)

    def _init_pkg_context_menu(self):
        """ Initalize context menu with all actions """
        self.select_cntx_menu = RoundedMenu()

        self.copy_ref_action = QAction("Copy reference", self)
        self.set_themed_icon(self.copy_ref_action, "icons/copy_link.png")
        self.select_cntx_menu.addAction(self.copy_ref_action)
        self.copy_ref_action.triggered.connect(self._search_controller.on_copy_ref_requested)

        self.show_conanfile_action = QAction("Show conanfile", self)
        self.show_conanfile_action.setIcon(QIcon(get_themed_asset_image("icons/file_preview.png")))
        self.select_cntx_menu.addAction(self.show_conanfile_action)
        self.show_conanfile_action.triggered.connect(self._search_controller.on_show_conanfile_requested)

        self.install_pkg_action = QAction("Install package", self)
        self.install_pkg_action.setIcon(QIcon(get_themed_asset_image("icons/download_pkg.png")))
        self.select_cntx_menu.addAction(self.install_pkg_action)
        self.install_pkg_action.triggered.connect(self._search_controller.on_install_pkg_requested)

        self.show_in_pkg_exp_action = QAction("Show in Package Explorer", self)
        self.show_in_pkg_exp_action.setIcon(QIcon(
            get_themed_asset_image("icons/search_packages.png")))
        self.select_cntx_menu.addAction(self.show_in_pkg_exp_action)
        self.show_in_pkg_exp_action.triggered.connect(self.on_show_in_pkg_exp)

    @pyqtSlot(QPoint)
    def on_pkg_context_menu_requested(self, position: QPoint):
        """ 
        Executes, when context menu is requested. 
        This is done to dynamically grey out some options depending on the item type.
        """
        item = self._search_controller.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        if item.empty:
            return
        if item.is_installed:
            self.show_in_pkg_exp_action.setEnabled(True)
        else:
            self.show_in_pkg_exp_action.setEnabled(False)
        self.select_cntx_menu.exec(self._ui.search_results_tree_view.mapToGlobal(position))

    @pyqtSlot()
    def on_show_in_pkg_exp(self):
        """ Switch to the main gui and select the item (ref or pkg) in the Local Package Explorer. """
        item = self._search_controller.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        if not self._page_widgets:
            return
        self._page_widgets.get_page_by_type(LocalConanPackageExplorer).select_local_package_from_ref(
            item.get_conan_ref())

    def resizeEvent(self, a0) -> None:  # override QtGui.QResizeEvent
        super().resizeEvent(a0)
        self._search_controller._resize_package_columns()
