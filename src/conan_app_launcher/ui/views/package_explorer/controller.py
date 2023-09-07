import os
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple

import conan_app_launcher.app as app
from conan_app_launcher import asset_path
from conan_app_launcher.app.loading import AsyncLoader  # using global module pattern
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.conan_wrapper.types import ConanPkg, ConanPkgRef, ConanRef
from conan_app_launcher.app.system import (calc_paste_same_dir_name, open_in_file_manager,
    copy_path_with_overwrite, delete_path, execute_cmd,  open_cmd_in_path, run_file)
from conan_app_launcher.settings import FILE_EDITOR_EXECUTABLE
from conan_app_launcher.ui.common import show_conanfile, re_register_signal, ConfigHighlighter
from conan_app_launcher.ui.config import UiAppLinkConfig
from conan_app_launcher.ui.dialogs import ConanRemoveDialog, ConanInstallDialog
from conan_app_launcher.ui.views import AppGridView
from PySide6.QtCore import (QItemSelectionModel, QMimeData, QModelIndex, QObject,
                            Qt, QUrl, SignalInstance)
from PySide6.QtWidgets import (QApplication, QTextBrowser, QLineEdit, QMessageBox, 
                               QTreeView, QWidget, QDialog, QVBoxLayout)
from PySide6.QtGui import QIcon
from .model import (PkgSelectionType, CalFileSystemModel, PackageFilter, PackageTreeItem,
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

    def on_pkg_refresh_clicked(self):
        self.refresh_pkg_selection_view(update=True)

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

    def on_show_build_info(self):
        conan_ref, pkg_id = self.get_selected_ref_with_pkg_id()
        pkg_info = app.conan_api.get_local_pkg_from_id(ConanPkgRef.loads(conan_ref + ":" + pkg_id))
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
        self.conan_config_highlighter = ConfigHighlighter(text_browser.document(), "ini")
        dialog.exec()

    def get_selected_pkg_source_items(self) -> List[PackageTreeItem]:
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:
            return []
        model: PackageFilter = indexes[0].model()  # type: ignore
        source_items: List[PackageTreeItem] = []
        for index in indexes:
            source_items.append(model.mapToSource(index).internalPointer())  # type: ignore
        return source_items

    def get_selected_ref_with_pkg_id(self) -> Tuple[str, str]:
        conan_refs = self.get_selected_conan_refs()
        if len(conan_refs) > 1:
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
                conan_ref_item: PackageTreeItem = conan_ref_item.parent() # type: ignore
            if not conan_ref_item:
                conan_refs.append("")
            conan_refs.append(conan_ref_item.item_data[0])
        return list(set(conan_refs))

    def get_selected_conan_pkg_info(self) -> ConanPkg:
        source_items = self.get_selected_pkg_source_items()
        if not len(source_items) == 1:
            return ConanPkg()
        source_item = source_items[0]
        if  source_item.type == PkgSelectionType.ref:
            return ConanPkg()
        return source_item.item_data[0]

    def on_copy_ref_requested(self):
        conan_refs = self.get_selected_conan_refs()
        QApplication.clipboard().setText("\n".join(conan_refs))

    def on_install_ref_requested(self):
        conan_ref, pkg_id = self.get_selected_ref_with_pkg_id()
        if not conan_ref:
            return
        if pkg_id:
            conan_ref += ":" + pkg_id
        dialog = ConanInstallDialog(self._view, conan_ref, self._base_signals.conan_pkg_installed, lock_reference=True)
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

    def select_local_package_from_ref(self, conan_ref: str, export=False) -> bool:
        """ Selects a reference:id pkg in the left pane and opens the file view """
        self._page_widgets.get_button_by_type(type(self.parent())).click()  # changes to this page and loads
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

        view_index = view_model.mapFromSource(internal_sel_index)
        self._view.scrollTo(view_index)
        sel_model.select(view_index, QItemSelectionModel.SelectionFlag.ClearAndSelect)
        sel_model.currentRowChanged.emit(proxy_index, internal_sel_index)
        Logger().debug(f"Selecting {view_index.data()} in Local Package Explorer")

        return True

    def on_pkg_selection_change(self):
        # get conan ref and pkg_id and emit signal
        source_items = self.get_selected_pkg_source_items()
        if len(source_items) != 1:
            return
        if source_items[0].type in [PkgSelectionType.ref, PkgSelectionType.editable]:
            return
        conan_refs = self.get_selected_conan_refs()
        self._conan_pkg_selected.emit(conan_refs[0], self.get_selected_conan_pkg_info(), source_items[0].type)


class PackageFileExplorerController(QObject):

    def __init__(self, parent: QWidget, view: QTreeView, pkg_path_label: QTextBrowser, 
                 conan_pkg_selected: SignalInstance, base_signals: "BaseSignals", 
                 page_widgets: "FluentWindow.PageStore"):
        super().__init__(parent)
        self._model = None
        self._page_widgets = page_widgets
        self._view = view
        self._pkg_path_label = pkg_path_label
        self._base_signals = base_signals
        self._conan_pkg_selected = conan_pkg_selected
        self._type = PkgSelectionType.ref

        self._current_ref: Optional[str] = None  # loaded conan ref
        self._current_pkg: Optional[ConanPkg] = None  # loaded conan pkg info

    def get_conan_pkg_info(self):
        return self._current_pkg

    def get_conan_pkg_type(self):
        return self._type

    def on_pkg_selection_change(self, conan_ref: str, pkg_info: ConanPkg, type: PkgSelectionType):
        """ Change folder in file view """
        self._current_ref = conan_ref
        self._current_pkg = pkg_info
        if type == PkgSelectionType.editable:
            pkg_path =  app.conan_api.get_editables_package_path(ConanRef.loads(conan_ref))
        if type == PkgSelectionType.export:
            pkg_path =  app.conan_api.get_export_folder(ConanRef.loads(conan_ref))
        else:
            pkg_path = app.conan_api.get_package_folder(ConanRef.loads(conan_ref), pkg_info.get("id", ""))
        if not pkg_path.exists():
            Logger().warning(
                f"Can't find package path for {conan_ref} and {str(pkg_info)} for File View")
            return
        if self._model:
            if pkg_path == Path(self._model.rootPath()):
                return
        self._model = CalFileSystemModel()
        self._model.setRootPath(str(pkg_path))
        self._model.sort(0, Qt.SortOrder.AscendingOrder)
        self._model.setReadOnly(False)
        self._view.setModel(self._model)
        self._view.setRootIndex(self._model.index(str(pkg_path)))
        self._view.setColumnHidden(2, True)  # file type
        self._model.layoutChanged.connect(self.resize_file_columns)
        self._view.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        # disable edit on double click, since we want to open
        re_register_signal(self._view.doubleClicked, self.on_file_double_click)  # type: ignore

        self._view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.resize_file_columns()


    def on_conan_pkg_removed(self, conan_ref: str, pkg_id: str):
        # clear file view if this pkg is selected
        if self._current_ref == conan_ref:
            self.close_files_view()

    def close_files_view(self):
        if self._model:
            self._model.deleteLater()
        self._model = None # type: ignore
        self._current_ref = ""
        self._current_pkg = None
        self._pkg_path_label.setText("")
        self._view.setModel(None)  # type: ignore
        self._pkg_path_label.setText("")

    def on_file_double_click(self, model_index):
        file_path = Path(model_index.model().fileInfo(model_index).absoluteFilePath())
        run_file(file_path, True, args="")

    def on_copy_file_as_path(self) -> str:
        files = self.get_selected_pkg_paths()
        file_paths = "\n".join(files)
        QApplication.clipboard().setText(file_paths)
        return file_paths

    def on_open_terminal_in_dir(self) -> int:
        selected_path = Path(self.get_selected_pkg_paths()[0]) # TODO!
        if selected_path.is_file():
            selected_path = selected_path.parent
        return open_cmd_in_path(selected_path)

    def on_edit_file(self):
        selected_paths = self.get_selected_pkg_paths()
        if len(selected_paths) != 1:
            return
        for selected_path in selected_paths:
            if not Path(selected_path).is_file():
                continue
            editor = app.active_settings.get_string(FILE_EDITOR_EXECUTABLE)
            if not editor:
                Logger().info("No editor set up! Please configure it in the settings menu.")
                return
            execute_cmd([editor, selected_path], False)

    def on_file_delete(self):
        selected_paths = self.get_selected_pkg_paths()
        msg = QMessageBox(parent=self._view)
        msg.setWindowTitle("Delete file")
        msg.setText("Are you sure, you want to permanently delete this file(s)/folder(s)?\t")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        msg.setIcon(QMessageBox.Icon.Warning)
        reply = msg.exec()
        if reply != QMessageBox.StandardButton.Yes:
            return
        for path in selected_paths:
            delete_path(Path(path))

    def on_files_copy(self) -> List[QUrl]:
        if not self._model:
            return []
        files = self.get_selected_pkg_paths()
        if not files:
            return []
        data = QMimeData()
        urls = []
        for file in files:
            urls.append(QUrl.fromLocalFile(file))
            self._model.clear_disabled_item(file)
            self._view.repaint()
        data.setUrls(urls)

        QApplication.clipboard().setMimeData(data)
        return urls
    
    def on_files_cut(self) -> List[QUrl]:
        if not self._model:
            return []
        files = self.get_selected_pkg_paths()
        if not files:
            return []
        urls = []
        for file in files:
            urls.append(QUrl.fromLocalFile(file))
        data = QMimeData()
        data.setUrls(urls)
        data.setProperty("action", "cut")
        self._model.clear_all_disabled_items() # type: ignore
        self._model.add_disabled_items(files) # type: ignore
        self._view.repaint()

        QApplication.clipboard().setMimeData(data)
        return urls
    
    def on_file_rename(self):
        file_view_indexes = self._get_pkg_file_source_items()
        if not file_view_indexes:
            return None
        # for multiselect: edit last item
        self._view.edit(file_view_indexes[-1])
        return file_view_indexes

    def on_files_paste(self):
        data = QApplication.clipboard().mimeData()
        if not data or not data.hasUrls():
            return
        urls = data.urls()
        # determine destination path
        sel_item_paths = self.get_selected_pkg_paths()
        if not sel_item_paths:
            return
        # determine destination path
        dst_dir_path = Path(sel_item_paths[0])

        # on multiselect it will paste once in the parent dir of the selected items
        if len(sel_item_paths) > 1:
            dst_dir_path = dst_dir_path.parent

        elif not self._is_selected_file_item_expanded():
            dst_dir_path = dst_dir_path.parent if dst_dir_path.is_file() else dst_dir_path
            
        for url in urls:
            # try to copy
            if not url.isLocalFile():
                continue
            source_path = Path(url.toLocalFile())
            new_path_str = os.path.join(dst_dir_path, url.fileName())
            cut = True if data.property("action") == "cut" else False
            self.paste_path(source_path, Path(new_path_str), cut)
            if cut: # restore disabled items
                self._model.clear_all_disabled_items() # type: ignore
                self._view.repaint()

    def paste_path(self, src: Path, dst: Path, cut=False):
        if src == dst and cut:
            return # do nothing
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
            if cut:
                delete_path(src)


    def on_add_app_link_from_file(self):
        selected_paths = self.get_selected_pkg_paths()
        if len(selected_paths) != 1:
            return
        file_path = Path(selected_paths[0])
        if not file_path.is_file():
            Logger().error("Please select a file, not a directory!")
            return
        if not self._current_ref:
            return 
        conan_ref = ConanRef.loads(self._current_ref)
        # determine relpath from package
        pkg_info = self._current_pkg
        if not pkg_info:
            Logger().error("Error on trying to adding Applink: No package info found.")
            return
        pkg_path = app.conan_api.get_package_folder(conan_ref, pkg_info.get("id", ""))
        rel_path = file_path.relative_to(pkg_path).as_posix() # no \ for UI config

        app_config = UiAppLinkConfig(
            name="NewLink", conan_ref=str(self._current_ref), executable=str(rel_path), 
            conan_options=pkg_info.get("options", {}))
        self._page_widgets.get_page_by_type(AppGridView).open_new_app_dialog_from_extern(app_config)

    def on_open_file_in_file_manager(self, model_index):
        file_path = Path(self.get_selected_pkg_paths()[-1])
        open_in_file_manager(file_path)

    def _get_pkg_file_source_items(self) -> List[QModelIndex]:
        indexes = []
        for index in self._view.selectedIndexes():
            if index.column() == 0: # we only need a row once
                indexes.append(index)
        return indexes


    def get_selected_pkg_paths(self) -> List[str]:
        file_paths = []
        if not self._model:
            return file_paths
        file_view_indexes = self._get_pkg_file_source_items()
        # if nothing selected return root
        if not file_view_indexes:
            return [self._model.rootPath()]
        for file_view_index in file_view_indexes:
            file_paths.append(self._model.fileInfo(file_view_index).absoluteFilePath())
        return file_paths 

    def _is_selected_file_item_expanded(self):
        file_view_indexes = self._get_pkg_file_source_items()
        # if nothing selected return root
        if len(file_view_indexes) != 1:
            return False
        return self._view.isExpanded(file_view_indexes[0])

    def resize_file_columns(self):
        if self._view:
            self._view.resizeColumnToContents(3)
            self._view.resizeColumnToContents(2)
            self._view.resizeColumnToContents(1)
            self._view.resizeColumnToContents(0)
