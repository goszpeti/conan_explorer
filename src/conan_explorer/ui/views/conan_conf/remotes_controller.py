from typing import List, Optional

from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt, SignalInstance
from PySide6.QtWidgets import QApplication, QDialog, QListWidgetItem, QStyle, QTreeView

import conan_explorer.app as app
from conan_explorer.app.logger import Logger
from conan_explorer.conan_wrapper.types import Remote
from conan_explorer.ui.dialogs import QuestionWithItemListDialog, ReorderController

from .remotes_model import RemotesModelItem, RemotesTableModel


class ConanRemoteController:
    def __init__(
        self, view: QTreeView, conan_remotes_updated: Optional[SignalInstance]
    ) -> None:
        self._view = view
        self._model = RemotesTableModel()
        self.conan_remotes_updated = conan_remotes_updated
        self._view.setModel(self._model)

    def notify_remotes_updates(self):
        if self.conan_remotes_updated:
            self.conan_remotes_updated.emit()

    def update(self):
        # save selected remote, if triggering a re-init
        self._remote_reorder_controller = ReorderController(self._view, self._model)

        self._model.setup_model_data()
        self._view.setItemsExpandable(False)
        self._view.setRootIsDecorated(False)
        self._view.expandAll()
        self.resize_remote_columns()

    def resize_remote_columns(self):
        for i in reversed(range(self._model.root_item.column_count() - 1)):
            self._view.resizeColumnToContents(i)
        self._view.setColumnWidth(1, 400)
        self._view.columnViewportPosition(0)

    def _select_remote(self, remote_name: str) -> bool:
        """Selects a remote in the view and returns true if it exists."""
        row_remote_to_sel = -1
        row = 0
        remote_item = None
        for row, remote_item in enumerate(self._model.items()):
            if remote_item.name == remote_name:
                row_remote_to_sel = row
                break
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

    def add(self, remote: Remote):
        self._model.add(remote)
        # otherwise half selections of multiple items occur somehow
        self._view.selectionModel().clearSelection()
        self.notify_remotes_updates()

    def rename(self, remote: Remote, new_name):
        self._model.rename(remote, new_name)
        self.notify_remotes_updates()

    def update_remote(self, remote: Remote):
        self._model.update(remote)
        self.notify_remotes_updates()

    def login_remotes(self, remotes: List[str], user: str, pwd: str):
        for remote in remotes:
            # will be canceled after the first error, so no lockout will occur,
            # because of multiple incorrect logins error is printed on the console
            try:
                self._model.update_login_info(remote, user, pwd)
            except Exception as e:
                Logger().error(f"Can't sign in to {remote}: {str(e)}")
                return
            Logger().info(f"Successfully logged in to {remote}")

    def on_remove(self):
        remote_items = self.get_selected_remotes()
        dialog = QuestionWithItemListDialog(
            self._view, QStyle.StandardPixmap.SP_MessageBoxWarning
        )
        dialog.setWindowTitle("Delete remote(s)")
        dialog.set_question_text("Are you sure, you want to delete these remotes?\t")
        for item in remote_items:
            list_item = QListWidgetItem(item.name)
            list_item.setCheckState(Qt.CheckState.Checked)
            dialog.item_list_widget.addItem(list_item)

        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            # get user Selection
            for list_row in range(dialog.item_list_widget.count()):
                list_item = dialog.item_list_widget.item(list_row)
                if list_item.checkState() == Qt.CheckState.Unchecked:
                    continue
                self._model.remove(list_item.text())
        self.notify_remotes_updates()

    def remote_disable(self):
        remote_items = self.get_selected_remotes()
        if not remote_items:
            return
        for remote_item in remote_items:
            self._model.toggle_state(remote_item.name)
        self.notify_remotes_updates()

    def copy_remote_name(self):
        remote_item = self.get_selected_remote()
        if not remote_item:
            return
        QApplication.clipboard().setText(remote_item.name)

    def get_selected_remote(self) -> Optional[Remote]:
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:  # can be multiple - always get 0
            Logger().debug("No selected item for context action")
            return None
        remote_model: RemotesModelItem = indexes[0].internalPointer()  # type: ignore
        for remote in app.conan_api.get_remotes(include_disabled=True):
            if remote.name == remote_model.name:
                return remote

    def get_selected_remotes(self) -> List[Remote]:
        indexes = self._view.selectedIndexes()
        remotes: List[Remote] = []

        for index in indexes:
            if index.column() != 0:  # we only need a row once
                continue
            remote_model: RemotesModelItem = index.internalPointer()  # type: ignore
            for remote in app.conan_api.get_remotes(include_disabled=True):
                if remote.name == remote_model.name:
                    remotes.append(remote)
        return remotes
