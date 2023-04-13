
from typing import Optional
import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.ui.common import (TreeModel, TreeModelItem,
                                          get_platform_icon)
from conans.client.cache.remote_registry import Remote
from conans.errors import ConanException
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from PySide6.QtGui import QFont


class RemotesModelItem(TreeModelItem):

    def __init__(self, remote: Remote, user: str, auth: bool, parent=None, lazy_loading=False):
        super().__init__([remote.name, remote.url, str(remote.verify_ssl),
                          user, str(auth)], parent, lazy_loading=lazy_loading)
        self.remote = remote


class RemotesTableModel(TreeModel):
    """
    Remotes displayed as a table with detail info - implemented as a tree with one level:
    this is necessary, because list model cannot have a header and multiple columns and a
    table looks like an ugly Excel clone
    """

    def __init__(self, *args, **kwargs):
        super(RemotesTableModel, self).__init__(checkable=True, *args, **kwargs)
        self.root_item = TreeModelItem(["Name", "URL", "SSL", "User", "Authenticated"])

    def setup_model_data(self):
        self.root_item.child_items = []
        for remote in app.conan_api.get_remotes(include_disabled=True):
            user_name = ""
            auth = False
            try:
                user_name, auth = app.conan_api.get_remote_user_info(remote.name)
            except ConanException as e:  # This methods throws an error on older conan version, if a remote is disabled
                Logger().debug(str(e))
            remote_item = RemotesModelItem(remote, user_name, auth, self.root_item)
            self.root_item.append_child(remote_item)

    def data(self, index: QModelIndex, role):  # override
        if not index.isValid():
            return None
        item: RemotesModelItem = index.internalPointer() # type: ignore
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                return item.data(index.column())
            except Exception:
                return ""

        if isinstance(item, RemotesModelItem):
            if role == Qt.ItemDataRole.FontRole and item.remote.disabled:
                font = QFont()
                font.setItalic(True)
                return font

        return None

    def rowCount(self, parent=None):
        return self.root_item.child_count()

    def save(self):
        """ Update every remote with new index and thus save to conan remotes file """
        i = 0
        for remote_item in self.root_item.child_items:
            remote: Remote = remote_item.remote
            # TODO dedicated function
            app.conan_api._conan.remote_update(remote.name, remote.url, remote.verify_ssl, i)
            i += 1

    def moveRow(self, source_parent: QModelIndex, source_row: int, destination_parent: QModelIndex, destination_child: int) -> bool:
        item_to_move = self.root_item.child_items[source_row]
        self.root_item.child_items.insert(destination_child, item_to_move)
        if source_row < destination_child:
            self.root_item.child_items.pop(source_row)
        else:
            self.root_item.child_items.pop(source_row+1)
        self.save()  # autosave
        return super().moveRow(source_parent, source_row, destination_parent, destination_child)


class ProfilesModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._profiles = app.conan_api.get_profiles()

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            text = self._profiles[index.row()]
            return text
        # platform logo
        if role == Qt.ItemDataRole.DecorationRole:
            text = self._profiles[index.row()]
            return get_platform_icon(text)

    def rowCount(self, index):
        return len(self._profiles)
    
    def update_profiles(self):
        self._profiles = app.conan_api.get_profiles()

    def get_index_from_profile(self, profile_name: str) -> Optional[QModelIndex]:
        index = None
        for i, profile in enumerate(self._profiles):
            if profile == profile_name:
                index = self.createIndex(i, 0)
                break
        return index
