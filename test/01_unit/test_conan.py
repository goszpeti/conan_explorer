import os
import platform
import time
from pathlib import Path
from typing import List

import conan_app_launcher
from conan_app_launcher.components.conan import (ConanApi,
                                                 _create_key_value_pair_list)
from conan_app_launcher.components.conan_worker import ConanWorker, ConanWorkerElement
from conans.model.ref import ConanFileReference

TEST_REF = "zlib/1.2.11@_/_"

def testConanProfileNameAliasBuilder():
    """ Test, that the build_conan_profile_name_alias returns human readable strings. """
    # check empty - should return a default name
    profile_name = ConanApi.build_conan_profile_name_alias({})
    assert profile_name == "default"

    # check a partial
    settings = {'os': 'Windows', 'arch': 'x86_64'}
    profile_name = ConanApi.build_conan_profile_name_alias(settings)
    assert profile_name == "Windows_x64"

    # check windows
    settings = {'os': 'Windows', 'os_build': 'Windows', 'arch': 'x86_64', 'arch_build': 'x86_64',
                'compiler': 'Visual Studio', 'compiler.version': '16', 'compiler.toolset': 'v142', 'build_type': 'Release'}
    profile_name = ConanApi.build_conan_profile_name_alias(settings)
    assert profile_name == "Windows_x64_vs16_v142_release"


    # check linux
    settings = {'os': 'Linux', 'arch': 'x86_64', 'compiler': 'gcc', 'compiler.version': '7.4', 'build_type': 'Debug'}
    profile_name = ConanApi.build_conan_profile_name_alias(settings)
    assert profile_name == "Linux_x64_gcc7.4_debug"


def testConanShortPathRoot():
    """ Test, that short path root can be read. """
    os.environ["CONAN_USER_HOME_SHORT"] = str(Path().home() / "._myconan")
    conan = ConanApi()
    if platform.system() == "Windows":
        assert conan.get_short_path_root() == Path().home() / "._myconan"
    else:
        assert not conan.get_short_path_root().exists()
    os.environ.pop("CONAN_USER_HOME_SHORT")

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
    default_settings = dict(conan.client_cache.default_profile.settings)

    pkgs = conan.search_package_in_remotes(ConanFileReference.loads(TEST_REF),  {"shared": "True"})
    assert len(pkgs) == 2
    pkg = pkgs[0]
    assert {"shared": "True"}.items() <= pkg["options"].items()

    for setting in default_settings:
        if setting in pkg["settings"].keys():
            assert default_settings[setting] in pkg["settings"][setting]


def testConanNotFindRemotePkgWrongOpts(base_fixture):
    """
    Test, if a wrong Option return causes an error.
    Empty list must be returned and the error be logged.
    """
    os.system(f"conan remove {TEST_REF} -f")
    conan = ConanApi()
    pkg = conan.search_package_in_remotes(ConanFileReference.loads(TEST_REF),  {"BogusOption": "True"})
    assert not pkg


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


def testInstallWithAnySettings(mocker, capfd):
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
    captured = capfd.readouterr()
    assert "ERROR" not in captured.err
    assert "Cannot install package" not in captured.err


def testCompilerNoSettings(base_fixture, capfd):
    """
    Test, if a package with no settings at all can install
    The actual installaton must not return an error.
    """
    ref = "hedley/15"  # header only
    os.system(f"conan remove {ref} -f")
    conan = ConanApi()
    package_folder = conan.get_path_or_install(ConanFileReference.loads(ref))
    assert (package_folder / "include").is_dir()
    captured = capfd.readouterr()
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
    """ Test, that an existing ref will be found in the remotes. """
    conan = ConanApi()
    res = conan.search_recipe_in_remotes(ConanFileReference.loads(TEST_REF))
    ref = ConanFileReference.loads(TEST_REF) # need to convert @_/_
    assert str(ref) in str(res)


def testConanWorker(base_fixture, mocker):
    """
    Test, if conan worker works on the queue.
    It is expected,that the queue size decreases over time.
    """
    conan_refs: List[ConanWorkerElement] = [{"reference": "m4/1.4.19@_/_", "options": {}},
                {"reference": "zlib/1.2.11@conan/stable", "options": {"shared": "True"}}]

    mocker.patch('conan_app_launcher.components.ConanApi.get_path_or_install')
    conan_worker = ConanWorker(conan_api=ConanApi())
    conan_worker.update_all_info(conan_refs)
    time.sleep(3)
    conan_worker.finish_working()

    conan_app_launcher.components.ConanApi.get_path_or_install.assert_called()

    assert conan_worker._conan_queue.qsize() == 0

# conan_server
# conan remote add private http://localhost:9300/
# conan upload example/1.0.0@myself/testing -r private
# conan user -r private -p demo demo
# .conan_server
# [write_permissions]
# */*@*/*: *
