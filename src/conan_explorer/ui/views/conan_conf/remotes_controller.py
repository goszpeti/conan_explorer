from typing import Optional, Union

import conan_explorer.app as app
from conan_explorer.app.logger import Logger
from conan_explorer.ui.dialogs import ReorderController
from PySide6.QtCore import QModelIndex, QItemSelectionModel, SignalInstance
from PySide6.QtWidgets import QApplication, QTreeView

from .remotes_model import RemotesModelItem, RemotesTableModel


class ConanRemoteController():

    def __init__(self, view: QTreeView, conan_remotes_updated: Optional[SignalInstance]) -> None:
        self._view = view
        self._model = RemotesTableModel()
        self.conan_remotes_updated = conan_remotes_updated

    def update(self):
        self._model = RemotesTableModel()
        # save selected remote, if triggering a re-init
        sel_remote = self.get_selected_remote()
        self._remote_reorder_controller = ReorderController(
            self._view, self._model)

        self._model.setup_model_data()
        self._view.setItemsExpandable(False)
        self._view.setRootIsDecorated(False)
        self._view.setModel(self._model)
        self._view.expandAll()
        self.resize_remote_columns()

        if sel_remote:
            self._select_remote(sel_remote.remote.name)
        if self.conan_remotes_updated:
            self.conan_remotes_updated.emit()

    def resize_remote_columns(self):
        for i in reversed(range(self._model.root_item.column_count() - 1)):
            self._view.resizeColumnToContents(i)
        # TODO calculate, if we need to make the name smaller
        self._view.setColumnWidth(1, 400)
        self._view.columnViewportPosition(0)

    def _select_remote(self, remote_name: str) -> bool:
        """ Selects a remote in the view and returns true if it exists. """
        row_remote_to_sel = -1
        row = 0
        remote_item = None
        for remote_item in self._model.root_item.child_items:
            if remote_item.item_data[0] == remote_name:
                row_remote_to_sel = row
                break
            row += 1
        if row_remote_to_sel < 0:
            Logger().debug("No remote to select")
            return False
        sel_model = self._view.selectionModel()
        sel_model.clearSelection()
        for column in range(self._model.columnCount(QModelIndex())):
            index = self._model.index(row_remote_to_sel, column, QModelIndex())
            sel_model.select(index, QItemSelectionModel.SelectionFlag.Select)
        return True

    def move_up(self):
        self._remote_reorder_controller.move_up()

    def move_down(self):
        self._remote_reorder_controller.move_down()

    def move_to_top(self):
        self._remote_reorder_controller.move_to_position(0)

    def move_to_bottom(self):
        self._remote_reorder_controller.move_to_position(-1)

    def remove(self, remote_name: str):
        app.conan_api.remove_remote(remote_name)
        self.update()

    def remote_disable(self, model_index):
        remote_item = self.get_selected_remote()
        if not remote_item:
            return
        app.conan_api.disable_remote(
            remote_item.remote.name, not remote_item.remote.disabled)
        self.update()

    def copy_remote_name(self):
        remote_item = self.get_selected_remote()
        if not remote_item:
            return
        QApplication.clipboard().setText(remote_item.remote.name)

    def get_selected_remote(self) -> Union[RemotesModelItem, None]:
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:  # can be multiple - always get 0
            Logger().debug("No selected item for context action")
            return None
        remote: RemotesModelItem = indexes[0].internalPointer()  # type: ignore
        return remote