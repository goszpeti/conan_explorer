import json
import tempfile
from distutils.file_util import copy_file
from pathlib import Path

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

import pytest
from conan_app_launcher.components import parse_config_file, write_config_file


def testCorrectFile(base_fixture):
    """
    Tests reading a correct config json with 2 tabs.
    Expects the same values as in the file.
    """
    tabs = parse_config_file(base_fixture.testdata_path / "app_config.json")
    assert tabs[0].name == "Basics"
    tab0_entries = tabs[0].get_app_entries()
    assert str(tab0_entries[0].conan_ref) == "m4_installer/1.4.18@bincrafters/stable"
    assert tab0_entries[0].executable.as_posix() == "bin/m4"
    assert tab0_entries[0].icon.name == "default_app_icon.png"
    assert tab0_entries[0].name == "App1 with spaces"
    assert tab0_entries[0].is_console_application
    assert tab0_entries[0].args == "-n name"

    assert str(tab0_entries[1].conan_ref) == "zlib/1.2.11@conan/stable"
    assert tab0_entries[1].executable.as_posix() == "bin/app2"
    assert tab0_entries[1].icon.name == "default_app_icon.png"
    assert tab0_entries[1].name == "App2"
    assert not tab0_entries[1].is_console_application  # default
    assert tab0_entries[1].args == ""
    assert tab0_entries[1].conan_options == {"shared": "True"}

    assert tabs[1].name == "Extra"
    tab1_entries = tabs[1].get_app_entries()
    assert str(tab1_entries[0].conan_ref) == "app2/1.0.0@user/stable"
    assert tab1_entries[0].executable.as_posix() == "bin/app2.exe"
    assert tab1_entries[0].icon.name == "default_app_icon.png"
    assert tab1_entries[0].name == "App2"


def testUpdate(base_fixture):
    temp_file = Path(tempfile.gettempdir()) / "update.json"
    copy_file(str(base_fixture.testdata_path / "config_file" / "update.json"), str(temp_file))

    tabs = parse_config_file(temp_file)
    assert tabs[0].name == "Basics"
    tab0_entries = tabs[0].get_app_entries()
    assert str(tab0_entries[0].conan_ref) == "m4_installer/1.4.18@bincrafters/stable"
    assert str(tab0_entries[1].conan_ref) == "boost_functional/1.69.0@bincrafters/stable"
    assert tabs[1].name == "Extra"
    tab1_entries = tabs[1].get_app_entries()
    assert str(tab1_entries[0].conan_ref) == "app2/1.0.0@user/stable"

    # now check the file, don't trust the own parser
    read_obj = {}
    with open(temp_file) as config_file:
        read_obj = json.load(config_file)
    assert read_obj.get("version") == "0.3.0"  # last version
    assert read_obj.get("tabs")[0].get("apps")[0].get("conan_ref") == "m4_installer/1.4.18@bincrafters/stable"
    assert read_obj.get("tabs")[0].get("apps")[0].get("package_id") is None


def testNoneExistantFilename(base_fixture, capsys):
    """
    Tests, that on reading a nonexistant file an error with an error mesage is printed to the logger.
    Expects the sdterr to contain the error level(ERROR) and the error cause.
    """
    tabs = parse_config_file(base_fixture.testdata_path / "nofile.json")
    assert tabs == []
    captured = capsys.readouterr()
    assert "ERROR" in captured.err
    assert "does not exist" in captured.err


def testInvalidVersion(base_fixture, capsys):
    """
    Tests, that reading a config file with the wrong version will print an error.
    Expects the sdterr to contain the error level(ERROR) and the error cause.
    """
    tabs = parse_config_file(base_fixture.testdata_path / "config_file" / "wrong_version.json")
    assert tabs == []
    captured = capsys.readouterr()
    assert "ERROR" in captured.err
    assert "Failed validating" in captured.err
    assert "version" in captured.err


def testInvalidContent(base_fixture, capsys):
    """
    Tests, that reading a config file with invalid syntax will print an error.
    Expects the sdterr to contain the error level(ERROR) and the error cause.
    """
    tabs = parse_config_file(base_fixture.testdata_path / "config_file" / "invalid_syntax.json")
    assert tabs == []
    captured = capsys.readouterr()
    assert "ERROR" in captured.err
    assert "Expecting property name" in captured.err


def testWriteConfigFile(base_fixture, tmp_path):
    """
    Tests, that writing a config file from internal state is correct.
    Expects the same content, as the original file.
    """
    test_file = Path(tmp_path) / "test.json"

    tabs = parse_config_file(base_fixture.testdata_path / "app_config.json")
    write_config_file(base_fixture.testdata_path / test_file, tabs)
    with open(str(base_fixture.testdata_path / "app_config.json")) as config:
        ref_dict = json.load(config)
    with open(str(test_file)) as config:
        test_dict = json.load(config)
    assert test_dict == ref_dict
