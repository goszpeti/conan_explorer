"""
These test starts the application but not with the main function,
so the qtbot is usable to inspect gui objects.
"""
from conans.model.ref import ConanFileReference as CFR
import os
import tempfile
from pathlib import Path

import conan_app_launcher.app as app
from conan_app_launcher.logger import Logger
from conan_app_launcher.settings import *
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.data import UiAppLinkConfig
from conan_app_launcher.ui.data.json_file import JsonUiConfig
from conan_app_launcher.ui.modules.app_grid.model import UiAppLinkModel
from conan_app_launcher.ui.modules.app_grid.tab import (AppLink, EditAppDialog,
                                                        TabGrid)
from conan_app_launcher.settings.ini_file import IniSettings
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt

TEST_REF = "zlib/1.2.11@_/_"


def test_rename_tab_dialog(ui_no_refs_config_fixture, qtbot, mocker):
    """ Test, that rename dialog change the guis"""

    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    
    new_text = "My Text"

    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=[new_text, True])
    main_gui.app_grid.on_tab_rename(0)
    assert main_gui.ui.tab_bar.tabBar().tabText(0) == new_text

    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=["OtherText", False])
    main_gui.app_grid.on_tab_rename(0)
    # text must be the same
    assert main_gui.ui.tab_bar.tabBar().tabText(0) == new_text


def test_add_tab_dialog(ui_no_refs_config_fixture, qtbot, mocker):
    """ """
    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    new_text = "My New Tab"
    prev_count = main_gui.ui.tab_bar.tabBar().count()
    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=[new_text, True])
    main_gui.app_grid.on_new_tab()
    assert main_gui.ui.tab_bar.tabBar().count() == prev_count + 1
    assert main_gui.ui.tab_bar.tabBar().tabText(prev_count) == new_text

    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().tabs
    assert len(config_tabs) == prev_count + 1

    # press cancel - count must still be original + 1
    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=["OtherText", False])
    main_gui.app_grid.on_tab_rename(0)
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().tabs
    assert main_gui.ui.tab_bar.tabBar().count() == prev_count + 1
    assert len(config_tabs) == prev_count + 1


def test_remove_tab_dialog(ui_no_refs_config_fixture, qtbot, mocker):
    from pytestqt.plugin import _qapp_instance
    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    id_to_delete = 0
    text = main_gui.ui.tab_bar.tabBar().tabText(id_to_delete)
    prev_count = main_gui.ui.tab_bar.tabBar().count()
    assert prev_count > 1, "Test won't work with one tab"

    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)
    main_gui.app_grid.on_tab_remove(id_to_delete)

    assert main_gui.ui.tab_bar.tabBar().count() == prev_count - 1
    assert main_gui.ui.tab_bar.tabBar().tabText(id_to_delete) != text
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().tabs
    assert len(config_tabs) == prev_count - 1

    # press no
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.No)
    main_gui.app_grid.on_tab_remove(0)
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().tabs
    assert main_gui.ui.tab_bar.tabBar().count() == prev_count - 1
    assert len(config_tabs) == prev_count - 1


def test_tab_move_is_saved(ui_no_refs_config_fixture, qtbot):
    """ Test, that the config file is saved, when the tab is moved. """
    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    assert main_gui.ui.tab_bar.tabBar().tabText(0) == "Basics"
    main_gui.ui.tab_bar.tabBar().moveTab(0,1) # move basics to the right

    assert main_gui.ui.tab_bar.tabBar().tabText(1) == "Basics"
    
    # re-read config
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().tabs
    assert config_tabs[0].name == "Extra"
    assert config_tabs[1].name == "Basics"


def test_edit_AppLink(base_fixture, ui_config_fixture, qtbot, mocker):
    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.load(ui_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.ui.tab_bar.findChildren(TabGrid)
    tab_model = tabs[1].model
    apps_model = tab_model.apps
    prev_count = len(apps_model)
    app_link: AppLink = tabs[1].app_links[0]

    ### check that no changes happens on cancel
    mocker.patch.object(EditAppDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Rejected)
    app_link.open_edit_dialog()
    config_tabs = JsonUiConfig(ui_config_fixture).load().tabs
    assert config_tabs[0].name == tab_model.name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].apps) == prev_count

    ### check, that changing something has the change in the saved config and we the same number of elements
    app_config = UiAppLinkConfig(name="NewApp", conan_ref=TEST_REF,
                                 executable="bin/exe")
    app_model = UiAppLinkModel().load(app_config, app_link.model.parent)
    mocker.patch.object(EditAppDialog, 'exec_', return_value=QtWidgets.QDialog.Accepted)
    app_link.open_edit_dialog(app_model)

    # check that the gui has updated
    assert len(app_link._parent_tab.app_links) == prev_count
    assert app_link.model.name == "NewApp"
    assert app_link._app_name_label.text() == "NewApp"
    assert app_link._app_version_cbox.currentText() == "1.2.11"
    assert app_link._app_channel_cbox.currentText() == UiAppLinkModel.OFFICIAL_RELEASE

    # check, that the config file has updated
    config_tabs = JsonUiConfig(ui_config_fixture).load().tabs
    assert config_tabs[0].name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].apps) == prev_count


def test_remove_AppLink(base_fixture, ui_no_refs_config_fixture, qtbot, mocker):
    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.ui.tab_bar.findChildren(TabGrid)
    tab_model = tabs[1].model
    apps_model = tab_model.apps
    prev_count = len(apps_model)

    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)
    app_link = tabs[1].app_links[0]
    app_link.remove()

    # check that the gui has updated
    apps = tab_model.apps
    assert len(apps) == prev_count - 1

    # check, that the config file has updated

    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().tabs
    assert len(config_tabs[0].apps) == prev_count - 1


def test_add_AppLink(base_fixture, ui_config_fixture, qtbot, mocker):
    app.active_settings.set(DISPLAY_APP_CHANNELS, False) # disable, to check if a new app uses it
    app.active_settings.set(DISPLAY_APP_VERSIONS, True)  # disable, to check if a new app uses it

    from pytestqt.plugin import _qapp_instance
    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.load(ui_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.ui.tab_bar.findChildren(TabGrid)
    tab = tabs[1]
    tab_model = tab.model
    apps_model = tab_model.apps
    prev_count = len(apps_model)
    app_link: AppLink = tab.app_links[0]
    app_config = UiAppLinkConfig(name="NewApp", conan_ref=CFR.loads(TEST_REF),
                                 executable="bin/exe")
    app_model = UiAppLinkModel().load(app_config, app_link.model.parent)

    mocker.patch.object(EditAppDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Accepted)
    new_app_link = tab.open_app_link_add_dialog(app_model)
    assert new_app_link
    assert tab._edit_app_dialog._ui.name_line_edit.text()

    _qapp_instance.processEvents() # call event loop once, so the hide/show attributes are refreshed
    
    # check that the gui has updated
    apps = tab_model.apps
    assert len(apps) == prev_count + 1
    assert new_app_link.model.name == "NewApp"
    assert new_app_link._app_name_label.text() == "NewApp"
    assert new_app_link._app_channel_cbox.isHidden()
    assert not new_app_link._app_version_cbox.isHidden()

    # check, that the config file has updated
    config_tabs = JsonUiConfig(ui_config_fixture).load().tabs
    assert config_tabs[0].name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].apps) == prev_count + 1
    # this test sometimes errors in the ci on teardown
    Logger.remove_qt_logger()


def test_multiple_apps_ungreying(base_fixture, qtbot):
    """
    Test, that apps ungrey, after their packages are loaded.
    Set greyed attribute of the underlying app button expected.
    """
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    app.active_settings = IniSettings(Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "config_file/multiple_apps_same_package.json"
    app.active_settings.set(LAST_CONFIG_FILE, str(config_file_path))
    # load path into local cache
    app.conan_api.get_path_or_install(ConanFileReference.loads("fft/cci.20061228@_/_"), {})
    

    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.load()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    # check app icons first two should be ungreyed, third is invalid->not ungreying
    for tab in main_gui.ui.tab_bar.findChildren(TabGrid):
        for test_app in tab.app_links:
            if test_app.model.name in ["App1 with spaces", "App1 new"]:
                assert not test_app._app_button._greyed_out, repr(test_app.model.__dict__)
            elif test_app.model.name in ["App1 wrong path", "App2"]:
                assert test_app._app_button._greyed_out



def test_open_file_explorer_on_AppLink(base_fixture, qtbot):
    # TODO
    pass

