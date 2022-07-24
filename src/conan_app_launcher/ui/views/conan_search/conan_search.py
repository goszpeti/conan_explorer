import pprint
from typing import List, Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.core import open_file
from conan_app_launcher.ui.common import AsyncLoader, get_themed_asset_image
from conan_app_launcher.ui.dialogs import ConanInstallDialog
from conan_app_launcher.ui.fluent_window import FluentWindow
from conan_app_launcher.ui.views import LocalConanPackageExplorer
from conan_app_launcher.ui.widgets import RoundedMenu
from conans.model.ref import ConanFileReference
from PyQt5.QtCore import QPoint, Qt, pyqtBoundSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QListWidgetItem,
                             QWidget)

from .conan_search_ui import Ui_Form
from .model import PROFILE_TYPE, PkgSearchModel, SearchedPackageTreeItem


class ConanSearchDialog(QDialog):

    def __init__(self, parent: Optional[QWidget], conan_pkg_installed: Optional[pyqtBoundSignal] = None,
                 conan_pkg_removed: Optional[pyqtBoundSignal] = None, conan_remotes_updated: Optional[pyqtBoundSignal] = None,
                 page_widgets: Optional[FluentWindow.PageStore] = None):
        # Add minimize and maximize buttons
        super().__init__(parent,  Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.page_widgets = page_widgets
        self.conan_pkg_installed = conan_pkg_installed
        self.conan_pkg_removed = conan_pkg_removed
        self.conan_remotes_updated = conan_remotes_updated

        self._ui = Ui_Form()
        self._ui.setupUi(self)

        # init search bar
        icon = QIcon(str(app.asset_path / "icons/icon.ico"))
        self.setWindowIcon(icon)

        self._ui.search_button.clicked.connect(self.on_search)
        self._ui.search_button.setEnabled(False)
        self._ui.search_line.validator_enabled = False
        self._ui.search_line.textChanged.connect(self._enable_search_button)

        self._ui.search_button.setShortcut(QKeySequence(Qt.Key_Return))

        # init remotes list
        if self.conan_remotes_updated:
            self.conan_remotes_updated.connect(self._init_remotes)
        else:  # call at least once
            self._init_remotes()
        self._pkg_result_model = PkgSearchModel()
        self._pkg_result_loader = AsyncLoader(self)
        self._ui.search_results_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.search_results_tree_view.customContextMenuRequested.connect(self.on_pkg_context_menu_requested)
        self.apply_theme()

    def _init_remotes(self):
        remotes = app.conan_api.get_remotes()
        self._ui.remote_list.clear()
        for remote in remotes:
            item = QListWidgetItem(remote.name, self._ui.remote_list)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)

    def apply_theme(self):
        icon = QIcon(get_themed_asset_image("icons/search_packages.png"))
        self._init_pkg_context_menu()
        self._ui.search_icon.setPixmap(icon.pixmap(20, 20))

    def load(self):  # TODO define interface for views
        pass

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
        self.copy_ref_action.setIcon(QIcon(get_themed_asset_image("icons/copy_link.png")))
        self.select_cntx_menu.addAction(self.copy_ref_action)
        self.copy_ref_action.triggered.connect(self.on_copy_ref_requested)

        self.show_conanfile_action = QAction("Show conanfile", self)
        self.show_conanfile_action.setIcon(QIcon(get_themed_asset_image("icons/file_preview.png")))
        self.select_cntx_menu.addAction(self.show_conanfile_action)
        self.show_conanfile_action.triggered.connect(self.on_show_conanfile_requested)

        self.install_pkg_action = QAction("Install package", self)
        self.install_pkg_action.setIcon(QIcon(get_themed_asset_image("icons/download_pkg.png")))
        self.select_cntx_menu.addAction(self.install_pkg_action)
        self.install_pkg_action.triggered.connect(self.on_install_pkg_requested)

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
        item = self.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        if item.empty:
            return
        if item.is_installed:
            self.show_in_pkg_exp_action.setEnabled(True)
        else:
            self.show_in_pkg_exp_action.setEnabled(False)
        self.select_cntx_menu.exec_(self._ui.search_results_tree_view.mapToGlobal(position))

    @pyqtSlot()
    def on_search(self):
        """ Search for the user entered text by re-initing the model"""
        # IMPORTANT! if put in async loading, the pyqt signal of the model will be created in another Qt thread
        # and not be able to emit to the GUI thread.
        if not self._ui.search_button.isEnabled():
            return
        self._pkg_result_model = PkgSearchModel(self.conan_pkg_installed, self.conan_pkg_removed)
        self._pkg_result_loader.async_loading(
            self, self._load_search_model, (), self._finish_load_search_model, "Searching for packages...")
        # reset info text
        self._ui.package_info_text.setText("")

    @pyqtSlot()
    def on_show_in_pkg_exp(self):
        """ Switch to the main gui and select the item (ref or pkg) in the Local Package Explorer. """
        item = self.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        if not self.page_widgets:
            return
        self.page_widgets.get_page_by_type(LocalConanPackageExplorer).select_local_package_from_ref(
            item.get_conan_ref(), refresh=True)

    def _load_search_model(self):
        """ Initialize tree view model by searching in conan """
        self._pkg_result_model.setup_model_data(self._ui.search_line.text(), self.get_selected_remotes())

    def _finish_load_search_model(self):
        """ After conan search adjust the view """
        self._ui.search_results_tree_view.setModel(self._pkg_result_model.proxy_model)
        self._resize_package_columns()
        self._ui.search_results_tree_view.sortByColumn(1, Qt.AscendingOrder)  # sort by remote at default
        self._ui.search_results_tree_view.selectionModel().selectionChanged.connect(self.on_package_selected)

    @pyqtSlot()
    def on_package_selected(self):
        """ Display package info only for pkg ref"""
        item = self.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        if item.type != PROFILE_TYPE:
            return
        pkg_info = pprint.pformat(item.pkg_data).translate(
            {ord("{"): None, ord("}"): None, ord(","): None, ord("'"): None})
        self._ui.package_info_text.setText(pkg_info)

    @pyqtSlot()
    def on_copy_ref_requested(self):
        """ Copy the selected reference to the clipboard """
        combined_ref = self.get_selected_combined_ref()
        QApplication.clipboard().setText(combined_ref)

    @pyqtSlot()
    def on_show_conanfile_requested(self):
        """ Show the conanfile by downloading and opening with the associated program """
        combined_ref = self.get_selected_combined_ref()
        conan_ref = combined_ref.split(":")[0]
        conanfile = app.conan_api.get_conanfile_path(ConanFileReference.loads(conan_ref))
        loader = AsyncLoader(self)
        loader.async_loading(self, open_file, (conanfile,), loading_text="Opening Conanfile...")
        loader.wait_for_finished()

    @pyqtSlot()
    def on_install_pkg_requested(self):
        """ Spawn the Conan install dialog """
        combined_ref = self.get_selected_combined_ref()
        dialog = ConanInstallDialog(self, combined_ref, self.conan_pkg_installed)
        dialog.show()

    def get_selected_remotes(self) -> List[str]:
        """ Returns the user selected remotes """
        selected_remotes = []
        for i in range(self._ui.remote_list.count()):
            item = self._ui.remote_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_remotes.append(item.text())
        return selected_remotes

    def get_selected_combined_ref(self) -> str:
        """ Returns the user selected ref in <ref>:<id> format """
        # no need to map from postition, since rightclick selects a single item
        source_item = self.get_selected_source_item(self._ui.search_results_tree_view)
        if not source_item:
            return ""
        conan_ref_item = source_item
        id_str = ""
        if source_item.type == PROFILE_TYPE:
            conan_ref_item = source_item.parent()
            id_str = ":" + source_item.pkg_data.get("id", "")
        if not conan_ref_item:
            return ""
        return conan_ref_item.item_data[0] + id_str

    def get_selected_source_item(self, view) -> Optional[SearchedPackageTreeItem]:
        """ Gets the selected item from a view """
        indexes = view.selectedIndexes()
        if not indexes:
            return None
        view_index = view.selectedIndexes()[0]
        source_item = view_index.model().mapToSource(view_index).internalPointer()
        return source_item

    def resizeEvent(self, a0) -> None:  # override QtGui.QResizeEvent
        super().resizeEvent(a0)
        self._resize_package_columns()
        
    def _resize_package_columns(self):
        self._ui.search_results_tree_view.resizeColumnToContents(2)
        self._ui.search_results_tree_view.resizeColumnToContents(1)
        self._ui.search_results_tree_view.resizeColumnToContents(0)
