
import os
import tempfile
from pathlib import Path
from conan_app_launcher.ui.dialogs.reorder_dialog.reorder_dialog import ReorderDialog
from test.conftest import TEST_REF

import conan_app_launcher.app as app
from conan_app_launcher.settings import *
from conan_app_launcher.settings.ini_file import IniSettings
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.config import UiAppLinkConfig
from conan_app_launcher.ui.config.json_file import JsonUiConfig
from conan_app_launcher.ui.views.app_grid.model import UiAppLinkModel
from conan_app_launcher.ui.views.app_grid.tab import (AppEditDialog, AppLinkBase,
                                                        TabGrid)
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt

def test_rename_tab_dialog(ui_no_refs_config_fixture, qtbot, mocker):
    """ Test, that rename dialog change the name """
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    new_text = "My Text"

    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=[new_text, True])
    main_gui.app_grid.on_tab_rename(0)
    assert main_gui.app_grid.tab_widget.tabBar().tabText(0) == new_text

    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=["OtherText", False])
    main_gui.app_grid.on_tab_rename(0)
    # text must be the same
    assert main_gui.app_grid.tab_widget.tabBar().tabText(0) == new_text


def test_add_tab_dialog(ui_no_refs_config_fixture, qtbot, mocker):
    """ Test, that Add Tab function adds a new tab """
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    new_text = "My New Tab"
    prev_count = main_gui.app_grid.tab_widget.tabBar().count()
    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=[new_text, True])
    main_gui.app_grid.on_new_tab()
    assert main_gui.app_grid.tab_widget.tabBar().count() == prev_count + 1
    assert main_gui.app_grid.tab_widget.tabBar().tabText(prev_count) == new_text

    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert len(config_tabs) == prev_count + 1

    # press cancel - count must still be original + 1
    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=["OtherText", False])
    main_gui.app_grid.on_tab_rename(0)
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert main_gui.app_grid.tab_widget.tabBar().count() == prev_count + 1
    assert len(config_tabs) == prev_count + 1


def test_remove_tab_dialog(ui_no_refs_config_fixture, qtbot, mocker):
    """ Test, that Remove Tab actually removes a tab. Last tab must not be deletable. """
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    id_to_delete = 0
    text = main_gui.app_grid.tab_widget.tabBar().tabText(id_to_delete)
    prev_count = main_gui.app_grid.tab_widget.tabBar().count()
    assert prev_count > 1, "Test won't work with one tab"

    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)
    mocker.patch.object(QtWidgets.QMenu, 'exec_',
                        return_value=None)
    tab_rect = main_gui.app_grid.tab_widget.tabBar().tabRect(id_to_delete)
    menu = main_gui.app_grid.on_tab_context_menu_requested(tab_rect.center())
    actions = menu.actions()
    delete_action = actions[1]
    delete_action.trigger()

    assert main_gui.app_grid.tab_widget.tabBar().count() == prev_count - 1
    assert main_gui.app_grid.tab_widget.tabBar().tabText(id_to_delete) != text
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert len(config_tabs) == prev_count - 1

    # press no
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.No)
    main_gui.app_grid.on_tab_remove(0)
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert main_gui.app_grid.tab_widget.tabBar().count() == prev_count - 1
    assert len(config_tabs) == prev_count - 1


def test_tab_move_is_saved(ui_no_refs_config_fixture, qtbot):
    """ Test, that the config file is saved, when the tab is moved. """
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    assert main_gui.app_grid.tab_widget.tabBar().tabText(0) == "Basics"
    main_gui.app_grid.tab_widget.tabBar().moveTab(0, 1)  # move basics to the right

    assert main_gui.app_grid.tab_widget.tabBar().tabText(1) == "Basics"

    # re-read config
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert config_tabs[0].name == "Extra"
    assert config_tabs[1].name == "Basics"


def test_edit_AppLink(qtbot, base_fixture, ui_config_fixture, mocker):
    """ Test, that Edit AppLink Dialog saves all the configured data s"""
    from pytestqt.plugin import _qapp_instance
    app.active_settings.set(APPLIST_ENABLED, False)
    app.active_settings.set(ENABLE_APP_COMBO_BOXES, False)

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.app_grid.tab_widget.findChildren(TabGrid)
    tab_model = tabs[1].model
    apps_model = tab_model.apps
    prev_count = len(apps_model)
    app_link: AppLinkBase = tabs[1].app_links[0]

    # check that no changes happens on cancel
    mocker.patch.object(AppEditDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Rejected)
    app_link.open_edit_dialog()
    config_tabs = JsonUiConfig(ui_config_fixture).load().app_grid.tabs
    assert config_tabs[0].name == tab_model.name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].apps) == prev_count

    # check, that changing something has the change in the saved config and we the same number of elements
    app_config = UiAppLinkConfig(name="NewApp", conan_ref=TEST_REF,
                                 executable="bin/exe")
    app_model = UiAppLinkModel().load(app_config, app_link.model.parent)
    mocker.patch.object(AppEditDialog, 'exec_', return_value=QtWidgets.QDialog.Accepted)
    app_link.open_edit_dialog(app_model)

    # check that the gui has updated
    assert len(app_link._parent_tab.app_links) == prev_count
    assert app_link.model.name == "NewApp"
    assert app_link._app_name.text() == "NewApp"
    assert app_link._app_version.text() == ConanFileReference.loads(TEST_REF).version
    assert app_link._app_channel.text() == ConanFileReference.loads(TEST_REF).channel

    # check, that the config file has updated
    config_tabs = JsonUiConfig(ui_config_fixture).load().app_grid.tabs
    assert config_tabs[0].name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].apps) == prev_count
    if app.conan_worker:  # manual wait for worker
        app.conan_worker.finish_working()


def test_remove_AppLink(qtbot, base_fixture, ui_no_refs_config_fixture, mocker):
    """ Test, that Remove Applink removes and AppLink and the last one is not deletable """
    from pytestqt.plugin import _qapp_instance
    app.active_settings.set(APPLIST_ENABLED, False)

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.app_grid.tab_widget.findChildren(TabGrid)
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

    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert len(config_tabs[0].apps) == prev_count - 1

    # press again - last link warning dialog must spawn and link not deleted
    app_link = tabs[1].app_links[0]
    app_link.remove()
    assert len(apps) == 1


def test_add_AppLink(qtbot, base_fixture, ui_no_refs_config_fixture, mocker):
    """ Tests, that the Edit App Dialog wotks for adding a new Link """
    from pytestqt.plugin import _qapp_instance
    app.active_settings.set(APPLIST_ENABLED, False)

    app.active_settings.set(DISPLAY_APP_CHANNELS, False)  # disable, to check if a new app uses it
    app.active_settings.set(DISPLAY_APP_VERSIONS, True)  # disable, to check if a new app uses it
    # preinstall ref, to see if link updates paths
    app.conan_api.get_path_or_auto_install(ConanFileReference.loads(TEST_REF), {})

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.app_grid.tab_widget.findChildren(TabGrid)
    tab = tabs[1]
    tab_model = tab.model
    apps_model = tab_model.apps
    prev_count = len(apps_model)
    app_link: AppLinkBase = tab.app_links[0]
    app_config = UiAppLinkConfig(name="NewApp", conan_ref=TEST_REF,
                                 executable="conanmanifest.txt")
    app_model = UiAppLinkModel().load(app_config, app_link.model.parent)

    mocker.patch.object(AppEditDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Accepted)
    new_app_link: AppLinkBase = tab.open_app_link_add_dialog(app_model)
    assert new_app_link
    assert tab._edit_app_dialog._ui.name_line_edit.text()

    _qapp_instance.processEvents()  # call event loop once, so the hide/show attributes are refreshed

    # check that the gui has updated
    apps = tab_model.apps
    assert len(apps) == prev_count + 1
    assert new_app_link.model.name == "NewApp"
    assert new_app_link._app_name.text() == "NewApp"
    assert new_app_link._app_channel.isHidden()
    assert new_app_link.model.package_folder.exists()

    # check, that the config file has updated
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert config_tabs[0].name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].apps) == prev_count + 1
    # wait until conan search finishes
    vt = tab._edit_app_dialog._ui.conan_ref_line_edit._completion_thread
    if vt and vt.is_alive():
        vt.join()


def test_move_AppLink(qtbot, base_fixture, ui_no_refs_config_fixture, mocker):
    """ Test, that the move dialog works and correctly updates the AppGrid. There are 2 apps on the loaded tab. """
    from pytestqt.plugin import _qapp_instance
    
    app.active_settings.set(APPLIST_ENABLED, False)

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.app_grid.tab_widget.findChildren(TabGrid)
    tab: TabGrid = tabs[1]
    tab_model = tab.model
    apps_model = tab_model.apps
    app_link = tab.app_links[0]
    move_dialog = ReorderDialog(parent=main_gui, model=tab_model)
    move_dialog.show()
    sel_idx = tab_model.index(0, 0, QtCore.QModelIndex())
    move_dialog._ui.list_view.selectionModel().select(sel_idx, QtCore.QItemSelectionModel.Select)
    move_dialog._ui.move_down_button.clicked.emit()
    # check model
    assert apps_model[1].name == app_link.model.name
    # click down again - nothing should happen
    move_dialog._ui.move_down_button.clicked.emit()
    assert apps_model[1].name == app_link.model.name
    # now the element is deselcted - select the same element again (now row 1)
    sel_idx = tab_model.index(1, 0, QtCore.QModelIndex())
    move_dialog._ui.list_view.selectionModel().select(sel_idx, QtCore.QItemSelectionModel.Select)
    # now move back
    move_dialog._ui.move_up_button.clicked.emit()
    assert apps_model[0].name == app_link.model.name
    # click up again - nothing should happen
    move_dialog._ui.move_up_button.clicked.emit()
    assert apps_model[0].name == app_link.model.name


def test_multiple_apps_ungreying(qtbot, base_fixture):
    """
    Test, that apps ungrey, after their packages are loaded.
    Set greyed attribute of the underlying app button expected.
    """
    from pytestqt.plugin import _qapp_instance

    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    app.active_settings = IniSettings(Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "config_file/multiple_apps_same_package.json"
    app.active_settings.set(LAST_CONFIG_FILE, str(config_file_path))
    app.active_settings.set(APPLIST_ENABLED, False)
    app.active_settings.set(ENABLE_APP_COMBO_BOXES, True)
    # load path into local cache
    app.conan_api.get_path_or_auto_install(ConanFileReference.loads(TEST_REF), {})

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    # check app icons first two should be ungreyed, third is invalid->not ungreying
    for tab in main_gui.app_grid.tab_widget.findChildren(TabGrid):
        for test_app in tab.app_links:
            if test_app.model.name in ["App1 with spaces", "App1 new"]:
                assert not test_app._app_button._greyed_out, repr(test_app.model.__dict__)
            elif test_app.model.name in ["App1 wrong path", "App2"]:
                assert test_app._app_button._greyed_out

    main_gui.close()  # cleanup
