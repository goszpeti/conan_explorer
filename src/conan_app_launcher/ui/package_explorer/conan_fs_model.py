from PyQt5 import QtCore, QtWidgets, QtGui
from pathlib import Path
from conan_app_launcher.components import parse_config_file, write_config_file, TabConfigEntry, ConanApi
from typing import TYPE_CHECKING, List, Optional
import os
Qt = QtCore.Qt


class ConanFilterProxyModel(QtCore.QSortFilterProxyModel):
    FILTERED_ITEMS = [".lock", ".count", "metadata.json",
                      "conaninfo.txt", "conanmanifest.txt"  # TODO ??
                      ]

    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        # filter out internal files
        # index = self.sourceModel().index(source_row, 0, source_parent)
        # # model_index = self.mapToSource(index)
        # name = self.sourceModel().fileName(index)
        # if self.sourceModel().fileInfo(index).isDir():
        #     return True

        # for item in self.FILTERED_ITEMS:
        #     if item in name:
        #         return False
        return True

    def sourceFileInfo(self, index):
        return super().sourceFileInfo(index)


class ConanFileSystemModel(QtWidgets.QFileSystemModel):
    def __init__(self):
        super().__init__()
        self._conan = ConanApi()
        self.setReadOnly(False)
        self.setOption(self.DontWatchForChanges, True)
        # Set up filters for builtin conan files
        self.proxy_model = ConanFilterProxyModel()
        self.proxy_model.setDynamicSortFilter(False)
        self.proxy_model.setSourceModel(self)
        #self.proxy_model.setFilterKeyColumn(0); # filter name
        # Initalize Short path sub fs model
        self.short_path_model = QtWidgets.QFileSystemModel()
        self.short_path_model.setFilter(QtCore.QDir.AllEntries | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.short_path_model.setRootPath(str(self._conan.get_short_path_root()))
        self.short_path_model.setOption(self.DontWatchForChanges, True)

        self.short_path_map = {}

    def is_sub_package_dir(self, proxy_index):
        index = self.proxy_model.mapToSource(proxy_index)
        path = Path(self.fileInfo(index).absoluteFilePath())
        if self.is_short_path_package_dir(index):
            return self.get_short_path_package_dir(index)
        # TODO currently only check if a folder named package is a parent folder
        if "package" in path.parents._parts:
            pkg_id_index = path.parents._parts.index("package") + 1
            path_parent_index = len(path.parents) - pkg_id_index - 1
            if path_parent_index == -1:
                return path
            if path_parent_index == -2:
                return False
            return path.parents[path_parent_index]
        return False

    def is_short_path_package_dir(self, model_index):
        #self.rowCount(self.index_from_path(r"C:\Users\goszp\.conan\data\example\1.0.0"))
        path = Path(self.fileInfo(model_index).absoluteFilePath())
        if not path.exists() or not path.is_absolute():
            return False
        # we are still in the conan data path
        if os.path.commonpath([self._conan.get_short_path_root()]) == os.path.commonpath([self._conan.get_short_path_root(), path]):
            return True
        return False

    def get_short_path_package_dir(self, model_index):
        """ TODO: use ConanAPI. """
        path = self.fileInfo(model_index).absoluteFilePath()
        if not self.short_path_map.get(path, ""):
            c_p = Path(path) / ".conan_link"
            if c_p.is_file():
                with c_p.open("r") as fp:
                    short_path = fp.read()
                    self.short_path_map[path] = short_path
                    return short_path
            return ""
        else:
            return self.short_path_map.get(path)

    # def fileInfo(self, index):
    #     file_info = super().fileInfo(index)
    #     return file_info

    def index(self, row, column, parent):
        # if self.short_path_model.checkIndex(index):
        #     return self.short_path_model.fileName(index)
        #if column == 0:
        short_path_dir = self.get_short_path_package_dir(parent)  # parent
        if os.path.exists(short_path_dir):
            #sh_index = self.short_path_model.index(short_path_dir, column)
            #list = os.listdir(short_path_dir)
            #i2 = self.short_path_model.index(row, column, sh_index)
            sh_index = self.short_path_model.index(os.path.join(short_path_dir, os.listdir(short_path_dir)[row]), column)
            return sh_index
        return super().index(row, column, parent)

    def index_from_path(self, path, column=0):
        return super().index(path, column)

    # def fetchMore(self, parent):
    #     fm = super().fetchMore(parent)
    #     return fm

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            if self.short_path_model.checkIndex(index):  # what to do for 1?
                name = self.short_path_model.data(index)
                return name
            # if role == QtCore.Qt.FilePathRole:

        # if role == QtCore.Qt.FileNameRole:
        return super().data(index, role)

    def rowCount(self, parent):
        if (parent.column() > 0):
            return 0
        count = super().rowCount(parent)
        short_path_dir = self.get_short_path_package_dir(parent)
        if os.path.exists(short_path_dir):
            return len(os.listdir(short_path_dir))
            # s_index = self.short_path_model.index(short_path_dir, 0)
            # self.short_path_model.fileInfo(s_index).absoluteFilePath()
            # return self.short_path_model.rowCount(s_index)
        # if self.short_path_model.checkIndex(index):
        #     return self.short_path_model.rowCount(index)
    #         if (parent.column() > 0)
    #     return 0

    # if (!parent.isValid())
    # return d -> root.visibleChildren.count()

    # const QFileSystemModelPrivate:: QFileSystemNode * parentNode = d -> node(parent)
    # return parentNode -> visibleChildren.count()
        return count
