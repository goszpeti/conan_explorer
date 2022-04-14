"""
These test starts the application but not with the main function,
so the qtbot is usable to inspect gui objects.
"""

import os
import platform
import time
from pathlib import Path
from shutil import rmtree

from conan_app_launcher import DEFAULT_UI_CFG_FILE_NAME, app, user_save_path
from conan_app_launcher.core import ConanApi
from conan_app_launcher.core.conan import ConanCleanup
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.settings import *
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.widgets import AnimatedToggle
from conan_app_launcher.ui.views.about_page import AboutPage
from conan_app_launcher.ui.views.app_grid.tab import TabGrid

from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt


def test_startup_no_config(base_fixture, ui_config_fixture, qtbot):
    """ Test, that when no condig file is set,
    a new tab with a new default app is automatically added."""
    from pytestqt.plugin import _qapp_instance

    # TEST SETUP
    # no settings entry
    app.active_settings.set(LAST_CONFIG_FILE, "")
    # delete default file, in case it exists and has content
    default_config_file_path = user_save_path / DEFAULT_UI_CFG_FILE_NAME
    if default_config_file_path.exists():
        os.remove(default_config_file_path)

    # TEST ACTION
    # init config file and parse
    main_gui = main_window.MainWindow(_qapp_instance)
    qtbot.addWidget(main_gui)
    main_gui.load()
    main_gui.show()
    qtbot.waitExposed(main_gui, timeout=3000)

    # TEST EVALUATION
    for tab in main_gui.app_grid.tab_widget.findChildren(TabGrid):
        assert tab.model.name == "New Tab"
        for test_app in tab.app_links:
            assert test_app.model.name == "New App"
    Logger.remove_qt_logger()


def test_startup_with_existing_config_and_open_menu(base_fixture, ui_config_fixture, qtbot):
    """
    Test, that loading a config file and opening the about menu, and clicking on OK
    The about dialog showing is expected.
    """
    from pytestqt.plugin import _qapp_instance

    # TEST SETUP
    main_gui = main_window.MainWindow(_qapp_instance)
    qtbot.addWidget(main_gui)
    main_gui.load()

    main_gui.show()
    qtbot.waitExposed(main_gui, timeout=3000)

    # TEST ACTION
    main_gui.page_widgets.get_button_by_type(AboutPage).click()
    time.sleep(3)

    # TEST EVALUATION
    assert main_gui.about_page.isVisible()

    Logger.remove_qt_logger()


def test_select_config_file_dialog(base_fixture, ui_config_fixture, qtbot, mocker):
    """
    Test, that clicking on on open config file and selecting a file writes it back to settings.
    Same file as selected expected in settings.
    """
    from pytestqt.plugin import _qapp_instance

    # TEST SETUP

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    # TEST ACTION
    selection = str(Path.home() / "new_config.json")
    mocker.patch.object(QtWidgets.QFileDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[selection])
    main_gui.page_widgets.get_side_menu_by_type(type(main_gui.app_grid)).get_menu_entry_by_name("Open Layout File").click()

    # TEST EVALUATION
    time.sleep(3)
    assert app.active_settings.get(LAST_CONFIG_FILE) == selection
    app.conan_worker.finish_working(3)
    Logger.remove_qt_logger()


def test_conan_cache_with_dialog(base_fixture, ui_config_fixture, qtbot, mocker):
    """
    Test, that clicking on on open config file and selecting a file writes it back to settings.
    Same file as selected expected in settings.
    """
    # TEST SETUP

    if not platform.system() == "Windows":  # Feature only "available" on Windows
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
    # shortpaths is enabled in conanfile
    conanfile = str(base_fixture.testdata_path / "conan" / "conanfile.py")
    os.system(f"conan create {conanfile} {ref}")
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
    os.system(f"conan create {conanfile} {ref}")

    exp_folder = conan.get_export_folder(ConanFileReference.loads(ref))
    conan = ConanApi()
    pkg = conan.find_best_local_package(ConanFileReference.loads(ref))
    pkg_cache_folder = os.path.abspath(os.path.join(exp_folder, "..", "package", pkg["id"]))
    pkg_dir = conan.get_package_folder(ConanFileReference.loads(ref), pkg["id"])
    rmtree(pkg_dir)

    paths_to_delete = ConanCleanup(conan).get_cleanup_cache_paths()
    assert pkg_cache_folder in paths_to_delete
    assert str(pkg_dir_to_delete.parent) in paths_to_delete

    # TEST ACTION
    from pytestqt.plugin import _qapp_instance
    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)

    button: QtWidgets.QPushButton = main_gui.main_general_settings_menu.get_menu_entry_by_name("Clean Conan Cache")
    button.click()
    time.sleep(3)

    # TEST EVALUATION
    assert not os.path.exists(pkg_cache_folder)
    assert not pkg_dir_to_delete.parent.exists()
    Logger.remove_qt_logger()


def test_tabs_cleanup_on_load_config_file(base_fixture, ui_config_fixture, qtbot):
    """
    Test, if the previously loaded tabs are deleted, when a new file is loaded
    The same tab number ist expected, as before.
    """
    from pytestqt.plugin import _qapp_instance

    # TEST SETUP
    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs_num = 2  # two tabs in this file
    assert main_gui.app_grid.tab_widget.tabBar().count() == tabs_num
    time.sleep(5)

    app.conan_worker.finish_working(10)

    main_gui.app_grid.re_init(main_gui.model.app_grid)  # re-init with same file

    # TEST EVALUATION
    time.sleep(5)
    assert main_gui.app_grid.tab_widget.tabBar().count() == tabs_num


def test_view_menu_options(base_fixture, ui_config_fixture, qtbot):
    """
    Test the view menu entries.
    Check, that activating the entry set the hide flag is set on the widget.
    """
    from pytestqt.plugin import _qapp_instance

    # deactivate all settings
    app.active_settings.set(DISPLAY_APP_CHANNELS, False)
    app.active_settings.set(DISPLAY_APP_VERSIONS, False)
    app.active_settings.set(DISPLAY_APP_USERS, False)

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    # TEST ACTION and EVALUATION
    # assert default state
    for tab in main_gui.app_grid.tab_widget.tabBar().findChildren(TabGrid):
        for test_app in tab.app_links:
            assert test_app._app_version_cbox.isHidden()
            assert test_app._app_user_cbox.isHidden()
            assert test_app._app_channel_cbox.isHidden()

    # click VERSIONS
    menu_entry = main_gui.page_widgets.get_side_menu_by_type(
        type(main_gui.app_grid))
    assert menu_entry
    version_toggle: AnimatedToggle = menu_entry.get_menu_entry_by_name("show_version_widget")
    version_toggle.setChecked(True)
    time.sleep(1)
    for tab in main_gui.app_grid.tab_widget.tabBar().findChildren(TabGrid):
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
    channel_toggle: AnimatedToggle = menu_entry.get_menu_entry_by_name("show_channel_widget")
    channel_toggle.setChecked(True)
    time.sleep(1)
    for tab in main_gui.app_grid.tab_widget.tabBar().findChildren(TabGrid):
        for test_app in tab.app_links:
            assert not test_app._app_version_cbox.isHidden()
            assert test_app._app_user_cbox.isHidden()
            assert not test_app._app_channel_cbox.isHidden()

    # click USERS
    user_toggle: AnimatedToggle = menu_entry.get_menu_entry_by_name("show_user_widget")
    user_toggle.setChecked(True)
    time.sleep(1)
    for tab in main_gui.app_grid.tab_widget.tabBar().findChildren(TabGrid):
        for test_app in tab.app_links:
            assert not test_app._app_version_cbox.isHidden()
            assert not test_app._app_user_cbox.isHidden()
            assert not test_app._app_channel_cbox.isHidden()

    # click again
    version_toggle.setChecked(False)
    channel_toggle.setChecked(False)
    user_toggle.setChecked(False)
    time.sleep(1)

    for tab in main_gui.app_grid.tab_widget.tabBar().findChildren(TabGrid):
        for test_app in tab.app_links:
            assert test_app._app_version_cbox.isHidden()
            assert test_app._app_user_cbox.isHidden()
            assert test_app._app_channel_cbox.isHidden()

    app.conan_worker.finish_working(10)
    Logger.remove_qt_logger()
