
from typing import List, Optional
import conan_explorer.app as app  # using global module pattern
from conan_explorer.app.logger import Logger
from conan_explorer.ui.common import TreeModel, TreeModelItem
from conan_explorer.conan_wrapper.types import Remote, ConanException
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QFont

class RemotesModelItem(TreeModelItem, Remote):

    def __init__(self, remote: Remote, user: str, auth: bool, parent=None, lazy_loading=False):
        TreeModelItem.__init__(self, [user, str(auth)], parent, lazy_loading=lazy_loading)
        Remote.__init__(self, remote.name, remote.url,
                        remote.verify_ssl, remote.disabled)

    def data(self, column):
        if column == 0:
            return self.name
        elif column == 1:
            return self.url
        elif column == 2:
            return str(self.verify_ssl)
        elif column == 3:
            return self.item_data[0]
        elif column == 4:
            return self.item_data[1]
        elif column == 5:
            return str(self.disabled)

    @property
    def user(self) -> str:
        return self.item_data[0]

    @user.setter
    def user(self, value: str):
        self.item_data[0] = value

    @property
    def auth(self) -> bool:
        return bool(self.item_data[1])
    @auth.setter
    def auth(self, value: bool):
        self.item_data[1] = str(value)


class RemotesTableModel(TreeModel):
    """
    Remotes displayed as a table with detail info - implemented as a tree with one level:
    this is necessary, because list model cannot have a header and multiple columns and a
    table looks like an ugly Excel clone
    """

    def __init__(self, *args, **kwargs):
        super(RemotesTableModel, self).__init__(checkable=True, *args, **kwargs)
        self.root_item = TreeModelItem(["Name", "URL", "SSL", "User", "Authenticated"])
        self.setup_model_data()

    def setup_model_data(self):
        self.clear_items()
        self.beginResetModel()
        for remote in app.conan_api.get_remotes(include_disabled=True):
            user_name = ""
            auth = False
            try:
                user_name, auth = app.conan_api.get_remote_user_info(remote.name)
            # Throws an error on older conan version, if a remote is disabled
            except ConanException as e:
                Logger().debug(str(e))
            remote_item = RemotesModelItem(remote, user_name, auth, self.root_item)
            self.root_item.append_child(remote_item)
        self.endResetModel()

    def data(self, index: QModelIndex, role):  # override
        if not index.isValid():
            return None
        item: RemotesModelItem = index.internalPointer()  # type: ignore
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                return item.data(index.column())
            except Exception:
                return ""

        if isinstance(item, RemotesModelItem):
            if role == Qt.ItemDataRole.FontRole and item.disabled:
                font = QFont()
                font.setItalic(True)
                return font

        return None

    def rowCount(self, parent=None): # TODO really?
        return self.root_item.child_count()
    
    def items(self) -> List[RemotesModelItem]:
        return self.root_item.child_items  # type: ignore
    
    def add(self, remote: Remote):
        app.conan_api.add_remote(remote.name, remote.url, remote.verify_ssl)
        super().add_item(RemotesModelItem(remote, "", False))

    def remove(self, remote: Remote):
        app.conan_api.remove_remote(remote.name)
        index = self.get_index_from_ref(remote.name)
        item: RemotesModelItem = index.internalPointer()  # type: ignore
        super().remove_item(item)
        return True
    
    def rename(self, remote: Remote, new_name):
        app.conan_api.rename_remote(remote.name, new_name)
        index = self.get_index_from_ref(remote.name)
        item: RemotesModelItem = index.internalPointer()  # type: ignore
        item.name = new_name
    
    def update(self, remote: Remote):
        app.conan_api.update_remote(
            remote.name, remote.url, remote.verify_ssl, remote.disabled, None)
        index = self.get_index_from_ref(remote.name)
        item: RemotesModelItem = index.internalPointer()  # type: ignore
        # copy all possible props
        item.url = remote.url
        item.verify_ssl = remote.verify_ssl
        item.disabled = remote.disabled

    def update_login_info(self, remote_name: str, user: str, pwd: str):
        app.conan_api.login_remote(remote_name, user, pwd)
        index = self.get_index_from_ref(remote_name)
        item: RemotesModelItem = index.internalPointer()  # type: ignore
        item.auth = True
        item.user = user

    def save(self):
        """ Update every remote with new index and then save to conan remotes file """
        i = 0
        for remote in self.items():
            app.conan_api.update_remote(
                remote.name, remote.url, remote.verify_ssl, remote.disabled, i)
            i += 1

    def moveRow(self, source_parent: QModelIndex, source_row: int, destination_parent: QModelIndex, destination_child: int) -> bool:
        item_to_move = self.items()[source_row]
        self.items().insert(destination_child, item_to_move)
        if source_row < destination_child:
            self.items().pop(source_row)
        else:
            self.items().pop(source_row+1)
        self.save()  # autosave
        return super().moveRow(source_parent, source_row, destination_parent, destination_child)

    def get_index_from_ref(self, conan_ref: str) -> Optional[QModelIndex]:
        for ref in self.items():
            if ref.name == conan_ref:
                return self.get_index_from_item(ref)
        return None
