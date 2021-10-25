"""
These test starts the application but not with the main function,
so the qtbot is usable to inspect gui objects.
"""

import os
import tempfile
import time
import platform
from pathlib import Path
from shutil import rmtree


from conans.model.ref import ConanFileReference

from conan_app_launcher.main import load_base_components
import conan_app_launcher as app
from conan_app_launcher.base import Logger
from conan_app_launcher.components import ConanApi, config_file
from conan_app_launcher.settings import *
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.app_grid.app_link import AppLink, OFFICIAL_RELEASE_DISP_NAME

from conan_app_launcher.ui.app_grid.tab_app_grid import TabAppGrid
from conan_app_launcher.components import AppConfigEntry
from conan_app_launcher.ui.app_grid.app_edit_dialog import EditAppDialog

from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt


def testStartupNoExistingConfig(base_fixture, settings_fixture, qtbot):
    # no settings entry
    app.settings.set(LAST_CONFIG_FILE, "")
    # delete default file, in case it exists and has content
    default_config_file_path = Path.home() / app.DEFAULT_GRID_CONFIG_FILE_NAME
    if default_config_file_path.exists():
        os.remove(default_config_file_path)
    # init config file and parse
    load_base_components(app.settings)

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
    Test, loading a config file and opening the about menu, and clicking on OK
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

    load_base_components(app.settings)

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
    assert app.settings.get(LAST_CONFIG_FILE) == selection
    app.conan_worker.finish_working(3)
    Logger.remove_qt_logger()


def testConanCacheWithDialog(base_fixture, settings_fixture, qtbot, mocker):
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
    ref = "example/1.0.0@user/testing"
    try:
        conan.conan.remove(ref, force=True)  # clean up for multiple runs
    except:
        pass
    conanfile = str(base_fixture.testdata_path / "conan" / "conanfile.py")
    os.system(f"conan create {conanfile} user/testing")
    pkg = conan.find_best_local_package(ConanFileReference.loads(ref))
    pkg_dir_to_delete = conan.get_package_folder(ConanFileReference.loads(ref), pkg)

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
    except:
        pass
    os.system(f"conan create {conanfile} user/orphan")

    exp_folder = conan.get_export_folder(ConanFileReference.loads(ref))
    conan = ConanApi()
    pkg = conan.find_best_local_package(ConanFileReference.loads(ref))
    pkg_cache_folder = os.path.abspath(os.path.join(exp_folder, "..", "package", pkg["id"]))
    pkg_dir = conan.get_package_folder(ConanFileReference.loads(ref), pkg)
    rmtree(pkg_dir)

    paths_to_delete = conan.get_cleanup_cache_paths()
    assert pkg_cache_folder in paths_to_delete
    assert str(pkg_dir_to_delete.parent) in paths_to_delete

    main_gui = main_window.MainUi()
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)

    main_gui.ui.menu_cleanup_cache.trigger()
    time.sleep(3)
    assert not os.path.exists(pkg_cache_folder)
    assert not pkg_dir_to_delete.parent.exists()
    Logger.remove_qt_logger()


def testMultipleAppsUngreying(base_fixture, qtbot):
    """
    Test, that apps ungrey, after their packages are loaded.
    Set greyed attribute of the underlying app button expected.
    """
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    app.settings = Settings(ini_file=Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "config_file/multiple_apps_same_package.json"
    app.settings.set(LAST_CONFIG_FILE, str(config_file_path))

    load_base_components(app.settings)

    main_gui = main_window.MainUi()
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    # wait for all tasks to finish
    app.conan_worker.finish_working(10)

    # check app icons first two should be ungreyed, third is invalid->not ungreying
    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        for test_app in tab.app_links:
            test_app.update_with_conan_info()  # signal is not emmited with qt bot, must call manually

            if test_app.config_data.name in ["App1 with spaces", "App1 new"]:
                assert not test_app._app_button._greyed_out
            elif test_app.config_data.name in ["App1 wrong path", "App2"]:
                assert test_app._app_button._greyed_out


def testTabsCleanupOnLoadConfigFile(base_fixture, settings_fixture, qtbot):
    """
    Test, if the previously loaded tabs are deleted, when a new file is loaded
    The same tab number ist expected, as before.
    """
    load_base_components(app.settings)

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
    load_base_components(app.settings)
    main_gui = main_window.MainUi()
    app.main_window = main_gui  # needed for signal access
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    time.sleep(5)
    # assert default state
    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        for test_app in tab.app_links:
            assert not test_app._app_version_cbox.isHidden()
            assert not test_app._app_channel_cbox.isHidden()

    # click and assert
    main_gui.ui.menu_set_display_versions.trigger()
    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        for test_app in tab.app_links:
            assert test_app._app_version_cbox.isHidden()
            assert not test_app._app_channel_cbox.isHidden()
    main_gui.ui.menu_set_display_channels.trigger()
    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        for test_app in tab.app_links:
            assert test_app._app_version_cbox.isHidden()
            assert test_app._app_channel_cbox.isHidden()
    # click again
    main_gui.ui.menu_set_display_versions.trigger()
    main_gui.ui.menu_set_display_channels.trigger()
    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        for test_app in tab.app_links:
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


def testRenameTabDialog(base_fixture, settings_fixture, qtbot, mocker):
    load_base_components(app.settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainUi()
    app.main_window = main_gui  # needed for signal access
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    # call right click
    # tab.customContextMenuRequested.emit(QtCore.QPoint(120, 41))
    #tab = main_gui.ui.tab_bar.tabBar()
    # assert main_gui.ui.tab_bar
    
    new_text = "My Text"

    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=[new_text, True])
    main_gui._app_grid.on_tab_rename(0)
    assert main_gui.ui.tab_bar.tabBar().tabText(0) == new_text

    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=["OtherText", False])
    main_gui._app_grid.on_tab_rename(0)
    # text must be the same
    assert main_gui.ui.tab_bar.tabBar().tabText(0) == new_text

    # for debug
    # while True:
    #    _qapp_instance.processEvents()


def testAddTabDialog(base_fixture, settings_fixture, qtbot, mocker):
    load_base_components(app.settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainUi()
    app.main_window = main_gui  # needed for signal access
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    new_text = "My New Tab"
    prev_count = main_gui.ui.tab_bar.tabBar().count()
    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=[new_text, True])
    main_gui._app_grid.on_new_tab()
    assert main_gui.ui.tab_bar.tabBar().count() == prev_count + 1
    assert main_gui.ui.tab_bar.tabBar().tabText(prev_count) == new_text
    config_tabs = config_file.parse_config_file(settings_fixture)
    assert len(config_tabs) == prev_count + 1

    # press cancel
    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=["OtherText", False])
    main_gui._app_grid.on_tab_rename(0)
    assert main_gui.ui.tab_bar.tabBar().count() == prev_count + 1
    config_tabs = config_file.parse_config_file(settings_fixture)
    assert len(config_tabs) == prev_count + 1

def testRemoveTabDialog(base_fixture, settings_fixture, qtbot, mocker):
    load_base_components(app.settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainUi()
    app.main_window = main_gui  # needed for signal access
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    id_to_delete = 0
    text = main_gui.ui.tab_bar.tabBar().tabText(id_to_delete)
    prev_count = main_gui.ui.tab_bar.tabBar().count()
    assert prev_count > 1, "Test won't work with one tab"

    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)
    main_gui._app_grid.on_tab_remove(id_to_delete)

    assert main_gui.ui.tab_bar.tabBar().count() == prev_count - 1
    assert main_gui.ui.tab_bar.tabBar().tabText(id_to_delete) != text
    config_tabs = config_file.parse_config_file(settings_fixture)
    assert len(config_tabs) == prev_count - 1

    # press no
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.No)
    main_gui._app_grid.on_tab_remove(0)
    assert main_gui.ui.tab_bar.tabBar().count() == prev_count - 1
    config_tabs = config_file.parse_config_file(settings_fixture)
    assert len(config_tabs) == prev_count - 1

# TODO
def testTabMoveIsSaved():
    pass

def testAddAppLink(base_fixture, settings_fixture, qtbot, mocker):
    load_base_components(app.settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainUi()
    app.main_window = main_gui  # needed for signal access
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.ui.tab_bar.findChildren(TabAppGrid)
    cd = tabs[1].config_data
    apps = cd.get_app_entries()
    prev_count = len(apps)
    app_link: AppLink = tabs[1].app_links[0] 
    app_info = AppConfigEntry(
        app_data={"name": "NewApp", "conan_ref": "zlib/1.2.11@_/_", "executable": "bin/exe"})

    mocker.patch.object(EditAppDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Accepted)
    app_link.open_app_link_add_dialog(app_info)
    assert app_link._edit_app_dialog._ui.name_line_edit.text()

    app_link._edit_app_dialog._ui.button_box.accepted.emit()

    # check that the gui has updated
    apps = cd.get_app_entries()
    assert len(apps) == prev_count + 1
    assert apps[-1].name == "NewApp"
    assert tabs[1].app_links[-1]._app_name_label.text() == "NewApp"

    # check, that the config file has updated
    config_tabs = config_file.parse_config_file(settings_fixture)
    assert config_tabs[0].name == cd.name == "Basics" # just safety that it is the same tab
    assert len(config_tabs[0].get_app_entries()) == prev_count + 1


def testEditAppLink(base_fixture, settings_fixture, qtbot, mocker):
    load_base_components(app.settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainUi()
    app.main_window = main_gui  # needed for signal access
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.ui.tab_bar.findChildren(TabAppGrid)
    cd = tabs[1].config_data
    apps = cd.get_app_entries()
    prev_count = len(apps)
    app_link: AppLink = tabs[1].app_links[0]

    ### check that no changes happens on cancel
    mocker.patch.object(EditAppDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Rejected)
    app_link.open_edit_dialog()
    config_tabs = config_file.parse_config_file(settings_fixture)
    assert config_tabs[0].name == cd.name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].get_app_entries()) == prev_count

    ### check, that changing something has the change in the saved config and we the same number of elements
    app_info = AppConfigEntry(
        app_data={"name": "NewApp", "conan_ref": "zlib/1.2.11@_/_", "executable": "bin/exe"})
    mocker.patch.object(EditAppDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Accepted)
    app_link.open_edit_dialog(app_info)

    # check that the gui has updated
    apps = cd.get_app_entries()
    assert len(apps) == prev_count
    assert app_link.config_data.name == "NewApp"
    assert app_link._app_name_label.text() == "NewApp"
    assert app_link._app_version_cbox.currentText() == "1.2.11"
    assert app_link._app_channel_cbox.currentText() == AppConfigEntry.OFFICIAL_RELEASE

    # check, that the config file has updated
    config_tabs = config_file.parse_config_file(settings_fixture)
    assert config_tabs[0].name == cd.name == "Basics" # just safety that it is the same tab
    assert len(config_tabs[0].get_app_entries()) == prev_count

def testRemoveAppLink(base_fixture, settings_fixture, qtbot, mocker):
    load_base_components(app.settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainUi()
    app.main_window = main_gui  # needed for signal access
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.ui.tab_bar.findChildren(TabAppGrid)
    cd = tabs[1].config_data
    apps = cd.get_app_entries()
    prev_count = len(apps)

    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)
    app_link = tabs[1].app_links[0]
    app_link.remove()

    # check that the gui has updated
    apps = cd.get_app_entries()
    assert len(apps) == prev_count - 1

    # check, that the config file has updated

    config_tabs = config_file.parse_config_file(settings_fixture)
    assert len(config_tabs[0].get_app_entries()) == prev_count - 1


def testOpenFileExplorerOnAppLink(base_fixture, qtbot):
    # TODO Negative test
    pass


def testCreateNewConfigFileOnFirstOpen():
    pass
