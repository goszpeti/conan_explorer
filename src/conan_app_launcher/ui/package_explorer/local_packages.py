import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import conan_app_launcher as this
from conan_app_launcher.base import Logger
from conan_app_launcher.components import (ConanApi, open_in_file_manager,
                                           run_file)
from conan_app_launcher.components.conan import ConanPkg
from conan_app_launcher.components.config_file import AppConfigEntry, AppType
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtGui, QtWidgets

from .pkg_select_model import PROFILE_TYPE, PkgSelectModel, TreeItem

Qt = QtCore.Qt

if TYPE_CHECKING:
    from conan_app_launcher.ui.main_window import MainUi


class LocalConanPackageExplorer():
    def __init__(self, main_window: "MainUi"):
        self._main_window = main_window
        self.pkg_sel_model = PkgSelectModel()
        # Set up filters for builtin conan files
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.pkg_sel_model)

        main_window.ui.package_select_view.setModel(self.proxy_model)
        main_window.ui.package_select_view.header().setVisible(True)
        main_window.ui.package_select_view.header().setSortIndicator(0, Qt.AscendingOrder)
        main_window.ui.package_select_view.setContextMenuPolicy(Qt.CustomContextMenu)
        main_window.ui.package_select_view.customContextMenuRequested.connect(
            self.on_selection_context_menu_requested)

        main_window.ui.package_select_view.selectionModel().selectionChanged.connect(self.on_pkg_selection_change)
        self._init_selection_context_menu()

        main_window.ui.refresh_button.clicked.connect(self.refresh_pkg_selection_view)
        main_window.ui.package_filter_edit.textChanged.connect(self.set_filter_wildcard)

    # Selection view context menu

    def _init_selection_context_menu(self):
        self.select_cntx_menu = QtWidgets.QMenu()
        icons_path = this.asset_path / "icons"

        self.copy_ref_action = QtWidgets.QAction("Copy reference", self._main_window)
        self.copy_ref_action.setIcon(QtGui.QIcon(str(icons_path / "copy_link.png")))
        self.select_cntx_menu.addAction(self.copy_ref_action)
        self.copy_ref_action.triggered.connect(self.copy_ref)

    def on_selection_context_menu_requested(self, position):
        self.select_cntx_menu.exec_(self._main_window.ui.package_select_view.mapToGlobal(position))

    def get_selected_pkg_source_item(self) -> Optional[TreeItem]:
        indexes = this.main_window.ui.package_select_view.selectedIndexes()
        if len(indexes) != 1:
            Logger().debug(f"Mismatch in selected items for context action: {str(len(indexes))}")
            return None
        view_index = this.main_window.ui.package_select_view.selectedIndexes()[0]
        source_item: TreeItem = view_index.model().mapToSource(view_index).internalPointer()
        return source_item

    def get_selected_conan_ref(self) -> str:
        # no need to map from postition, since rightclick selects a single item
        source_item = self.get_selected_pkg_source_item()
        if not source_item:
            return ""
        conan_ref_item = source_item
        if source_item.type == PROFILE_TYPE:
            conan_ref_item = source_item.parent()
        return conan_ref_item.itemData[0]

    def get_selected_conan_pkg_info(self) -> ConanPkg:
        source_item = self.get_selected_pkg_source_item()
        if not source_item:
            return {}
        return source_item.itemData[0]

    def copy_ref(self):
        conan_ref = self.get_selected_conan_ref()
        this.qt_app.clipboard().setText(conan_ref)

    # Global pane and cross connection slots

    def refresh_pkg_selection_view(self):
        self._main_window.ui.package_select_view
        self.pkg_sel_model = PkgSelectModel()
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.pkg_sel_model)
        self._main_window.ui.package_select_view.setModel(self.proxy_model)
        self._main_window.ui.package_select_view.selectionModel().selectionChanged.connect(self.on_pkg_selection_change)
    
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
        pkg_path = ConanApi().get_package_folder(ConanFileReference.loads(conan_ref), self.get_selected_conan_pkg_info())
        if not pkg_path.exists():
            Logger().warning(f"Can't find package path for {conan_ref} and {str(source_item.itemData[0])}")
            return
        self.fs_model = QtWidgets.QFileSystemModel()
        self.fs_model.setReadOnly(False) # TODO connect the edit checkbox
        self.fs_model.setRootPath(str(pkg_path))
        self.fs_model.sort(0, Qt.AscendingOrder)
        self.fs_model.fileRenamed.connect(self.on_file_double_click)
        self._main_window.ui.package_file_view.setModel(self.fs_model)
        self._main_window.ui.package_file_view.setRootIndex(self.fs_model.index(str(pkg_path)))
        self._main_window.ui.package_file_view.setColumnHidden(2, True)  # file type
        self._main_window.ui.package_file_view.setColumnWidth(0, 200)
        self._main_window.ui.package_file_view.header().setSortIndicator(0, Qt.AscendingOrder)
        self._main_window.ui.package_file_view.doubleClicked.connect(self.on_file_double_click)
        # disable edit on double click, since we want to open
        self._main_window.ui.package_file_view.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed)
        self._main_window.ui.package_path_label.setText(str(pkg_path))

        self._main_window.ui.package_file_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._main_window.ui.package_file_view.customContextMenuRequested.connect(
            self.on_pkg_context_menu_requested)
        self._init_pkg_context_menu()

    def on_file_double_click(self, model_index):
        file_path = Path(model_index.model().fileInfo(model_index).absoluteFilePath())
        run_file(file_path, True, args="")

    def _init_pkg_context_menu(self):
        self.file_cntx_menu = QtWidgets.QMenu()
        icons_path = this.asset_path / "icons"

        self.open_fm_action = QtWidgets.QAction("Show in file manager", self._main_window)
        self.open_fm_action.setIcon(QtGui.QIcon(str(icons_path / "file-explorer.png")))
        self.file_cntx_menu.addAction(self.open_fm_action)
        self.open_fm_action.triggered.connect(self.on_open_in_file_manager)

        self.paste_action = QtWidgets.QAction("Copy as Path", self._main_window)
        self.paste_action.setIcon(QtGui.QIcon(str(icons_path / "copy_to_clipboard.png")))
        self.file_cntx_menu.addAction(self.paste_action)
        self.paste_action.triggered.connect(self.on_copy_as_path)

        self.file_cntx_menu.addSeparator()

        self.copy_action = QtWidgets.QAction("Copy", self._main_window)
        self.copy_action.setIcon(QtGui.QIcon(str(icons_path / "copy.png")))
        self.file_cntx_menu.addAction(self.copy_action)
        self.copy_action.triggered.connect(self.on_copy)

        self.paste_action = QtWidgets.QAction("Paste", self._main_window)
        self.paste_action.setIcon(QtGui.QIcon(str(icons_path / "paste.png")))
        self.file_cntx_menu.addAction(self.paste_action)
        self.paste_action.triggered.connect(self.on_paste)

        self.paste_action = QtWidgets.QAction("Delete", self._main_window)
        self.paste_action.setIcon(QtGui.QIcon(str(icons_path / "delete.png")))
        self.file_cntx_menu.addAction(self.paste_action)
        self.paste_action.triggered.connect(self.on_delete)

        self.file_cntx_menu.addSeparator()

        self.add_link_action = QtWidgets.QAction("Add link to App Grid", self._main_window)
        self.add_link_action.setIcon(QtGui.QIcon(str(icons_path / "add_link.png")))
        self.file_cntx_menu.addAction(self.add_link_action)
        self.add_link_action.triggered.connect(self.on_add_app_link)

    def on_pkg_context_menu_requested(self, position):
        self.file_cntx_menu.exec_(self._main_window.ui.package_file_view.mapToGlobal(position))

    def on_copy_as_path(self):
        file = self._get_selected_pkg_file()
        this.qt_app.clipboard().setText(file)

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

        this.qt_app.clipboard().setMimeData(data)

    def on_paste(self):
        data = this.qt_app.clipboard().mimeData()
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
                dir = os.path.basename(file)
            else:
                dir = file
            new_path = os.path.join(dir, url.fileName())
            QtCore.QFile(url.toLocalFile()).copy(new_path)

    def on_add_app_link(self):
        file_path = Path(self._get_selected_pkg_file())
        conan_ref = self.get_selected_conan_ref()
        # determine relpath from package
        pkg_path = ConanApi().get_package_folder(ConanFileReference.loads(conan_ref), self.get_selected_conan_pkg_info())
        rel_path = file_path.relative_to(pkg_path)
        # TODO get conan options from curent package?
        app_data: AppType = {"name": "NewLink", "conan_ref": conan_ref, "executable": str(rel_path),
                            "icon": "", "console_application": False, "args": "", "conan_options": []}
        self._main_window.open_new_app_dialog_from_extern(AppConfigEntry(app_data))

    def on_open_in_file_manager(self, model_index):
        file_path = Path(self._get_selected_pkg_file())
        open_in_file_manager(file_path)

    def _get_pkg_file_source_item(self) -> Optional[TreeItem]:
        indexes = this.main_window.ui.package_file_view.selectedIndexes()
        if len(indexes) == 0:  # can be multiple - always get 0
            Logger().debug(f"No selected item for context action")
            return None
        return this.main_window.ui.package_file_view.selectedIndexes()[0]

    def _get_selected_pkg_file(self) -> str:
        file_view_index = self._get_pkg_file_source_item()
        if not file_view_index:
            return self.fs_model.rootPath()
        return file_view_index.model().fileInfo(file_view_index).absoluteFilePath()
