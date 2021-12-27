import os
from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Optional
from threading import Thread
from conan_app_launcher import asset_path
import conan_app_launcher.app as app  # using gobal module pattern

from conan_app_launcher.ui.common import Worker
from conan_app_launcher.logger import Logger
from conan_app_launcher.components import (open_in_file_manager, run_file, open_file, open_cmd_in_path)
from conan_app_launcher.components.conan import ConanPkg
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtGui, QtWidgets
from conan_app_launcher.ui.data import UiAppLinkConfig
from .model import PROFILE_TYPE, REF_TYPE, PackageFilter, PkgSelectModel, PackageTreeItem

Qt = QtCore.Qt

if TYPE_CHECKING:  # pragma: no cover
    from conan_app_launcher.ui.main_window import MainWindow

class LocalConanPackageExplorer(QtCore.QObject):
    def __init__(self, main_window: "MainWindow"):
        super().__init__()
        self._main_window = main_window
        self.pkg_sel_model = None
        self.fs_model = None
        self._init_model_thread = None
        # TODO belongs in a model?
        self._current_ref: Optional[str] = None # loaded conan ref
        self._current_pkg: Optional[ConanPkg] = None  # loaded conan pkg info

        main_window.ui.package_select_view.header().setVisible(True)
        main_window.ui.package_select_view.header().setSortIndicator(0, Qt.AscendingOrder)
        main_window.ui.package_select_view.setContextMenuPolicy(Qt.CustomContextMenu)
        main_window.ui.package_select_view.customContextMenuRequested.connect(
            self.on_selection_context_menu_requested)
        self._init_selection_context_menu()

        main_window.ui.refresh_button.clicked.connect(self.on_pkg_refresh_clicked)
        main_window.ui.package_filter_edit.textChanged.connect(self.set_filter_wildcard)
        main_window.ui.main_toolbox.currentChanged.connect(self.on_toolbox_changed)
    # Selection view context menu

    def _init_selection_context_menu(self):
        self.select_cntx_menu = QtWidgets.QMenu()
        icons_path = asset_path / "icons"

        self.copy_ref_action = QtWidgets.QAction("Copy reference", self._main_window)
        self.copy_ref_action.setIcon(QtGui.QIcon(str(icons_path / "copy_link.png")))
        self.select_cntx_menu.addAction(self.copy_ref_action)
        self.copy_ref_action.triggered.connect(self.on_copy_ref_requested)

        self.open_export_action = QtWidgets.QAction("Open export Folder", self._main_window)
        self.open_export_action.setIcon(QtGui.QIcon(str(icons_path / "opened_folder.png")))
        self.select_cntx_menu.addAction(self.open_export_action)
        self.open_export_action.triggered.connect(self.on_open_export_folder_requested)

        self.show_conanfile_action = QtWidgets.QAction("Show conanfile", self._main_window)
        self.show_conanfile_action.setIcon(QtGui.QIcon(str(icons_path / "file_preview.png")))
        self.select_cntx_menu.addAction(self.show_conanfile_action)
        self.show_conanfile_action.triggered.connect(self.on_show_conanfile_requested)


        self.remove_ref_action = QtWidgets.QAction("Remove package", self._main_window)
        self.remove_ref_action.setIcon(QtGui.QIcon(str(icons_path / "delete.png")))
        self.select_cntx_menu.addAction(self.remove_ref_action)
        self.remove_ref_action.triggered.connect(self.on_remove_ref_requested)

    def on_open_export_folder_requested(self):
        conan_ref = self.get_selected_conan_ref()
        conanfile = app.conan_api.get_conanfile_path(ConanFileReference.loads(conan_ref))
        open_in_file_manager(conanfile)

    def on_show_conanfile_requested(self):
        conan_ref = self.get_selected_conan_ref()
        conanfile = app.conan_api.get_conanfile_path(ConanFileReference.loads(conan_ref))
        open_file(conanfile)

    def on_selection_context_menu_requested(self, position):
        self.select_cntx_menu.exec_(self._main_window.ui.package_select_view.mapToGlobal(position))

    def on_toolbox_changed(self, index):
        self.refresh_pkg_selection_view(update=False)

    def on_pkg_refresh_clicked(self):
        self.refresh_pkg_selection_view(update=True)

    def get_selected_pkg_source_item(self) -> Optional[PackageTreeItem]:
        indexes = self._main_window.ui.package_select_view.selectedIndexes()
        if len(indexes) != 1:
            Logger().debug(f"Mismatch in selected items for context action: {str(len(indexes))}")
            return None
        view_index = self._main_window.ui.package_select_view.selectedIndexes()[0]
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
        return conan_ref_item.item_data[0]

    def get_selected_conan_pkg_info(self) -> ConanPkg:
        source_item = self.get_selected_pkg_source_item()
        if not source_item or source_item.type == REF_TYPE:
            return {}
        return source_item.item_data[0]

    def on_copy_ref_requested(self):
        conan_ref = self.get_selected_conan_ref()
        QtWidgets.QApplication.clipboard().setText(conan_ref)

    def on_remove_ref_requested(self):
        source_item = self.get_selected_pkg_source_item()
        if not source_item:
            return
        conan_ref = self.get_selected_conan_ref()
        pkg_info = self.get_selected_conan_pkg_info()
        pkg_ids = None
        if pkg_info:
            pkg_id = pkg_info.get("id")
            pkg_ids = ([pkg_id] if pkg_id else None)
        self.delete_conan_package_dialog(conan_ref, pkg_ids)


    def delete_conan_package_dialog(self, conan_ref: str, pkg_ids: Optional[List[str]]):
        msg = QtWidgets.QMessageBox(parent=self._main_window)
        msg.setWindowTitle("Delete package")
        msg.setText("Are you sure, you want to delete this package?")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        reply = msg.exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                app.conan_api.conan.remove(conan_ref, packages=pkg_ids, force=True)
            except Exception as e:
                Logger().error(f"Error while removing package {conan_ref}: {str(e)}")

            # Clear view, if this pkg is selected
            if self.fs_model:
                try:
                    self.fs_model.deleteLater()
                except Exception:
                    pass # sometimes this can crash...
                self._main_window.ui.package_path_label.setText("")
            self.refresh_pkg_selection_view()

    # Global pane and cross connection slots

    def refresh_pkg_selection_view(self, update=True):
        """
        Refresh all packages by reading it from local drive. Can take a while.
        Update flag can be used for enabling and disabling it. 
        """
        if not update and self.pkg_sel_model: # loads only at first init
            return
        self.progress_dialog = QtWidgets.QProgressDialog(self._main_window)
        self.progress_dialog.setLabelText("Reading Packages")
        self.progress_dialog.setWindowTitle("Loading")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setModal(True) # otherwise user can trigger it twice -> crash
        self.progress_dialog.setRange(0,0)
        self.progress_dialog.show()
        self.worker = Worker(self.init_select_model)
        self._init_model_thread = QtCore.QThread()
        self.worker.moveToThread(self._init_model_thread)
        self._init_model_thread.started.connect(self.worker.work)
        self.worker.finished.connect(self.finish_select_model_init)
        self.worker.finished.connect(self._init_model_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self._init_model_thread.finished.connect(self._init_model_thread.deleteLater)
        self._init_model_thread.start()

    def finish_select_model_init(self):
        self.proxy_model = PackageFilter()
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        if self.pkg_sel_model:
            self.proxy_model.setSourceModel(self.pkg_sel_model)
            self._main_window.ui.package_select_view.setModel(self.proxy_model)
            self._main_window.ui.package_select_view.selectionModel().selectionChanged.connect(self.on_pkg_selection_change)
            self.progress_dialog.hide()
            self.set_filter_wildcard() # reapply package filter query
        else:
            Logger().error("Can't load local packages!")

    def init_select_model(self):
        self.pkg_sel_model = PkgSelectModel()

    def set_filter_wildcard(self):
        # use strip to remove unnecessary whitespace
        text = self._main_window.ui.package_filter_edit.toPlainText().strip()
        self.proxy_model.setFilterWildcard(text)

    # Package file view init and functions

    def on_pkg_selection_change(self):
        """ """
        # change folder in file view
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
            Logger().warning(f"Can't find package path for {conan_ref} and {str(source_item.item_data[0])}")
            return
        self.fs_model = QtWidgets.QFileSystemModel()
        self.fs_model.setRootPath(str(pkg_path))
        self.fs_model.sort(0, Qt.AscendingOrder)
        self.re_register_signal(self.fs_model.fileRenamed, self.on_file_double_click)
        self._main_window.ui.package_file_view.setModel(self.fs_model)
        self._main_window.ui.package_file_view.setRootIndex(self.fs_model.index(str(pkg_path)))
        self._main_window.ui.package_file_view.setColumnHidden(2, True)  # file type
        self._main_window.ui.package_file_view.setColumnWidth(0, 200)
        self._main_window.ui.package_file_view.header().setSortIndicator(0, Qt.AscendingOrder)
        self.re_register_signal(self._main_window.ui.package_file_view.doubleClicked,
                                self.on_file_double_click)
        # disable edit on double click, since we want to open
        self._main_window.ui.package_file_view.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed)
        self._main_window.ui.package_path_label.setText(str(pkg_path))

        self._main_window.ui.package_file_view.setContextMenuPolicy(Qt.CustomContextMenu)

        self.re_register_signal(self._main_window.ui.package_file_view.customContextMenuRequested,
                                self.on_file_context_menu_requested)
        self._init_pkg_context_menu()

    @classmethod
    def re_register_signal(cls, signal: QtCore.pyqtBoundSignal, slot: Callable):
        try:  # need to be removed, otherwise will be called multiple times
            signal.disconnect()
        except TypeError:
            # no way to check if it is connected and it will throw an error
            pass
        signal.connect(slot)

    def on_file_double_click(self, model_index):
        file_path = Path(model_index.model().fileInfo(model_index).absoluteFilePath())
        run_file(file_path, True, args="")

    def _init_pkg_context_menu(self):
        self.file_cntx_menu = QtWidgets.QMenu()
        icons_path = asset_path / "icons"

        self.open_fm_action = QtWidgets.QAction("Show in File Manager", self._main_window)
        self.open_fm_action.setIcon(QtGui.QIcon(str(icons_path / "file-explorer.png")))
        self.file_cntx_menu.addAction(self.open_fm_action)
        self.open_fm_action.triggered.connect(self.on_open_in_file_manager)

        self.paste_action = QtWidgets.QAction("Copy as Path", self._main_window)
        self.paste_action.setIcon(QtGui.QIcon(str(icons_path / "copy_to_clipboard.png")))
        self.file_cntx_menu.addAction(self.paste_action)
        self.paste_action.triggered.connect(self.on_copy_as_path)

        self.open_terminal_action = QtWidgets.QAction("Open terminal here", self._main_window)
        self.open_terminal_action.setIcon(QtGui.QIcon(str(icons_path / "cmd.png")))
        self.file_cntx_menu.addAction(self.open_terminal_action)
        self.open_terminal_action.triggered.connect(self.on_open_terminal)

        self.file_cntx_menu.addSeparator()

        self.copy_action = QtWidgets.QAction("Copy", self._main_window)
        self.copy_action.setIcon(QtGui.QIcon(str(icons_path / "copy.png")))
        self.copy_action.setShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_C))
        self.file_cntx_menu.addAction(self.copy_action)
        self.copy_action.triggered.connect(self.on_copy)

        self.paste_action = QtWidgets.QAction("Paste", self._main_window)
        self.paste_action.setIcon(QtGui.QIcon(str(icons_path / "paste.png")))
        self.paste_action.setShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_V))
        self.file_cntx_menu.addAction(self.paste_action)
        self.paste_action.triggered.connect(self.on_paste)

        self.delete_action = QtWidgets.QAction("Delete", self._main_window)
        self.delete_action.setIcon(QtGui.QIcon(str(icons_path / "delete.png")))
        self.delete_action.setShortcut(QtGui.QKeySequence(Qt.Key_Delete))
        self.file_cntx_menu.addAction(self.delete_action)
        self.delete_action.triggered.connect(self.on_delete)

        self.file_cntx_menu.addSeparator()

        self.add_link_action = QtWidgets.QAction("Add link to App Grid", self._main_window)
        self.add_link_action.setIcon(QtGui.QIcon(str(icons_path / "add_link.png")))
        self.file_cntx_menu.addAction(self.add_link_action)
        self.add_link_action.triggered.connect(self.on_add_app_link)

    def on_file_context_menu_requested(self, position):
        self.file_cntx_menu.exec_(self._main_window.ui.package_file_view.mapToGlobal(position))

    def on_copy_as_path(self):
        file = self._get_selected_pkg_file()
        QtWidgets.QApplication.clipboard().setText(file)

    def on_open_terminal(self) -> int:
        selected_path = Path(self._get_selected_pkg_file())
        if selected_path.is_file():
            selected_path = selected_path.parent
        return open_cmd_in_path(selected_path)

    def on_delete(self):
        file = self._get_selected_pkg_file()
        msg = QtWidgets.QMessageBox(parent=self._main_window)
        msg.setWindowTitle("Delete file")
        msg.setText("Are you sure, you want to delete this file\t")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        reply = msg.exec_()
        if reply != QtWidgets.QMessageBox.Yes:
            return
        try:
            os.remove(file)
        except Exception as e:
            Logger().warning(f"Can't delete {file}: {str(e)}")

    def on_copy(self):
        file = self._get_selected_pkg_file()
        data = QtCore.QMimeData()
        url = QtCore.QUrl.fromLocalFile(file)
        data.setUrls([url])

        QtWidgets.QApplication.clipboard().setMimeData(data)

    def on_paste(self):
        data = QtWidgets.QApplication.clipboard().mimeData()
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
            if os.path.isfile(file):
                directory = os.path.dirname(file)
            else:
                directory = file
            new_path = os.path.join(directory, url.fileName())
            QtCore.QFile(url.toLocalFile()).copy(new_path)

    def on_add_app_link(self):
        file_path = Path(self._get_selected_pkg_file())
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
        self._main_window.app_grid.open_new_app_dialog_from_extern(app_config)

    def on_open_in_file_manager(self, model_index):
        file_path = Path(self._get_selected_pkg_file())
        open_in_file_manager(file_path)

    def _get_pkg_file_source_item(self) -> Optional[PackageTreeItem]:
        indexes = self._main_window.ui.package_file_view.selectedIndexes()
        if len(indexes) == 0:  # can be multiple - always get 0
            Logger().debug(f"No selected item for context action")
            return None
        return self._main_window.ui.package_file_view.selectedIndexes()[0]

    def _get_selected_pkg_file(self) -> str:
        file_view_index = self._get_pkg_file_source_item()
        if not file_view_index:
            return self.fs_model.rootPath()
        return file_view_index.model().fileInfo(file_view_index).absoluteFilePath()
