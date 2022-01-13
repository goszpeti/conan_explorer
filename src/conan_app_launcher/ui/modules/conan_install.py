import pprint
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

from conans.model.ref import ConanFileReference, PackageReference

import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher import asset_path
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from conan_app_launcher.components import conan

Qt = QtCore.Qt


class ConanInstallDialog(QtWidgets.QDialog):
    def __init__(self, parent:Optional[QtWidgets.QWidget], conan_ref: str):
        super().__init__(parent)
        current_dir = Path(__file__).parent
        self._ui = uic.loadUi(current_dir / "conan_install.ui", baseinstance=self)
        self.setMinimumSize(200, 200)

        self.conan_ref_line_edit.setText(conan_ref)
        # init search bar
        icon = QtGui.QIcon(str(asset_path / "icons" / "download_pkg.png"))
        self._ui.install_icon.setPixmap(icon.pixmap(20, 20))
        self._ui.install_icon.validator_enabled = False
        self.button_box.accepted.connect(self.on_install)

    def on_install(self):
        conan_ref = PackageReference.loads(self.conan_ref_line_edit.text())

        update_check_state = False
        if self.update_check_box.checkState() == Qt.Checked:
            update_check_state = True

        # package ref
        if conan_ref.id:
            package = None
            for remote in app.conan_api.get_remotes():
                packages = app.conan_api.get_packages_in_remote(conan_ref.ref, remote.name)
                for package in packages:
                    if package.get("id", "") == conan_ref.id:
                        app.conan_api.install_package(conan_ref.ref, package, update_check_state)
                        return
        # recipe ref
        auto_install_checked = False
        if self.auto_install_check_box.checkState() == Qt.Checked:
            auto_install_checked = True
        if auto_install_checked:
            app.conan_api.install_best_matching_package(conan_ref.ref, update=update_check_state)
        else:
            app.conan_api.conan.install_reference(conan_ref.ref, update=update_check_state)
