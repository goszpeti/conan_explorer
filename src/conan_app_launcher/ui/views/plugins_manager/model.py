from pathlib import Path
from typing import Dict, List, Optional, Union

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.core import ConanApi
from conan_app_launcher.core.conan_common import ConanPkg
from conan_app_launcher.settings import PLUGINS_SECTION_NAME
from conan_app_launcher.ui.common import TreeModel, TreeModelItem, get_platform_icon, get_themed_asset_image
from conan_app_launcher.core.conan_common import ConanFileReference
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, Slot, SignalInstance
from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, SignalInstance

from conan_app_launcher.ui.common.loading import AsyncLoader
from conan_app_launcher.ui.fluent_window.plugins import PluginDescription, PluginFile

REF_TYPE = 0
PROFILE_TYPE = 1


class PluginFileModelItem(TreeModelItem):

    def __init__(self, file_path: str, parent):
        super().__init__(["built-in", "", "", ""], parent, lazy_loading=False)

class PluginModelItem(TreeModelItem):

    def __init__(self, plugin: PluginDescription, parent):
        super().__init__([plugin.name, plugin.version, plugin.author, plugin.description], parent, lazy_loading=False)
        self._icon = plugin.icon


class PluginModel(TreeModel):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(checkable=True, *args, **kwargs)
        self.root_item = TreeModelItem(["Name", "Version", "Author", "Description"])


    def setup_model_data(self):
        self.root_item.child_items = []
        for plugin_group_name in app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME):
            plugin_path = app.active_settings.get_string(plugin_group_name)
            # plugin_file_element = PluginFileModelItem(plugin_path, self.root_item)
            # .append_child(plugin_file_element)
            plugins = PluginFile.read_file(plugin_path)
            for plugin in plugins:
                plugin_element = PluginModelItem(plugin, self.root_item)
                self.root_item.append_child(plugin_element)


        #     self.root_item.append_child(remote_item)

    def data(self, index: QModelIndex, role):  # override
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                return item.data(index.column())
            except Exception:
                return ""
        if role == Qt.ItemDataRole.DecorationRole:
            if index.column() != 0:  # only display icon for first column
                return
            if isinstance(item, PluginModelItem):
                return QtGui.QIcon(get_themed_asset_image(item._icon))

        # if isinstance(item, RemotesModelItem):
        #     if role == Qt.ItemDataRole.FontRole and item.remote.disabled:
        #         font = QFont()
        #         font.setItalic(True)
        #         return font

        return None
    def save(self):
        """ Update every remote with new index and thus save to conan remotes file """
        pass
        # i = 0
        # for remote_item in self.root_item.child_items:
        #     remote = remote_item.remote
        #     app.conan_api.conan.remote_update(remote.name, remote.url, remote.verify_ssl, i)
        #     i += 1
