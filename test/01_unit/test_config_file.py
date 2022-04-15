import json
import tempfile
from distutils.file_util import copy_file
from pathlib import Path

from conan_app_launcher.ui.data.json_file import JsonUiConfig
from conans.model.ref import ConanFileReference


def test_new_filename_is_created(base_fixture):
    """
    Tests, that on reading a nonexistant file an error with an error mesage is printed to the logger.
    Expects the sdterr to contain the error level(ERROR) and the error cause.
    """
    new_file_path = Path(tempfile.gettempdir()) / "newfile.config"
    config = JsonUiConfig(new_file_path).load()
    assert len(config.app_grid.tabs) == 1  # default tab
    assert new_file_path.exists()


def test_read_correct_file(base_fixture, ui_config_fixture):
    """
    Tests reading a correct config json with 2 tabs.
    Expects the same values as in the file.
    """
    tabs = JsonUiConfig(ui_config_fixture).load().app_grid.tabs
    assert tabs[0].name == "Basics"
    tab0_entries = tabs[0].apps
    assert tab0_entries[0].conan_ref == "example/9.9.9@local/testing"
    assert tab0_entries[0].executable == "bin/python"
    assert tab0_entries[0].icon == "NonExistantIcon.png"
    assert tab0_entries[0].name == "App1 with spaces"
    assert tab0_entries[0].is_console_application
    assert tab0_entries[0].args == "-n name"

    assert tab0_entries[1].conan_ref == "example/1.0.0@_/_"
    assert tab0_entries[1].executable == "bin/python"
    assert tab0_entries[1].icon == "icon.ico"
    assert tab0_entries[1].name == "App2"
    assert not tab0_entries[1].is_console_application  # default
    assert tab0_entries[1].args == ""
    assert tab0_entries[1].conan_options == {"shared": "True", "Option2": "Value2"}

    assert tabs[1].name == "Extra"
    tab1_entries = tabs[1].apps
    assert tab1_entries[0].conan_ref == "example/1.0.0@_/_"
    assert tab1_entries[0].executable == "bin/app2.exe"
    assert tab1_entries[0].icon == "//myicon.png"
    assert tab1_entries[0].name == "App2"


def test_update(base_fixture):
    """ Test that the oldest schema version updates correctly to the newest one """
    temp_file = Path(tempfile.gettempdir()) / "update.json"
    copy_file(str(base_fixture.testdata_path / "config_file" / "update.json"), str(temp_file))

    tabs = JsonUiConfig(temp_file).load().app_grid.tabs
    assert tabs[0].name == "Basics"
    tab0_entries = tabs[0].apps
    assert tab0_entries[0].conan_ref == "m4/1.4.19@_/_"
    assert tab0_entries[1].conan_ref == "boost_functional/1.69.0@bincrafters/stable"
    assert tabs[1].name == "Extra"
    tab1_entries = tabs[1].apps
    assert tab1_entries[0].conan_ref == "app2/1.0.0@user/stable"

    # now check the file, don't trust the own parser
    read_obj = {}
    with open(temp_file) as config_file:
        read_obj = json.load(config_file)
    assert read_obj.get("version") == "0.4.0"  # last version
    assert read_obj.get("tabs")[0].get("apps")[0].get("conan_ref") == "m4/1.4.19@_/_"
    assert read_obj.get("tabs")[0].get("apps")[0].get("package_id") is None
    assert read_obj.get("tabs")[0].get("apps")[0].get("is_console_application") is True
    assert read_obj.get("tabs")[0].get("apps")[0].get("console_application") is None


def test_read_invalid_version(base_fixture, capfd):
    """
    Tests, that reading a config file with the wrong version will print an error.
    Expects the sdterr to contain the error level(ERROR) and the error cause.
    """
    config = JsonUiConfig(base_fixture.testdata_path / "config_file" / "wrong_version.json").load()
    assert len(config.app_grid.tabs) == 1
    captured = capfd.readouterr()
    assert "Failed validating" in captured.err
    assert "version" in captured.err


def test_read_invalid_content(base_fixture, capfd):
    """
    Tests, that reading a config file with invalid syntax will print an error.
    Expects the sdterr to contain the error level(ERROR) and the error cause.
    """
    config = JsonUiConfig(base_fixture.testdata_path / "config_file" / "invalid_syntax.json").load()
    assert len(config.app_grid.tabs) == 1
    captured = capfd.readouterr()
    assert "Expecting property name" in captured.err


def check_config(ref_dict, test_dict):
    """ Check dict entries to a ref dict (recursive) """
    for key in test_dict:
        if ref_dict.get(key):
            if isinstance(ref_dict.get(key), list):
                test_list = ref_dict.get(key)
                ref_list = test_dict.get(key)
                for i in range(len(test_list)):
                    check_config(test_list[i], ref_list[i])
            elif isinstance(ref_dict.get(key), dict):
                check_config(ref_dict.get(key), test_dict.get(key))
                continue
            else:
                try:  # test if it is conanref in string form.
                    # We don't care if it is written differently, as long as it is the same object
                    ConanFileReference.loads(test_dict.get(
                        key)) == ConanFileReference.loads(ref_dict.get(key))
                except Exception:
                    assert test_dict.get(key) == ref_dict.get(key)
        else:
            assert not test_dict.get(key)


def test_write_config_file(base_fixture, ui_config_fixture, tmp_path):
    """
    Tests, that writing a config file from internal state is correct.
    Expects the same content, as the original file.
    """
    test_file = Path(tmp_path) / "test.json"

    config = JsonUiConfig(ui_config_fixture)
    tabs = config.load()
    new_config = JsonUiConfig(test_file)
    new_config.save(tabs)
    with open(str(ui_config_fixture)) as config:
        ref_dict = json.load(config)
    with open(str(test_file)) as config:
        test_dict = json.load(config)
    # there are diffs - the file written always contains all keys, whereas the (legacy) user config
    # can omit values, so test_dict is a superset of ref_dict
    # so test, that all all values from ref_dict are equal and the new ones are empty
    check_config(ref_dict, test_dict)
