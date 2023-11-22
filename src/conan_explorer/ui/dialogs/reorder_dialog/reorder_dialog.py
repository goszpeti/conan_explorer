
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from conan_explorer.app.logger import Logger
from PySide6.QtCore import QItemSelectionModel, QModelIndex, QPersistentModelIndex
from PySide6.QtWidgets import QWidget, QAbstractItemView, QDialog, QListView, QTreeView

from conan_explorer.ui.common.theming import get_themed_asset_icon


if TYPE_CHECKING:
    from typing import Protocol
else:
    try:
        from typing import Protocol
    except ImportError:
        from typing_extensions import Protocol

current_dir = Path(__file__).parent
class ReorderingModel(Protocol):
    def index(self, row: int, column: int, parent: "QModelIndex | QPersistentModelIndex") -> QModelIndex:
        ...

    def columnCount(self, parent: "QModelIndex | QPersistentModelIndex") -> int: ...

    def moveRow(self, source_parent: QModelIndex, source_row: int, 
                destination_parent: QModelIndex, destination_child: int) -> bool:
        ...

    def beginMoveRows(self, sourceParent: QModelIndex, sourceFirst: int, sourceLast: int, 
                      destinationParent: "QModelIndex | QPersistentModelIndex", destinationRow: int) -> bool:
        ...

    def endMoveRows(self):
        ...

    def save(self):
        ...

    def rowCount(self) -> int:
        ...

class ReorderDialog(QDialog):

    def __init__(self, model: ReorderingModel, parent: Optional[QWidget]):
        super().__init__(parent=parent)
        from .reorder_dialog_ui import Ui_rearrange_dialog
        self._ui = Ui_rearrange_dialog()
        self._ui.setupUi(self)

        self.setWindowIcon(get_themed_asset_icon("icons/rearrange.svg", True))
        
        self._controller = ReorderController(self._ui.list_view, model)
        self._ui.list_view.setModel(model) # type: ignore

        self._ui.list_view.setUpdatesEnabled(True)
        self._ui.list_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._ui.list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self._ui.move_up_button.clicked.connect(self._controller.move_up)
        self._ui.move_down_button.clicked.connect(self._controller.move_down)
        self._ui.button_box.accepted.connect(self.on_save)
        
    def on_save(self):
        self._controller.save()
        self.accept()

class ReorderController():
    
    def __init__(self, view: "QListView| QTreeView", model: ReorderingModel) -> None:
        self._view = view
        self._model = model

    def move_to_position(self, position: int):
        """ Moves the selected item up in the list """
        sel_indexes = self._view.selectedIndexes()
        rows_selected = set([index.row() for index in sel_indexes])

        if len(rows_selected) != 1:
            Logger().info('Select at exactly one item from list!')
            return

        target_position = position
        if position == -1: # use -1 for last element
            position = self._model.rowCount() - 1
            target_position = position  + 1 # insert after last element

        try:
            self._view.selectionModel().clearSelection()
            idx = sel_indexes[0]
            if idx is None:
                return
            row = idx.row()
            if row == position:
                return
            pre_idx = self._model.index(position, 0, self._view.rootIndex())
            self._view.model().beginMoveRows(idx, row, row, pre_idx, pre_idx.row())
            self._view.model().moveRow(idx, row, pre_idx, target_position)
            self._view.model().endMoveRows()
            # for all columns
            for column in range(self._model.columnCount(QModelIndex())):
                index = self._model.index(position, column, QModelIndex())
                self._view.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
        except Exception as e:
            print(e)

    def move_up(self):
        """ Moves the selected item(s) up in the list """
        sel_indexes = self._view.selectedIndexes()
        if len(sel_indexes) == 0:
            Logger().info('Select at least one item from list!')
            return

        try:
            # selected indexes need to be sorted
            sel_indexes.sort() # type: ignore 
            first_row = sel_indexes[0].row() - 1
            if first_row < 0:
                return
            self._view.selectionModel().clearSelection()

            rows_moved = [] # optimize for multiple coloumns
            for idx in sel_indexes:
                if idx is None:
                    continue
                row = idx.row()
                if row in rows_moved:
                    continue
                rows_moved.append(row)

                pre_idx = self._model.index(row - 1, 0, self._view.rootIndex())
                self._view.model().beginMoveRows(idx, row, row, pre_idx, pre_idx.row())
                self._view.model().moveRow(idx, row, pre_idx, pre_idx.row())
                self._view.model().endMoveRows()
                # for all columns
                for column in range(self._model.columnCount(QModelIndex())):
                    index = self._model.index(row-1, column, QModelIndex())
                    self._view.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
        except Exception as e:
            print(e)

    def move_down(self):
        """ Moves the selected item(s) down in the list """
        max_row = self._view.model().rowCount()
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:
            Logger().info('Select at least one item from list!')
            return

        try:  # modify from reverse so qt index does not get reset
            indexes.sort() # type: ignore
            self._view.selectionModel().clearSelection()
            last_sel_row = indexes[-1].row() + 1
            if last_sel_row >= max_row:  # cannot be moved down
                return
            rows_moved = [] # optimize for multiple coloumns
            for idx in reversed(indexes):
                if idx is None:
                    continue
                row = idx.row()
                if row in rows_moved:
                    continue
                rows_moved.append(row)

                post_idx = self._model.index(row + 2, 0, self._view.rootIndex())
                post_sel_idx = self._model.index(row + 1, 0, self._view.rootIndex())
                self._model.beginMoveRows(idx, row, row, post_sel_idx, post_sel_idx.row())
                self._model.moveRow(idx, row, post_idx, row + 2)
                self._model.endMoveRows()

                # for all columns
                for column in range(self._model.columnCount(QModelIndex())):
                    index = self._model.index(row+1, column, QModelIndex())
                    self._view.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
        except Exception as e:
            print(e)

    def save(self):
        self._model.save()