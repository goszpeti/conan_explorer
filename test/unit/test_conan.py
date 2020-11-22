import os
import time
from conans.model.ref import ConanFileReference

from conan_app_launcher.components.conan import (get_conan_package_folder, _getConanAPI,
                                                 install_conan_package, _create_key_value_pair_list)
from conan_app_launcher.components.conan_worker import ConanWorker
from conan_app_launcher.components import parse_config_file

from PyQt5 import QtCore


def testInstallAndGetPath():
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


def testInstallAndGetPathWithDefaultOptions():
    """
    Test, if a package with an option can be found. TODO: currently don't care about multiple matching packages
    The lib dir in the package must NOT exist (for now)
    """
    ref = "zlib/1.2.11@conan/stable"
    os.system(f"conan remove {ref} -f")
    package_folder = get_conan_package_folder(ConanFileReference.loads(ref))
    assert (package_folder / "lib").is_dir()


def testManualOptionsInstall(capsys):
    """
    Test, if a package with options can install.
    The actual installaton must not return an error and non given options be merged with default options.
    """
    # This package has an option "shared" and is fairly small.
    ref = "gtest/1.7.0@bincrafters/stable"
    conan, cache, user_io = _getConanAPI()

    # assert not install_conan_package(conan, cache, ConanFileReference.loads(ref))

    # captured = capsys.readouterr()
    # assert "multiple" not in captured.err


def testCompilerAnySettings(mocker, capsys):
    """
    Test, if a package with <setting>=Any flags can install
    The actual installaton must not return an error.
    """
    # mock the remote response
    ref = "m4_installer/1.4.18@bincrafters/stable"

    result = {'error': False,
              'results':
              [{'remote': 'conan-center',
                'items': [
                    {'recipe': {'id': 'm4_installer/1.4.18@bincrafters/stable'},
                     'packages':
                     [
                        {'id': '44fcf6b9a7fb86b2586303e3db40189d3b511830', 'options': {}, 'settings': {
                          'arch_build': 'any', 'os_build': 'Linux', "build_type": "ANY"}, 'requires': [], 'outdated': False},
                        {'id': '456f15897172eef340fcbac8a70811f2beb26a93', 'options': {}, 'settings': {
                            'arch_build': 'anY', 'os_build': 'Windows', "build_type": "ANY"}, 'requires': [], 'outdated': False},
                    ]}]}]}
    config = {"return_value": result}
    mocker.patch("conans.client.conan_api.ConanAPIV1.search_packages", **config)

    conan, cache, user_io = _getConanAPI()

    install_conan_package(conan, cache, ConanFileReference.loads(ref))
    captured = capsys.readouterr()
    assert "ERROR" not in captured.err
    assert "Cannot install package" not in captured.err


def testCompilerNoSettings(mocker, capsys):
    """
    Test, if a package with no settings at all can install
    The actual installaton must not return an error.
    """
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

    conan, cache, user_io = _getConanAPI()

    install_conan_package(conan, cache, ConanFileReference.loads(ref))
    captured = capsys.readouterr()
    assert "Can't find a matching package" not in captured.err


def testCreateKeyValueList():
    """
    Test, that key value pairs can be extracted as strings. No arrays or other tpyes supported.
    The return value must be a list of strings in the format ["key1=value1", "key2=value2]
    "Any" values are ignored. (case insensitive)
    """
    inp = {"Key1": "Value1"}
    res = _create_key_value_pair_list(inp)
    assert res == ["Key1=Value1"]
    inp = {"Key1": "Value1", "Key2": "Value2"}
    res = _create_key_value_pair_list(inp)
    assert res == ["Key1=Value1", "Key2=Value2"]
    inp = {"Key1": "Value1", "Key2": "Any"}
    res = _create_key_value_pair_list(inp)
    assert res == ["Key1=Value1"]


def testAutoOptionsInstallDefaultSettings(capsys):
    """
    Test, if a package with options can install.
    The actual installaton must not return an error.
    """
    # This package has an option "shared" and is fairly small.
    ref = "zlib/1.2.11@conan/stable"
    conan, cache, user_io = _getConanAPI()

    assert install_conan_package(conan, cache, ConanFileReference.loads(ref))

    captured = capsys.readouterr()
    assert "multiple" not in captured.err


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
