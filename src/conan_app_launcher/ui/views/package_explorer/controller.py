import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

import conan_app_launcher.app as app
from conan_app_launcher.app.loading import AsyncLoader  # using global module pattern
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.conan_wrapper.types import ConanPkg, ConanRef
from conan_app_launcher.app.system import (calc_paste_same_dir_name, copy_path_with_overwrite,
                                           delete_path, execute_cmd, open_cmd_in_path, open_in_file_manager, run_file)
from conan_app_launcher.settings import FILE_EDITOR_EXECUTABLE
from conan_app_launcher.ui.common import FileSystemModel, show_conanfile
from conan_app_launcher.ui.common.model import re_register_signal
from conan_app_launcher.ui.config import UiAppLinkConfig
from conan_app_launcher.ui.dialogs import ConanRemoveDialog, ConanInstallDialog
from conan_app_launcher.ui.views import AppGridView
from PySide6.QtCore import (QItemSelectionModel, QMimeData, QModelIndex, QObject,
                            Qt, QUrl, SignalInstance)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QLabel,
                               QLineEdit, QMessageBox, QTreeView, QWidget)

from .model import (PROFILE_TYPE, REF_TYPE, PackageFilter, PackageTreeItem,
                    PkgSelectModel)

if TYPE_CHECKING:
    from conan_app_launcher.ui.fluent_window import FluentWindow
    from conan_app_launcher.ui.main_window import BaseSignals


class PackageSelectionController(QObject):

    def __init__(self, parent: QWidget, view: QTreeView, package_filter_edit: QLineEdit, conan_pkg_selected: SignalInstance,
                 base_signals: "BaseSignals", page_widgets: "FluentWindow.PageStore"):
        super().__init__(parent)
        self._base_signals = base_signals
        self._conan_pkg_selected = conan_pkg_selected
        self._model = None
        self._loader = AsyncLoader(self)
        self._page_widgets = page_widgets
        self._view = view
        self._package_filter_edit = package_filter_edit

        base_signals.conan_pkg_removed.connect(self.on_conan_pkg_removed)

    def on_open_export_folder_requested(self):
        conan_ref = self.get_selected_conan_ref()
        conanfile = app.conan_api.get_conanfile_path(ConanRef.loads(conan_ref))
        open_in_file_manager(conanfile)

    def on_show_conanfile_requested(self):
        conan_ref = self.get_selected_conan_ref()
        loader = AsyncLoader(self)
        loader.async_loading(self._view, show_conanfile, (conan_ref,), loading_text="Opening Conanfile...")
        loader.wait_for_finished()

    def on_pkg_refresh_clicked(self):
        self.refresh_pkg_selection_view(update=True)

    def get_selected_pkg_source_item(self) -> Optional[PackageTreeItem]:
        indexes = self._view.selectedIndexes()
        if len(indexes) != 1:
            Logger().debug(f"Mismatch in selected items for context action: {str(len(indexes))}")
            return None
        view_index = self._view.selectedIndexes()[0]
        model: PackageFilter = view_index.model()  # type: ignore
        source_item: PackageTreeItem = model.mapToSource(view_index).internalPointer()  # type: ignore
        return source_item

    def get_selected_ref_with_pkg_id(self) -> Tuple[str, str]:
        conan_ref = self.get_selected_conan_ref()
        pkg_info = self.get_selected_conan_pkg_info()
        pkg_id = ""
        if pkg_info:
            pkg_id = pkg_info.get("id", "")
        return conan_ref, pkg_id

    def get_selected_conan_ref(self) -> str:
        # no need to map from postition, since rightclick selects a single item
        source_item = self.get_selected_pkg_source_item()
        if not source_item:
            return ""
        conan_ref_item = source_item
        if source_item.type == PROFILE_TYPE:
            conan_ref_item = source_item.parent()
        if not conan_ref_item:
            return ""
        return conan_ref_item.item_data[0]

    def get_selected_conan_pkg_info(self) -> ConanPkg:
        source_item = self.get_selected_pkg_source_item()
        if not source_item or source_item.type == REF_TYPE:
            return ConanPkg()
        return source_item.item_data[0]

    def on_copy_ref_requested(self):
        conan_ref = self.get_selected_conan_ref()
        QApplication.clipboard().setText(conan_ref)

    def on_install_ref_requested(self):
        conan_ref, pkg_id = self.get_selected_ref_with_pkg_id()
        if not conan_ref:
            return
        if pkg_id:
            conan_ref += ":" + pkg_id
        dialog = ConanInstallDialog(self._view, conan_ref, self._base_signals.conan_pkg_installed, lock_ref=True)
        dialog.show()

    def on_remove_ref_requested(self):
        conan_ref, pkg_id = self.get_selected_ref_with_pkg_id()
        if not conan_ref:
            return
        dialog = ConanRemoveDialog(self._view, conan_ref, pkg_id, self._base_signals.conan_pkg_removed)
        dialog.show()

    def on_conan_pkg_removed(self, conan_ref: str, pkg_id: str):
        self.refresh_pkg_selection_view()

    # Global pane and cross connection slots

    def refresh_pkg_selection_view(self, update=True):
        """
        Refresh all packages by reading it from local drive. Can take a while.
        Update flag can be used for enabling and disabling it. 
        """
        if not update and self._model:  # loads only at first init
            return
        self._model = PkgSelectModel()
        self._loader.async_loading(
            self._view, self._model.setup_model_data, (), self.finish_select_model_init, "Reading Packages")

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
                    for pkg_row in range(item.child_count()):
                        pkg_item = item.child_items[pkg_row]
                        if pkg_item.item_data[0].get("id") == pkg_id:
                            return ref_row
                    return -1
                else:
                    return ref_row
        return -1

    def select_local_package_from_ref(self, conan_ref: str) -> bool:
        """ Selects a reference:id pkg in the left pane and opens the file view"""
        self._page_widgets.get_button_by_type(type(self.parent())).click()  # changes to this page and loads
        self._loader.wait_for_finished()

        if not self._model:  # guard
            return False

        # Reset filter, otherwise the element to be shown could be hidden
        self._package_filter_edit.setText("*")

        # find out if we need to find a ref or or a package
        split_ref = conan_ref.split(":")
        pkg_id = ""
        if len(split_ref) > 1:  # has id
            conan_ref = split_ref[0]
            pkg_id = split_ref[1]

        if self.find_item_in_pkg_sel_model(conan_ref, pkg_id) == -1:
            self.refresh_pkg_selection_view()

        # wait for model to be loaded
        self._loader.wait_for_finished()
        ref_row = self.find_item_in_pkg_sel_model(conan_ref, pkg_id)
        if ref_row == -1:
            Logger().debug(f"Cannot find {conan_ref} in Local Package Explorer for selection")
            return False
        Logger().debug(f"Found {conan_ref}@{str(ref_row)} in Local Package Explorer for selection")

        # map to package view model
        proxy_index = self._model.index(ref_row, 0, QModelIndex())
        sel_model = self._view.selectionModel()
        view_model: PackageFilter = self._view.model()  # type: ignore
        self._view.expand(view_model.mapFromSource(proxy_index))

        if pkg_id:
            item: PackageTreeItem = proxy_index.internalPointer()  # type: ignore
            i = 0
            for i in range(len(item.child_items)):
                if item.child_items[i].item_data[0].get("id", "") == pkg_id:
                    break
            internal_sel_index = self._model.index(i, 0, proxy_index)
        else:
            internal_sel_index = proxy_index

        view_index = view_model.mapFromSource(internal_sel_index)
        self._view.scrollTo(view_index)
        sel_model.select(view_index, QItemSelectionModel.SelectionFlag.ClearAndSelect)
        sel_model.currentRowChanged.emit(proxy_index, internal_sel_index)
        Logger().debug(f"Selecting {view_index.data()} in Local Package Explorer")

        return True

    def on_pkg_selection_change(self):
        # get conan ref and pkg_id and emit signal
        source_item = self.get_selected_pkg_source_item()
        if not source_item:
            return
        if source_item.type != PROFILE_TYPE:
            return
        conan_ref = self.get_selected_conan_ref()
        self._conan_pkg_selected.emit(conan_ref, self.get_selected_conan_pkg_info())


class PackageFileExplorerController(QObject):

    def __init__(self, parent: QWidget, view: QTreeView, pkg_path_label: QLabel, conan_pkg_selected: SignalInstance,
                 base_signals: "BaseSignals", page_widgets: "FluentWindow.PageStore"):
        super().__init__(parent)
        self._model = None
        self._page_widgets = page_widgets
        self._view = view
        self._pkg_path_label = pkg_path_label
        self._base_signals = base_signals
        self._conan_pkg_selected = conan_pkg_selected
        self._conan_pkg_selected.connect(self.on_pkg_selection_change)

        self._current_ref: Optional[str] = None  # loaded conan ref
        self._current_pkg: Optional[ConanPkg] = None  # loaded conan pkg info

    def on_pkg_selection_change(self, conan_ref: str, pkg_info: ConanPkg):
        """ Change folder in file view """
        self._current_ref = conan_ref
        self._current_pkg = pkg_info
        pkg_path = app.conan_api.get_package_folder(
            ConanRef.loads(conan_ref), pkg_info.get("id", ""))
        if not pkg_path.exists():
            Logger().warning(
                f"Can't find package path for {conan_ref} and {str(pkg_info)} for File View")
            return
        self._model = FileSystemModel()
        self._model.setRootPath(str(pkg_path))
        self._model.sort(0, Qt.SortOrder.AscendingOrder)
        re_register_signal(self._model.fileRenamed, self.on_file_double_click)  # type: ignore
        self._view.setModel(self._model)
        self._view.setRootIndex(self._model.index(str(pkg_path)))
        self._view.setColumnHidden(2, True)  # file type
        self._model.layoutChanged.connect(self.resize_file_columns)
        self._view.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        re_register_signal(self._view.doubleClicked, self.on_file_double_click)  # type: ignore
        # disable edit on double click, since we want to open
        self._view.setEditTriggers(QAbstractItemView.EditTrigger.EditKeyPressed)
        self._pkg_path_label.setText(str(pkg_path))
        self._pkg_path_label.setAlignment(Qt.AlignmentFlag.AlignRight) # must be called after every text set
        self._view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.resize_file_columns()

    def on_conan_pkg_removed(self, conan_ref: str, pkg_id: str):
        # clear file view if this pkg is selected
        if self._current_ref == conan_ref:
            self.close_files_view()

    def close_files_view(self):
        if self._model:
            self._model.deleteLater()
        self._model = None
        self._current_ref = ""
        self._current_pkg = None
        self._pkg_path_label.setText("")
        self._view.setModel(None)  # type: ignore
        self._pkg_path_label.setText("")

    def on_file_double_click(self, model_index):
        file_path = Path(model_index.model().fileInfo(model_index).absoluteFilePath())
        run_file(file_path, True, args="")

    def on_copy_file_as_path(self) -> str:
        file = self.get_selected_pkg_path()
        QApplication.clipboard().setText(file)
        return file

    def on_open_terminal_in_dir(self) -> int:
        selected_path = Path(self.get_selected_pkg_path())
        if selected_path.is_file():
            selected_path = selected_path.parent
        return open_cmd_in_path(selected_path)

    def on_edit_file(self):
        selected_path = Path(self.get_selected_pkg_path())
        if not selected_path.is_file():
            return
        editor = app.active_settings.get_string(FILE_EDITOR_EXECUTABLE)
        if not editor:
            Logger().info("No editor set up! Please configure it in the settings menu.")
            return
        execute_cmd([editor, str(selected_path)], False)

    def on_file_delete(self):
        path_to_delete = Path(self.get_selected_pkg_path())
        msg = QMessageBox(parent=self._view)
        msg.setWindowTitle("Delete file")
        msg.setText("Are you sure, you want to permanently delete this file/folder?\t")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        msg.setIcon(QMessageBox.Icon.Warning)
        reply = msg.exec()
        if reply != QMessageBox.StandardButton.Yes:
            return
        delete_path(Path(path_to_delete))

    def on_file_copy(self) -> Optional[QUrl]:
        file = self.get_selected_pkg_path()
        if not file:
            return None
        data = QMimeData()
        url = QUrl.fromLocalFile(file)
        data.setUrls([url])

        QApplication.clipboard().setMimeData(data)
        return url

    def on_file_paste(self):
        data = QApplication.clipboard().mimeData()
        if not data:
            return
        if not data.hasUrls():
            return
        urls = data.urls()
        for url in urls:
            # try to copy
            if not url.isLocalFile():
                continue
            sel_item_path = self.get_selected_pkg_path()
            if not sel_item_path:
                return
            if self._is_selected_item_expanded():
                dst_dir_path = Path(sel_item_path)
            else:
                dst_dir_path = Path(sel_item_path).parent
            new_path_str = os.path.join(dst_dir_path, url.fileName())
            self.paste_path(Path(url.toLocalFile()), Path(new_path_str))

    def paste_path(self, src: Path, dst: Path):
        if src == dst:  # same target -> create numbered copies
            new_dst = calc_paste_same_dir_name(dst)
            copy_path_with_overwrite(src, new_dst)
        else:
            if dst.exists():
                msg = QMessageBox(parent=self._view)
                msg.setWindowTitle("Overwrite file/folder")
                msg.setText("Are you sure, you want to overwrite this file/folder?\t")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
                msg.setIcon(QMessageBox.Icon.Warning)
                reply = msg.exec()
                if reply == QMessageBox.StandardButton.Yes:
                    copy_path_with_overwrite(src, dst)
            else:
                copy_path_with_overwrite(src, dst)

    def on_add_app_link_from_file(self):
        file_path = Path(self.get_selected_pkg_path())
        if not file_path.is_file():
            Logger().error("Please select a file, not a directory!")
            return
        conan_ref = ConanRef.loads(self._current_ref)
        # determine relpath from package
        pkg_info = self._current_pkg
        if not pkg_info:
            Logger().error("Error on trying to adding Applink: No package info found.")
            return
        pkg_path = app.conan_api.get_package_folder(conan_ref, pkg_info.get("id", ""))
        rel_path = file_path.relative_to(pkg_path)

        app_config = UiAppLinkConfig(
            name="NewLink", conan_ref=str(self._current_ref), executable=str(rel_path))
        self._page_widgets.get_page_by_type(AppGridView).open_new_app_dialog_from_extern(app_config)

    def on_open_file_in_file_manager(self, model_index):
        file_path = Path(self.get_selected_pkg_path())
        open_in_file_manager(file_path)

    def _get_pkg_file_source_item(self) -> Optional[QModelIndex]:
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:  # can be multiple - always get 0
            Logger().debug(f"No selected item for context action")
            return None
        return self._view.selectedIndexes()[0]

    def get_selected_pkg_path(self) -> str:
        if not self._model:
            return ""
        file_view_index = self._get_pkg_file_source_item()
        # if nothing selected return root
        if not file_view_index:
            return self._model.rootPath()
        return self._model.fileInfo(file_view_index).absoluteFilePath()

    def _is_selected_item_expanded(self):
        file_view_index = self._get_pkg_file_source_item()
        # if nothing selected return root
        if not file_view_index:
            return False
        return self._view.isExpanded(file_view_index)

    def resize_file_columns(self):
        if self._view:
            self._view.resizeColumnToContents(3)
            self._view.resizeColumnToContents(2)
            self._view.resizeColumnToContents(1)
            self._view.resizeColumnToContents(0)
