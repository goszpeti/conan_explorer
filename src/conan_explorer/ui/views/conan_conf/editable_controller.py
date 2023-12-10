from typing import Union

import conan_explorer.app as app
from conan_explorer.app.logger import Logger
from PySide6.QtCore import QModelIndex, QItemSelectionModel
from PySide6.QtWidgets import QTreeView

from conan_explorer.conan_wrapper.types import EditablePkg

from .editable_model import EditableModel, EditableModelItem

class ConanEditableController():

    def __init__(self, view: QTreeView) -> None:
        self._view = view
        self._model = EditableModel()
        self._view.setModel(self._model)
        self.update()

    def update(self):
        # save selected remote, if triggering a re-init
        sel_edit = self.get_selected_editable()
        self._model.setup_model_data()
        self._view.setItemsExpandable(False)
        self._view.setRootIsDecorated(False)
        self._view.expandAll()
        self.resize_remote_columns()

        if sel_edit:
            self._select_editable(sel_edit.conan_ref)

    def resize_remote_columns(self):
        for i in reversed(range(self._model.root_item.column_count() - 1)):
            self._view.resizeColumnToContents(i)
        # TODO calculate, if we need to make the name smaller
        self._view.setColumnWidth(1, 400)
        self._view.columnViewportPosition(0)

    def _select_editable(self, name: str) -> bool:
        """ Selects ane idtable in the view and returns true if it exists. """
        row_remote_to_sel = -1
        row = 0
        editable_item = None
        for editable_item in self._model.root_item.child_items:
            if editable_item.name == name:
                row_remote_to_sel = row
                break
            row += 1
        if row_remote_to_sel < 0:
            Logger().debug("No editable to select")
            return False
        sel_model = self._view.selectionModel()
        sel_model.clearSelection()
        for column in range(self._model.columnCount(QModelIndex())):
            index = self._model.index(row_remote_to_sel, column, QModelIndex())
            sel_model.select(index, QItemSelectionModel.SelectionFlag.Select)
        return True

    def add(self, editable: EditablePkg):
        if not editable:
            return
        return self._model.add(editable)

    def remove(self, editable: EditablePkg):
        if not editable:
            return
        return self._model.remove(editable)

    def get_selected_editable(self) -> Union[EditablePkg, None]:
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:  # can be multiple - always get 0
            Logger().debug("No selected item for context action")
            return None
        item: EditableModelItem = indexes[0].internalPointer()  # type: ignore
        return app.conan_api.get_editable(item.name)


