"""
This test starts the application.
It is called z_integration, so that it launches last.
"""

import os
import tempfile
import time
import platform
from pathlib import Path
from shutil import rmtree


from conans.model.ref import ConanFileReference

import conan_app_launcher as app
from conan_app_launcher.base import Logger
from conan_app_launcher.components import ConanApi
from conan_app_launcher.settings import *
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.tab_app_grid import TabAppGrid
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt


def testStartupWithExistingConfigAndOpenMenu(base_fixture, qtbot):
    """
    Test, loading a config file and opening the about menu, and clicking on OK
    The about dialog showing is expected.
    """
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    settings = Settings(ini_file=Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "app_config.json"
    settings.set(LAST_CONFIG_FILE, str(config_file_path))

    main_gui = main_window.MainUi(settings)
    qtbot.addWidget(main_gui)
    main_gui.show()
    qtbot.waitExposed(main_gui, 3000)
    main_gui._ui.menu_about_action.trigger()
    time.sleep(3)
    assert main_gui._about_dialog.isEnabled()
    qtbot.mouseClick(main_gui._about_dialog._button_box.buttons()[0], Qt.LeftButton)
    app.conan_worker.finish_working(3)
    Logger.remove_qt_logger()


def testSelectConfigFileDialog(base_fixture, qtbot, mocker):
    """
    Test, that clicking on on open config file and selecting a file writes it back to settings.
    Same file as selected expected in settings.
    """
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    settings = Settings(ini_file=Path(temp_ini_path))

    main_gui = main_window.MainUi(settings)
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, 3000)
    selection = str(Path.home() / "new_config.json")
    mocker.patch.object(QtWidgets.QFileDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[selection])

    main_gui._ui.menu_open_config_file.trigger()
    time.sleep(3)
    assert settings.get(LAST_CONFIG_FILE) == selection
    app.conan_worker.finish_working(3)
    Logger.remove_qt_logger()


def testConanCacheWithDialog(base_fixture, qtbot, mocker):
    """
    Test, that clicking on on open config file and selecting a file writes it back to settings.
    Same file as selected expected in settings.
    """
    if not platform.system() == "Windows":
        return
    from conans.util.windows import CONAN_REAL_PATH
    conan = ConanApi()

    # Set up broken packages to have something to cleanup
    # in short path - edit .real_path
    ref = "boost_base/1.69.0@bincrafters/stable"
    try:
        conan.conan.remove(ref, force=True)  # clean up for multiple runs
    except:
        pass
    os.system(f"conan install {ref}")
    pkg = conan.get_local_package(ConanFileReference.loads(ref))
    pkg_dir_to_delete = conan.get_package_folder(ConanFileReference.loads(ref), pkg)

    real_path_file = pkg_dir_to_delete / ".." / CONAN_REAL_PATH
    with open(str(real_path_file), "r+") as fp:
        line = fp.readline()
        line = line + "3"  # add bogus number to path
        fp.seek(0)
        fp.write(line)

    # in cache - delete Short path, so that cache folder is oprhaned
    ref = "boost_config/1.69.0@bincrafters/stable"
    try:
        conan.conan.remove(ref, force=True)  # clean up for multiple runs
    except:
        pass
    os.system(f"conan install {ref}")

    exp_folder = conan.get_export_folder(ConanFileReference.loads(ref))
    conan = ConanApi()
    pkg = conan.get_local_package(ConanFileReference.loads(ref))
    pkg_cache_folder = os.path.abspath(os.path.join(exp_folder, "..", "package", pkg["id"]))
    pkg_dir = conan.get_package_folder(ConanFileReference.loads(ref), pkg)
    rmtree(pkg_dir)

    paths_to_delete = conan.get_cleanup_cache_paths()
    assert pkg_cache_folder in paths_to_delete
    assert str(pkg_dir_to_delete.parent) in paths_to_delete

    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    settings = Settings(ini_file=Path(temp_ini_path))

    main_gui = main_window.MainUi(settings)
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, 3000)
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)

    main_gui._ui.menu_cleanup_cache.trigger()
    time.sleep(3)
    assert not os.path.exists(pkg_cache_folder)
    assert not pkg_dir_to_delete.parent.exists()
    app.conan_worker.finish_working()
    Logger.remove_qt_logger()


def testMultipleAppsUngreying(base_fixture, qtbot):
    """
    Test, that apps ungrey, after their packages are loaded.
    Set greyed attribute of the underlying app button expected.
    """
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    settings = Settings(ini_file=Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "config_file/multiple_apps_same_package.json"
    settings.set(LAST_CONFIG_FILE, str(config_file_path))

    main_gui = main_window.MainUi(settings)
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, 3000)

    # wait for all tasks to finish
    app.conan_worker.finish_working(10)
    main_gui.update_layout()  # TODO: signal does not emit in test, must call manually

    # check app icons first two should be ungreyed, third is invalid->not ungreying
    for tab in main_gui._ui.tabs.findChildren(TabAppGrid):
        for test_app in tab.apps:
            if test_app._app_info.name in ["App1 with spaces", "App1 new"]:
                assert not test_app._app_button._greyed_out
            elif test_app._app_info.name in ["App1 wrong path", "App2"]:
                assert test_app._app_button._greyed_out


def testTabsCleanupOnLoadConfigFile(base_fixture, qtbot):
    """
    Test, if the previously loaded tabs are deleted, when a new file is loaded
    The same tab number ist expected, as before.
    """
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    settings = Settings(ini_file=Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "app_config.json"
    settings.set(LAST_CONFIG_FILE, str(config_file_path))

    main_gui = main_window.MainUi(settings)
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, 3000)

    tabs_num = 2  # two tabs in this file
    assert main_gui._ui.tabs.count() == tabs_num
    time.sleep(5)

    app.conan_worker.finish_working(10)

    main_gui._re_init()  # re-init with same file
    time.sleep(5)

    assert main_gui._ui.tabs.count() == tabs_num
    app.conan_worker.finish_working(10)


def testViewMenuOptions(base_fixture, qtbot):
    """
    Test the view menu entries.
    Check, that activating the entry set the hide flag is set on the widget.
    """
    temp_ini_path = os.path.join(tempfile.gettempdir(), "config.ini")

    settings = Settings(ini_file=Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "app_config.json"
    settings.set(LAST_CONFIG_FILE, str(config_file_path))

    main_gui = main_window.MainUi(settings)
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, 3000)

    time.sleep(5)
   # assert default state
    for tab in main_gui._ui.tabs.findChildren(TabAppGrid):
        for test_app in tab.apps:
            assert not test_app._app_version_cbox.isHidden()
            assert not test_app._app_channel_cbox.isHidden()

    # click and assert
    main_gui._ui.menu_set_display_versions.trigger()
    for tab in main_gui._ui.tabs.findChildren(TabAppGrid):
        for test_app in tab.apps:
            assert test_app._app_version_cbox.isHidden()
            assert not test_app._app_channel_cbox.isHidden()
    main_gui._ui.menu_set_display_channels.trigger()
    for tab in main_gui._ui.tabs.findChildren(TabAppGrid):
        for test_app in tab.apps:
            assert test_app._app_version_cbox.isHidden()
            assert test_app._app_channel_cbox.isHidden()
    # click again
    main_gui._ui.menu_set_display_versions.trigger()
    main_gui._ui.menu_set_display_channels.trigger()
    for tab in main_gui._ui.tabs.findChildren(TabAppGrid):
        for test_app in tab.apps:
            assert not test_app._app_version_cbox.isHidden()
            assert not test_app._app_channel_cbox.isHidden()

    app.conan_worker.finish_working(10)
    Logger.remove_qt_logger()


def testIconUpdateFromExecutable():
    """
    Test, that an extracted icon from an exe is displayed after loaded and then retrived from cache.
    Check, that the icon has the temp path.
    """
    # TODO
