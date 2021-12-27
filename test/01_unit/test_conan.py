import os
import platform
import tempfile
import time
from pathlib import Path
from typing import List

import conan_app_launcher
import pytest
from conan_app_launcher.components.conan import (ConanApi,
                                                 _create_key_value_pair_list)
from conan_app_launcher.components.conan_worker import (ConanWorker,
                                                        ConanWorkerElement)
from conans import __version__
from conans.model.ref import ConanFileReference
from packaging import version

TEST_REF = "zlib/1.2.8@_/_"

def test_conan_profile_name_alias_builder():
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


def test_conan_short_path_root():
    """ Test, that short path root can be read. """
    new_short_home = Path(tempfile.gettempdir()) / "._myconan_short"
    os.environ["CONAN_USER_HOME_SHORT"] = str(new_short_home)
    conan = ConanApi()
    if platform.system() == "Windows":
        assert conan.get_short_path_root() == new_short_home
    else:
        assert not conan.get_short_path_root().exists()
    os.environ.pop("CONAN_USER_HOME_SHORT")

def test_empty_cleanup_cache(base_fixture):
    """
    Test, if a clean cache returns no dirs. Actual functionality is tested with gui.
    It is assumed, that the cash is clean, like it would be on the CI.
    """
    os.environ["CONAN_USER_HOME"] = str(Path(tempfile.gettempdir()) / "._myconan_home")
    os.environ["CONAN_USER_HOME_SHORT"] = str(Path(tempfile.gettempdir()) / "._myconan_short")
    conan = ConanApi()
    paths = conan.get_cleanup_cache_paths()
    assert not paths
    os.environ.pop("CONAN_USER_HOME")
    os.environ.pop("CONAN_USER_HOME_SHORT")


def test_conan_find_remote_pkg(base_fixture):
    """
    Test, if search_package_in_remotes finds a package for the current system and the specified options.
    The function must find exactly one pacakge, which uses the spec. options and corresponds to the
    default settings.
    """
    os.system(f"conan remove {TEST_REF} -f")
    conan = ConanApi()
    default_settings = dict(conan.client_cache.default_profile.settings)

    pkgs = conan.search_package_in_remotes(ConanFileReference.loads(TEST_REF),  {"shared": "True"})
    assert len(pkgs) >= 1
    pkg = pkgs[0]
    assert {"shared": "True"}.items() <= pkg["options"].items()

    for setting in default_settings:
        if setting in pkg["settings"].keys():
            assert default_settings[setting] in pkg["settings"][setting]


def test_conan_not_find_remote_pkg_wrong_opts(base_fixture):
    """
    Test, if a wrong Option return causes an error.
    Empty list must be returned and the error be logged.
    """
    os.system(f"conan remove {TEST_REF} -f")
    conan = ConanApi()
    pkg = conan.search_package_in_remotes(ConanFileReference.loads(TEST_REF),  {"BogusOption": "True"})
    assert not pkg


def test_conan_find_local_pkg(base_fixture):
    """
    Test, if get_package installs the package and returns the path and check it again.
    The bin dir in the package must exist (indicating it was correctly downloaded)
    """
    os.system(f"conan install {TEST_REF}")
    conan = ConanApi()
    pkgs = conan.find_best_matching_packages(ConanFileReference.loads(TEST_REF))
    assert len(pkgs) == 1


def test_get_path_or_install(base_fixture):
    """
    Test, if get_package installs the package and returns the path and check it again.
    The bin dir in the package must exist (indicating it was correctly downloaded)
    """
    # can't find a package on conan-center which works with conan version lower then 1.33
    if version.parse(__version__) < version.parse("1.33"):
        pytest.skip()
    install_ref = TEST_REF
    dir_to_check = "lib"
    os.system(f"conan remove {install_ref} -f")
    conan = ConanApi()
    # Gets package path / installs the package
    package_folder = conan.get_path_or_install(ConanFileReference.loads(install_ref))
    assert (package_folder / dir_to_check).is_dir()
    # check again for already installed package
    package_folder = conan.get_path_or_install(ConanFileReference.loads(install_ref))
    assert (package_folder / dir_to_check).is_dir()


def test_get_path_or_install_manual_options(capsys):
    """
    Test, if a package with options can install.
    The actual installaton must not return an error and non given options be merged with default options.
    """
    # can't find a package on conan-center which works with conan version lower then 1.33
    if version.parse(__version__) < version.parse("1.33"):
        pytest.skip()
    # This package has an option "shared" and is fairly small.
    os.system(f"conan remove {TEST_REF} -f")
    conan = ConanApi()
    package_folder = conan.get_path_or_install(ConanFileReference.loads(TEST_REF), {"shared": "True"})
    if platform.system() == "Windows":
        assert (package_folder / "lib" / "zlib.lib").is_file()
    elif platform.system() == "Linux":
        assert (package_folder / "lib" / "libz.so").is_file()


def test_install_with_any_settings(mocker, capfd):
    """
    Test, if a package with <setting>=Any flags can install
    The actual installaton must not return an error.
    """
    # mock the remote response
    os.system(f"conan remove {TEST_REF} -f")
    conan = ConanApi()

    assert conan.install_package(
        ConanFileReference.loads(TEST_REF), 
        {'id': '3fb49604f9c2f729b85ba3115852006824e72cab', 'options': {}, 'settings': {
        'arch_build': 'any', 'os_build': 'Linux', "build_type": "ANY"}, 'requires': [], 'outdated': False},)
    captured = capfd.readouterr()
    assert "ERROR" not in captured.err
    assert "Cannot install package" not in captured.err


def test_compiler_no_settings(base_fixture, capfd):
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


def test_resolve_default_options(base_fixture):
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


def test_create_key_value_list(base_fixture):
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


def test_search_for_all_packages(base_fixture):
    """ Test, that an existing ref will be found in the remotes. """
    conan = ConanApi()
    res = conan.search_recipe_in_remotes(ConanFileReference.loads(TEST_REF))
    ref = ConanFileReference.loads(TEST_REF) # need to convert @_/_
    assert str(ref) in str(res)


def test_conan_worker(base_fixture, mocker):
    """
    Test, if conan worker works on the queue.
    It is expected,that the queue size decreases over time.
    """
    conan_refs: List[ConanWorkerElement] = [{"reference": "m4/1.4.19@_/_", "options": {}},
                {"reference": "zlib/1.2.11@conan/stable", "options": {"shared": "True"}}]

    mock_func = mocker.patch('conan_app_launcher.components.ConanApi.get_path_or_install')
    conan_worker = ConanWorker(conan_api=ConanApi())
    conan_worker.update_all_info(conan_refs, None)
    time.sleep(3)
    conan_worker.finish_working()

    mock_func.assert_called()

    assert conan_worker._conan_install_queue.qsize() == 0

# conan_server
# conan remote add private http://localhost:9300/
# conan upload example/1.0.0@myself/testing -r private
# conan user -r private -p demo demo
# .conan_server
# [write_permissions]
# */*@*/*: *
