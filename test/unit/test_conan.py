import os
import time
import platform
from conans.model.ref import ConanFileReference

import conan_app_launcher as app
from conan_app_launcher.components.conan import _create_key_value_pair_list, ConanApi
from conan_app_launcher.components.conan_worker import ConanWorker
from conan_app_launcher.components import parse_config_file


def testEmptyCleanupCache():
    """
    Test, if a clean cache returns no dirs. Actual functionality is tested with gui.
    It is assumed, that the cash is clean, like it would be on the CI.
    """
    conan = ConanApi()
    paths = conan.get_cleanup_cache_paths()
    assert not paths


def testConanFindRemotePkg():
    """
    Test, if search_package_in_remotes finds a package for the current system and the specified options.
    The function must find exactly one pacakge, which uses the spec. options and corresponds to the
    default settings.
    """
    ref = "zlib/1.2.11@conan/stable"
    os.system(f"conan remove {ref} -f")
    conan = ConanApi()
    default_settings = dict(conan.cache.default_profile.settings)

    pkgs = conan.search_package_in_remotes(ConanFileReference.loads(ref),  {"shared": "True"})
    assert len(pkgs) == 1
    pkg = pkgs[0]
    assert {"shared": "True"}.items() <= pkg["options"].items()

    for setting in default_settings:
        if setting in pkg["settings"].keys():
            assert default_settings[setting] in pkg["settings"][setting]


def testConanNotFindRemotePkgWrongOpts(capsys):
    """
    Test, if a wrong Option return causes an error.
    Empty list must be returned and the error be logged.
    """
    ref = "zlib/1.2.11@conan/stable"
    os.system(f"conan remove {ref} -f")
    conan = ConanApi()
    pkg = conan.search_package_in_remotes(ConanFileReference.loads(ref),  {"BogusOption": "True"})
    captured = capsys.readouterr()
    assert not pkg
    assert "Can't find a matching package" in captured.err


def testConanFindLocalPkg():
    """
    Test, if get_package installs the package and returns the path and check it again.
    The bin dir in the package must exist (indicating it was correctly downloaded)
    """
    ref = "zlib/1.2.11@conan/stable"
    os.system(f"conan install {ref}")
    conan = ConanApi()
    pkgs = conan.find_best_matching_packages(ConanFileReference.loads(ref))
    assert len(pkgs) == 1


def testGetPathOrInstall():
    """
    Test, if get_package installs the package and returns the path and check it again.
    The bin dir in the package must exist (indicating it was correctly downloaded)
    """
    ref = "m4_installer/1.4.18@bincrafters/stable"
    os.system(f"conan remove {ref} -f")
    conan = ConanApi()
    # Gets package path / installs the package
    package_folder = conan.get_path_or_install(ConanFileReference.loads(ref))
    assert (package_folder / "bin").is_dir()
    # check again for already installed package
    package_folder = conan.get_path_or_install(ConanFileReference.loads(ref))
    assert (package_folder / "bin").is_dir()


def testGetPathOrInstallManualOptions(capsys):
    """
    Test, if a package with options can install.
    The actual installaton must not return an error and non given options be merged with default options.
    """
    # This package has an option "shared" and is fairly small.
    ref = "zlib/1.2.11@conan/stable"
    os.system(f"conan remove {ref} -f")
    conan = ConanApi()
    package_folder = conan.get_path_or_install(ConanFileReference.loads(ref), {"shared": "True"})
    if platform.system() == "Windows":
        assert (package_folder / "lib" / "zlib.lib").is_file()
    elif platform.system() == "Linux":
        assert (package_folder / "lib" / "libz.so").is_file()


def testInstallWithAnySettings(mocker, capsys):
    """
    Test, if a package with <setting>=Any flags can install
    The actual installaton must not return an error.
    """
    # mock the remote response
    ref = "m4_installer/1.4.18@bincrafters/stable"
    os.system(f"conan remove {ref} -f")
    conan = ConanApi()

    assert conan.install_package(ConanFileReference.loads(ref), {'id': '44fcf6b9a7fb86b2586303e3db40189d3b511830', 'options': {}, 'settings': {
        'arch_build': 'any', 'os_build': 'Linux', "build_type": "ANY"}, 'requires': [], 'outdated': False},)
    captured = capsys.readouterr()
    assert "ERROR" not in captured.err
    assert "Cannot install package" not in captured.err


def testCompilerNoSettings(capsys):
    """
    Test, if a package with no settings at all can install
    The actual installaton must not return an error.
    """
    # mock the remote response
    ref = "CLI11/1.9.1@cliutils/stable"  # header only
    os.system(f"conan remove {ref} -f")
    conan = ConanApi()
    package_folder = conan.get_path_or_install(ConanFileReference.loads(ref))
    assert (package_folder / "include").is_dir()
    captured = capsys.readouterr()
    assert "ERROR" not in captured.err
    assert "Can't find a matching package" not in captured.err


def testResolveDefaultOptions():
    """
    Test, if different kind of types of default options can be converted to a dict
    Dict is expected.
    """
    conan = ConanApi()

    str_val = "option=value"
    ret = conan._resolve_default_options(str_val)
    assert ret.items()

    tup_val = ("option=value", "options2=value2")
    ret = conan._resolve_default_options(tup_val)
    assert ret.items()

    list_val = ["option=value", "options2=value2"]
    ret = conan._resolve_default_options(list_val)
    assert ret.items()


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


def testSearchForAllPackages():
    ref = "zlib/1.2.8@conan/stable"
    #os.system(f"conan remove {ref} -f")
    conan = ConanApi()
    res = conan.search_recipe_in_remotes(ConanFileReference.loads(ref))
    assert "zlib/1.2.8@conan/stable" in str(res)


def testConanWorker(base_fixture, settings_fixture):
    """
    Test, if conan worker works on the queue.
    It is expected,that the queue size decreases over time.
    """
    # class DummySignal():

    #     def emit(self):
    #         pass
    # sig = DummySignal()
    app.tab_configs = parse_config_file(settings_fixture)
    conan_worker = ConanWorker()
    elements_before = conan_worker._conan_queue.qsize()
    time.sleep(10)

    assert conan_worker._conan_queue.qsize() < elements_before
    conan_worker.finish_working()

    # conan_server
    # conan remote add private http://localhost:9300/
    # conan upload example/1.0.0@myself/testing -r private
    # .conan_server
    # [write_permissions]
    # */*@*/*: *
