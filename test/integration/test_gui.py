"""
This test starts the application.
It is called z_integration, so that it launches last.
"""

import os
import tempfile
import time
from pathlib import Path


import conan_app_launcher as app
from conan_app_launcher.base import Logger
from conan_app_launcher.settings import *
from conan_app_launcher.ui import main_ui
from conan_app_launcher.ui.layout_entries import TabUiGrid
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt


def testSelectConfigFileDialog(base_fixture, qtbot, mocker):
    """
    Test, that clicking on on open config file and selecting a file writes it back to settings.
    Same file as selected expected in settings.
    """
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    settings = Settings(ini_file=Path(temp_ini_path))

    main_gui = main_ui.MainUi(settings)
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, 3000)
    selection = "C:/new_config.json"
    mocker.patch.object(QtWidgets.QFileDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[selection])

    main_gui._ui.menu_open_config_file_action.trigger()
    time.sleep(3)
    assert settings.get(LAST_CONFIG_FILE) == selection
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

    main_gui = main_ui.MainUi(settings)
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, 3000)

    # wait for all tasks to finish
    app.conan_worker._worker.join()
    main_gui.update_layout()  # TODO: signal does not emit in test, must call manually

    # check app icons first two should be ungreyed, third is invalid->not ungreying
    for tab in main_gui._ui.tabs.findChildren(TabUiGrid):
        for test_app in tab.apps:
            if test_app._app_info.name in ["App1 with spaces", "App1 new"]:
                assert not test_app._app_button._greyed_out
            elif test_app._app_info.name in ["App1 wrong path", "App2"]:
                assert test_app._app_button._greyed_out
    app.conan_worker.finish_working()


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

    main_gui = main_ui.MainUi(settings)
    qtbot.addWidget(main_gui)
    main_gui.show()
    qtbot.waitExposed(main_gui, 3000)
    tabs_num = 2  # two tabs in this file
    assert main_gui._ui.tabs.count() == tabs_num

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, 3000)

    app.conan_worker.finish_working()

    main_gui._re_init()  # re-init with same file

    assert main_gui._ui.tabs.count() == tabs_num
    app.conan_worker.finish_working()


def testStartupWithExistingConfigAndOpenMenu(base_fixture, qtbot):
    """
    Test, loading a config file and opening the about menu, and clicking on OK
    The about dialog showing is expected.
    """
    temp_ini_path = os.path.join(tempfile.gettempdir(), "config.ini")

    settings = Settings(ini_file=Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "app_config.json"
    settings.set(LAST_CONFIG_FILE, str(config_file_path))
    main_gui = main_ui.MainUi(settings)
    qtbot.addWidget(main_gui)

    main_gui.show()
    qtbot.waitExposed(main_gui, 3000)
    main_gui._ui.menu_about_action.trigger()
    time.sleep(3)
    assert main_gui._about_dialog.isEnabled()
    qtbot.mouseClick(main_gui._about_dialog._button_box.buttons()[0], Qt.LeftButton)
    app.conan_worker.finish_working()


def testViewMenuOptions():
    # TODO
    """
    Test the view menu entries.
    Check, that activating the entry set the hide flag is set on the widget.
    """
    pass
