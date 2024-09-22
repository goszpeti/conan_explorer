
import os
import tempfile
from pathlib import Path
from test.conftest import TEST_REF, conan_install_ref

from PySide6 import QtCore, QtWidgets

import conan_explorer.app as app
from conan_explorer.conan_wrapper.types import ConanRef
from conan_explorer.settings import *
from conan_explorer.settings.ini_file import IniSettings
from conan_explorer.ui import main_window
from conan_explorer.ui.dialogs import ReorderDialog
from conan_explorer.ui.views.app_grid.config import UiAppLinkConfig
from conan_explorer.ui.views.app_grid.config.json_file import JsonUiConfig
from conan_explorer.ui.views.app_grid.model import UiAppLinkModel
from conan_explorer.ui.views.app_grid.tab import AppEditDialog, ListAppLink

Qt = QtCore.Qt

def test_rename_tab_dialog(app_qt_fixture, ui_no_refs_config_fixture, mocker):
    """ Test, that rename dialog change the name """
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    app_qt_fixture.addWidget(main_gui)
    app_qt_fixture.waitExposed(main_gui, timeout=5000)

    new_text = "My Text"

    mocker.patch.object(QtWidgets.QInputDialog, 'getText', return_value=[new_text, True])
    main_gui.app_grid.on_tab_rename(0)
    assert main_gui.app_grid.tab_widget.tabBar().tabText(0) == new_text

    mocker.patch.object(QtWidgets.QInputDialog, 'getText', return_value=["OtherText", False])
    main_gui.app_grid.on_tab_rename(0)
    # text must be the same
    assert main_gui.app_grid.tab_widget.tabBar().tabText(0) == new_text
    main_gui.close()  # cleanup


def test_add_tab_dialog(app_qt_fixture, ui_no_refs_config_fixture, mocker):
    """ Test, that Add Tab function adds a new tab """
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    app_qt_fixture.addWidget(main_gui)
    app_qt_fixture.waitExposed(main_gui, timeout=3000)

    new_text = "My New Tab"
    prev_count = main_gui.app_grid.tab_widget.tabBar().count()
    mocker.patch.object(QtWidgets.QInputDialog, 'getText', return_value=[new_text, True])
    main_gui.app_grid.on_new_tab()
    assert main_gui.app_grid.tab_widget.tabBar().count() == prev_count + 1
    assert main_gui.app_grid.tab_widget.tabBar().tabText(prev_count) == new_text

    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert len(config_tabs) == prev_count + 1

    # press cancel - count must still be original + 1
    mocker.patch.object(QtWidgets.QInputDialog, 'getText',
                        return_value=["OtherText", False])
    main_gui.app_grid.on_new_tab()
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert main_gui.app_grid.tab_widget.tabBar().count() == prev_count + 1
    assert len(config_tabs) == prev_count + 1

    main_gui.close()  # cleanup


def test_remove_tab_dialog(app_qt_fixture, ui_no_refs_config_fixture, mocker):
    """ Test, that Remove Tab actually removes a tab. Last tab must not be deletable. """
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    print("Load gui")
    main_gui.load(ui_no_refs_config_fixture)

    app_qt_fixture.addWidget(main_gui)
    app_qt_fixture.waitExposed(main_gui, timeout=5000)

    id_to_delete = 0
    text = main_gui.app_grid.tab_widget.tabBar().tabText(id_to_delete)
    prev_count = main_gui.app_grid.tab_widget.tabBar().count()
    assert prev_count > 1, "Test won't work with one tab"

    # press no
    print("Test pressing no")
    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.No)
    main_gui.app_grid.on_tab_remove(0)
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert main_gui.app_grid.tab_widget.tabBar().count() == prev_count
    assert len(config_tabs) == prev_count


    print("Test pressing yes")
    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    print("Execute remove")
    main_gui.app_grid.on_tab_remove(0)

    assert main_gui.app_grid.tab_widget.tabBar().count() == prev_count - 1
    assert main_gui.app_grid.tab_widget.tabBar().tabText(id_to_delete) != text
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert len(config_tabs) == prev_count - 1

    main_gui.close()


def test_tab_move_is_saved(app_qt_fixture, ui_no_refs_config_fixture):
    """ Test, that the config file is saved, when the tab is moved. """
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    app_qt_fixture.addWidget(main_gui)
    app_qt_fixture.waitExposed(main_gui, timeout=3000)

    assert main_gui.app_grid.tab_widget.tabBar().tabText(0) == "Basics"
    main_gui.app_grid.tab_widget.tabBar().moveTab(0, 1)  # move basics to the right

    assert main_gui.app_grid.tab_widget.tabBar().tabText(1) == "Basics"

    # re-read config
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert config_tabs[0].name == "Extra"
    assert config_tabs[1].name == "Basics"
    main_gui.close()


def test_edit_AppLink(app_qt_fixture, base_fixture, ui_config_fixture, mocker):
    """ Test, that Edit AppLink Dialog saves all the configured data s"""
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_config_fixture)

    app_qt_fixture.addWidget(main_gui)
    app_qt_fixture.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.app_grid.get_tabs()
    tab_model = tabs[1].model
    apps_model = tab_model.apps
    prev_count = len(apps_model)
    app_link: ListAppLink = tabs[1].app_links[0]

    # check that no changes happens on cancel
    mocker.patch.object(AppEditDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Rejected)
    app_link.open_edit_dialog()
    config_tabs = JsonUiConfig(ui_config_fixture).load().app_grid.tabs
    assert config_tabs[0].name == tab_model.name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].apps) == prev_count

    # check, that changing something has the change in the saved config and we the same number of elements
    app_config = UiAppLinkConfig(name="NewApp", conan_ref=TEST_REF,
                                 executable="bin/exe")
    app_model = UiAppLinkModel().load(app_config, app_link.model.parent)
    mocker.patch.object(AppEditDialog, 'exec', return_value=QtWidgets.QDialog.DialogCode.Accepted)
    app_link.open_edit_dialog(app_model)

    # check that the gui has updated
    assert len(app_link._parent_tab.app_links) == prev_count
    assert app_link.model.name == "NewApp"
    assert app_link._ui.app_name_label.text() == "NewApp"  # TEST_REF
    assert app_link._ui.conan_ref_value_label.text() == TEST_REF
    # check, that the config file has updated
    config_tabs = JsonUiConfig(ui_config_fixture).load().app_grid.tabs
    assert config_tabs[0].name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].apps) == prev_count
    if app.conan_worker:  # manual wait for worker
        app.conan_worker.finish_working()
    main_gui.close()


def test_remove_AppLink(app_qt_fixture, base_fixture, ui_no_refs_config_fixture, mocker):
    """ Test, that Remove Applink removes and AppLink and the last one is not deletable """
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    app_qt_fixture.addWidget(main_gui)
    app_qt_fixture.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.app_grid.get_tabs()
    tab_model = tabs[1].model
    apps_model = tab_model.apps
    prev_count = len(apps_model)

    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    app_link = tabs[1].app_links[0]
    app_link.remove()

    # check that the gui has updated
    apps = tab_model.apps
    assert len(apps) == prev_count - 1

    # check, that the config file has updated

    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert len(config_tabs[0].apps) == prev_count - 1


def test_add_AppLink(app_qt_fixture, base_fixture, ui_no_refs_config_fixture, mocker):
    """ Tests, that the Edit App Dialog wotks for adding a new Link """
    from pytestqt.plugin import _qapp_instance

    # preinstall ref, to see if link updates paths
    app.conan_api.get_path_or_auto_install(ConanRef.loads(TEST_REF), {})

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    app_qt_fixture.addWidget(main_gui)
    app_qt_fixture.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.app_grid.get_tabs()
    tab = tabs[1]
    tab_model = tab.model
    apps_model = tab_model.apps
    prev_count = len(apps_model)
    app_link: ListAppLink = tab.app_links[0]
    app_config = UiAppLinkConfig(name="NewApp", conan_ref=TEST_REF,
                                 executable="conanmanifest.txt")
    app_model = UiAppLinkModel().load(app_config, app_link.model.parent)

    mocker.patch.object(AppEditDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Accepted)
    new_app_link = tab.open_app_link_add_dialog(app_model)
    assert new_app_link
    assert tab._edit_app_dialog._ui.name_line_edit.text()

    _qapp_instance.processEvents()  # call event loop once, so the hide/show attributes are refreshed

    # check that the gui has updated
    apps = tab_model.apps
    assert len(apps) == prev_count + 1
    assert new_app_link.name == "NewApp"
    assert new_app_link.package_folder.exists()

    # check, that the config file has updated
    config_tabs = JsonUiConfig(ui_no_refs_config_fixture).load().app_grid.tabs
    assert config_tabs[0].name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].apps) == prev_count + 1
    # wait until conan search finishes
    vt = tab._edit_app_dialog._ui.conan_ref_line_edit._completion_thread
    if vt and vt.is_alive():
        vt.join()
    main_gui.close()


def test_move_AppLink(app_qt_fixture, base_fixture, ui_no_refs_config_fixture, mocker):
    """ Test, that the move dialog works and correctly updates the AppGrid. There are 2 apps on the loaded tab. """
    from pytestqt.plugin import _qapp_instance
    
    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    app_qt_fixture.addWidget(main_gui)
    app_qt_fixture.waitExposed(main_gui, timeout=3000)

    tabs = main_gui.app_grid.get_tabs()
    tab = tabs[1]
    tab_model = tab.model
    apps_model = tab_model.apps
    app_link = tab.app_links[0]
    move_dialog = ReorderDialog(parent=main_gui, model=tab_model)
    move_dialog.show()
    sel_idx = tab_model.index(0, 0, QtCore.QModelIndex())
    move_dialog._ui.list_view.selectionModel().select(sel_idx, QtCore.QItemSelectionModel.SelectionFlag.Select)
    move_dialog._ui.move_down_button.clicked.emit()
    # check model
    assert apps_model[1].name == app_link.model.name
    # click down again - nothing should happen
    move_dialog._ui.move_down_button.clicked.emit()
    assert apps_model[1].name == app_link.model.name
    # now the element is deselcted - select the same element again (now row 1)
    sel_idx = tab_model.index(1, 0, QtCore.QModelIndex())
    move_dialog._ui.list_view.selectionModel().select(sel_idx, QtCore.QItemSelectionModel.SelectionFlag.Select)
    # now move back
    move_dialog._ui.move_up_button.clicked.emit()
    assert apps_model[0].name == app_link.model.name
    # click up again - nothing should happen
    move_dialog._ui.move_up_button.clicked.emit()
    assert apps_model[0].name == app_link.model.name
    move_dialog.close()
    main_gui.close()


def test_multiple_apps_ungreying(app_qt_fixture, base_fixture):
    """
    Test, that apps ungrey, after their packages are loaded.
    Set greyed attribute of the underlying app button expected.
    """
    from pytestqt.plugin import _qapp_instance
    conan_install_ref(TEST_REF, "-u")

    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    app.active_settings = IniSettings(Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "config_file/multiple_apps_same_package.json"
    app.active_settings.set(AUTO_INSTALL_QUICKLAUNCH_REFS, False)
    app.active_settings.set(LAST_CONFIG_FILE, str(config_file_path))
    # load path into local cache
    app.conan_api.get_path_or_auto_install(ConanRef.loads(TEST_REF), {})

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load()

    app_qt_fixture.addWidget(main_gui)
    app_qt_fixture.waitExposed(main_gui, timeout=3000)
    # check app icons first two should be ungreyed, third is invalid->not ungreying
    for tab in main_gui.app_grid.get_tabs():
        for test_app in tab.app_links:
            if test_app.model.name in ["App1 with spaces", "App1 new"]:
                assert not test_app._ui.app_button._greyed_out, repr(test_app.model.__dict__)
            elif test_app.model.name in ["App1 wrong path", "App2"]:
                assert test_app._ui.app_button._greyed_out

    main_gui.close()  # cleanup
