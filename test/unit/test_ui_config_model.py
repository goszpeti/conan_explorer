import json
import os
import platform
import sys
import tempfile
from distutils.file_util import copy_file
from pathlib import Path

from conan_app_launcher.data.ui_config.json_file import JsonUiConfig

def testExecutableEval(base_fixture, capfd):
    """
    Tests, that the executable setter works on all cases.
    Expects correct file, error messoge on wrong file an error message on no file.
    """
    tabs = JsonUiConfig(base_fixture.testdata_path / "nofile.json").load()
    app_data = {"name": "AppName", "executable": "python"}
    exe = Path(sys.executable)
    app_link = AppConfigEntry(app_data)

    app_link.set_package_info(exe.parent)  # trigger set
    assert app_link.executable == exe

    app_link.executable = "nonexistant"
    captured = capfd.readouterr()
    assert "ERROR" in captured.err
    assert "Can't find file" in captured.err

    app_link.executable = ""
    captured = capfd.readouterr()
    assert "ERROR" in captured.err
    assert "No file" in captured.err


def testIconEval(base_fixture, ui_config_fixture, tmp_path):
    """
    Tests, that the icon setter works on all cases.
    Expects package relative file, config-file rel. file, automaticaly extracted file,
    and error message and default icon on no file.
    """

    tabs = JsonUiConfig(base_fixture.testdata_path / "nofile.json").load()
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
    rel_path = "icons/../icons"
    new_ico_path = ui_config_fixture.parent / rel_path
    os.makedirs(str(new_ico_path), exist_ok=True)
    copy_file(app.asset_path / "icons" / "icon.ico", new_ico_path)
    app_link.icon = rel_path + "/icon.ico"
    assert app_link.icon == (new_ico_path / "icon.ico").resolve()

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


def testIconEvalWrongPath(capfd, base_fixture, tmp_path):
    """ Test, that a nonexistant path returns an error """
    app_data = {"conan_ref": "zlib/1.2.11@conan/stable", "name": "AppName",
                "icon": str(Path.home() / "nonexistant.png"), "executable": sys.executable}
    app_link = AppConfigEntry(app_data)

    # wrong path
    captured = capfd.readouterr()
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


def testOfficialRelease(base_fixture):
    """
    Test, if an official reference in the format name/1.0.0@_/_ works correctly.
    Expects the same option name and value as given to the constructor.
    """
    app_data = {"name": "AppName", "conan_ref": "zlib/1.2.11@_/_"}
    app_link = AppConfigEntry(app_data)
    assert app_link.channel == AppConfigEntry.OFFICIAL_RELEASE
    assert str(app_link.conan_ref) == "zlib/1.2.11"  # both formats are valid, so we accept the shortened one

    # check, that setting channel works too
    app_link.channel = "stable"
    app_link.channel = AppConfigEntry.OFFICIAL_RELEASE
    assert app_link.channel == AppConfigEntry.OFFICIAL_RELEASE

    # check, that changing the version does not invalidate the channel or user
    app_link.conan_ref = "zlib/1.2.11@_/_"
    assert str(app_link.conan_ref) == "zlib/1.2.11"
    app_link.version = "1.0.0"
    assert app_link.channel == AppConfigEntry.OFFICIAL_RELEASE
    assert app_link.conan_ref.user is None
