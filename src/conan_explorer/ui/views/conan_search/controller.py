import pprint
from typing import List, Optional

from conan_explorer.app import AsyncLoader  # using global module pattern
from conan_explorer.ui.common import show_conanfile
from conan_explorer.ui.dialogs import ConanInstallDialog
from PySide6.QtCore import Qt, SignalInstance, QObject, QModelIndex
from PySide6.QtWidgets import (QApplication, QTreeView, QPushButton, QTextBrowser, QListWidget)
from conan_explorer.ui.dialogs.pkg_diff.diff import PkgDiffDialog

from conan_explorer.ui.widgets.conan_line_edit import ConanRefLineEdit

from .model import PROFILE_TYPE, PkgSearchModel, SearchedPackageTreeItem

class ConanSearchController(QObject):

    def __init__(self, view: QTreeView, search_line: ConanRefLineEdit, search_button: QPushButton, 
                 remote_list: QListWidget, detail_view: QTextBrowser, 
                 conan_pkg_installed: Optional[SignalInstance], 
                 conan_pkg_removed: Optional[SignalInstance]) -> None:
        super().__init__(view)
        self._view = view
        self._search_line = search_line
        self._search_button = search_button
        self._remote_list = remote_list
        self._detail_view = detail_view
        self._model = PkgSearchModel()
        self._loader = AsyncLoader(self)
        self.conan_pkg_installed = conan_pkg_installed
        self.conan_pkg_removed = conan_pkg_removed

    def on_search(self):
        """ Search for the user entered text by re-initing the model"""
        # IMPORTANT! if put in async loading, the pyqt signal of the model will be created in another Qt thread
        # and not be able to emit to the GUI thread.
        if not self._search_button.isEnabled():
            return
        self._model = PkgSearchModel(self.conan_pkg_installed, self.conan_pkg_removed)
        self._loader.async_loading(
            self._view, self._load_search_model, (), self._finish_load_search_model, 
            "Searching for packages...")

        # reset info text
        self._detail_view.setText("")

    def _load_search_model(self):
        """ Initialize tree view model by searching in conan """
        self._model.setup_model_data(self._search_line.text(), self.get_selected_remotes(), 
                                     self._loader.loading_string_signal)

    def _finish_load_search_model(self, ret=None):
        """ After conan search adjust the view """
        self._view.setModel(self._model.proxy_model)
        self._resize_search_result_columns()
        self._view.sortByColumn(1, Qt.SortOrder.AscendingOrder)  # sort by remote at default
        self._view.selectionModel().selectionChanged.connect(self.on_package_selected)
        self._search_line.load_completion_refs()

    def on_package_selected(self):
        """ Display package info only for pkg type"""
        items = self.get_selected_source_items()
        if len(items) != 1:
            return
        item = items[0]
        if item.type != PROFILE_TYPE:
            return
        pkg_info = pprint.pformat(item.pkg_info).translate(
            {ord("{"): None, ord("}"): None, ord("'"): None})
        self._detail_view.setText(pkg_info)

    def on_copy_ref_requested(self):
        """ Copy the selected reference to the clipboard """
        combined_ref = self.get_selected_combined_ref()
        QApplication.clipboard().setText(combined_ref)

    def on_show_conanfile_requested(self):
        """ Show the conanfile by downloading and opening with the associated program """
        combined_ref = self.get_selected_combined_ref()
        conan_ref = combined_ref.split(":")[0]
        loader = AsyncLoader(self)
        loader.async_loading(self._view, show_conanfile, (conan_ref,), loading_text="Opening Conanfile...")
        loader.wait_for_finished()

    def on_install_pkg_requested(self):
        """ Spawn the Conan install dialog """
        combined_ref = self.get_selected_combined_ref()
        self.install(combined_ref)

    def on_install_button(self):
        self.install(self._search_line.text())

    def on_diff_requested(self):
        dialog = PkgDiffDialog(self._view)
        items = self.get_selected_source_items()
        if len(items) < 2:
            return
        for item in items:
            if not item.pkg_info:
                continue
            dialog.add_diff_item(item.pkg_info)
        dialog.show()

    def install(self, ref):
        dialog = ConanInstallDialog(self._view, ref, self.conan_pkg_installed)
        dialog.show()

    def get_selected_remotes(self) -> List[str]:
        """ Returns the user selected remotes """
        selected_remotes = []
        for i in range(self._remote_list.count()):
            item = self._remote_list.item(i)
            if item is None:
                continue
            if item.checkState() == Qt.CheckState.Checked:
                selected_remotes.append(item.text())
        return selected_remotes

    def get_selected_combined_ref(self) -> str:
        """ Returns the user selected ref in <ref>:<id> format """
        # no need to map from postition, since rightclick selects a single item
        source_items = self.get_selected_source_items()
        if len(source_items) != 1:
            return ""
        source_item = source_items[0]
        conan_ref_item = source_item
        id_str = ""
        if source_item.type == PROFILE_TYPE:
            conan_ref_item = source_item.parent()
            if source_item.pkg_info is not None:
                id_str = ":" + source_item.pkg_info.get("id", "")
        if not conan_ref_item:
            return ""
        return conan_ref_item.item_data[0] + id_str

    def get_selected_source_items(self) -> List[SearchedPackageTreeItem]:
        """ Gets the selected item from a view """
        indexes = self._get_selected_source_indexes()
        source_items: List[SearchedPackageTreeItem] = []
        for index in indexes:
            source_items.append(index.model().mapToSource(index).internalPointer()) # type: ignore

        return source_items
    
    def _get_selected_source_indexes(self) -> List[QModelIndex]:
        indexes = []
        for index in self._view.selectedIndexes():
            if index.column() == 0:  # we only need a row once
                indexes.append(index)
        return indexes

    def _resize_search_result_columns(self):
        for i in reversed(range(self._model.root_item.column_count() - 1)):
            self._view.resizeColumnToContents(i)
