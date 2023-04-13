from typing import Dict, List, Optional, Union

import conan_app_launcher.app as app
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.ui.dialogs import ReorderController
from conans.client.cache.remote_registry import Remote
from PySide6.QtCore import QModelIndex, QItemSelectionModel, SignalInstance
from PySide6.QtWidgets import QApplication, QTreeView

from conan_app_launcher.ui.views.conan_conf.model import RemotesModelItem, RemotesTableModel


class ConanRemoteController():

    def __init__(self, view: QTreeView, conan_remotes_updated: Optional[SignalInstance]) -> None:
        self._view = view
        self._model = RemotesTableModel()
        self.conan_remotes_updated = conan_remotes_updated

    def update(self):
        self._model = RemotesTableModel()
        # save selected remote, if triggering a re-init
        sel_remote = self.get_selected_remote()
        self._remote_reorder_controller = ReorderController(self._view, self._model)

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
        self._view.resizeColumnToContents(4)
        self._view.resizeColumnToContents(3)
        self._view.resizeColumnToContents(2)
        self._view.resizeColumnToContents(1)
        self._view.resizeColumnToContents(0)

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
        for column in range(self._model.columnCount(QModelIndex())):
            index = self._model.index(row_remote_to_sel, column, QModelIndex())
            sel_model.select(index, QItemSelectionModel.SelectionFlag.Select)
        return True

    def move_up(self):
        self._remote_reorder_controller.move_up()

    def move_down(self):
        self._remote_reorder_controller.move_down()

    def remote_disable(self, model_index):
        remote_item = self.get_selected_remote()
        if not remote_item:
            return
        # TODO dedicated function
        app.conan_api._conan.remote_set_disabled_state(remote_item.remote.name, not remote_item.remote.disabled)
        self.update()

    def get_selected_remote(self) -> Union[RemotesModelItem, None]:
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:  # can be multiple - always get 0
            Logger().debug(f"No selected item for context action")
            return None
        remote: RemotesModelItem = indexes[0].internalPointer() # type: ignore
        return remote

    def copy_remote_name(self):
        remote_item = self.get_selected_remote()
        if not remote_item:
            return
        QApplication.clipboard().setText(remote_item.remote.name)

    def get_remotes_from_same_server(self, remote: Remote):
        remote_groups = self.get_remote_groups()
        for remotes in remote_groups.values():
            for check_remote in remotes:
                if check_remote == remote:
                    return remotes
        return None

    def get_remote_groups(self) -> Dict[str, List[Remote]]:
        """
        Try to group similar URLs(currently only for artifactory links) 
        and return them in a dict grouped by the full URL.
        """
        remote_groups: Dict[str, List[Remote]] = {}
        for remote in app.conan_api.get_remotes(include_disabled=True):
            if "artifactory" in remote.url:
                # try to determine root address
                possible_base_url = "/".join(remote.url.split("/")[0:3])
                if not remote_groups.get(possible_base_url):
                    remote_groups[possible_base_url] = [remote]
                else:
                    remotes = remote_groups[possible_base_url]
                    remotes.append(remote)
                    remote_groups.update({possible_base_url: remotes})
            else:
                remote_groups[remote.url] = [remote]
        return remote_groups
