from typing import TYPE_CHECKING, List, Tuple

import conan_explorer.app as app
from conan_explorer import asset_path
from conan_explorer.app import AsyncLoader  # using global module pattern
from conan_explorer.app.logger import Logger
from conan_explorer.conan_wrapper.types import ConanPkg, ConanPkgRef, ConanRef
from conan_explorer.app.system import (open_in_file_manager)
from conan_explorer.ui.common import show_conanfile, ConfigHighlighter
from conan_explorer.ui.dialogs import ConanRemoveDialog, ConanInstallDialog
from PySide6.QtCore import (QItemSelectionModel, QModelIndex, QObject,
                            SignalInstance)
from PySide6.QtWidgets import (QApplication, QTextBrowser,
                               QLineEdit, QTreeView, QWidget, QDialog, QVBoxLayout)
from PySide6.QtGui import QIcon
from .sel_model import PkgSelectionType, PackageFilter, PackageTreeItem, PkgSelectModel

if TYPE_CHECKING:
    from conan_explorer.ui.fluent_window import FluentWindow
    from conan_explorer.ui.main_window import BaseSignals


class PackageSelectionController(QObject):

    def __init__(self, parent: QWidget, view: QTreeView, package_filter_edit: QLineEdit, 
                 conan_pkg_selected: SignalInstance, base_signals: "BaseSignals", 
                 page_widgets: "FluentWindow.PageStore"):
        super().__init__(parent)
        self._base_signals = base_signals
        self._conan_pkg_selected = conan_pkg_selected
        self._model = None
        self._loader = AsyncLoader(self)
        self._page_widgets = page_widgets
        self._view = view
        self._package_filter_edit = package_filter_edit

        base_signals.conan_pkg_removed.connect(self.on_conan_pkg_removed)

    # Own slots

    def on_pkg_refresh_clicked(self):
        self.refresh_pkg_selection_view()

    def on_open_export_folder_requested(self):
        conan_refs = self.get_selected_conan_refs()
        if len(conan_refs) != 1:
            return
        conanfile = app.conan_api.get_conanfile_path(ConanRef.loads(conan_refs[0]))
        open_in_file_manager(conanfile)

    def on_show_conanfile_requested(self):
        conan_refs = self.get_selected_conan_refs()
        if len(conan_refs) != 1:
            return
        loader = AsyncLoader(self)
        loader.async_loading(self._view, show_conanfile, (conan_refs[0],),
                             loading_text="Opening Conanfile...")
        loader.wait_for_finished()

    def on_copy_ref_requested(self):
        conan_refs = self.get_selected_conan_refs()
        QApplication.clipboard().setText("\n".join(conan_refs))

    def on_install_ref_requested(self):
        conan_ref, pkg_id = self.get_selected_ref_with_pkg_id()
        if not conan_ref:
            return
        if pkg_id:
            conan_ref += ":" + pkg_id
        dialog = ConanInstallDialog(
            self._view, conan_ref, self._base_signals.conan_pkg_installed, lock_reference=True)
        dialog.show()

    def on_remove_ref_requested(self):
        conan_ref, pkg_id = self.get_selected_ref_with_pkg_id()
        if not conan_ref:
            return
        dialog = ConanRemoveDialog(self._view, conan_ref,
                                   pkg_id, self._base_signals.conan_pkg_removed)
        dialog.show()

    def on_conan_pkg_removed(self, conan_ref: str, pkg_id: str):
        self.refresh_pkg_selection_view()

    def on_show_build_info(self):
        conan_ref, pkg_id = self.get_selected_ref_with_pkg_id()
        if not conan_ref or not pkg_id:
            return
        pkg_info = app.conan_api.get_local_pkg_from_id(
            ConanPkgRef.loads(conan_ref + ":" + pkg_id))
        loader = AsyncLoader(self)
        loader.async_loading(self._view, app.conan_api.get_conan_buildinfo,
                             (ConanRef.loads(conan_ref), pkg_info.get("settings", ""),
                              pkg_info.get("options", {})), self.show_buildinfo_dialog,
                             loading_text="Loading build info...")
        loader.wait_for_finished()

    def show_buildinfo_dialog(self, buildinfos: str):
        if not buildinfos:
            return
        dialog = QDialog()
        dialog.setWindowIcon(QIcon(str(asset_path / "icons" / "icon.ico")))
        dialog.setWindowTitle("Build Info")
        dialog.resize(800, 500)
        verticalLayout = QVBoxLayout(dialog)
        text_browser = QTextBrowser(dialog)
        text_browser.setReadOnly(True)
        text_browser.setOpenExternalLinks(True)
        text_browser.setText(buildinfos)
        verticalLayout.addWidget(text_browser)
        self.conan_config_highlighter = ConfigHighlighter(
            text_browser.document(), "ini")
        dialog.exec()

    # Model selection helpers

    def get_selected_pkg_source_items(self) -> List[PackageTreeItem]:
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:
            return []
        model: PackageFilter = indexes[0].model()  # type: ignore
        source_items: List[PackageTreeItem] = []
        for index in indexes:
            source_items.append(model.mapToSource(
                index).internalPointer())  # type: ignore
        return source_items

    def get_selected_ref_with_pkg_id(self) -> Tuple[str, str]:
        conan_refs = self.get_selected_conan_refs()
        if len(conan_refs) != 1:
            return "", ""
        pkg_info = self.get_selected_conan_pkg_info()
        pkg_id = ""
        if pkg_info:
            pkg_id = pkg_info.get("id", "")
        return conan_refs[0], pkg_id

    def get_selected_conan_refs(self) -> List[str]:
        # no need to map from postition, since rightclick selects a single item
        source_items = self.get_selected_pkg_source_items()
        conan_refs = []
        for conan_ref_item in source_items:
            if conan_ref_item.type in [PkgSelectionType.pkg, PkgSelectionType.export]:
                conan_ref_item: PackageTreeItem = conan_ref_item.parent()  # type: ignore
            if not conan_ref_item:
                conan_refs.append("")
            conan_refs.append(conan_ref_item.item_data[0])
        return list(set(conan_refs))

    def get_selected_conan_pkg_info(self) -> ConanPkg:
        source_items = self.get_selected_pkg_source_items()
        if not len(source_items) == 1:
            return ConanPkg()
        source_item = source_items[0]
        if source_item.type == PkgSelectionType.ref:
            return ConanPkg()
        return source_item.item_data[0]

    # Global pane and cross connection slots

    def on_pkg_selection_change(self):
        # get conan ref and pkg_id and emit signal
        source_items = self.get_selected_pkg_source_items()
        if len(source_items) != 1:
            return
        if source_items[0].type in [PkgSelectionType.ref]:
            return
        conan_refs = self.get_selected_conan_refs()
        self._conan_pkg_selected.emit(
            conan_refs[0], self.get_selected_conan_pkg_info(), source_items[0].type)

    def refresh_pkg_selection_view(self, force_update=True):
        """
        Refresh all packages by reading it from local drive. Can take a while.
        """
        if self._model and not force_update:  # loads only at first init
            return
        if not self._model:
           self._model = PkgSelectModel()
        self._loader.async_loading(
            self._view, self._model.setup_model_data, (),
            self.finish_select_model_init, "Reading Packages")

    def finish_select_model_init(self):
        if self._model:
            self._view.setModel(self._model.proxy_model)
            self._view.selectionModel().selectionChanged.connect(self.on_pkg_selection_change)
            self.set_filter_wildcard()  # re-apply package filter query
        else:
            Logger().error("Can't load local packages!")

    def set_filter_wildcard(self):
        # use strip to remove unnecessary whitespace
        text = self._package_filter_edit.text().strip()  # toPlainText
        if self._model:
            self._model.proxy_model.setFilterWildcard(text)

    def find_item_in_pkg_sel_model(self, conan_ref: str, pkg_id="") -> int:
        # find the row with the matching reference
        if not self._model:
            return False
        for ref_row in range(self._model.root_item.child_count()):
            item = self._model.root_item.child_items[ref_row]
            if item.item_data[0] == conan_ref:
                if pkg_id:
                    if item.child_count() < 2: # try to fetch, pkd_id probably not loaded yet
                        item.load_children()
                    for pkg_row in range(item.child_count()):
                        pkg_item = item.child_items[pkg_row]
                        if pkg_item.item_data[0].get("id") == pkg_id:
                            return ref_row
                    return -1
                else:
                    return ref_row
        return -1

    def select_local_package_from_ref(self, conan_ref: str, export=False) -> bool:
        """ Selects a reference:id pkg in the left pane and opens the file view """
        # change to this page and loads
        self._page_widgets.get_button_by_type(type(self.parent())).click()
        self._loader.wait_for_finished()
        if not self._model:
            return False

        # Reset filter, otherwise the element to be shown could be hidden
        self._package_filter_edit.setText("*")

        # find out if we need to find a ref or or a package
        error_message_suffix = " in Local Package Explorer for selection."
        split_ref = conan_ref.split(":")
        pkg_id = ""
        if len(split_ref) > 1:  # has id
            if export:
                Logger().debug("Cannot use pkg id and export arg at the same time" +
                               error_message_suffix)
                return False
            conan_ref = split_ref[0]
            pkg_id = split_ref[1]

        # not found ref or id - start refresh package list
        if self.find_item_in_pkg_sel_model(conan_ref, pkg_id) == -1:
            self.refresh_pkg_selection_view()

        # wait for model to be loaded
        self._loader.wait_for_finished()
        ref_row = self.find_item_in_pkg_sel_model(conan_ref, pkg_id)
        if ref_row == -1:
            Logger().debug(f"Cannot find {conan_ref}" + error_message_suffix)
            return False
        Logger().debug(f"Found {conan_ref}@{str(ref_row)}" + error_message_suffix)

        # map to package view model
        proxy_index = self._model.index(ref_row, 0, QModelIndex())
        sel_model = self._view.selectionModel()
        view_model: PackageFilter = self._view.model()  # type: ignore
        self._view.expand(view_model.mapFromSource(proxy_index))

        # retrieve item from id, export or ref
        if pkg_id:
            item: PackageTreeItem = proxy_index.internalPointer()  # type: ignore
            i = 0
            for i, child_item in enumerate(item.child_items):
                if child_item.type == PkgSelectionType.pkg:
                    if child_item.item_data[0].get("id", "") == pkg_id:
                        break
            internal_sel_index = self._model.index(i, 0, proxy_index)
        else:
            if export:
                item: PackageTreeItem = proxy_index.internalPointer()  # type: ignore
                i = 0
                for i, child_item in enumerate(item.child_items):
                    if child_item.type == PkgSelectionType.export:
                        break
                internal_sel_index = self._model.index(i, 0, proxy_index)
            else:
                internal_sel_index = proxy_index

        # Scroll to item and select
        view_index = view_model.mapFromSource(internal_sel_index)
        self._view.scrollTo(view_index)
        sel_model.select(view_index, QItemSelectionModel.SelectionFlag.ClearAndSelect)
        sel_model.currentRowChanged.emit(proxy_index, internal_sel_index)
        Logger().debug(f"Selecting {view_index.data()} in Local Package Explorer")

        return True
