import os
import time
from conans.model.ref import ConanFileReference

from conan_app_launcher.components.conan import get_conan_package_folder, getConanAPI, ConanWorker, install_conan_package
from conan_app_launcher.components import parse_config_file

from PyQt5 import QtCore


def testConanApi():
    """
    Test, if get_package installs the package and returns the path and checkit again.
    The bin dir in the package must exist (indicating it was correctly downloaded)
    """
    ref = "m4_installer/1.4.18@bincrafters/stable"
    os.system(f"conan remove {ref} -f")
    # Gets package path / installs the package
    package_folder = get_conan_package_folder(ConanFileReference.loads(ref))
    assert (package_folder / "bin").is_dir()
    # check again for already installed package
    package_folder = get_conan_package_folder(ConanFileReference.loads(ref))
    assert (package_folder / "bin").is_dir()


def testCompilerAnySettings(mocker, capsys):

    # mock the remote response
    ref = "m4_installer/1.4.18@bincrafters/stable"

    result = {'error': False,
              'results':
              [{'remote': 'conan-center',
                'items': [
                    {'recipe': {'id': 'm4_installer/1.4.18@bincrafters/stable'},
                     'packages':
                     [{'id': '445cf80f611c1d1eda08bde2ebc5066218ca9701', 'options': {}, 'settings': {'arch_build': 'x86', 'os_build': 'Linux', "build_type": "ANY"}, 'requires': [], 'outdated': False},
                      {'id': '44fcf6b9a7fb86b2586303e3db40189d3b511830', 'options': {}, 'settings': {
                          'arch_build': 'x86_64', 'os_build': 'Linux', "build_type": "ANY"}, 'requires': [], 'outdated': False},
                      {'id': '456f15897172eef340fcbac8a70811f2beb26a93', 'options': {}, 'settings': {
                          'arch_build': 'x86_64', 'os_build': 'Windows', "build_type": "ANY"}, 'requires': [], 'outdated': False},
                      {'id': '743cf0321be3152777da4d05247a66d1552e70a2', 'options': {}, 'settings': {
                          'arch_build': 'x86_64', 'os_build': 'Macos'}, 'requires': [], 'outdated': False},
                      {'id': 'b2fcbc60b3bee75023a4f7934cadb723eec550bd', 'options': {}, 'settings': {'arch_build': 'x86', 'os_build': 'Windows', "build_type": "ANY"}, 'requires': [], 'outdated': False}]}]}]}
    config = {"return_value": result}
    mocker.patch("conans.client.conan_api.ConanAPIV1.search_packages", **config)

    conan, cache, user_io = getConanAPI()

    install_conan_package(conan, cache, ConanFileReference.loads(ref))
    captured = capsys.readouterr()
    assert "ERROR" not in captured.err
    assert "Cannot install package" not in captured.err


def testCompilerNoSettings(mocker, capsys):

    # mock the remote response
    ref = "m4_installer/1.4.18@bincrafters/stable"

    result = {'error': False,
              'results':
              [{'remote': 'conan-center',
                'items': [
                    {'recipe': {'id': 'm4_installer/1.4.18@bincrafters/stable'},
                     'packages':
                     [{'id': '445cf80f611c1d1eda08bde2ebc5066218ca9701', 'options': {}, 'settings': {}, 'requires': [], 'outdated': False}]}]}]}
    config = {"return_value": result}
    mocker.patch("conans.client.conan_api.ConanAPIV1.search_packages", **config)

    conan, cache, user_io = getConanAPI()

    install_conan_package(conan, cache, ConanFileReference.loads(ref))
    captured = capsys.readouterr()
    assert "Can't find a matching package" not in captured.err


class DummySignal():

    def emit(self):
        pass


def testConanWorker(base_fixture):
    """
    Test, if conan worker works on the queue.
    It is expected,that the queue size decreases over time.
    """
    sig = DummySignal()
    tab_info = parse_config_file(base_fixture.testdata_path / "app_config.json")
    conan_worker = ConanWorker(tab_info, sig)
    elements_before = conan_worker._conan_queue.qsize()
    time.sleep(8)

    assert conan_worker._conan_queue.qsize() < elements_before
    conan_worker.finish_working()
