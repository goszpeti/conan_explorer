from pathlib import Path
from typing import Optional

import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher.core.conan_worker import ConanWorkerElement
from conan_app_launcher.ui.common.icon import get_themed_asset_image
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtBoundSignal

Qt = QtCore.Qt


class ConanInstallDialog(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget], conan_ref: str, pkg_installed_signal: Optional[pyqtBoundSignal] = None):
        """ conan_ref can be in full ref format with <ref>:<id> """
        super().__init__(parent)
        current_dir = Path(__file__).parent
        self._ui = uic.loadUi(current_dir / "conan_install.ui", baseinstance=self)
        self._ui.conan_ref_line_edit.setText(conan_ref)
        self.pkg_installed_signal = pkg_installed_signal

        # init search bar
        icon = QtGui.QIcon(get_themed_asset_image("icons/download_pkg.png"))
        self.setWindowIcon(icon)
        self._ui.install_icon.setPixmap(icon.pixmap(20, 20))
        self._ui.conan_ref_line_edit.validator_enabled = False
        self._ui.conan_ref_line_edit.textChanged.connect(self.toggle_auto_install_on_pkg_ref)
        self._ui.button_box.accepted.connect(self.on_install)

        self.adjust_to_size()
        self.toggle_auto_install_on_pkg_ref(self._ui.conan_ref_line_edit.text()) # initial evaluation

    def adjust_to_size(self):
        """ Expands the dialog to the length of the install ref text.
        (Somehow the dialog sets a much smaller size then it should via expanding size policy and layout.)
        """
        self._ui.conan_ref_line_edit.adjustSize()
        self.adjustSize()
        h_offset = (self.size() - self.conan_ref_line_edit.size()).width()
        width = self._ui.conan_ref_line_edit.fontMetrics().boundingRect(self._ui.conan_ref_line_edit.text()).width()
        self.resize(QtCore.QSize(width + h_offset + 15, self.height()))  # 15 margin

    def toggle_auto_install_on_pkg_ref(self, text: str):
        if ":" in text: # if a package id is given, auto install does not make sense
            self.auto_install_check_box.setEnabled(False)
        else:
            self.auto_install_check_box.setEnabled(True)

    def on_install(self):
        update_check_state = False
        if self.update_check_box.checkState() == Qt.Checked:
            update_check_state = True
        auto_install_checked = False
        if self.auto_install_check_box.checkState() == Qt.Checked:
            auto_install_checked = True
        ref_text = self.conan_ref_line_edit.text()
        conan_worker_element: ConanWorkerElement = {"ref_pkg_id": ref_text, "settings": {},
                                                    "options": {}, "update": update_check_state, "auto_install": auto_install_checked}

        app.conan_worker.put_ref_in_install_queue(conan_worker_element, self.pkg_installed_signal)
