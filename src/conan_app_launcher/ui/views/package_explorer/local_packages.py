import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.core import (open_cmd_in_path, open_file,
                                     open_in_file_manager, run_file)
from conan_app_launcher.core.conan import ConanPkg
from conan_app_launcher.ui.common import (AsyncLoader, FileSystemModel,
                                          get_themed_asset_image)
from conan_app_launcher.ui.common.model import re_register_signal
from conan_app_launcher.ui.data import UiAppLinkConfig
from conan_app_launcher.ui.dialogs import ConanRemoveDialog
from conan_app_launcher.ui.views import AppGridView
from conan_app_launcher.ui.widgets import RoundedMenu
from conans.model.ref import ConanFileReference
from PyQt5.QtCore import (QFile, QItemSelectionModel, QMimeData, QModelIndex,
                          Qt, QUrl, pyqtBoundSignal)
from PyQt5.QtGui import QIcon, QKeySequence, QShowEvent, QResizeEvent
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
                             QMessageBox, QWidget)

from .model import PROFILE_TYPE, REF_TYPE, PackageTreeItem, PkgSelectModel
from .package_explorer_ui import Ui_Form

if TYPE_CHECKING:  # pragma: no cover
    from conan_app_launcher.ui.fluent_window import FluentWindow


class LocalConanPackageExplorer(QWidget):

    def __init__(self, parent: QWidget, conan_pkg_removed: pyqtBoundSignal, page_widgets: "FluentWindow.PageStore"):
        super().__init__(parent)
        self.page_widgets = page_widgets
        self.conan_pkg_removed = conan_pkg_removed
        self.pkg_sel_model = None
        self._pkg_sel_model_loader = AsyncLoader(self)
        self.fs_model = None

        self._ui = Ui_Form()
        self._ui.setupUi(self)

        self._current_ref: Optional[str] = None  # loaded conan ref
        self._current_pkg: Optional[ConanPkg] = None  # loaded conan pkg info
        self._ui.refresh_button.setIcon(QIcon(get_themed_asset_image("icons/refresh.png")))

        self._ui.package_select_view.header().setSortIndicator(0, Qt.AscendingOrder)
        self._ui.package_select_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.package_select_view.customContextMenuRequested.connect(
            self.on_selection_context_menu_requested)
        self._init_selection_context_menu()

        self._ui.refresh_button.clicked.connect(self.on_pkg_refresh_clicked)
        self._ui.package_filter_edit.textChanged.connect(self.set_filter_wildcard)
        conan_pkg_removed.connect(self.on_conan_pkg_removed)

    def showEvent(self, a0: QShowEvent) -> None:
        self.refresh_pkg_selection_view(update=False)  # only update the first time
        return super().showEvent(a0)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        # resize filter splitter to roughly match file view splitter
        sizes = self._ui.splitter.sizes()
        offset = self._ui.package_filter_label.width() + self._ui.refresh_button.width()
        self._ui.splitter_filter.setSizes([sizes[0] - offset, self._ui.splitter_filter.width()
                                           - sizes[0] + offset])
        self._resize_file_columns()
        super().resizeEvent(a0)

    def apply_theme(self):
        self._ui.refresh_button.setIcon(QIcon(get_themed_asset_image("icons/refresh.png")))
        self._init_selection_context_menu()
        self._init_pkg_file_context_menu()

    # Selection view context menu

    def _init_selection_context_menu(self):
        self.select_cntx_menu = RoundedMenu()

        self.copy_ref_action = QAction("Copy reference", self)
        self.copy_ref_action.setIcon(QIcon(get_themed_asset_image("icons/copy_link.png")))
        self.select_cntx_menu.addAction(self.copy_ref_action)
        self.copy_ref_action.triggered.connect(self.on_copy_ref_requested)

        self.open_export_action = QAction("Open export Folder", self)
        self.open_export_action.setIcon(QIcon(get_themed_asset_image("icons/opened_folder.png")))
        self.select_cntx_menu.addAction(self.open_export_action)
        self.open_export_action.triggered.connect(self.on_open_export_folder_requested)

        self.show_conanfile_action = QAction("Show conanfile", self)
        self.show_conanfile_action.setIcon(QIcon(get_themed_asset_image("icons/file_preview.png")))
        self.select_cntx_menu.addAction(self.show_conanfile_action)
        self.show_conanfile_action.triggered.connect(self.on_show_conanfile_requested)

        self.remove_ref_action = QAction("Remove package", self)
        self.remove_ref_action.setIcon(QIcon(get_themed_asset_image("icons/delete.png")))
        self.select_cntx_menu.addAction(self.remove_ref_action)
        self.remove_ref_action.triggered.connect(self.on_remove_ref_requested)

    def on_open_export_folder_requested(self):
        conan_ref = self.get_selected_conan_ref()
        conanfile = app.conan_api.get_conanfile_path(ConanFileReference.loads(conan_ref))
        open_in_file_manager(conanfile)

    def on_show_conanfile_requested(self):
        conan_ref = self.get_selected_conan_ref()
        conanfile = app.conan_api.get_conanfile_path(ConanFileReference.loads(conan_ref))
        loader = AsyncLoader(self)
        loader.async_loading(self, open_file, (conanfile,), loading_text="Opening Conanfile...")
        loader.wait_for_finished()

    def on_selection_context_menu_requested(self, position):
        self.select_cntx_menu.exec_(self._ui.package_select_view.mapToGlobal(position))

    def on_pkg_refresh_clicked(self):
        self.refresh_pkg_selection_view(update=True)

    def get_selected_pkg_source_item(self) -> Optional[PackageTreeItem]:
        indexes = self._ui.package_select_view.selectedIndexes()
        if len(indexes) != 1:
            Logger().debug(f"Mismatch in selected items for context action: {str(len(indexes))}")
            return None
        view_index = self._ui.package_select_view.selectedIndexes()[0]
        source_item: PackageTreeItem = view_index.model().mapToSource(view_index).internalPointer()
        return source_item

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

    def on_remove_ref_requested(self):
        source_item = self.get_selected_pkg_source_item()
        if not source_item:
            return
        conan_ref = self.get_selected_conan_ref()
        pkg_info = self.get_selected_conan_pkg_info()
        pkg_id = ""
        if pkg_info:
            pkg_id = pkg_info.get("id", "")
        dialog = ConanRemoveDialog(self, conan_ref, pkg_id, self.conan_pkg_removed)
        dialog.show()

    def on_conan_pkg_removed(self, conan_ref: str, pkg_id: str):
        # clear file view if this pkg is selected
        if self._current_ref == conan_ref:
            self.close_files_view()
        # TODO this can be done cheaper by removing the item from the model
        self.refresh_pkg_selection_view()

    # Global pane and cross connection slots

    def refresh_pkg_selection_view(self, update=True):
        """
        Refresh all packages by reading it from local drive. Can take a while.
        Update flag can be used for enabling and disabling it. 
        """
        if not update and self.pkg_sel_model:  # loads only at first init
            return
        self.pkg_sel_model = PkgSelectModel()
        self._pkg_sel_model_loader.async_loading(
            self, self.pkg_sel_model.setup_model_data, (), self.finish_select_model_init, "Reading Packages")

    def finish_select_model_init(self):
        if self.pkg_sel_model:
            self._ui.package_select_view.setModel(self.pkg_sel_model.proxy_model)
            self._ui.package_select_view.selectionModel().selectionChanged.connect(self.on_pkg_selection_change)
            self.set_filter_wildcard()  # re-apply package filter query
        else:
            Logger().error("Can't load local packages!")

    def set_filter_wildcard(self):
        # use strip to remove unnecessary whitespace
        text = self._ui.package_filter_edit.text().strip()  # toPlainText
        if self.pkg_sel_model:
            self.pkg_sel_model.proxy_model.setFilterWildcard(text)

    def find_item_in_pkg_sel_model(self, conan_ref: str) -> int:
        # find the row with the matching reference
        if not self.pkg_sel_model:
            return False
        for ref_row in range(self.pkg_sel_model.root_item.child_count()):
            item = self.pkg_sel_model.root_item.child_items[ref_row]
            if item.item_data[0] == conan_ref:
                return ref_row
        return -1

    def select_local_package_from_ref(self, conan_ref: str, refresh=False) -> bool:
        """ Selects a reference:id pkg in the left pane and opens the file view"""
        self.page_widgets.get_button_by_type(type(self)).click()  # changes to this page and loads
       # needed, if refresh==True, so the async loader can finish, otherwise the QtThread can't be deleted
        self._pkg_sel_model_loader.wait_for_finished()

        if not self.pkg_sel_model:  # guard
            return False

        # Reset filter, otherwise the element to be shown could be hidden
        self._ui.package_filter_edit.setText("*")

        # find out if we need to find a ref or or a package
        split_ref = conan_ref.split(":")
        pkg_id = ""
        if len(split_ref) > 1:  # has id
            conan_ref = split_ref[0]
            pkg_id = split_ref[1]

        if self.find_item_in_pkg_sel_model(conan_ref) == -1:  # TODO  also need pkg id
            self.refresh_pkg_selection_view()

        # wait for model to be loaded
        self._pkg_sel_model_loader.wait_for_finished()
        ref_row = self.find_item_in_pkg_sel_model(conan_ref)
        if ref_row == -1:
            Logger().debug(f"Cannot find {conan_ref} in Local Package Explorer for selection")
            return False
        Logger().debug(f"Found {conan_ref}@{str(ref_row)} in Local Package Explorer for selection")

        # map to package view model
        proxy_index = self.pkg_sel_model.index(ref_row, 0, QModelIndex())
        sel_model = self._ui.package_select_view.selectionModel()
        view_model = self._ui.package_select_view.model()
        self._ui.package_select_view.expand(view_model.mapFromSource(proxy_index))

        if pkg_id:
            item: PackageTreeItem = proxy_index.internalPointer()
            i = 0
            for i in range(len(item.child_items)):
                if item.child_items[i].item_data[0].get("id", "") == pkg_id:
                    break
            internal_sel_index = proxy_index.child(i, 0)
        else:
            internal_sel_index = proxy_index

        view_index = view_model.mapFromSource(internal_sel_index)
        self._ui.package_select_view.scrollTo(view_index)
        sel_model.select(view_index, QItemSelectionModel.ClearAndSelect)
        sel_model.currentRowChanged.emit(proxy_index, internal_sel_index)
        Logger().debug(f"Selecting {view_index.data()} in Local Package Explorer")

        return True

    # Package file view init and functions

    def on_pkg_selection_change(self):
        """ Change folder in file view """
        source_item = self.get_selected_pkg_source_item()
        if not source_item:
            return
        if source_item.type != PROFILE_TYPE:
            return
        conan_ref = self.get_selected_conan_ref()
        self._current_ref = conan_ref
        self._current_pkg = self.get_selected_conan_pkg_info()
        pkg_id = self.get_selected_conan_pkg_info().get("id", "")
        pkg_path = app.conan_api.get_package_folder(
            ConanFileReference.loads(conan_ref), pkg_id)
        if not pkg_path.exists():
            Logger().warning(
                f"Can't find package path for {conan_ref} and {str(source_item.item_data[0])} for File View")
            return
        self.fs_model = FileSystemModel()
        self.fs_model.setRootPath(str(pkg_path))
        self.fs_model.sort(0, Qt.AscendingOrder)
        re_register_signal(self.fs_model.fileRenamed, self.on_file_double_click)
        self._ui.package_file_view.setModel(self.fs_model)
        self._ui.package_file_view.setRootIndex(self.fs_model.index(str(pkg_path)))
        self._ui.package_file_view.setColumnHidden(2, True)  # file type
        self.fs_model.layoutChanged.connect(self._resize_file_columns)
        self._ui.package_file_view.header().setSortIndicator(0, Qt.AscendingOrder)
        re_register_signal(self._ui.package_file_view.doubleClicked,
                                self.on_file_double_click)
        # disable edit on double click, since we want to open
        self._ui.package_file_view.setEditTriggers(QAbstractItemView.EditKeyPressed)
        self._ui.package_path_label.setText(str(pkg_path))

        self._ui.package_file_view.setContextMenuPolicy(Qt.CustomContextMenu)

        re_register_signal(self._ui.package_file_view.customContextMenuRequested,
                                self.on_file_context_menu_requested)
        self._init_pkg_file_context_menu()
        self._resize_file_columns()

    def close_files_view(self):
        if self.fs_model:
            self.fs_model.deleteLater()
        self.fs_model = None
        self._current_ref = ""
        self._current_pkg = None
        self._ui.package_path_label.setText("")
        self._ui.package_file_view.setModel(None)
        self._ui.package_path_label.setText("")


    def on_file_double_click(self, model_index):
        file_path = Path(model_index.model().fileInfo(model_index).absoluteFilePath())
        run_file(file_path, True, args="")

    def _init_pkg_file_context_menu(self):
        self.file_cntx_menu = RoundedMenu()

        self.open_fm_action = QAction("Show in File Manager", self)
        self.open_fm_action.setIcon(QIcon(get_themed_asset_image("icons/file-explorer.png")))
        self.file_cntx_menu.addAction(self.open_fm_action)
        self.open_fm_action.triggered.connect(self.on_open_file_in_file_manager)

        self.copy_as_path_action = QAction("Copy as Path", self)
        self.copy_as_path_action.setIcon(QIcon(get_themed_asset_image("icons/copy_to_clipboard.png")))
        self.file_cntx_menu.addAction(self.copy_as_path_action)
        self.copy_as_path_action.triggered.connect(self.on_copy_file_as_path)

        self.open_terminal_action = QAction("Open terminal here", self)
        self.open_terminal_action.setIcon(QIcon(get_themed_asset_image("icons/cmd.png")))
        self.file_cntx_menu.addAction(self.open_terminal_action)
        self.open_terminal_action.triggered.connect(self.on_open_terminal_in_dir)

        self.file_cntx_menu.addSeparator()

        self.copy_action = QAction("Copy", self)
        self.copy_action.setIcon(QIcon(get_themed_asset_image("icons/copy.png")))
        self.copy_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_C))
        self.file_cntx_menu.addAction(self.copy_action)
        # for the shortcut to work, the action has to be added to a higher level widget
        self.addAction(self.copy_action)
        self.copy_action.triggered.connect(self.on_file_copy)

        self.paste_action = QAction("Paste", self)
        self.paste_action.setIcon(QIcon(get_themed_asset_image("icons/paste.png")))
        self.paste_action.setShortcut(QKeySequence("Ctrl+v"))  # Qt.CTRL + Qt.Key_V))
        self.paste_action.setShortcutContext(Qt.ApplicationShortcut)
        self.addAction(self.paste_action)
        self.file_cntx_menu.addAction(self.paste_action)
        self.paste_action.triggered.connect(self.on_file_paste)

        self.delete_action = QAction("Delete", self)
        self.delete_action.setIcon(QIcon(get_themed_asset_image("icons/delete.png")))
        self.delete_action.setShortcut(QKeySequence(Qt.Key_Delete))
        self.file_cntx_menu.addAction(self.delete_action)
        self.addAction(self.delete_action)
        self.delete_action.triggered.connect(self.on_file_delete)

        self.file_cntx_menu.addSeparator()

        self.add_link_action = QAction("Add link to App Grid", self)
        self.add_link_action.setIcon(QIcon(get_themed_asset_image("icons/add_link.png")))
        self.file_cntx_menu.addAction(self.add_link_action)
        self.add_link_action.triggered.connect(self.on_add_app_link_from_file)

    def on_file_context_menu_requested(self, position):
        self.file_cntx_menu.exec_(self._ui.package_file_view.mapToGlobal(position))

    def on_copy_file_as_path(self) -> str:
        file = self._get_selected_pkg_file()
        QApplication.clipboard().setText(file)
        return file

    def on_open_terminal_in_dir(self) -> int:
        selected_path = Path(self._get_selected_pkg_file())
        if selected_path.is_file():
            selected_path = selected_path.parent
        return open_cmd_in_path(selected_path)

    def on_file_delete(self):
        file = self._get_selected_pkg_file()
        msg = QMessageBox(parent=self)
        msg.setWindowTitle("Delete file")
        msg.setText("Are you sure, you want to delete this file\t")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.setIcon(QMessageBox.Warning)
        reply = msg.exec_()
        if reply != QMessageBox.Yes:
            return
        try:
            os.remove(file)
        except Exception as e:
            Logger().warning(f"Can't delete {file}: {str(e)}")

    def on_file_copy(self) -> Optional[QUrl]:
        file = self._get_selected_pkg_file()
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
            file = self._get_selected_pkg_file()
            if not file:
                return
            if os.path.isfile(file):
                directory = os.path.dirname(file)
            else:
                directory = file
            # if nothing selected -> root
            new_path = os.path.join(directory, url.fileName())
            QFile(url.toLocalFile()).copy(new_path)

    def on_add_app_link_from_file(self):
        file_path = Path(self._get_selected_pkg_file())
        if not file_path.is_file():
            Logger().error("Please select a file, not a directory!")
            return
        conan_ref = ConanFileReference.loads(self._current_ref)
        # determine relpath from package
        pkg_info = self._current_pkg
        if not pkg_info:
            Logger().error("Error on trying to adding Applink: No package info found.")
            return
        pkg_path = app.conan_api.get_package_folder(conan_ref, pkg_info.get("id", ""))
        rel_path = file_path.relative_to(pkg_path)

        app_config = UiAppLinkConfig(
            name="NewLink", conan_ref=self.get_selected_conan_ref(), executable=str(rel_path))
        self.page_widgets.get_page_by_type(AppGridView).open_new_app_dialog_from_extern(app_config)

    def on_open_file_in_file_manager(self, model_index):
        file_path = Path(self._get_selected_pkg_file())
        open_in_file_manager(file_path)

    def _get_pkg_file_source_item(self) -> Optional[QModelIndex]:
        indexes = self._ui.package_file_view.selectedIndexes()
        if len(indexes) == 0:  # can be multiple - always get 0
            Logger().debug(f"No selected item for context action")
            return None
        return self._ui.package_file_view.selectedIndexes()[0]

    def _get_selected_pkg_file(self) -> str:
        file_view_index = self._get_pkg_file_source_item()
        if not file_view_index:
            if self.fs_model:
                return self.fs_model.rootPath()
            else:
                return ""
        return file_view_index.model().fileInfo(file_view_index).absoluteFilePath()

    def _resize_file_columns(self):
        self._ui.package_file_view.resizeColumnToContents(3)
        self._ui.package_file_view.resizeColumnToContents(2)
        self._ui.package_file_view.resizeColumnToContents(1)
        self._ui.package_file_view.resizeColumnToContents(0)
