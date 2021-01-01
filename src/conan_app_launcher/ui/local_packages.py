from PyQt5 import QtCore, QtWidgets, QtGui, uic


class CustomProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        # self.setDynamicSortFilter(True)

    def rowCount(self, index):
        model_index = self.mapToSource(index)
        if not model_index.isValid():
            return 0
        new_rc = self.sourceModel().rowCount(model_index) + 1
        # self.insertRows(0)
        return new_rc

    def insertRows(self, position, rows=1, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for row in range(rows):
            self.insertRows(position, row, parent)
            self.setData(parent, "AWESOME")
            print('AWESOME VIRTUAL ROW')
        self.endInsertRows()
        return True


self.model = QtWidgets.QFileSystemModel()
self.model.setRootPath(r"C:\Users\goszp\.conan\data")

# dirModel -> setFilter(QDir: : NoDotAndDotDot |
#                       QDir:: AllDirs);
self.proxy = CustomProxyModel()
self.proxy.setSourceModel(self.model)
self.model_index = self.model.index(self.model.rootDirectory().absolutePath())
print(self.model.rootDirectory().absolutePath())
self.proxy_index = self.proxy.mapFromSource(self.model_index)
self._ui.treeView.setModel(self.proxy)

self._ui.treeView.setRootIndex(self.proxy_index)
self.fileModel = QtWidgets.QFileSystemModel(self)
self.fileModel.setFilter(QtCore.QDir.NoDotAndDotDot |
                         QtCore.QDir.Files)
self.fileModel.setRootPath(self.model.rootDirectory().absolutePath())
self._ui.listView.setModel(self.fileModel)

# self._ui.treeView.clicked.connect(self.on_click)
self._ui.treeView.setColumnHidden(1, True)
self._ui.treeView.setColumnHidden(2, True)
self._ui.treeView.setColumnWidth(0, 310)
# self._ui.treeView.setRootIsDecorated(False)
# self._ui.treeView.setItemsExpandable(False)
self._ui.treeView.selectionModel().selectionChanged.connect(
    self.on_selection_change)
