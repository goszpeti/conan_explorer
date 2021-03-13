from PyQt5 import QtCore, QtWidgets, QtGui
from pathlib import Path
from conan_app_launcher.components import parse_config_file, write_config_file, TabConfigEntry, ConanApi
from typing import TYPE_CHECKING, List, Optional

Qt = QtCore.Qt

if TYPE_CHECKING:
    from conan_app_launcher.ui.main_window import MainUi


class ConanFileSystemModel(QtWidgets.QFileSystemModel):  # QtCore.QSortFilterProxyModel):
    FILTERED_ITEMS = [".lock", ".count", "metadata.json",
                      "conaninfo.txt", "conanmanifest.txt"  # TODO ??
                      ]

    def __init__(self):
        # self.setDynamicSortFilter(True)
        # self.setRecursiveFilteringEnabled(True)
        # self.setFilterKeyColumn(0)
        #self = QtWidgets.QFileSystemModel(self.sourceModel())
        super().__init__()
        #self.base_path = r"C:\Users\goszp\.conan\data"
        #self.short_path = r"C:\.conan"
        #self.short_path_model = QtWidgets.QFileSystemModel()
        #self.short_path_model.setRootPath(self.short_path)

    def is_short_path_package_dir(self, model_index):
        path = self.fileInfo(model_index).absoluteFilePath()
        c_p = Path(path) / ".conan_link"

        if c_p.is_file():
            with c_p.open("r") as fp:
                return fp.read()
        return ""

    # def index(self, row, column, parent):
    #     index = super().index(row, column, parent)
    #     # if self.short_path_model.checkIndex(index):
    #     #     return self.short_path_model.fileName(index)
    #     if column == 0:
    #         model_index = index  # self.mapToSource(index)
    #         short_path_dir = self.is_short_path_package_dir(model_index)
    #         path = self.fileInfo(model_index).absoluteFilePath()
    #         if short_path_dir:
    #             new_index = self.short_path_model.index(short_path_dir, column)
    #             path = self.short_path_model.fileInfo(new_index).absoluteFilePath()
    #             print("index: " + path + " " + short_path_dir)
    #             return new_index
    #     return index

    # def index(self, path, column=0):
    #     return super().index(path, column)

    # def data(self, index, role):
    #     data = super().data(index, role)
    #     if role == QtCore.Qt.DisplayRole:
    #         if self.short_path_model.checkIndex(index):
    #             return self.short_path_model.fileName(index)
    #         #     model_index = self.mapToSource(index)
    #         #     short_path_dir = self.is_short_path_package_dir(model_index)
    #         #     path = self.fileInfo(model_index).absoluteFilePath()
    #         #     if short_path_dir:
    #         #         #new_index = self.short_path_model.index(short_path_dir, 0)
    #         #         return Path(short_path_dir).name  # self.short_path_model.fileName(new_index)
    #         #     return data
    #     return data

    # def rowCount(self, index):
    #     model_index = index  # self.mapToSource(index)
    #     path = self.fileInfo(model_index).absoluteFilePath()
    #     short_path_dir = self.is_short_path_package_dir(model_index)

    #     if self.short_path in path or short_path_dir:
    #         return len(sorted(Path(short_path_dir).glob("*")))
    #     if self.short_path_model.checkIndex(index):
    #         path = self.short_path_model.fileInfo(index).absoluteFilePath()
    #         print(path + " " + str(self.short_path_model.rowCount(index)))
    #         return self.short_path_model.rowCount(index)
    #     print(path + " " + str(super().rowCount(index)))
    #     return super().rowCount(index)

    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        # filter out internal files
        index = self.index(source_row, 0, source_parent)
        # model_index = self.mapToSource(index)
        name = self.fileName(index)
        if self.fileInfo(index).isDir():
            return True

        for item in self.FILTERED_ITEMS:
            if item in name:
                return False
        return True


class LocalConanPackageExplorer():
    def __init__(self, main_window: "MainUi"):
        self._main_window = main_window
        # TODO display conaninfo.txt on the right
        # self.model = QtWidgets.QFileSystemModel()
        # self.model.setRootPath(r"C:\Users\goszp\.conan\data")

        # dirModel -> setFilter(QDir: : NoDotAndDotDot |
        #                       QDir:: AllDirs);
        self.proxy = ConanFileSystemModel()
        storage_path = Path(ConanApi().conan.config_get("storage.path"))

        self.proxy.setRootPath(str(storage_path))

        # self.proxy.setSourceModel(self.model)
        # self.model_index = self.model.index(self.model.rootDirectory().absolutePath())
        # print(self.model.rootDirectory().absolutePath())
        # self.proxy_index = self.proxy.mapFromSource(self.model_index)
        self._main_window.ui.package_view.setModel(self.proxy)
        self.proxy.sort(0, Qt.AscendingOrder)
        self._main_window.ui.package_view.setRootIndex(
            self.proxy.index(self.proxy.rootDirectory().absolutePath()))

        # self._main_window.ui.package_view.clicked.connect(self.on_click)
        self._main_window.ui.package_view.setColumnHidden(1, True)
        self._main_window.ui.package_view.setColumnHidden(2, True)
        self._main_window.ui.package_view.setColumnWidth(0, 310)
        # self._main_window.ui.package_view.setRootIsDecorated(False)
        # self._main_window.ui.package_view.setItemsExpandable(False)
        self._main_window.ui.package_view.selectionModel().selectionChanged.connect(
            self.on_selection_change)

    # @pyqtSlot(int)
    def on_selection_change(self):  # , index: int):
        # change folder in file view
        view_index = self._main_window.ui.package_view.selectionModel().selectedIndexes()[0]
        # proxy_index = self.proxy.mapToSource(view_index)
        # item_name = self.model.fileName(proxy_index)
        # # TODO discover upstream, if in package
        # path = self.model.fileInfo(proxy_index).absoluteFilePath()
        # c_p = Path(path) / "conaninfo.txt"
        # if c_p.is_file():
        #     text = ""
        #     with open(c_p, "r") as fp:
        #         text = fp.read()
        #     self.package_info.setText(text)
