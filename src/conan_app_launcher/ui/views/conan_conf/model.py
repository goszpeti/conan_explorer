
from typing import Dict, List
import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.ui.common import TreeModel, TreeModelItem, get_platform_icon
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex
from PyQt5.QtGui import QFont
# app.conan_api.get_remotes()
from conans.client.cache.remote_registry import Remote

from conan_app_launcher.ui.dialogs.reorder_dialog.reorder_dialog import ReorderingModel


class RemotesModelItem(TreeModelItem):

    def __init__(self, remote: Remote, user: str, auth: bool, parent=None, lazy_loading=False):
        super().__init__([remote.name, remote.url, str(remote.verify_ssl),
                          user, str(auth)], parent, lazy_loading=lazy_loading)
        self.remote = remote


class RemotesListModel(ReorderingModel):
    def __init__(self):
        super().__init__()
        self._remotes = app.conan_api.get_remotes(include_disabled=True)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self._remotes[index.row()].name
            return text

    def rowCount(self, parent=None):
        return len(self._remotes)
    
    def setData(self, index, value, role):
        if role == Qt.UserRole:
            self._remotes[index.row()] = value
            
    def save(self):
        # update every remote with new index
        i = 0
        for remote in self._remotes:
            app.conan_api.conan.remote_update(remote.name, remote.url, remote.verify_ssl, i)
            i+=1

    def moveRow(self, source_parent: QModelIndex, source_row: int, destination_parent: QModelIndex, destination_child: int) -> bool:
        app_to_move = self._remotes[source_row]
        self._remotes.insert(destination_child, app_to_move)
        if source_row < destination_child:
            self._remotes.pop(source_row)
            app.conan_api.conan.remote_list
        else:
            self._remotes.pop(source_row+1)
        return super().moveRow(source_parent, source_row, destination_parent, destination_child)


class RemotesTreeModel(TreeModel):

    def __init__(self, *args, **kwargs):
        super(TreeModel, self).__init__(*args, **kwargs)
        self.root_item = TreeModelItem(["Name", "URL", "SSL", "User", "Authenticated"])

    def setup_model_data(self):
        # group remotes from URL for artifactory
        remote_groups: Dict[str, List[Remote]] = {}
        for remote in app.conan_api.get_remotes(include_disabled=True):
            if "artifactory" in remote.url:
                # try to determine root address ->  TODO recursive
                possible_base_url = "/".join(remote.url.split("/")[0:3])
                hit_counter = 0
                for try_remote in app.conan_api.get_remotes(include_disabled=True):
                    if possible_base_url in try_remote.url:
                        hit_counter += 1
                if hit_counter > 0:
                    if not remote_groups.get(possible_base_url):
                        remote_groups[possible_base_url] = [remote]
                    else:
                        remotes = remote_groups[possible_base_url]
                        remotes.append(remote)
                        remote_groups.update({possible_base_url: remotes})
            else:
                remote_groups[remote.url] = [remote]

        for group_name, remotes in remote_groups.items():
            # RemotesModelItem(Remote(group_name, "", False, False), self.root_item)
            remote_group_item = TreeModelItem([group_name, "", "", "", ""], self.root_item)
            for remote in remotes:
                user_name, auth = app.conan_api.get_remote_user_info(remote.name)
                remote_item = RemotesModelItem(remote, user_name, auth, remote_group_item)
                remote_group_item.append_child(remote_item)
            self.root_item.append_child(remote_group_item)

    def data(self, index: QModelIndex, role):  # override
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            try:
                return item.data(index.column())
            except:
                return ""
        if isinstance(item, RemotesModelItem):
            if role == Qt.FontRole and item.remote.disabled:
                font = QFont()
                font.setItalic(True)
                return font

        return None


class ProfilesModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._profiles = app.conan_api.conan.profile_list()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self._profiles[index.row()]
            return text
        # platform logo
        if role == Qt.DecorationRole:
            text = self._profiles[index.row()]
            return get_platform_icon(text)

    def rowCount(self, index):
        return len(self._profiles)
