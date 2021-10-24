from PyQt5 import QtCore, QtWidgets, QtGui
from pathlib import Path
from conan_app_launcher.components import parse_config_file, write_config_file, TabConfigEntry, ConanApi
from typing import TYPE_CHECKING, List, Optional
import os
Qt = QtCore.Qt

class ConanFileSystemModel(QtWidgets.QFileSystemModel):
    def __init__(self):
        super().__init__()
        self._conan = ConanApi()
        self.setReadOnly(False)
        self.setOption(self.DontWatchForChanges, True)
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
                    return 
            return ""
        else:
            return self.short_path_map.get(path)
            self.createIndex()

    # def fileInfo(self, index):
    #     file_info = super().fileInfo(index)
    #     return file_info

    def index(self, row, column, parent):
        model_index = super().index(row, column, parent)
        # if self.short_path_model.checkIndex(index):
        #     return self.short_path_model.fileName(index)
        # if column == 0:
        #     short_path_dir = self.get_short_path_package_dir(model_index)  # parent
        #     if short_path_dir:
        #         sh_index = self.short_path_model.index(short_path_dir, column)
        #         i2 = self.short_path_model.index(row, column, sh_index)
        #         return i2
            
            # i = self.short_path_model.index(self.fileInfo(model_index).absoluteFilePath(), column)
            # if self.short_path_model.checkIndex(model_index):
            #     return i
            #     #path = self.fileInfo(model_index).absoluteFilePath()
            #     #short_path_dir = self.get_short_path_package_dir(model_index)
            #     new_index = self.short_path_model.index(short_path_dir, column)
            #     # path = self.short_path_model.fileInfo(new_index).absoluteFilePath()
            #     # print("index: " + path + " " + short_path_dir)
            #     return new_index
        return model_index

    def index_from_path(self, path, column=0):
        return super().index(path, column)

    def data(self, index, role):
        #data = super().data(index, role)
        # if role == QtCore.Qt.DisplayRole:
        #     if self.short_path_model.checkIndex(index):  # what to do for 1?
        #         name = self.short_path_model.data(index)
        #         # if name == "1":
        #         #     return "package"
        #         return name
            #     model_index = self.mapToSource(index)
            #     short_path_dir = self.is_short_path_package_dir(model_index)
            #     path = self.fileInfo(model_index).absoluteFilePath()
            #     if short_path_dir:
            #         #new_index = self.short_path_model.index(short_path_dir, 0)
            #         return Path(short_path_dir).name  # self.short_path_model.fileName(new_index)
            #     return data
        return super().data(index, role)

    # def rowCount(self, index):
    #     count = super().rowCount(index)
    #     short_path_dir = self.get_short_path_package_dir(index)
    #     if short_path_dir:
    #         return len(os.listdir(short_path_dir))
    #         # s_index = self.short_path_model.index(short_path_dir, 0)
    #         # self.short_path_model.fileInfo(s_index).absoluteFilePath()
    #         # return self.short_path_model.rowCount(s_index)
    #     # if self.short_path_model.checkIndex(index):
    #     #     return self.short_path_model.rowCount(index)
        
    #     return count
