import os
import platform
from pprint import pprint
import tempfile
import time
from pathlib import Path

import pytest
from test.conftest import TEST_REF, conan_install_ref, conan_remove_ref
from typing import List

from conan_explorer.conan_wrapper import ConanApi
from conan_explorer.conan_wrapper.types import ConanPkg, create_key_value_pair_list
from conan_explorer.conan_wrapper.conan_worker import (ConanWorker,
                                                           ConanWorkerElement)
from conan_explorer.conan_wrapper.conan_cleanup import ConanCleanup
from conan_explorer.conan_wrapper.types import ConanRef

def test_conan_get_conan_buildinfo():
    """
    Check, that get_conan_buildinfo actually retrieves as a string for the linux pkg 
    """
    conan = ConanApi().init_api()
    LINUX_X64_GCC9_SETTINGS = {'os': 'Linux', 'arch': 'x86_64', 'compiler': 'gcc', 
        "compiler.libcxx": "libstdc++11",'compiler.version': '9', 'build_type': 'Release'}
    buildinfo = conan.get_conan_buildinfo(ConanRef.loads(TEST_REF), LINUX_X64_GCC9_SETTINGS)
    assert "USER_example" in buildinfo
    assert "ENV_example" in buildinfo

def test_conan_profile_name_alias_builder():
    """ Test, that the build_conan_profile_name_alias returns human readable strings. """
    # check empty - should return a default name
    profile_name = ConanApi.build_conan_profile_name_alias({})
    assert profile_name == "No Settings"

    # check a partial
    settings = {'os': 'Windows', 'arch': 'x86_64'}
    profile_name = ConanApi.build_conan_profile_name_alias(settings)
    assert profile_name == "Windows_x64"

    # check windows
    WINDOWS_x64_VS16_SETTINGS = {'os': 'Windows', 'os_build': 'Windows', 'arch': 'x86_64', 
                             'arch_build': 'x86_64', 'compiler': 'Visual Studio', 
                             'compiler.version': '16', 'compiler.toolset': 'v142', 
                             'build_type': 'Release'}
    profile_name = ConanApi.build_conan_profile_name_alias(WINDOWS_x64_VS16_SETTINGS)
    assert profile_name == "Windows_x64_vs16_v142_release"

    # check linux
    LINUX_X64_GCC7_SETTINGS = {'os': 'Linux', 'arch': 'x86_64', 'compiler': 'gcc', 
                           'compiler.version': '7.4', 'build_type': 'Debug'}
    profile_name = ConanApi.build_conan_profile_name_alias(LINUX_X64_GCC7_SETTINGS)
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
    paths = ConanCleanup(ConanApi().init_api()).get_cleanup_cache_paths()
    assert not paths
    os.environ.pop("CONAN_USER_HOME")
    os.environ.pop("CONAN_USER_HOME_SHORT")

@pytest.mark.conanv2
def test_conan_find_remote_pkg(base_fixture):
    """
    Test, if search_package_in_remotes finds a package for the current system and the specified options.
    The function must find exactly one pacakge, which uses the spec. options and corresponds to the
    default settings.
    """
    conan_remove_ref(TEST_REF)
    conan = ConanApi().init_api()
    default_settings = conan.get_default_settings()

    pkgs = conan.find_best_matching_package_in_remotes(ConanRef.loads(TEST_REF), 
                                                        {"shared": "True"})
    assert len(pkgs) > 0
    pkg = pkgs[0]
    assert {"shared": "True"}.items() <= pkg["options"].items()

    for setting in default_settings:
        if setting in pkg["settings"].keys():
            if "compiler." in setting: # don't evaluate comp. details
                continue
            assert default_settings[setting] in pkg["settings"][setting]

# @pytest.mark.conanv2
def test_conan_not_find_remote_pkg_wrong_opts(base_fixture):
    """
    Test, if a wrong Option return causes an error.
    Empty list must be returned and the error be logged.
    """
    conan_remove_ref(TEST_REF)
    conan = ConanApi().init_api()
    pkg = conan.find_best_matching_package_in_remotes(ConanRef.loads(TEST_REF),  
                                                      {"BogusOption": "True"})
    assert not pkg

@pytest.mark.conanv2
def test_conan_find_local_pkg(base_fixture):
    """
    Test, if get_package installs the package and returns the path and check it again.
    The bin dir in the package must exist (indicating it was correctly downloaded)
    """
    conan_remove_ref(TEST_REF)
    conan_install_ref(TEST_REF)
    conan = ConanApi().init_api()
    pkgs = conan.find_best_matching_packages(ConanRef.loads(TEST_REF))
    assert len(pkgs) == 1 # default options are filtered

@pytest.mark.conanv2
def test_get_path_or_install(base_fixture):
    """
    Test, if get_package installs the package and returns the path and check it again.
    The bin dir in the package must exist (indicating it was correctly downloaded)
    """
    dir_to_check = "bin"
    conan_remove_ref(TEST_REF)

    conan = ConanApi().init_api()
    # Gets package path / installs the package
    id, package_folder = conan.get_path_or_auto_install(ConanRef.loads(TEST_REF))
    assert (package_folder / dir_to_check).is_dir()
    # check again for already installed package
    id, package_folder = conan.get_path_or_auto_install(ConanRef.loads(TEST_REF))
    assert (package_folder / dir_to_check).is_dir()

@pytest.mark.conanv2
def test_get_path_or_install_manual_options():
    """
    Test, if a package with options can install.
    The actual installaton must not return an error and non given options be merged with default options.
    """
    # This package has an option "shared" and is fairly small.
    conan_remove_ref(TEST_REF)
    conan = ConanApi().init_api()
    id, package_folder = conan.get_path_or_auto_install(ConanRef.loads(TEST_REF), {"shared": "True"})
    if platform.system() == "Windows":
        assert (package_folder / "bin" / "python.exe").is_file()
    elif platform.system() == "Linux":
        assert (package_folder / "bin" / "python").is_file()

# @pytest.mark.conanv2 TODO: Create v2 compatible testcase
def test_install_with_any_settings(mocker, capfd):
    """
    Test, if a package with <setting>=Any flags can install
    The actual installaton must not return an error.
    """
    # mock the remote response
    conan_remove_ref(TEST_REF)
    # Create the "any" package
    conan = ConanApi().init_api()
    assert conan.install_package(ConanRef.loads(TEST_REF), {
        'id': '325c44fdb228c32b3de52146f3e3ff8d94dddb60', 'options': {},
        'settings': {'arch_build': 'any', 'os_build': 'Linux', "build_type": "ANY"},
        'requires': [], 'outdated': False},)
    captured = capfd.readouterr()
    assert "ERROR" not in captured.err
    assert "Cannot install package" not in captured.err

# @pytest.mark.conanv2 TODO create package for it
def test_compiler_no_settings(base_fixture, capfd):
    """
    Test, if a package with no settings at all can install
    The actual installaton must not return an error.
    """
    ref = "nocompsettings/1.0.0@local/no_sets"
    conan_remove_ref(ref)
    capfd.readouterr() # remove can result in error message - clear
    conan = ConanApi().init_api()

    id, package_folder = conan.get_path_or_auto_install(ConanRef.loads(ref))
    assert (package_folder / "bin").is_dir()
    captured = capfd.readouterr()
    assert "ERROR" not in captured.err
    assert "Can't find a matching package" not in captured.err
    conan_remove_ref(ref)

@pytest.mark.conanv2
def test_resolve_default_options(base_fixture):
    """
    Test, if different kind of types of default options can be converted to a dict
    Dict is expected.
    """
    conan = ConanApi().init_api()

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
    res = create_key_value_pair_list(inp)
    assert res == ["Key1=Value1"]
    inp = {"Key1": "Value1", "Key2": "Value2"}
    res = create_key_value_pair_list(inp)
    assert res == ["Key1=Value1", "Key2=Value2"]
    inp = {"Key1": "Value1", "Key2": "Any"}
    res = create_key_value_pair_list(inp)
    assert res == ["Key1=Value1"]

#@pytest.mark.conanv2
def test_search_for_all_packages(base_fixture):
    """ Test, that an existing ref will be found in the remotes. """
    conan = ConanApi().init_api()
    res = conan.search_recipe_all_versions_in_remotes(ConanRef.loads(TEST_REF))
    ref = ConanRef.loads(TEST_REF)  # need to convert @_/_
    assert str(ref) in str(res)

@pytest.mark.conanv2
def test_conan_worker(base_fixture, mocker):
    """
    Test, if conan worker works on the queue.
    It is expected,that the queue size decreases over time.
    """
    conan_refs: List[ConanWorkerElement] = \
    [{"ref_pkg_id": "m4/1.4.19@_/_", "options": {},
    "settings": {}, "update": False,  "auto_install": True, "profile": ""},
    {"ref_pkg_id": "zlib/1.2.11@conan/stable", "options": {"shared": "True"},
        "settings": {}, "update": False,  "auto_install": True, "profile": ""}
    ]

    mock_func = mocker.patch('conan_explorer.conan_wrapper.ConanApi.get_path_or_auto_install')
    import conan_explorer.app as app

    conan_worker = ConanWorker(ConanApi().init_api(), app.active_settings)
    conan_worker.update_all_info(conan_refs, None)
    time.sleep(3)
    conan_worker.finish_working()

    mock_func.assert_called()

    assert conan_worker._conan_install_queue.qsize() == 0

# def test_conan_diff(base_fixture):
#     conan = ConanApi()
#     conan.init_api()
#     available_refs = conan.get_remote_pkgs_from_ref(ConanRef.loads(TEST_REF), None)
#     wanted_ref = { # add default options
#         'id': '', 'options': {"shared": "False", "variant": "var1", "fPIC2": "True"},
#         'settings': {'arch_build': 'x86_64', 'os_build': 'Linux', "build_type": "Release"},
#         'requires': [], 'outdated': False}
#     pkg_diff = []
#     from dictdiffer import diff
#     for remote_ref in available_refs:
#         opt_diff = diff(remote_ref.get("options", {}), wanted_ref.get("options", {}))
#                             #ignore_type_subclasses=True)
#         settings_diff = diff(remote_ref.get("settings", {}), wanted_ref.get("settings", {}))
#         pkg_diff.append({"options": opt_diff, "settings": settings_diff})
#     pprint(pkg_diff)
