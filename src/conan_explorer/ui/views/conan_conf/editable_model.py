
from typing import List, Optional
import conan_explorer.app as app
from conan_explorer.conan_wrapper.types import ConanRef  # using global module pattern
from conan_explorer.ui.common import (get_platform_icon)
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from conan_explorer.ui.common import TreeModel, TreeModelItem

class EditableModelItem(TreeModelItem):

    def __init__(self, name, path, output, parent=None, lazy_loading=False):
        super().__init__([name, path, output], parent, lazy_loading=lazy_loading)


class EditableModel(TreeModel):
    def __init__(self):
        super(EditableModel, self).__init__(checkable=True)
        self.root_item = TreeModelItem(["Name", "Path", "Output folder"])  # "Layout",
        self.setup_model_data()

    def setup_model_data(self):
        editables = app.conan_api.get_editable_references()
        self.root_item.child_items = []
        for editable_ref in editables:
            ref_obj = ConanRef.loads(editable_ref)
            path = app.conan_api.get_editables_package_path(ref_obj)
            output = app.conan_api.get_editables_output_folder(ref_obj)
            remote_item = EditableModelItem(
                editable_ref, str(path), output, self.root_item)
            self.root_item.append_child(remote_item)

    def data(self, index: QModelIndex, role):  # override
        if not index.isValid():
            return None
        item: EditableModelItem = index.internalPointer()  # type: ignore
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                return item.data(index.column())
            except Exception:
                return ""
        return None

    def rowCount(self, parent=None):
        return self.root_item.child_count()

    # def data(self, index, role):
    #     if role == Qt.ItemDataRole.DisplayRole:
    #         text = self._profiles[index.column()]
    #         return text
    #     # platform logo
    #     if role == Qt.ItemDataRole.DecorationRole:
    #         text = self._profiles[index.column()]
    #         return get_platform_icon(text)

    # def get_index_from_profile(self, profile_name: str) -> Optional[QModelIndex]:
    #     index = None
    #     for i, profile in enumerate(self._profiles):
    #         if profile == profile_name:
    #             index = self.createIndex(i, 0)
    #             break
    #     return index
