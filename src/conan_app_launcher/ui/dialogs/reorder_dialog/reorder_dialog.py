
from pathlib import Path
from typing import Optional, Union

from conan_app_launcher import asset_path
from conan_app_launcher.app.logger import Logger
from PyQt5.QtCore import Qt, QItemSelectionModel, QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QDialog, QListView, QTreeView
from PyQt5.QtGui import QIcon

from .reorder_dialog_ui import Ui_rearrange_dialog

current_dir = Path(__file__).parent


class ReorderingModel(QAbstractListModel):

    def moveRow(self, source_parent: QModelIndex, source_row: int, destination_parent: QModelIndex, destination_child: int) -> bool:
        ...

    def save(self):
        ...

class ReorderDialog(QDialog):

    def __init__(self, model: ReorderingModel, parent: Optional[QWidget], flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self._ui = Ui_rearrange_dialog()
        self._ui.setupUi(self)

        self.setWindowIcon(QIcon(str(asset_path / "icons" / "rearrange.png")))
        
        self._controller = ReorderController(self._ui.list_view, model)

        self._ui.list_view.setModel(model)

        self._ui.list_view.setUpdatesEnabled(True)
        self._ui.list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._ui.list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self._ui.move_up_button.clicked.connect(self._controller.move_up)
        self._ui.move_down_button.clicked.connect(self._controller.move_down)
        self._ui.button_box.accepted.connect(self.on_save)
        
    def on_save(self):
        self._controller.save()
        self.accept()

class ReorderController():
    
    def __init__(self, view: Union[QListView, QTreeView], model: ReorderingModel) -> None:
        self._view = view
        self._model = model
        
        self._view.setModel(model)

    def move_up(self):
        """ Moves the selected item(s) up in the list """
        sel_indexes = self._view.selectedIndexes()
        if len(sel_indexes) == 0:
            Logger().info('Select at least one item from list!')

        try:
            sel_indexes.sort()  # selected indexes need to be sorted
            first_row = sel_indexes[0].row() - 1
            if first_row < 0:
                return
            self._view.selectionModel().clearSelection()

            for idx in sel_indexes:
                if idx is None:
                    continue
                row = idx.row()
                pre_idx = self._model.index(row - 1, 0, self._view.rootIndex())
                self._view.model().beginMoveRows(idx, row, row, pre_idx, pre_idx.row())
                self._view.model().moveRow(idx, row, pre_idx, pre_idx.row())
                self._view.model().endMoveRows()
                # for all columns
                for column in range(self._model.columnCount(QModelIndex())):
                    index = self._model.index(row-1, column, QModelIndex())
                    self._view.selectionModel().select(index, QItemSelectionModel.Select)
        except Exception as e:
            print(e)

    def move_down(self):
        """ Moves the selected item(s) down in the list """
        max_row = self._view.model().rowCount()
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:
            Logger().info('Select at least one item from list!')

        try:  # modify from reverse so qt index does not get reset
            indexes.sort()
            self._view.selectionModel().clearSelection()
            last_sel_row = indexes[-1].row() + 1
            if last_sel_row >= max_row:  # cannot be moved down
                return
            for idx in reversed(indexes):
                if idx is None:
                    continue
                row = idx.row()
                post_idx = self._model.index(row + 2, 0, self._view.rootIndex())
                post_sel_idx = self._model.index(row + 1, 0, self._view.rootIndex())
                self._model.beginMoveRows(idx, row, row, post_sel_idx, post_sel_idx.row())
                self._model.moveRow(idx, row, post_idx, row + 2)
                self._model.endMoveRows()
                # for all columns
                for column in range(self._model.columnCount(QModelIndex())):
                    index = self._model.index(row+1, column, QModelIndex())
                    self._view.selectionModel().select(index, QItemSelectionModel.Select)
        except Exception as e:
            print(e)

    def save(self):
        self._model.save()