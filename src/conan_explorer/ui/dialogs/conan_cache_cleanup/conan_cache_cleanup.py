from typing import Dict, List, Optional

import conan_explorer.app as app
from conan_explorer.app import LoaderGui  # using global module pattern
from conan_explorer.app.logger import Logger

from PySide6.QtCore import SignalInstance, Qt
from PySide6.QtWidgets import QDialog, QWidget, QDialogButtonBox, QListWidgetItem

from conan_explorer.conan_wrapper.types import ConanRef


class ConanCacheCleanupDialog(QDialog):

    def __init__(self, parent: Optional[QWidget], conan_refs_with_pkg_ids: Dict[str, List[str]],
                 conan_pkg_removed: Optional[SignalInstance] = None):
        super().__init__(parent)
        self._conan_pkg_removed_sig = conan_pkg_removed
        from .conan_cache_cleanup_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
