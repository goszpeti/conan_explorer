"""
These test starts the application but not with the main function,
so the qtbot is usable to inspect gui objects.
"""

import os
import platform
from subprocess import PIPE, STDOUT, check_output, run
import sys
import time
from pathlib import Path
from shutil import rmtree

import pytest
import requests
from conan_explorer.ui.fluent_window.side_menu import SideSubMenu
from conan_explorer.ui.plugin.handler import PluginFile
from conan_explorer.ui.views.app_grid.tab import TabList
from conan_explorer import DEFAULT_UI_CFG_FILE_NAME, user_save_path
from conan_explorer.conan_wrapper import ConanApi
from conan_explorer.conan_wrapper.conan_cleanup import ConanCleanup
from conan_explorer.app.logger import Logger
from conan_explorer.settings import *
from conan_explorer.ui import main_window
from conan_explorer.ui.views import AboutPage
import conan_explorer.app as app  # using global module pattern

from conan_explorer.conan_wrapper.types import ConanRef
from PySide6 import QtCore, QtWidgets

from test.conftest import PathSetup, conan_remove_ref

Qt = QtCore.Qt


@pytest.mark.conanv2
def test_startup_no_config(qtbot, base_fixture, ui_config_fixture, mocker):
    """ Test, that when no config file is set,
    a new tab with a new default app is automatically added."""
    from pytestqt.plugin import _qapp_instance

    # no settings entry
    app.active_settings.set(LAST_CONFIG_FILE, "")
    # set dark mode to to at least call the functions once
    app.active_settings.set(GUI_MODE, GUI_MODE_DARK)

    # delete default file, in case it exists and has content
    default_config_file_path = user_save_path / (DEFAULT_UI_CFG_FILE_NAME + ".json")
    if default_config_file_path.exists():
        os.remove(default_config_file_path)

    # init config file and parse
    main_gui = main_window.MainWindow(_qapp_instance)
    qtbot.addWidget(main_gui)
    main_gui.load()
    main_gui.show()
    qtbot.waitExposed(main_gui, timeout=3000)

    for tab in main_gui.app_grid.findChildren(TabList):
        assert tab.model.name == "New Tab"
        for test_app in tab.app_links:
            assert test_app.model.name == "New App"

    # check, if doc search works
    open_url_mock = mocker.patch("PySide6.QtGui.QDesktopServices.openUrl")
    main_gui.ui.search_bar_line_edit.setText("query")
    main_gui.on_docs_searched()
    url = open_url_mock.call_args[0][0]
    assert "query" in url
    # check via html query
    res = requests.get(url)
    assert res.status_code == 200

    # check, if save_window_state doesn't crash
    main_gui.save_window_state()
    main_gui.close()

def test_gui_mod_and_style(qtbot, base_fixture, ui_config_fixture):
    """ Test, that
    1. gui mode /dark light
    2. gui icon style
    3. auto open view
    functions do not crash and set the app settings.
    TODO: check, if icons have been reloaded
    """
    from pytestqt.plugin import _qapp_instance
    main_window.ENABLE_GUI_STYLES = True
    app.active_settings.set(GUI_MODE, GUI_MODE_LIGHT)
    app.active_settings.set(GUI_STYLE, GUI_STYLE_MATERIAL)
    app.active_settings.set(AUTO_OPEN_LAST_VIEW, True)
    app.active_settings.set(LAST_VIEW, "Manage Plugins")

    main_gui = main_window.MainWindow(_qapp_instance)
    qtbot.addWidget(main_gui)
    main_gui.load()
    main_gui.show()
    qtbot.waitExposed(main_gui, timeout=3000)

    # check auto open feature
    assert main_gui.plugins_page.isVisible()

    view_side_menu: SideSubMenu = main_gui.ui.right_menu_bottom_content_sw.findChild(QtWidgets.QWidget, "view_widget")

    dark_mode_toggle = view_side_menu.get_menu_entry_by_name("dark_mode_widget")
    dark_mode_toggle.toggle()
    assert app.active_settings.get(GUI_MODE) == GUI_MODE_DARK

    # icon_style_widget = view_side_menu.get_menu_entry_by_name("Icon Style")

    # assert main_gui._style_chooser_radio_material.isChecked()
    # main_gui._style_chooser_radio_fluent.click()

    # assert app.active_settings.get(GUI_STYLE) == GUI_STYLE_FLUENT
    main_gui.close()


@pytest.mark.conanv2
def test_startup_with_existing_config_and_open_menu(qtbot, base_fixture, ui_config_fixture):
    """
    Test, that loading a config file and opening the about menu, and clicking on OK
    The about dialog showing is expected.
    """
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    qtbot.addWidget(main_gui)
    main_gui.load()
    main_gui.show()
    qtbot.waitExposed(main_gui, timeout=3000)

    main_gui.page_widgets.get_button_by_type(AboutPage).click()
    time.sleep(3)

    assert main_gui.about_page.isVisible()
    main_gui.close()


def test_select_config_file_dialog(base_fixture, ui_config_fixture, qtbot, mocker):
    """
    Test, that clicking on on open config file and selecting a file writes it back to settings.
    Same file as selected expected in settings.
    """
    from pytestqt.plugin import _qapp_instance

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    main_gui.load()

    selection = str(Path.home() / "new_config.json")
    mocker.patch.object(QtWidgets.QFileDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[selection])
    side_menu = main_gui.page_widgets.get_side_menu_by_type(type(main_gui.app_grid))
    assert side_menu
    side_menu.get_menu_entry_by_name("Open Layout File").click()

    time.sleep(3)
    assert app.active_settings.get(LAST_CONFIG_FILE) == selection
    app.conan_worker.finish_working(3)
    main_gui.close()


def test_conan_cache_with_dialog(qtbot, base_fixture, ui_config_fixture, mocker):
    """
    Test, that clicking on on open config file and selecting a file writes it back to settings.
    Same file as selected expected in settings.
    """

    if not platform.system() == "Windows":  # Feature only "available" on Windows
        return
    from conans.util.windows import CONAN_REAL_PATH
    conan = ConanApi().init_api()

    # Set up broken packages to have something to cleanup
    # in short path - edit .real_path
    ref = "example/1.0.0@user/testing"
    conan_remove_ref(ref)  # clean up for multiple runs
    # shortpaths is enabled in conanfile
    conanfile = str(base_fixture.testdata_path / "conan" / "conanfile.py")
    ret = os.system(f"conan create {conanfile} {ref}")
    assert ret == 0

    pkg = conan.find_best_matching_local_package(ConanRef.loads(ref))
    remotes = conan.get_remotes()
    Logger().debug("Remotes:" + repr(remotes))
    time.sleep(1)
    assert pkg["id"], f"Package: {pkg}"
    pkg_dir_to_delete = conan.get_package_folder(ConanRef.loads(ref), pkg["id"])

    real_path_file = pkg_dir_to_delete / ".." / CONAN_REAL_PATH
    with open(str(real_path_file), "r+") as fp:
        line = fp.readline()
        line = line + "3"  # add bogus number to path
        fp.seek(0)
        fp.write(line)

    # in cache - delete Short path, so that cache folder is orphaned
    ref = "example/1.0.0@user/orphan"
    conan_remove_ref(ref)
    ret = run(f"conan create {conanfile} {ref}", stdout=PIPE, stderr=STDOUT, shell=True)
    output = ""
    if ret.stderr:
        output += ret.stderr.decode("utf-8")
    if ret.stdout:
        output += ret.stdout.decode("utf-8")
    assert ret.returncode == 0, output
    exp_folder = conan.get_export_folder(ConanRef.loads(ref))
    pkg = conan.find_best_matching_local_package(ConanRef.loads(ref))
    pkg_cache_folder = os.path.abspath(os.path.join(exp_folder, "..", "package", pkg["id"]))
    pkg_dir = conan.get_package_folder(ConanRef.loads(ref), pkg["id"])
    rmtree(pkg_dir)

    paths_to_delete = ConanCleanup(conan).get_cleanup_cache_paths()
    assert pkg_cache_folder in paths_to_delete
    assert str(pkg_dir_to_delete.parent) in paths_to_delete

    from pytestqt.plugin import _qapp_instance
    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.Yes)

    button: QtWidgets.QPushButton = main_gui.main_general_settings_menu.get_menu_entry_by_name("Clean Conan Cache")
    button.click()
    time.sleep(3)

    assert not os.path.exists(pkg_cache_folder)
    assert not pkg_dir_to_delete.parent.exists()
    main_gui.close()


def test_tabs_cleanup_on_load_config_file(base_fixture, ui_config_fixture, qtbot):
    """
    Test, if the previously loaded tabs are deleted, when a new file is loaded
    The same tab number ist expected, as before.
    """
    from pytestqt.plugin import _qapp_instance

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

    time.sleep(5)
    assert main_gui.app_grid.tab_widget.tabBar().count() == tabs_num
    main_gui.close()


@pytest.mark.conanv1
def test_example_plugin(app_qt_fixture, base_fixture: PathSetup):
    example_plugin_path = base_fixture.core_path / "doc/example_plugin"
    os.system(f"{sys.executable} -m pip install wheel") # needed for --no-use-pep517
    os.system(f"{sys.executable} -m pip install {example_plugin_path} --no-use-pep517")
    plugin_file_path = example_plugin_path / "cal_example_plugin" / "plugin.ini"
    assert plugin_file_path.exists()
    app.active_settings._read_ini()  # reload settings

    # start window
    from pytestqt.plugin import _qapp_instance
    main_gui = main_window.MainWindow(_qapp_instance)
    app_qt_fixture.addWidget(main_gui)
    main_gui.load()

    main_gui.show()
    app_qt_fixture.waitExposed(main_gui, timeout=3000)

    # assert, that plugin is loaded
    plugin = main_gui.page_widgets.get_page_by_name("My Example Plugin")
    # path is dynamically loaded
    from cal_example_plugin.my_cal_plugin import SamplePluginView
    assert isinstance(plugin, SamplePluginView)

    main_gui.close()
    PluginFile.unregister(plugin_file_path)
