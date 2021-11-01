"""
These test starts the application but not with the main function,
so the qtbot is usable to inspect gui objects.
"""

import os
import platform
import tempfile
import time
from pathlib import Path
from shutil import rmtree

import conan_app_launcher as app
from conan_app_launcher.__main__ import load_base_components
from conan_app_launcher.base import Logger
from conan_app_launcher.components import ConanApi
from conan_app_launcher.settings import *
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.app_grid.tab_app_grid import TabAppGrid
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt


def testStartupNoExistingConfig(base_fixture, settings_fixture, qtbot):
    # no settings entry
    app.active_settings.set(LAST_CONFIG_FILE, "")
    # delete default file, in case it exists and has content
    default_config_file_path = Path.home() / app.DEFAULT_GRID_CONFIG_FILE_NAME
    if default_config_file_path.exists():
        os.remove(default_config_file_path)
    # init config file and parse
    load_base_components(app.active_settings)

    main_gui = main_window.MainUi()
    qtbot.addWidget(main_gui)
    main_gui.start_app_grid()

    main_gui.show()
    qtbot.waitExposed(main_gui, timeout=3000)
    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        assert tab.config_data.name == "New Tab"
        for test_app in tab.app_links:
            assert test_app.config_data.name == "My App Link"
    Logger.remove_qt_logger()

def testStartupWithExistingConfigAndOpenMenu(base_fixture, settings_fixture, qtbot):
    """
    Test, that loading a config file and opening the about menu, and clicking on OK
    The about dialog showing is expected.
    """
    main_gui = main_window.MainUi()
    qtbot.addWidget(main_gui)
    main_gui.start_app_grid()

    main_gui.show()
    qtbot.waitExposed(main_gui, timeout=3000)
    main_gui.ui.menu_about_action.trigger()
    time.sleep(3)
    assert main_gui._about_dialog.isEnabled()
    qtbot.mouseClick(main_gui._about_dialog._button_box.buttons()[0], Qt.LeftButton)
    Logger.remove_qt_logger()


def testSelectConfigFileDialog(base_fixture, settings_fixture, qtbot, mocker):
    """
    Test, that clicking on on open config file and selecting a file writes it back to settings.
    Same file as selected expected in settings.
    """

    load_base_components(app.active_settings)

    main_gui = main_window.MainUi()
    main_gui.show()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    selection = str(Path.home() / "new_config.json")
    mocker.patch.object(QtWidgets.QFileDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[selection])

    main_gui.ui.menu_open_config_file.trigger()
    time.sleep(3)
    assert app.active_settings.get(LAST_CONFIG_FILE) == selection
    app.conan_worker.finish_working(3)
    Logger.remove_qt_logger()


def testConanCacheWithDialog(base_fixture, settings_fixture, qtbot, mocker):
    """
    Test, that clicking on on open config file and selecting a file writes it back to settings.
    Same file as selected expected in settings.
    """
    ### TEST SETUP

    if not platform.system() == "Windows": # Feature only "available" on Windows
        return
    from conans.util.windows import CONAN_REAL_PATH
    conan = ConanApi()

    # Set up broken packages to have something to cleanup
    # in short path - edit .real_path
    ref = "example/1.0.0@user/testing"
    try:
        conan.conan.remove(ref, force=True)  # clean up for multiple runs
    except Exception:
        pass
    # shortpaths is enbaled in conanfile
    conanfile = str(base_fixture.testdata_path / "conan" / "conanfile.py")
    os.system(f"conan create {conanfile} user/testing")
    pkg = conan.find_best_local_package(ConanFileReference.loads(ref))
    assert pkg["id"]
    pkg_dir_to_delete = conan.get_package_folder(ConanFileReference.loads(ref), pkg["id"])

    real_path_file = pkg_dir_to_delete / ".." / CONAN_REAL_PATH
    with open(str(real_path_file), "r+") as fp:
        line = fp.readline()
        line = line + "3"  # add bogus number to path
        fp.seek(0)
        fp.write(line)

    # in cache - delete Short path, so that cache folder is orphaned
    ref = "example/1.0.0@user/orphan"
    try:
        conan.conan.remove(ref, force=True)  # clean up for multiple runs
    except Exception:
        pass
    os.system(f"conan create {conanfile} user/orphan")

    exp_folder = conan.get_export_folder(ConanFileReference.loads(ref))
    conan = ConanApi()
    pkg = conan.find_best_local_package(ConanFileReference.loads(ref))
    pkg_cache_folder = os.path.abspath(os.path.join(exp_folder, "..", "package", pkg["id"]))
    pkg_dir = conan.get_package_folder(ConanFileReference.loads(ref), pkg["id"])
    rmtree(pkg_dir)

    paths_to_delete = conan.get_cleanup_cache_paths()
    assert pkg_cache_folder in paths_to_delete
    assert str(pkg_dir_to_delete.parent) in paths_to_delete

    ### TEST ACTION

    main_gui = main_window.MainUi()
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)

    main_gui.ui.menu_cleanup_cache.trigger()
    time.sleep(3)

    ### TEST EVALUATION

    assert not os.path.exists(pkg_cache_folder)
    assert not pkg_dir_to_delete.parent.exists()
    Logger.remove_qt_logger()

def testTabsCleanupOnLoadConfigFile(base_fixture, settings_fixture, qtbot):
    """
    Test, if the previously loaded tabs are deleted, when a new file is loaded
    The same tab number ist expected, as before.
    """
    load_base_components(app.active_settings)

    main_gui = main_window.MainUi()
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs_num = 2  # two tabs in this file
    assert main_gui.ui.tab_bar.count() == tabs_num
    time.sleep(5)

    app.conan_worker.finish_working(10)

    main_gui._app_grid.re_init() # re-init with same file
    time.sleep(5)

    assert main_gui.ui.tab_bar.count() == tabs_num
    app.conan_worker.finish_working(10)


def testViewMenuOptions(base_fixture, settings_fixture, qtbot):
    """
    Test the view menu entries.
    Check, that activating the entry set the hide flag is set on the widget.
    """
    # deactivate all settings
    app.active_settings.set(DISPLAY_APP_CHANNELS, False)
    app.active_settings.set(DISPLAY_APP_VERSIONS, False)
    app.active_settings.set(DISPLAY_APP_USERS, False)

    load_base_components(app.active_settings)
    main_gui = main_window.MainUi()
    app.main_window = main_gui  # needed for signal access
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    # assert default state
    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        for test_app in tab.app_links:
            assert test_app._app_version_cbox.isHidden()
            assert test_app._app_user_cbox.isHidden()
            assert test_app._app_channel_cbox.isHidden()

    # click VERSIONS
    main_gui.ui.menu_toggle_display_versions.trigger()
    time.sleep(1)
    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        for test_app in tab.app_links:
            assert not test_app._app_version_cbox.isHidden()
            assert test_app._app_user_cbox.isHidden()
            assert test_app._app_channel_cbox.isHidden()

    # check settings
    assert app.active_settings.get(DISPLAY_APP_VERSIONS)

    # reload settings and check again
    app.active_settings._read_ini()
    assert app.active_settings.get(DISPLAY_APP_VERSIONS)

    # click CHANNELS
    main_gui.ui.menu_toggle_display_channels.trigger()
    time.sleep(1)
    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        for test_app in tab.app_links:
            assert not test_app._app_version_cbox.isHidden()
            assert test_app._app_user_cbox.isHidden()
            assert not test_app._app_channel_cbox.isHidden()

    # click USERS
    main_gui.ui.menu_toggle_display_users.trigger()
    time.sleep(1)
    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        for test_app in tab.app_links:
            assert not test_app._app_version_cbox.isHidden()
            assert not test_app._app_user_cbox.isHidden()
            assert not test_app._app_channel_cbox.isHidden()

    # click again
    main_gui.ui.menu_toggle_display_versions.trigger()
    main_gui.ui.menu_toggle_display_channels.trigger()
    main_gui.ui.menu_toggle_display_users.trigger()
    time.sleep(1)

    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        for test_app in tab.app_links:
            assert test_app._app_version_cbox.isHidden()
            assert test_app._app_user_cbox.isHidden()
            assert test_app._app_channel_cbox.isHidden()


    app.conan_worker.finish_working(10)
    Logger.remove_qt_logger()


def testIconUpdateFromExecutable():
    """
    Test, that an extracted icon from an exe is displayed after loaded and then retrived from cache.
    Check, that the icon has the temp path. Use python executable for testing.
    """
    # TODO
