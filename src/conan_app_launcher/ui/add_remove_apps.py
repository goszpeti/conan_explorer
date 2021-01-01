from PyQt5 import QtCore, QtWidgets
from typing import List
from conan_app_launcher.components import AppConfigEntry
from conan_app_launcher.ui.qt import add_remove_apps
from conan_app_launcher.ui.edit_app import EditAppDialog

Qt = QtCore.Qt


class AppsListModel(QtCore.QAbstractListModel):
    def __init__(self, apps=List[AppConfigEntry]):
        super().__init__()
        self.apps = apps.get_app_entries()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.apps[index.row()].name
            return text

        # if role == Qt.DecorationRole:
         #   status, _ = self.apps[index.row()]
            # if status:
            #     return tick

    def rowCount(self, index):
        return len(self.apps)


class AddRemoveAppsDialog(QtWidgets.QDialog):

    def __init__(self, tab, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        # save dialog, otherwise it will close
        self.tab = tab
        self.dialog = QtWidgets.QDialog()
        self.dialog.setModal(True)
        self._add_dialog = add_remove_apps.Ui_Dialog()
        self._add_dialog.setupUi(self.dialog)
        # self.addButton.pressed.connect(self.add)
        # self.deleteButton.pressed.connect(self.delete)
        self.model = AppsListModel(tab)
        self._add_dialog.app_list_view.setModel(self.model)
        self._add_dialog.app_list_view.doubleClicked.connect(self.double_click_item)
        self.dialog.show()

    def double_click_item(self):
        index = self._add_dialog.app_list_view.selectionModel().currentIndex()
        data = self.model.itemData(index)
        app_name = data.get(0)  # 0th entry
        app = self.tab.get_app_entry(app_name)
        if app:
            self._edit_app_dialog = EditAppDialog(app, self)
