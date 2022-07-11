
import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.ui.common.model import TreeModel, TreeModelItem
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex


#app.conan_api.get_remotes()
from conans.client.cache.remote_registry import Remote


class RemotesModelItem(TreeModelItem):

    def __init__(self, remote: Remote, parent=None, lazy_loading=False):
        super().__init__([remote.name, remote.url, str(remote.verify_ssl)], parent, lazy_loading=lazy_loading)
        self.remote = remote


class RemotesModel(TreeModel):

    def __init__(self, *args, **kwargs):
        super(TreeModel, self).__init__(*args, **kwargs)
        self.root_item = TreeModelItem(["Name", "URL", "SSL"])
        # self.proxy_model = PackageFilter()
        # self.proxy_model.setDynamicSortFilter(True)
        # self.proxy_model.setSourceModel(self)
        # self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def setup_model_data(self):
        pass
        for remote in app.conan_api.get_remotes():
            conan_item = RemotesModelItem(remote, self.root_item)
            # infos = app.conan_api.get_local_pkgs_from_ref(conan_ref)
            # for info in infos:
            #     pkg_item = PackageTreeItem([info], conan_item, PROFILE_TYPE)
            #     conan_item.append_child(pkg_item)
            self.root_item.append_child(conan_item)

    def data(self, index: QModelIndex, role):  # override
        if not index.isValid():
            return None
        item: RemotesModelItem = index.internalPointer()
    #     if role == Qt.ToolTipRole:
    #         if item.type == PROFILE_TYPE:
    #             data = item.data(0)
    #             # remove dict style print characters
    #             return pprint.pformat(data).translate({ord("{"): None, ord("}"): None, ord(","): None, ord("'"): None})
    #     if role == Qt.DecorationRole:
    #         if item.type == REF_TYPE:
    #             return QIcon(get_themed_asset_image("icons/package.png"))
    #         if item.type == PROFILE_TYPE:
    #             profile_name = self.get_quick_profile_name(item)
    #             return get_platform_icon(profile_name)
        if role == Qt.DisplayRole:
            return item.data(index.column())

        return None


class ProfilesModel(QAbstractListModel):
  def __init__(self, todos=None):
    super().__init__()
    self.profiles = app.conan_api.conan.profile_list()

  def data(self, index, role):
    if role == Qt.DisplayRole:
        text = self.profiles[index.row()]
        return text
    # if role == Qt.DecorationRole:
    #     status, _ = self.todos[index.row()]
    #     if status:
    #         return ""

  def rowCount(self, index):
      return len(self.profiles)
