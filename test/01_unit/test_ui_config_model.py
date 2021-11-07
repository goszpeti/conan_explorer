import platform
import sys
import tempfile
from distutils.file_util import copy_file
from pathlib import Path

from conans.model.ref import ConanFileReference as CFR
from conan_app_launcher.ui.modules.app_grid.model import UiAppLinkModel, UiAppLinkConfig
from conan_app_launcher import asset_path
from conan_app_launcher.ui.data.json_file import JsonUiConfig

TEST_REF = "zlib/1.2.11@_/_"


def test_executable_eval(base_fixture, capfd):
    """
    Tests, that the executable setter works on all cases.
    Expects correct file, error messoge on wrong file an error message on no file.
    """
    app_config = UiAppLinkConfig("AppName", executable="python")
    exe = Path(sys.executable)
    app_link = UiAppLinkModel()
    app_link.load(app_config, None)

    app_link.set_package_info(exe.parent)  # trigger set
    assert app_link.get_executable_path() == exe

    app_link.executable = "nonexistant"
    app_link.get_executable_path()
    captured = capfd.readouterr()
    assert "Can't find file" in captured.err

    app_link.executable = ""
    captured = capfd.readouterr()
    assert "No file" in captured.err


def test_icon_eval(base_fixture, ui_config_fixture, tmp_path):
    """
    Tests, that the icon setter works on all cases.
    Expects package relative file, config-file rel. file, automaticaly extracted file,
    and error message and default icon on no file.
    """

    # copy icons to tmp_path to fake package path
    copy_file(str(asset_path / "icons" / "icon.ico"), tmp_path)
    copy_file(str(asset_path / "icons" / "app.png"), tmp_path)

    # relative to package with // notation - migrate from old setting
    app_link = UiAppLinkModel("AppName", icon="//icon.ico")
    app_link.set_package_info(tmp_path)  # trigger set
    assert app_link.get_icon_path() == tmp_path / "icon.ico"
    assert app_link.icon == "./icon.ico"

    # absolute path
    app_link.icon = str(tmp_path / "icon.ico")
    assert app_link.get_icon_path() == tmp_path / "icon.ico"

    # extract icon
    app_link.icon = ""
    if platform.system() == "Windows":
        app_link.executable = sys.executable
        icon_path = Path(tempfile.gettempdir()) / "cal_icons" / (str(Path(sys.executable).name) + ".img")
        assert app_link.get_icon_path() == icon_path.resolve()
    elif platform.system() == "Linux":
        assert app_link.get_icon_path() == asset_path / "icons" / "app.png"


def test_icon_eval_wrong_path(capfd, base_fixture, tmp_path):
    """ Test, that a nonexistant path returns an error """

    app_link = UiAppLinkModel("AppName", icon=str(Path.home() / "nonexistant.png"), executable="abc")
    app_link.get_icon_path() # eval
    # wrong path
    captured = capfd.readouterr()
    assert "Can't find icon" in captured.err
    assert app_link.get_icon_path() == asset_path / "icons" / "app.png"


def test_official_release(base_fixture):
    """
    Test, if an official reference in the format name/1.0.0@_/_ works correctly.
    Expects the same option name and value as given to the constructor.
    """
    conan_ref_short = str(CFR.loads(TEST_REF))
    app_link = UiAppLinkModel("AppName", conan_ref=CFR.loads(TEST_REF))
    assert app_link.channel == UiAppLinkModel.OFFICIAL_RELEASE
    # both formats are valid, so we accept the shortened one
    assert str(app_link.conan_ref) == conan_ref_short

    # check, that setting channel works too
    app_link.channel = "stable"
    assert str(app_link.conan_ref) == conan_ref_short
    app_link.channel = UiAppLinkModel.OFFICIAL_RELEASE
    assert app_link.channel == UiAppLinkModel.OFFICIAL_RELEASE

    # check, that changing back to normal user works
    app_link.user = "user"
    assert app_link.user == "user"
    assert app_link.channel == "NA"


    # check, that changing the version does not invalidate the channel or user
    app_link.conan_ref = CFR.loads("zlib/1.2.12@_/_")
    assert str(app_link.conan_ref) == "zlib/1.2.12"
    app_link.version = "1.0.0"
    assert app_link.channel == UiAppLinkModel.OFFICIAL_RELEASE
    assert app_link.conan_ref.user is None
