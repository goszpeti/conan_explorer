"""
These test starts the application but not with the main function,
so the qtbot is usable to inspect gui objects.
"""
import os
import tempfile
from pathlib import Path
import time

import conan_app_launcher as app
from conan_app_launcher.__main__ import load_base_components
from conan_app_launcher.logger import Logger
from conan_app_launcher.components import AppConfigEntry, config_file
from conan_app_launcher.settings import *
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.app_grid.app_edit_dialog import EditAppDialog
from conan_app_launcher.ui.app_grid.app_link import AppLink
from conan_app_launcher.ui.app_grid.tab_app_grid import TabAppGrid
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt



def test_rename_tab_dialog(base_fixture, ui_config_fixture, qtbot, mocker):
    load_base_components(app.active_settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainWindow()
    app.main_window = main_gui  # needed for signal access
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    
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


def test_add_tab_dialog(base_fixture, ui_config_fixture, qtbot, mocker):
    load_base_components(app.active_settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainWindow()
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
    config_tabs = config_file.load_config_file(ui_config_fixture)
    assert len(config_tabs) == prev_count + 1

    # press cancel
    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=["OtherText", False])
    main_gui._app_grid.on_tab_rename(0)
    assert main_gui.ui.tab_bar.tabBar().count() == prev_count + 1
    config_tabs = config_file.load_config_file(ui_config_fixture)
    assert len(config_tabs) == prev_count + 1

def test_remove_tab_dialog(base_fixture, ui_config_fixture, qtbot, mocker):
    load_base_components(app.active_settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainWindow()
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
    config_tabs = config_file.load_config_file(ui_config_fixture)
    assert len(config_tabs) == prev_count - 1

    # press no
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.No)
    main_gui._app_grid.on_tab_remove(0)
    assert main_gui.ui.tab_bar.tabBar().count() == prev_count - 1
    config_tabs = config_file.load_config_file(ui_config_fixture)
    assert len(config_tabs) == prev_count - 1


def test_tab_move_is_saved(base_fixture, ui_config_fixture, qtbot):
    """ Test, that the config file is saved, when the tab is moved. """
    load_base_components(app.active_settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainWindow()
    app.main_window = main_gui  # needed for signal access
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    assert main_gui.ui.tab_bar.tabBar().tabText(0) == "Basics"
    main_gui.ui.tab_bar.tabBar().moveTab(0,1) # move basics to the right

    assert main_gui.ui.tab_bar.tabBar().tabText(1) == "Basics"
    
    # re-read config
    tabs = config_file.load_config_file(ui_config_fixture)
    assert tabs[0].name == "Extra"
    assert tabs[1].name == "Basics"


def test_edit_AppLink(base_fixture, ui_config_fixture, qtbot, mocker):
    load_base_components(app.active_settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainWindow()
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
    config_tabs = config_file.load_config_file(ui_config_fixture)
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
    config_tabs = config_file.load_config_file(ui_config_fixture)
    assert config_tabs[0].name == cd.name == "Basics" # just safety that it is the same tab
    assert len(config_tabs[0].get_app_entries()) == prev_count

def test_remove_AppLink(base_fixture, ui_config_fixture, qtbot, mocker):
    load_base_components(app.active_settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainWindow()
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

    config_tabs = config_file.load_config_file(ui_config_fixture)
    assert len(config_tabs[0].get_app_entries()) == prev_count - 1


def test_add_AppLink(base_fixture, ui_config_fixture, qtbot, mocker):
    app.active_settings.set(DISPLAY_APP_CHANNELS, False) # disable, to check if a new app uses it
    app.active_settings.set(DISPLAY_APP_VERSIONS, True)  # disable, to check if a new app uses it

    load_base_components(app.active_settings)
    from pytestqt.plugin import _qapp_instance
    app.qt_app = _qapp_instance
    main_gui = main_window.MainWindow()
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
    new_app_link = app_link.open_app_link_add_dialog(app_info)
    assert app_link._edit_app_dialog._ui.name_line_edit.text()
    _qapp_instance.processEvents() # call event loop once, so the hide/show attributes are refreshed
    
    # check that the gui has updated
    apps = cd.get_app_entries()
    assert len(apps) == prev_count + 1
    assert new_app_link.config_data.name == "NewApp"
    assert new_app_link._app_name_label.text() == "NewApp"
    assert new_app_link._app_channel_cbox.isHidden()
    assert not new_app_link._app_version_cbox.isHidden()

    # check, that the config file has updated
    config_tabs = config_file.load_config_file(ui_config_fixture)
    assert config_tabs[0].name == cd.name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].get_app_entries()) == prev_count + 1
    # this test sometimes errors in the ci on teardown
    Logger.remove_qt_logger()


def test_multiple_apps_ungreying(base_fixture, qtbot):
    """
    Test, that apps ungrey, after their packages are loaded.
    Set greyed attribute of the underlying app button expected.
    """
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    app.active_settings = Settings(ini_file=Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "config_file/multiple_apps_same_package.json"
    app.active_settings.set(LAST_CONFIG_FILE, str(config_file_path))

    load_base_components(app.active_settings)

    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.start_app_grid()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    # wait for all tasks to finish
    app.conan_worker.finish_working(15)

    # check app icons first two should be ungreyed, third is invalid->not ungreying
    for tab in main_gui.ui.tab_bar.findChildren(TabAppGrid):
        for test_app in tab.app_links:
            test_app.update_with_conan_info()  # signal is not emmited with qt bot, must call manually
            if test_app.config_data.name in ["App1 with spaces", "App1 new"]:
                assert not test_app._app_button._greyed_out, repr(test_app.config_data.__dict__)
            elif test_app.config_data.name in ["App1 wrong path", "App2"]:
                assert test_app._app_button._greyed_out



def test_open_file_explorer_on_AppLink(base_fixture, qtbot):
    # TODO
    pass


def test_AppLink_cbox_switch(base_fixture, ui_config_fixture, qtbot):
    """
    Test, that changing the version resets the channel and user correctly
    """
    # all versions have different user and channel names, so we can distinguish them
    conanfile = str(base_fixture.testdata_path / "conan" / "conanfile_custom.py")
    # os.system(f"conan create {conanfile} switch_test/1.0.0@user1/channel1")
    # os.system(f"conan create {conanfile} switch_test/1.0.0@user1/channel2")
    # os.system(f"conan create {conanfile} switch_test/1.0.0@user2/channel3")
    # os.system(f"conan create {conanfile} switch_test/1.0.0@user2/channel4")
    # os.system(f"conan create {conanfile} switch_test/2.0.0@user3/channel5")
    # os.system(f"conan create {conanfile} switch_test/2.0.0@user3/channel6")
    # os.system(f"conan create {conanfile} switch_test/2.0.0@user4/channel7")
    # os.system(f"conan create {conanfile} switch_test/2.0.0@user4/channel8")
    # need cache
    app.active_settings.set(DISPLAY_APP_USERS, True)
    load_base_components(app.active_settings)

    app_data: config_file.AppType = {"name": "test", "conan_ref": "switch_test/1.0.0@user1/channel1", "args": "", "conan_options": [],
                         "executable": "", "console_application": True, "icon": ""}
    app_info = AppConfigEntry(app_data)
    #app_info._executable = Path(sys.executable)

    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    app_link = AppLink(root_obj, app_info)
    root_obj.setFixedSize(100, 200)
    root_obj.show()
    from pytestqt.plugin import _qapp_instance

    qtbot.waitExposed(root_obj)
    # for debug
    # while True:
    #    _qapp_instance.processEvents()

    # check initial state
    assert app_link._app_version_cbox.count() == 2
    assert app_link._app_version_cbox.itemText(0) == "1.0.0"
    assert app_link._app_version_cbox.itemText(1) == "2.0.0"
    assert app_link._app_user_cbox.count() == 2
    assert app_link._app_user_cbox.itemText(0) == "user1"
    assert app_link._app_user_cbox.itemText(1) == "user2"
    assert app_link._app_channel_cbox.count() == 2
    assert app_link._app_channel_cbox.itemText(0) == "channel1"
    assert app_link._app_channel_cbox.itemText(1) == "channel2"

    # now change version to 2.0.0 -> user can change to default, channel should go to NA
    # this is done, so that the user can select it and not autinstall something random
    app_link._app_version_cbox.setCurrentIndex(1)
    assert app_link._app_version_cbox.count() == 2
    assert app_link._app_version_cbox.itemText(0) == "1.0.0"
    assert app_link._app_version_cbox.itemText(1) == "2.0.0"
    assert app_link._app_user_cbox.count() == 2
    assert app_link._app_user_cbox.itemText(0) == "user1"
    assert app_link._app_user_cbox.itemText(1) == "user2"
    assert app_link._app_channel_cbox.count() == 2
    assert app_link._app_channel_cbox.itemText(0) == "channel1"
    assert app_link._app_channel_cbox.itemText(1) == "channel2"
    # check that reference and executable has updated


    # now change back to 1.0.0 -> user can change to default, channel should go to NA
    app_link._app_version_cbox.setCurrentIndex(0)
