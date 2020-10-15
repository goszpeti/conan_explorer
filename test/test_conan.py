import os
import time
from conans.model.ref import ConanFileReference

from conan_app_launcher.conan import get_conan_package_folder, ConanWorker

from conan_app_launcher.config_file import parse_config_file
from PyQt5 import QtCore, QtWidgets


def testConanApi():
    ref = "m4_installer/1.4.18@bincrafters/stable"
    os.system("conan remove %s -f" % ref)
    # Gets package path / installs the package
    package_folder = get_conan_package_folder(ConanFileReference.loads(ref))
    assert (package_folder / "bin").is_dir()
    # check again for already installed package
    package_folder = get_conan_package_folder(ConanFileReference.loads(ref))
    assert (package_folder / "bin").is_dir()


def testConanWorker(base_fixture, qtbot):
    conan_info_updated = QtCore.pyqtSignal()
    tab_info = parse_config_file(base_fixture.testdata_path / "app_config.json")
    conan_worker = ConanWorker(tab_info, conan_info_updated)
    elements_before = conan_worker.app_queue.qsize()
    time.sleep(5)
    assert conan_worker.app_queue.qsize() < elements_before
