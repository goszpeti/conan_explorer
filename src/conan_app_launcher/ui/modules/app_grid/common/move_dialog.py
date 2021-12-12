
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from conan_app_launcher import asset_path
from conan_app_launcher.logger import Logger
from conan_app_launcher.ui.modules.app_grid.model import UiAppLinkModel, UiTabModel

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt

current_dir = Path(__file__).parent


class MoveAppLinksDialog(QtWidgets.QDialog):

    def __init__(self,  tab_ui_model: UiTabModel, parent: QtWidgets.QWidget, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self._ui = uic.loadUi(current_dir / "app_link_sort_dialog.ui", baseinstance=self)
        self.setWindowIcon(QtGui.QIcon(str(asset_path / "icons" / "rearrange.png")))

        self._ui.list_view.setModel(tab_ui_model)

        self._ui.list_view.setUpdatesEnabled(True)
        self._ui.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._ui.list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self._ui.move_up_button.clicked.connect(self.move_up)
        self._ui.move_down_button.clicked.connect(self.move_down)
        self._ui.button_box.accepted.connect(self.accept)

    def move_up(self):
        """ Moves the selected item(s) up in the list """
        sel_indexes = self._ui.list_view.selectedIndexes()
        if len(sel_indexes) == 0:
            Logger().info('Select at least one item from list!')

        try:
            sel_indexes.sort()  # selected indexes need to be sorted
            first_row = sel_indexes[0].row() - 1
            if not first_row >= 0:
                return
            self.list_view.selectionModel().clearSelection()

            for idx in sel_indexes:
                if idx is None:
                    continue
                row = idx.row()
                pre_idx = self.list_view.model().index(row - 1)
                self.list_view.model().beginMoveRows(idx, row, row, pre_idx, pre_idx.row())
                self.list_view.model().moveRow(idx, row, pre_idx, pre_idx.row())
                self.list_view.model().endMoveRows()
                self.list_view.selectionModel().select(pre_idx, QtCore.QItemSelectionModel.Select)
        except Exception as e:
            print(e)

    def move_down(self):
        """ Moves the selected item(s) down in the list """
        max_row = self._ui.list_view.model().rowCount()
        indexes = self.list_view.selectedIndexes()
        if len(indexes) == 0:
            Logger().info('Select at least one item from list!')

        try:  # modify from reverse so qt index does not get reset
            indexes.sort()
            self.list_view.selectionModel().clearSelection()
            last_sel_row = indexes[-1].row() + 1
            if not last_sel_row < max_row:  # cannot be moved down
                return
            for idx in reversed(indexes):
                if idx is None:
                    continue
                row = idx.row()
                post_idx = self.list_view.model().index(row + 2)
                post_sel_idx = self.list_view.model().index(row + 1)
                self.list_view.model().beginMoveRows(idx, row, row, post_sel_idx, post_sel_idx.row())
                self.list_view.model().moveRow(idx, row, post_idx, row + 2)
                self.list_view.model().endMoveRows()
                self.list_view.selectionModel().select(post_sel_idx, QtCore.QItemSelectionModel.Select)
        except Exception as e:
            print(e)

    def save(self):
        self._ui.list_view.model().save()
