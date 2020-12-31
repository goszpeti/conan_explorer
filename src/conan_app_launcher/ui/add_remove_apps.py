from PyQt5 import QtCore, QtWidgets

from conan_app_launcher.ui.qt import add_remove_apps
Qt = QtCore.Qt


class EditAppDialog(QtWidgets.QDialog):

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        # save dialog, otherwise it will close
        self.dialog = QtWidgets.QDialog()
        self.dialog.setModal(True)
        self._add_dialog = add_remove_apps.Ui_Dialog()
        self._add_dialog.setupUi(self.dialog)
        # self.addButton.pressed.connect(self.add)
        # self.deleteButton.pressed.connect(self.delete)
        self.model = AppsListModel(self._tab_info[0])
        self._add_dialog.app_list_view.setModel(self.model)
        self._add_dialog.app_list_view.doubleClicked.connect(self.double_click_item)
        self.dialog.show()

    def double_click_item(self):
        app = self.model[self._add_dialog.app_list_view.selectionModel().currentIndex()
                         ]
