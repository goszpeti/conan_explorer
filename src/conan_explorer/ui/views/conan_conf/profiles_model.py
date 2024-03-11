
from typing import List, Optional

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from typing_extensions import override

import conan_explorer.app as app  # using global module pattern
from conan_explorer.ui.common import get_platform_icon


class ProfilesModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._profiles: List[str] = []
        self.setup_model_data()

    def setup_model_data(self):
        self._profiles = app.conan_api.get_profiles()

    @override
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            text = self._profiles[index.row()]
            return text
        # platform logo
        if role == Qt.ItemDataRole.DecorationRole:
            text = self._profiles[index.row()]
            return get_platform_icon(text)

    @override
    def rowCount(self, parent):
        return len(self._profiles)

    def get_index_from_profile(self, profile_name: str) -> Optional[QModelIndex]:
        index = None
        for i, profile in enumerate(self._profiles):
            if profile == profile_name:
                index = self.createIndex(i, 0)
                break
        return index
