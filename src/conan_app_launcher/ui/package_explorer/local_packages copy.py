from PyQt5 import QtCore, QtWidgets, QtGui, uic
from pathlib import Path


class CustomProxyModel(QtWidgets.QFileSystemModel):  # QtCore.QSortFilterProxyModel):
    FILTERED_ITEMS = [".lock", ".count", "metadata.json",
                      "conaninfo.txt", "conanmanifest.txt"  # TODO ??
                      ]

    def __init__(self):
        super().__init__()
        # self.setDynamicSortFilter(True)
        # self.setRecursiveFilteringEnabled(True)
        # self.setFilterKeyColumn(0)
        #self.model = QtWidgets.QFileSystemModel(self.sourceModel())
        self.setRootPath(r"C:\Users\goszp\.conan\data")
        self.base_path = r"C:\Users\goszp\.conan\data"
        self.short_path = r"C:\.conan"
        self.short_path_model = QtWidgets.QFileSystemModel()
        self.short_path_model.setRootPath(self.short_path)

    def is_short_path_package_dir(self, model_index):
        path = self.model.fileInfo(model_index).absoluteFilePath()
        c_p = Path(path) / ".conan_link"

        if c_p.is_file():
            with c_p.open("r") as fp:
                return fp.read()
        return ""

    def index(self, row, column, parent):
        index = super().index(row, column, parent)
        # if self.short_path_model.checkIndex(index):
        #     return self.short_path_model.fileName(index)
        if column == 0:
            model_index = self.mapToSource(index)
            short_path_dir = self.is_short_path_package_dir(model_index)
            path = self.model.fileInfo(model_index).absoluteFilePath()
            if short_path_dir:
                new_index = self.short_path_model.index(short_path_dir, column)
                path = self.short_path_model.fileInfo(new_index).absoluteFilePath()
                print("index: " + path + " " + short_path_dir)
                return new_index
        return index

    # def index(self, path, column=0):
    #     index = super().index(path, column)
    #     return index

    def data(self, index, role):
        data = super().data(index, role)
        if role == QtCore.Qt.DisplayRole:
            if self.short_path_model.checkIndex(index):
                return self.short_path_model.fileName(index)
            #     model_index = self.mapToSource(index)
            #     short_path_dir = self.is_short_path_package_dir(model_index)
            #     path = self.model.fileInfo(model_index).absoluteFilePath()
            #     if short_path_dir:
            #         #new_index = self.short_path_model.index(short_path_dir, 0)
            #         return Path(short_path_dir).name  # self.short_path_model.fileName(new_index)
            #     return data
        return data

    def rowCount(self, index):
        model_index = self.mapToSource(index)
        path = self.model.fileInfo(model_index).absoluteFilePath()
        short_path_dir = self.is_short_path_package_dir(model_index)

        if self.short_path in path or short_path_dir:
            return len(sorted(Path(short_path_dir).glob("*")))
        if self.short_path_model.checkIndex(index):
            path = self.short_path_model.fileInfo(index).absoluteFilePath()
            print(path + " " + str(self.short_path_model.rowCount(index)))
            return self.short_path_model.rowCount(index)
        print(path + " " + str(super().rowCount(index)))
        return super().rowCount(index)

    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        # filter out internal files
        index = self.sourceModel().index(source_row, 0, source_parent)
        # model_index = self.mapToSource(index)
        name = self.model.fileName(index)
        if self.model.fileInfo(index).isDir():
            return True

        for item in self.FILTERED_ITEMS:
            if item in name:
                return False
        return True

    def insertRows(self, position, rows=1, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for row in range(rows):
            self.insertRows(position, row, parent)
            self.setData(parent, "AWESOME")
            print('AWESOME VIRTUAL ROW')
        self.endInsertRows()
        return True
