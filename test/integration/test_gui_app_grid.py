"""
These test starts the application but not with the main function,
so the qtbot is usable to inspect gui objects.
"""
from conan_app_launcher.__main__ import load_base_components
import conan_app_launcher as app
from conan_app_launcher.base import Logger
from conan_app_launcher.components import config_file
from conan_app_launcher.settings import *
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.app_grid.app_link import AppLink, OFFICIAL_RELEASE_DISP_NAME

from conan_app_launcher.ui.app_grid.tab_app_grid import TabAppGrid
from conan_app_launcher.components import AppConfigEntry
from conan_app_launcher.ui.app_grid.app_edit_dialog import EditAppDialog

from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt

def testIconUpdateFromExecutable():
    """
    Test, that an extracted icon from an exe is displayed after loaded and then retrived from cache.
    Check, that the icon has the temp path.
    """
    # TODO


def testRenameTabDialog(base_fixture, settings_fixture, qtbot, mocker):
    load_base_components(app.active_settings)
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
    load_base_components(app.active_settings)
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
    load_base_components(app.active_settings)
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

def testEditAppLink(base_fixture, settings_fixture, qtbot, mocker):
    load_base_components(app.active_settings)
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
    load_base_components(app.active_settings)
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


def testAddAppLink(base_fixture, settings_fixture, qtbot, mocker):
    load_base_components(app.active_settings)
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
    assert config_tabs[0].name == cd.name == "Basics"  # just safety that it is the same tab
    assert len(config_tabs[0].get_app_entries()) == prev_count + 1
    # this test sometimes errors in the ci on teardown
    Logger.remove_qt_logger()


def testOpenFileExplorerOnAppLink(base_fixture, qtbot):
    # TODO Negative test
    pass

