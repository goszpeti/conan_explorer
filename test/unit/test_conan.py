import os
import time
import platform
from pathlib import Path
from conans.model.ref import ConanFileReference

import conan_app_launcher as app
from conan_app_launcher.components.conan import _create_key_value_pair_list, ConanApi
from conan_app_launcher.components.conan_worker import ConanWorker
from conan_app_launcher.components import parse_config_file

TEST_REF = "zlib/1.2.11@_/_"

def testConanShortPathRoot():
    os.environ["CONAN_USER_HOME_SHORT"] = str(Path().home() / "._myconan")
    conan = ConanApi()
    assert conan.get_short_path_root() == Path().home() / "._myconan"

def testEmptyCleanupCache(base_fixture):
    """
    Test, if a clean cache returns no dirs. Actual functionality is tested with gui.
    It is assumed, that the cash is clean, like it would be on the CI.
    """
    conan = ConanApi()
    paths = conan.get_cleanup_cache_paths()
    assert not paths


def testConanFindRemotePkg(base_fixture):
    """
    Test, if search_package_in_remotes finds a package for the current system and the specified options.
    The function must find exactly one pacakge, which uses the spec. options and corresponds to the
    default settings.
    """
    os.system(f"conan remove {TEST_REF} -f")
    conan = ConanApi()
    default_settings = dict(conan.cache.default_profile.settings)

    pkgs = conan.search_package_in_remotes(ConanFileReference.loads(TEST_REF),  {"shared": "True"})
    assert len(pkgs) == 2
    pkg = pkgs[0]
    assert {"shared": "True"}.items() <= pkg["options"].items()

    for setting in default_settings:
        if setting in pkg["settings"].keys():
            assert default_settings[setting] in pkg["settings"][setting]


def testConanNotFindRemotePkgWrongOpts(base_fixture, capsys):
    """
    Test, if a wrong Option return causes an error.
    Empty list must be returned and the error be logged.
    """
    os.system(f"conan remove {TEST_REF} -f")
    conan = ConanApi()
    pkg = conan.search_package_in_remotes(ConanFileReference.loads(TEST_REF),  {"BogusOption": "True"})
    captured = capsys.readouterr()
    assert not pkg
    assert "Can't find a matching package" in captured.err


def testConanFindLocalPkg(base_fixture):
    """
    Test, if get_package installs the package and returns the path and check it again.
    The bin dir in the package must exist (indicating it was correctly downloaded)
    """
    os.system(f"conan install {TEST_REF}")
    conan = ConanApi()
    pkgs = conan.find_best_matching_packages(ConanFileReference.loads(TEST_REF))
    assert len(pkgs) == 1


def testGetPathOrInstall(base_fixture):
    """
    Test, if get_package installs the package and returns the path and check it again.
    The bin dir in the package must exist (indicating it was correctly downloaded)
    """
    os.system(f"conan remove {TEST_REF} -f")
    conan = ConanApi()
    # Gets package path / installs the package
    package_folder = conan.get_path_or_install(ConanFileReference.loads(TEST_REF))
    assert (package_folder / "lib").is_dir()
    # check again for already installed package
    package_folder = conan.get_path_or_install(ConanFileReference.loads(TEST_REF))
    assert (package_folder / "lib").is_dir()


def testGetPathOrInstallManualOptions(capsys):
    """
    Test, if a package with options can install.
    The actual installaton must not return an error and non given options be merged with default options.
    """
    # This package has an option "shared" and is fairly small.
    os.system(f"conan remove {TEST_REF} -f")
    conan = ConanApi()
    package_folder = conan.get_path_or_install(ConanFileReference.loads(TEST_REF), {"shared": "True"})
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
    os.system(f"conan remove {TEST_REF} -f")
    conan = ConanApi()

    assert conan.install_package(ConanFileReference.loads(TEST_REF), 
        {'id': '6cc50b139b9c3d27b3e9042d5f5372d327b3a9f7', 'options': {}, 'settings': {
        'arch_build': 'any', 'os_build': 'Linux', "build_type": "ANY"}, 'requires': [], 'outdated': False},)
    captured = capsys.readouterr()
    assert "ERROR" not in captured.err
    assert "Cannot install package" not in captured.err


def testCompilerNoSettings(base_fixture, capsys):
    """
    Test, if a package with no settings at all can install
    The actual installaton must not return an error.
    """
    ref = "hedley/15"  # header only
    os.system(f"conan remove {ref} -f")
    conan = ConanApi()
    package_folder = conan.get_path_or_install(ConanFileReference.loads(ref))
    assert (package_folder / "include").is_dir()
    captured = capsys.readouterr()
    assert "ERROR" not in captured.err
    assert "Can't find a matching package" not in captured.err


def testResolveDefaultOptions(base_fixture):
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


def testCreateKeyValueList(base_fixture):
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


def testSearchForAllPackages(base_fixture):
    conan = ConanApi()
    res = conan.search_recipe_in_remotes(ConanFileReference.loads(TEST_REF))
    ref = ConanFileReference.loads(TEST_REF) # need to convert @_/_
    assert str(ref) in str(res)


def testConanWorker(base_fixture, settings_fixture):
    """
    Test, if conan worker works on the queue.
    It is expected,that the queue size decreases over time.
    """

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
