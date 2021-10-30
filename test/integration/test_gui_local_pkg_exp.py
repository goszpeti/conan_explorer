"""
Test the self written qt gui components, which can be instantiated without
using the whole application (standalone).
"""
import tempfile
from pathlib import Path

import conan_app_launcher as app
from conan_app_launcher.__main__ import load_base_components
from conan_app_launcher.settings.settings import Settings
from conan_app_launcher.ui import main_window
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets
from pytestqt.plugin import _qapp_instance

Qt = QtCore.Qt
TEST_REF = "zlib/1.2.11@_/_"


def test_delete_package_dialog(base_fixture, qtbot, mocker):
    """ Test, that the delete package dialog deletes a reference with id, 
    without id and cancel does nothing"""
    app.active_settings = Settings(Path(tempfile.mktemp()))
    load_base_components(app.active_settings)
    cfr = ConanFileReference.loads(TEST_REF)
    app.conan_api.conan.install_reference(cfr)

    # precheck, that the package is found
    found_pkg = app.conan_api.get_local_pkgs_from_ref(cfr)
    assert found_pkg

    app.qt_app = _qapp_instance
    main_gui = main_window.MainUi()
    app.main_window = main_gui  # needed for signal access
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    # check cancel does nothing
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Cancel)
    app.main_window.ui._local_package_explorer.delete_conan_package_dialog(TEST_REF, None)
    found_pkg = app.conan_api.find_best_local_package(cfr)
    assert found_pkg.get("id", "")

    # check without pkg id
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)
    app.main_window.ui._local_package_explorer.delete_conan_package_dialog(TEST_REF, None)

    # check, that the package is deleted
    found_pkg = app.conan_api.find_best_local_package(cfr)
    assert not found_pkg.get("id", "")
    
    # check with pkg id
    app.conan_api.conan.install_reference(cfr)
    app.main_window.ui._local_package_explorer.delete_conan_package_dialog(TEST_REF, None)
    found_pkg = app.conan_api.find_best_local_package(cfr)
    assert not found_pkg.get("id", "")
