import json
import sys
import tempfile
import platform
from distutils.file_util import copy_file
from pathlib import Path

import conan_app_launcher as app
from conan_app_launcher.components import parse_config_file, write_config_file, AppConfigEntry


def testCorrectFile(base_fixture, settings_fixture):
    """
    Tests reading a correct config json with 2 tabs.
    Expects the same values as in the file.
    """
    tabs = parse_config_file(settings_fixture)
    assert tabs[0].name == "Basics"
    tab0_entries = tabs[0].get_app_entries()
    assert str(tab0_entries[0].conan_ref) == "m4_installer/1.4.18@bincrafters/stable"
    assert tab0_entries[0].app_data.get("executable") == "bin/m4"
    assert tab0_entries[0].app_data.get("icon") == "NonExistantIcon.png"
    assert tab0_entries[0].name == "App1 with spaces"
    assert tab0_entries[0].is_console_application
    assert tab0_entries[0].args == "-n name"

    assert str(tab0_entries[1].conan_ref) == "zlib/1.2.11@conan/stable"
    assert tab0_entries[1].app_data.get("executable") == "bin/app2"
    assert tab0_entries[1].app_data.get("icon") == "icon.ico"
    assert tab0_entries[1].name == "App2"
    assert not tab0_entries[1].is_console_application  # default
    assert tab0_entries[1].args == ""
    assert tab0_entries[1].conan_options == {"shared": "True"}

    assert tabs[1].name == "Extra"
    tab1_entries = tabs[1].get_app_entries()
    assert str(tab1_entries[0].conan_ref) == "app2/1.0.0@user/stable"
    assert tab1_entries[0].app_data["executable"] == "bin/app2.exe"
    assert tab1_entries[0].app_data.get("icon") == "//myicon.png"
    assert tab1_entries[0].name == "App2"


def testUpdate(base_fixture, settings_fixture):
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
    assert read_obj.get("version") == "0.3.1"  # last version
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


def testWriteConfigFile(base_fixture, settings_fixture, tmp_path):
    """
    Tests, that writing a config file from internal state is correct.
    Expects the same content, as the original file.
    """
    test_file = Path(tmp_path) / "test.json"

    tabs = parse_config_file(settings_fixture)
    write_config_file(base_fixture.testdata_path / test_file, tabs)
    with open(str(settings_fixture)) as config:
        ref_dict = json.load(config)
    with open(str(test_file)) as config:
        test_dict = json.load(config)
    assert test_dict == ref_dict


def testExecutableEval(base_fixture, capsys):
    """
    Tests, that the executable setter works on all cases.
    Expects correct file, error messoge on wrong file an error message on no file.
    """
    app_data = {"name": "AppName", "executable": "python"}
    exe = Path(sys.executable)
    app_link = AppConfigEntry(app_data)

    app_link.set_package_info(exe.parent)  # trigger set
    assert app_link.executable == exe

    app_link.executable = "nonexistant"
    captured = capsys.readouterr()
    assert "ERROR" in captured.err
    assert "Can't find file" in captured.err

    app_link.executable = ""
    captured = capsys.readouterr()
    assert "ERROR" in captured.err
    assert "No file" in captured.err


def testIconEval(base_fixture, settings_fixture, tmp_path):
    """
    Tests, that the icon setter works on all cases.
    Expects package relative file, config-file rel. file, automaticaly extracted file,
    and error message and default icon on no file.
    """

    # copy icons to tmp_path to fake package path
    copy_file(app.asset_path / "icons" / "icon.ico", tmp_path)
    copy_file(app.asset_path / "icons" / "app.png", tmp_path)

    # relative to package with // notation
    app_data = {"name": "AppName", "icon": "//icon.ico", "executable": sys.executable}
    app_link = AppConfigEntry(app_data)
    app_link.set_package_info(tmp_path)  # trigger set
    assert app_link.icon == tmp_path / "icon.ico"
    assert app_link.app_data["icon"] == "//icon.ico"

    # relative to config file
    app_link.icon = "../../src/conan_app_launcher/assets/icons/icon.ico"
    assert app_link.icon == app.base_path / "assets" / "icons" / "icon.ico"

    # absolute path
    app_link.icon = str(tmp_path / "icon.ico")
    assert app_link.icon == tmp_path / "icon.ico"

    # extract icon
    app_link.icon = ""
    if platform.system() == "Windows":
        icon_path = Path(tempfile.gettempdir()) / (str(Path(sys.executable).name) + ".img")
        assert app_link.icon == icon_path.resolve()
    elif platform.system() == "Linux":
        assert app_link.icon == app.asset_path / "icons" / "app.png"


def testIconEvalWrongPath(capsys, base_fixture, tmp_path):
    """ Test, that a nonexistant path returns an error """
    app_data = {"conan_ref": "zlib/1.2.11@conan/stable", "name": "AppName",
                "icon": str(Path.home() / "nonexistant.png"), "executable": sys.executable}
    app_link = AppConfigEntry(app_data)

    # wrong path
    captured = capsys.readouterr()
    assert "ERROR" in captured.err
    assert "Can't find icon" in captured.err
    assert app_link.icon == app.asset_path / "icons" / "app.png"


def testOptionsEval(base_fixture):
    """
    Test, if extraction of option works correctly.
    Expects the same option name and value as given to the constructor.
    """
    app_data = {"name": "AppName", "executable": "python",
                "conan_options": [{"name": "myopt", "value": "myvalue"}]}
    app_link = AppConfigEntry(app_data)

    # one value
    assert app_link.conan_options == {"myopt": "myvalue"}

    # multi value
    app_link.conan_options = {"myopt1": "myvalue1", "myopt2": "myvalue2"}
    assert app_link.app_data["conan_options"] == [{"name": "myopt1", "value": "myvalue1"},
                                                  {"name": "myopt2", "value": "myvalue2"}]
    assert app_link.conan_options == {"myopt1": "myvalue1", "myopt2": "myvalue2"}

    # empty value
    app_link.conan_options = []
    assert app_link.conan_options == {}
