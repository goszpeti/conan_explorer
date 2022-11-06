import pprint
from typing import List, Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.core import open_file
from conan_app_launcher.ui.common import AsyncLoader
from conan_app_launcher.ui.dialogs import ConanInstallDialog
from conan_app_launcher.core.conan import ConanFileReference
from PyQt6.QtCore import Qt, pyqtSlot, pyqtBoundSignal, QObject
from PyQt6.QtWidgets import (QApplication, QTreeView, QLineEdit, QPushButton, QTextBrowser, QListWidget)

from .model import PROFILE_TYPE, PluginModel, PluginModelItem

class PluginController(QObject):

    def __init__(self, view: QTreeView) -> None:
        super().__init__(view)
        self._view = view
        self._model = PluginModel()

    def update(self):
        self._model = PluginModel()
        self._model.setup_model_data()
        self._view.setItemsExpandable(False)
        self._view.setRootIsDecorated(False)
        self._view.setModel(self._model)
        self._view.expandAll()
        self._resize_package_columns()

    def get_selected_source_item(self, view) -> Optional[PluginModelItem]:
        """ Gets the selected item from a view """
        indexes = view.selectedIndexes()
        if not indexes:
            return None
        view_index = view.selectedIndexes()[0]
        source_item = view_index.model().mapToSource(view_index).internalPointer()
        return source_item

    def _resize_package_columns(self):
        self._view.resizeColumnToContents(2)
        self._view.resizeColumnToContents(1)
        self._view.resizeColumnToContents(0)
