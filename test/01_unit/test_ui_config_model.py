import sys
from distutils.file_util import copy_file
from pathlib import Path
from test.conftest import TEST_REF_OFFICIAL

from conan_app_launcher import asset_path
from conan_app_launcher.ui.modules.app_grid.model import (UiAppLinkConfig,
                                                          UiAppLinkModel)
from conans.model.ref import ConanFileReference as CFR


def test_executable_eval(base_fixture):
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

    app_link.executable = ""
    assert app_link.get_executable_path() == Path("NULL")


def test_icon_eval(base_fixture, tmp_path, qtbot):
    """
    Tests, that the icon setter works on all cases.
    Expects package relative file, config-file rel. file, automaticaly extracted file,
    and error message and default icon on no file.
    """

    # copy icons to tmp_path to fake package path
    copy_file(str(asset_path / "icons" / "icon.ico"), tmp_path)
    copy_file(str(asset_path / "icons" / "app.png"), tmp_path)

    # relative to package with // notation - migrate from old setting
    app_config = UiAppLinkConfig("AppName", icon="//icon.ico")
    app_link = UiAppLinkModel().load(app_config, None)
    app_link.set_package_info(tmp_path)  # trigger set
    assert not app_link.get_icon().isNull()
    assert str(app_link._eval_icon_path()) == str(tmp_path / "icon.ico")

    # absolute path
    app_link.icon = str(tmp_path / "icon.ico")
    assert not app_link.get_icon().isNull()
    assert str(app_link._eval_icon_path()) == str(tmp_path / "icon.ico")

    # extract icon
    app_link.icon = ""
    assert not app_link.get_icon().isNull()


def test_icon_eval_wrong_path(base_fixture, tmp_path, qtbot):
    """ Test, that a nonexistant path sets to default (check for error removed) """

    app_link = UiAppLinkModel("AppName", icon=str(Path.home() / "nonexistant.png"), executable="abc")
    assert not app_link.get_icon().isNull()
    assert str(app_link._eval_icon_path()) == str(Path.home() / "nonexistant.png")


def test_official_release(base_fixture):
    """
    Test, if an official reference in the format name/1.0.0@_/_ works correctly.
    Expects the same option name and value as given to the constructor.
    """
    conan_ref_short = str(CFR.loads(TEST_REF_OFFICIAL))
    app_config = UiAppLinkConfig("AppName", conan_ref=TEST_REF_OFFICIAL)
    app_link = UiAppLinkModel().load(app_config, None)
    assert app_link.channel == UiAppLinkModel.OFFICIAL_RELEASE
    # both formats are valid, so we accept the shortened one
    assert str(app_link.conan_file_reference) == conan_ref_short

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
    app_link.conan_ref = "example/1.1.0@_/_"
    assert str(app_link.conan_file_reference) == "example/1.1.0"
    app_link.version = "1.1.0"
    assert app_link.channel == UiAppLinkModel.OFFICIAL_RELEASE
    assert app_link.conan_file_reference.user is None
