
import conan_explorer.app as app
from conan_explorer.conan_wrapper.types import ConanRef  # using global module pattern
from PySide6.QtCore import QModelIndex, Qt
from conan_explorer.ui.common import TreeModel, TreeModelItem

class EditableModelItem(TreeModelItem):

    def __init__(self, name, path, output, parent=None, lazy_loading=False):
        super().__init__([name, path, output], parent, lazy_loading=lazy_loading)

    @property
    def name(self):
        return self.item_data[0]
    @name.setter
    def name(self, value: str):
        self.item_data[0] = value

    @property
    def path(self):
        return self.item_data[1]
    @path.setter
    def path(self, value: str):
        self.item_data[1] = value

    @property
    def output(self):
        return self.item_data[2]
    @output.setter
    def output(self, value: str):
        self.item_data[2] = value

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
