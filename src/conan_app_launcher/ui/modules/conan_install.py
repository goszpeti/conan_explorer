from pathlib import Path
from typing import Optional

import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher.ui.common.icon import get_themed_asset_image
from conans.model.ref import ConanFileReference, PackageReference
from PyQt5 import QtCore, QtGui, QtWidgets, uic

Qt = QtCore.Qt


class ConanInstallDialog(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget], conan_ref: str):
        """ conan_ref can be in full ref format with <ref>:<id> """
        super().__init__(parent)
        current_dir = Path(__file__).parent
        self._ui = uic.loadUi(current_dir / "conan_install.ui", baseinstance=self)
        self.conan_ref_line_edit.setText(conan_ref)
        # init search bar
        icon = QtGui.QIcon(get_themed_asset_image("icons/download_pkg.png"))
        self.setWindowIcon(icon)
        self._ui.install_icon.setPixmap(icon.pixmap(20, 20))
        self._ui.conan_ref_line_edit.validator_enabled = False
        self.button_box.accepted.connect(self.on_install)
        self.pkg_installed = ""
        self.adjust_to_size()

    def adjust_to_size(self):
        """ Expands the dialog to the length of the install ref text.
        (Somehow the dialog sets a much smaller size then it should via expanding size policy and layout.)
        """
        self._ui.conan_ref_line_edit.adjustSize()
        self.adjustSize()
        h_offset = (self.size() - self.conan_ref_line_edit.size()).width()
        width = self._ui.conan_ref_line_edit.fontMetrics().boundingRect(self._ui.conan_ref_line_edit.text()).width()
        self.resize(QtCore.QSize(width + h_offset + 5, self.height()))  # 5 margin

    def on_install(self):
        update_check_state = False
        if self.update_check_box.checkState() == Qt.Checked:
            update_check_state = True

        ref_text = self.conan_ref_line_edit.text()
        if ":" in ref_text:  # pkg ref
            pkg_ref = PackageReference.loads(ref_text)
            package = app.conan_api.get_remote_pkg_from_id(pkg_ref)
            app.conan_api.install_package(pkg_ref.ref, package, update_check_state)
            self.pkg_installed = pkg_ref.id
            return
        else:  # recipe ref
            conan_ref = ConanFileReference.loads(ref_text)
            auto_install_checked = False
            if self.auto_install_check_box.checkState() == Qt.Checked:
                auto_install_checked = True
            # TODO do in thread!
            if auto_install_checked:
                pkg_id, pkg_path = app.conan_api.install_best_matching_package(
                    conan_ref, update=update_check_state)
                if pkg_path.is_dir():
                    self.pkg_installed = pkg_id
            else:
                infos = app.conan_api.conan.install_reference(conan_ref, update=update_check_state)
                if not infos.get("error", True):
                    id = infos.get("installed", [{}])[0].get("packages", [{}])[0].get("id", "")
                    self.pkg_installed = id
