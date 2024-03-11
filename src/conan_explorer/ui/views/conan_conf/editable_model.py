
from typing import Any, List, Optional, Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from typing_extensions import override

import conan_explorer.app as app  # using global module pattern
from conan_explorer.conan_wrapper.types import EditablePkg
from conan_explorer.ui.common import TreeModel, TreeModelItem


class EditableModelItemRoot(TreeModelItem):
    def __init__(self, data: List[str], parent=None, lazy_loading=False):
        self.child_items: List[EditableModelItem] = []
        super().__init__(data, parent, lazy_loading)


class EditableModelItem(TreeModelItem):

    def __init__(self, name: str, path: str, output: str, parent=None, lazy_loading=False):
        super().__init__([name, path, output], parent, lazy_loading=lazy_loading)

    @property
    def name(self) -> str:
        return self.item_data[0]

    @name.setter
    def name(self, value: str):
        self.item_data[0] = value

    @property
    def path(self) -> str:
        return self.item_data[1]

    @path.setter
    def path(self, value: str):
        self.item_data[1] = value

    @property
    def output(self) -> str:
        return self.item_data[2]

    @output.setter
    def output(self, value: str):
        self.item_data[2] = value


class EditableModel(TreeModel):
    def __init__(self):
        super(EditableModel, self).__init__(checkable=True)
        self.root_item = EditableModelItemRoot(["Name", "Path", "Output folder"])  # "Layout",
        self.setup_model_data()

    def setup_model_data(self):
        editables = app.conan_api.get_editable_references()
        self.clear_items()
        self.beginResetModel()
        for editable_ref in editables:
            path = app.conan_api.get_editables_package_path(editable_ref)
            output = app.conan_api.get_editables_output_folder(editable_ref)
            output_str = str(output) if output else ""
            remote_item = EditableModelItem(
                str(editable_ref), str(path), output_str, self.root_item)
            self.root_item.append_child(remote_item)
        self.endResetModel()

    def add(self, editable: EditablePkg):
        args = (editable.conan_ref, editable.path, str(editable.output_folder))
        if app.conan_api.add_editable(*args):
            super().add_item(EditableModelItem(*args))
            return True
        return False

    def remove(self, editable: EditablePkg):
        if app.conan_api.remove_editable(editable.conan_ref):
            index = self.get_index_from_ref(editable.conan_ref)
            item: EditableModelItem = index.internalPointer()  # type: ignore
            super().remove_item(item)
            return True
        return False

    @override
    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> Any:
        if not index.isValid():
            return None
        item: EditableModelItem = index.internalPointer()  # type: ignore
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                return item.data(index.column())
            except Exception:
                return ""
        return None

    @override
    def rowCount(self, parent=None):
        return self.root_item.child_count()

    def get_index_from_ref(self, conan_ref: str) -> Optional[QModelIndex]:
        for ref in self.root_item.child_items: # type: ignore
            ref: EditableModelItem
            if ref.name == conan_ref:
                return self.get_index_from_item(ref)
        return None
