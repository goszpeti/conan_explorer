from PyQt5 import QtCore, QtWidgets, QtGui
from pathlib import Path
from conan_app_launcher.components import parse_config_file, write_config_file, TabConfigEntry, ConanApi
from .conan_fs_model import ConanFileSystemModel
from .pkg_select_model import PkgSelectModel
from typing import TYPE_CHECKING, List, Optional
import os
Qt = QtCore.Qt

if TYPE_CHECKING:
    from conan_app_launcher.ui.main_window import MainUi


class LocalConanPackageExplorer():
    def __init__(self, main_window: "MainUi"):
        self._main_window = main_window
        self.fs_model = ConanFileSystemModel()
        storage_path = Path(ConanApi().cache.store) # conan.config_get("storage.path"))
        #self.fs_model.setRootPath(str(storage_path))
        #self.fs_model.setRootPath(str(ConanApi().get_short_path_root()))
        self.pkg_sel_model = PkgSelectModel()
        main_window.ui.refresh_button.clicked.connect(self.refresh_pkg_selection_view)
        # Set up filters for builtin conan files
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.pkg_sel_model)
        self._main_window.ui.package_select_view.setModel(self.proxy_model)
        self._main_window.ui.package_select_view.header().setVisible(True)
        self._main_window.ui.package_filter_edit.textChanged.connect(self.set_filter_wildcard)
        
        from conan_app_launcher.ui.package_explorer.fs_light import FileSystemModelLite
        from .sandbox_fs_model import SandBoxItemModel
        # import glob
        # file_list = glob.glob(str(storage_path) + "/**", recursive=True)
        model = SandBoxItemModel(main_window)
        #model.setSandBoxDetails()
        self._main_window.ui.package_file_view.setModel(self.fs_model.proxy_model)
            #FileSystemModelLite(file_list))  # self.fs_model.proxy_model)
        self.fs_model.sort(0, Qt.AscendingOrder)
        self._main_window.ui.package_file_view.setRootIndex(self.fs_model.proxy_model.mapFromSource(
            self.fs_model.index_from_path(self.fs_model.rootDirectory().absolutePath())))

        # self._main_window.ui.package_file_view.clicked.connect(self.on_click)
        self._main_window.ui.package_file_view.setColumnHidden(1, True)
        self._main_window.ui.package_file_view.setColumnHidden(2, True)
        self._main_window.ui.package_file_view.setColumnWidth(0, 310)
        # self._main_window.ui.package_file_view.setRootIsDecorated(False)
        # self._main_window.ui.package_file_view.setItemsExpandable(False)
        # self._main_window.ui.package_file_view.selectionModel().selectionChanged.connect(
        #     self.on_selection_change)
        #self._main_window.ui.package_file_view.expanded.connect(self.on_expand)

    def refresh_pkg_selection_view(self):
        self._main_window.ui.package_select_view
        self.pkg_sel_model = PkgSelectModel()
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.pkg_sel_model)
        self._main_window.ui.package_select_view.setModel(self.proxy_model)

    def set_filter_wildcard(self):
        text = self._main_window.ui.package_filter_edit.toPlainText()
        self.proxy_model.setFilterWildcard(text)


    # def on_expand(self, index):
    #     # Todo skip empty folders
    #     # get child index
    #     # self._main_window.ui.package_file_view.expand(index)
    #     pass

    # def on_selection_change(self, item_selection):
    #     # change folder in file view
    #     view_index = self._main_window.ui.package_file_view.selectionModel().selectedIndexes()[0]
    #     pkg_id_path = self.fs_model.is_sub_package_dir(view_index)
    #     if pkg_id_path:
    #         # proxy_index = self.proxy.mapToSource(view_index)
    #         # item_name = self.model.fileName(proxy_index)
    #         # # TODO discover upstream, if in package
    #         #path = self.fs_model.fileInfo(view_index).absoluteFilePath()
    #         c_p = pkg_id_path / "conaninfo.txt"
    #         if c_p.is_file():
    #             text = ""
    #             with open(c_p, "r") as fp:
    #                 text = fp.read()
    #             self._main_window.ui.package_info.setText(text)
