
import os
import platform
from pathlib import Path
from conan_explorer.app.system import delete_path
from test.conftest import (TEST_REF, TEST_REF_OFFICIAL, PathSetup,
                           conan_add_editables, conan_install_ref)
from time import sleep
from typing import Generator, Tuple

import pytest
import pytest_check as check
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QApplication
from pytest_mock import MockerFixture

import conan_explorer  # for mocker
import conan_explorer.app as app  # using global module pattern
from conan_explorer import conan_version
from conan_explorer.conan_wrapper.types import ConanRef
from conan_explorer.settings import FILE_EDITOR_EXECUTABLE
from conan_explorer.ui import main_window
from conan_explorer.ui.dialogs.conan_remove import ConanRemoveDialog
from conan_explorer.ui.views import LocalConanPackageExplorer
from conan_explorer.ui.views.app_grid.tab import AppEditDialog
from conan_explorer.ui.views.package_explorer.sel_model import PkgSelectionType

Qt = QtCore.Qt
SelFlags = QtCore.QItemSelectionModel.SelectionFlag
# For debug:
# from pytestqt.plugin import _qapp_instance
# while True:
#    _qapp_instance.processEvents()

LPESetupType = Tuple[QApplication, LocalConanPackageExplorer, main_window.MainWindow]

@pytest.fixture
def setup_local_package_explorer(qtbot,
    base_fixture, ui_no_refs_config_fixture) -> Generator[LPESetupType, None, None]:
    from pytestqt.plugin import _qapp_instance

    # 1. Switch to another package view
    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    app.conan_worker.finish_working()
    lpe = main_gui.page_widgets.get_page_by_type(LocalConanPackageExplorer)

    # change to local explorer page   
    main_gui.page_widgets.get_button_by_type(type(lpe)).click() 
    lpe._pkg_sel_ctrl._loader.wait_for_finished()

    yield (_qapp_instance, lpe, main_gui)
    main_gui.close()


@pytest.mark.conanv2
def test_local_package_explorer_pkg_selection(qtbot, mocker, 
                setup_local_package_explorer: LPESetupType,
                base_fixture, ui_no_refs_config_fixture: Path):
    """
    Test Local Pacakge Explorer functions.
    1. Change to Page, check if the installed package is in the list.
    2. Select a ref, nothing should change.
    3. Expand ref and select the pkg, fileview should open.
    4. Select another profile of the seame package
    5. Select export folder
    """
    from conan_explorer.app.logger import Logger
    _qapp_instance, lpe, main_gui = setup_local_package_explorer
    # 1. Switch to another package view
    # need new id
    cfr = ConanRef.loads(TEST_REF)
    print("*** Installing package from other platform ***")
    if platform.system() == "Windows":
        conan_install_ref(TEST_REF, profile="linux")
    else:
        conan_install_ref(TEST_REF, profile="windows")

    installed_pkgs = app.conan_api.get_local_pkgs_from_ref(cfr)
    assert len(installed_pkgs) >= 2
    pkg_id1 = installed_pkgs[0].get("id")
    pkg_id2 = installed_pkgs[1].get("id")
    assert pkg_id1
    assert pkg_id2
    pkg_path1 =  app.conan_api.get_package_folder(cfr, pkg_id1)
    pkg_path2 =  app.conan_api.get_package_folder(cfr, pkg_id2)
    export_path = app.conan_api.get_export_folder(cfr)

    # restart reload (check for thread safety)
    Logger().debug("Reload")
    lpe._ui.refresh_button.clicked.emit()
    lpe._pkg_sel_ctrl._loader.wait_for_finished()

    pkg_sel_model = lpe._pkg_sel_ctrl._model
    assert pkg_sel_model
    assert lpe._ui.package_select_view.model().columnCount() == 1

    # check, that the ref + pkg is in the list
    found_tst_pkg = False
    for pkg in pkg_sel_model.root_item.child_items:
        if pkg.item_data[0] == TEST_REF:
            found_tst_pkg = True
            # check it's child
            for child in pkg.child_items:
                if child.type.value == PkgSelectionType.export.value:
                    continue
                assert pkg_sel_model.get_quick_profile_name(child) in [
                    "Windows_x64_vs16_release", "Linux_x64_gcc9_release", 
                    "Windows_x64_msvc192_release"] # ConanV2
    assert found_tst_pkg

    # 2. select package (ref, not profile)
    assert lpe.select_local_package_from_ref(TEST_REF)
    Logger().debug("Selected ref")
    assert not lpe._pkg_tabs_ctrl[0]._model  # view not changed

    # 3. ensure, that we select the pkg with the correct options
    Logger().debug("Select pkg1")
    assert lpe.select_local_package_from_ref(TEST_REF + ":" + pkg_id1)

    assert lpe._pkg_tabs_ctrl[0]._model  # view selected -> fs_model is set
    assert Path(lpe._pkg_tabs_ctrl[0]._model.rootPath()) == pkg_path1

    # 4. switch to another package
    Logger().debug("Select pkg2")
    assert lpe.select_local_package_from_ref(TEST_REF+ ":" + pkg_id2)

    assert lpe._pkg_tabs_ctrl[0]._model  # view selected -> fs_model is set
    assert Path(lpe._pkg_tabs_ctrl[0]._model.rootPath()) == pkg_path2

    #5.Select export folder
    Logger().debug("Select export folder")
    assert lpe._pkg_sel_ctrl.select_local_package_from_ref(TEST_REF, export=True)

    assert lpe._pkg_tabs_ctrl[0]._model  # view selected -> fs_model is set
    assert Path(lpe._pkg_tabs_ctrl[0]._model.rootPath()) == export_path

@pytest.mark.conanv2
def test_local_package_explorer_pkg_selection_editables(qtbot, mocker, 
                setup_local_package_explorer: LPESetupType,
                base_fixture :PathSetup, ui_no_refs_config_fixture: Path):
    """
    Check editable packages open set root path.
    """
    editable_ref = "example/9.9.9@editable/testing"
    base_path = base_fixture.testdata_path / "conan"
    if conan_version.major == 2:
        conan_add_editables(str(base_path / "conanfileV2.py"), ConanRef.loads(editable_ref))
    else:
        conan_add_editables(str(base_path), ConanRef.loads(editable_ref))
    _qapp_instance, lpe, main_gui = setup_local_package_explorer

    lpe._ui.refresh_button.clicked.emit()
    lpe._pkg_sel_ctrl._loader.wait_for_finished()

    assert lpe.select_local_package_from_ref(editable_ref)

    assert lpe._pkg_tabs_ctrl[0]._model  # view selected -> fs_model is set
    assert Path(lpe._pkg_tabs_ctrl[0]._model.rootPath()) == base_path


@pytest.mark.conanv2
def test_local_package_explorer_pkg_sel_functions(qtbot, mocker: MockerFixture, base_fixture,
        ui_no_refs_config_fixture, setup_local_package_explorer: LPESetupType):
    """
    Test Local Pacakge Explorer functions.
    1. Change to Page
    2. Expand ref and select the pkg, fileview should open.
        Test context menu functions of Pkg Selection View
        1. Copy ref - Copy conan reference to clipboard (no pkg id!)
        2. Open export folder - Opens in file manager
        3. Show Conanfile - Opens in default texteditor
        5. Install reference
        6. Show buildinfo
    """
    # disable editor to force open file
    app.active_settings.set(FILE_EDITOR_EXECUTABLE, "UNKNOWN")
    _qapp_instance, lpe, main_gui = setup_local_package_explorer

    from conan_explorer.app.logger import Logger
    cfr = ConanRef.loads(TEST_REF)
    conanfile_path = app.conan_api.get_conanfile_path(cfr)
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)
    assert id
    assert pkg_path.exists()

    # ensure, that we select the pkg with the correct options
    Logger().debug("Select pkg")
    assert lpe.select_local_package_from_ref(TEST_REF + ":" + id)
    assert lpe._pkg_tabs_ctrl[0]._model  # view selected -> fs_model is set

    ### Test pkg reference context menu functions ###
    # test copy ref
    Logger().debug("test copy ref")
    lpe._pkg_sel_ctrl.on_copy_ref_requested()
    assert QtWidgets.QApplication.clipboard().text() == str(cfr)
    sleep(1)

    # test open export folder
    Logger().debug("open export folder")
    # !!!IMPORTANT!!! Because of the relative import of controller in package_explorer
    # the mock has to be relative too 😭
    oifm_mock = mocker.patch("package_explorer.sel_controller.open_in_file_manager")
    lpe._pkg_sel_ctrl.on_open_export_folder_requested()
    oifm_mock.assert_called_once_with(conanfile_path)
    sleep(1)

    # test show conanfile
    Logger().debug("open show conanfile")
    mock_open_file = mocker.patch("conan_explorer.ui.common.open_file")
    lpe._pkg_sel_ctrl.on_show_conanfile_requested()
    mock_open_file.assert_called_once_with(conanfile_path)
    sleep(1)

    # test install ref 
    Logger().debug("open install ref")
    mock_install_dialog = mocker.patch("package_explorer.sel_controller.ConanInstallDialog")
    lpe._pkg_sel_ctrl.on_install_ref_requested()
    
    mock_install_dialog.assert_called_with(lpe._pkg_sel_ctrl._view,  TEST_REF + ":" + id, 
                    lpe._pkg_sel_ctrl._base_signals.conan_pkg_installed, lock_reference=True)

    # check show buildinfo
    Logger().debug("show buildinfo")
    mock_b = mocker.patch.object(app.conan_api, 'get_conan_buildinfo', return_value="Dummy")
    mocker.patch.object(QtWidgets.QDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Accepted)
    lpe._pkg_sel_ctrl.on_show_build_info()
    if platform.system() == "Linux":
        settings = {'arch': 'x86_64', 'build_type': 'Release', 'compiler': 'gcc', 
                    'compiler.libcxx': 'libstdc++11', 'compiler.version': '9', 'os': 'Linux'}
    else:
        settings = {'arch': 'x86_64', 'build_type': 'Release', 'compiler': 'Visual Studio', 
                'compiler.runtime': 'MD', 'compiler.version': '16', 'os': 'Windows'}
    options = {'fPIC2': 'True', 'shared': 'True', 'variant': 'var1'}
    mock_b.assert_called_with(ConanRef.loads(TEST_REF), settings, options)


@pytest.mark.conanv2
def test_local_package_explorer_tabs(qtbot, mocker, base_fixture, ui_no_refs_config_fixture,
                                     setup_local_package_explorer: LPESetupType):
    """ Test tabs feature
    1. Check that last tab can not be closed
    1. Change to Page, check if the installed package is in the list.
    3. Select view for tab 1
    4. Add tab and switch to tab 2 - no view
    5. Load another package into tab 2 - check model root
    6. Close tab2 - switches back to tab1
    7. Check tab1 still has right path
    """
    _qapp_instance, lpe, main_gui = setup_local_package_explorer

    # 1. Can't close tab 1
    lpe.on_close_tab(0)
    assert lpe._ui.package_tab_widget.tabBar().count() == 2

    # 2 setup packages
    cfr = ConanRef.loads(TEST_REF)
    print("*** Installing package from other platform ***")
    if platform.system() == "Windows":
        conan_install_ref(TEST_REF, profile="linux")
    else:
        conan_install_ref(TEST_REF, profile="windows")
    from conan_explorer.app.logger import Logger

    installed_pkgs = app.conan_api.get_local_pkgs_from_ref(cfr)
    assert len(installed_pkgs) >= 2
    pkg_id1 = installed_pkgs[0].get("id")
    pkg_id2 = installed_pkgs[1].get("id")
    assert pkg_id1
    assert pkg_id2
    pkg_path1 =  app.conan_api.get_package_folder(cfr, pkg_id1)
    pkg_path2 =  app.conan_api.get_package_folder(cfr, pkg_id2)

    # 3. ensure, that we select the pkg with the correct options
    Logger().debug("Select pkg1")
    assert lpe.select_local_package_from_ref(TEST_REF + ":" + pkg_id1)
    assert lpe._pkg_tabs_ctrl[0]._model  # view selected -> fs_model is set
    assert Path(lpe._pkg_tabs_ctrl[0]._model.rootPath()) == pkg_path1

    #4 
    # switches to + tab and back to create new view
    lpe._ui.package_tab_widget.tabBar().setCurrentIndex(1)
    assert lpe._ui.package_tab_widget.tabBar().currentIndex() == 1
    assert lpe._ui.package_tab_widget.tabBar().count() == 3
    assert lpe._ui.package_tab_widget.tabBar().tabText(1) == "New tab"
    assert "+" in lpe._ui.package_tab_widget.tabBar().tabText(2) 
    assert lpe._pkg_tabs_ctrl[1]._model is None

    # 5
    Logger().debug("Select pkg2")
    lpe.on_pkg_selection_change(TEST_REF, installed_pkgs[1], PkgSelectionType.pkg)
    assert lpe._pkg_tabs_ctrl[1]._model  # view selected -> fs_model is set
    assert Path(lpe._pkg_tabs_ctrl[1]._model.rootPath()) == pkg_path2

    # 6
    lpe.on_close_tab(1)
    assert lpe._ui.package_tab_widget.tabBar().count() == 2
    assert lpe._ui.package_tab_widget.tabBar().currentIndex() == 0

    # 7
    assert Path(lpe._pkg_tabs_ctrl[0]._model.rootPath()) == pkg_path1


@pytest.mark.conanv2
def test_local_package_explorer_simple_functions(qtbot, mocker, base_fixture, 
            ui_no_refs_config_fixture, setup_local_package_explorer: LPESetupType):
    """
    Test simple context menu functions of File View
    1. Change to Page, check if the installed package is in the list.
    2. Expand ref and select the pkg, fileview should open.
        1. Copy file as path - on clipboard
        2. Open terminal - in the same folder as file or the selected folder
        3. Open in File Manager
        4. "Add AppLink to AppGrid"
        5. Edit file
    """
    # disable editor to force open file
    app.active_settings.set(FILE_EDITOR_EXECUTABLE, "UNKNOWN")
    _qapp_instance, lpe, main_gui = setup_local_package_explorer

    from conan_explorer.app.logger import Logger

    cfr = ConanRef.loads(TEST_REF)
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)
    assert id
    assert pkg_path.exists()

    pkg_sel_model = lpe._pkg_sel_ctrl._model
    assert pkg_sel_model

    # ensure, that we select the pkg with the correct options
    Logger().debug("Select pkg")
    assert lpe.select_local_package_from_ref(TEST_REF + ":" + id)
    assert lpe._pkg_tabs_ctrl[0]._model  # view selected -> fs_model is set

    #### Test file context menu functions ###
    # Setup: select a file
    Logger().debug("select a file")
    pkg_root_path = Path(lpe._pkg_tabs_ctrl[0]._model.rootPath())
    selected_pkg_file = pkg_root_path / "conaninfo.txt"
    sel_idx = lpe._pkg_tabs_ctrl[0]._model.index(str(selected_pkg_file), 0)
    lpe._ui.package_file_view.selectionModel().select(sel_idx, SelFlags.ClearAndSelect)

    # 2.1 check copy as path - don't check the clipboard, it has issues in windows with qtbot
    cp_text = lpe._pkg_tabs_ctrl[0].on_copy_file_as_path()
    assert Path(cp_text) == selected_pkg_file

    # 2.2 check open terminal
    Logger().debug("open terminal")
    open_cmd_in_path_mock = mocker.patch("package_explorer.file_controller.open_cmd_in_path")
    lpe._pkg_tabs_ctrl[0].on_open_terminal_in_dir()
    open_cmd_in_path_mock.assert_called_with(pkg_root_path)

    # 2.3 check "open in file manager"
    Logger().debug("open in file manager")
    oifm_mock = mocker.patch("package_explorer.file_controller.open_in_file_manager")
    lpe._pkg_tabs_ctrl[0].on_open_file_in_file_manager(None)
    oifm_mock.assert_called_with(Path(cp_text))

    # 2.4 check "Add AppLink to AppGrid"
    mocker.patch.object(QtWidgets.QInputDialog, 'exec',
                        return_value=QtWidgets.QInputDialog.DialogCode.Accepted)
    mocker.patch.object(QtWidgets.QInputDialog, 'textValue', return_value="Basics")
    mocker.patch.object(AppEditDialog, 'exec', return_value=QtWidgets.QDialog.DialogCode.Accepted)

    lpe._pkg_tabs_ctrl[0].on_add_app_link_from_file()
    # assert that the link has been created
    last_app_link = main_gui.app_grid.model.tabs[0].apps[-1]
    assert last_app_link.executable == "conaninfo.txt"
    assert str(last_app_link.conan_file_reference) == str(cfr)

    # 2.5 check edit file
    # Cheat here: use the selected file as the name of the editor and the file to be opened too 
    # - only check the mocked CLI call
    mock_execute_cmd = mocker.patch("package_explorer.file_controller.execute_cmd")
    app.active_settings.set(FILE_EDITOR_EXECUTABLE, str(selected_pkg_file))

    lpe._pkg_tabs_ctrl[0].on_edit_file()
    mock_execute_cmd.assert_called_with([str(selected_pkg_file), selected_pkg_file.as_posix()], False)

def test_local_package_explorer_file_functions(qtbot, mocker, base_fixture, 
            ui_no_refs_config_fixture, setup_local_package_explorer: LPESetupType):
    """ Test file related context menu functions of File View
    1. Change to Page, check if the installed package is in the list.
    2. Expand ref and select the pkg, fileview should open.
        1. Copy - copy file to clipboard (MIME)
        2. Paste - paste file from  clipboard (MIME)
        3. Cut
        4. Cut-paste
        5. Rename
        6. Delete file
    """
    # disable editor to force open file
    app.active_settings.set(FILE_EDITOR_EXECUTABLE, "UNKNOWN")
    _qapp_instance, lpe, main_gui = setup_local_package_explorer

    from conan_explorer.app.logger import Logger

    cfr = ConanRef.loads(TEST_REF)
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)
    assert id
    assert pkg_path.exists()

    pkg_sel_model = lpe._pkg_sel_ctrl._model
    assert pkg_sel_model

    # ensure, that we select the pkg with the correct options
    Logger().debug("Select pkg")
    assert lpe.select_local_package_from_ref(TEST_REF + ":" + id)
    assert lpe._pkg_tabs_ctrl[0]._model  # view selected -> fs_model is set

    #### Test file context menu functions ###
    # Setup: select a file
    Logger().debug("select a file")
    pkg_root_path = Path(lpe._pkg_tabs_ctrl[0]._model.rootPath())
    selected_pkg_file = pkg_root_path / "conaninfo.txt"
    sel_idx = lpe._pkg_tabs_ctrl[0]._model.index(str(selected_pkg_file), 0)
    lpe._ui.package_file_view.selectionModel().select(sel_idx, SelFlags.ClearAndSelect)

    # 2.1 check copy
    mime_files = lpe._pkg_tabs_ctrl[0].on_files_copy()
    mime_file_text = mime_files[0].toString()
    cp_text = lpe._pkg_tabs_ctrl[0].on_copy_file_as_path()
    assert "file://" in mime_file_text and cp_text in mime_file_text

    # 2.2 check paste
    Logger().debug("check paste")
    config_path: Path = ui_no_refs_config_fixture  # use the config file as test data to be pasted
    data = QtCore.QMimeData()
    url = QtCore.QUrl.fromLocalFile(str(config_path))
    data.setUrls([url])
    _qapp_instance.clipboard().setMimeData(data)
    
    delete_path((pkg_root_path / config_path.name)) # delete file is there
    lpe._pkg_tabs_ctrl[0].on_files_paste()
    # check new file
    check.is_true((pkg_root_path / config_path.name).exists())

    # 2.3 check cut
    # use the previously copied file
    Logger().debug("check cut")
    (pkg_root_path / config_path.name).write_text("TEST")
    sel_idx = lpe._pkg_tabs_ctrl[0]._model.index(str(pkg_root_path / config_path.name), 0)
    lpe._ui.package_file_view.selectionModel().select(sel_idx, SelFlags.ClearAndSelect)

    mime_files = lpe._pkg_tabs_ctrl[0].on_files_cut()
    file_row = lpe._pkg_tabs_ctrl[0]._model.index((pkg_root_path / config_path.name).as_posix(), 0).row()
    check.is_true(file_row in lpe._pkg_tabs_ctrl[0]._model._disabled_rows)

    # 2.4 check cut-paste
    # create a new dir in the pkg to paste into
    try:
        os.remove(str(pkg_root_path / "newdir" / config_path.name))
    except:
        pass
    (pkg_root_path / "newdir").mkdir(exist_ok=True)
    # select dir
    sel_idx = lpe._pkg_tabs_ctrl[0]._model.index(str(pkg_root_path / "newdir"), 0)
    lpe._ui.package_file_view.selectionModel().select(sel_idx, SelFlags.ClearAndSelect)
    lpe._pkg_tabs_ctrl[0].on_files_paste()
    check.is_true((pkg_root_path / "newdir" / config_path.name).exists())

    # 2.5 check rename
    mock_rename_cmd = mocker.patch.object(QtWidgets.QTreeView, 'edit')
    lpe._pkg_tabs_ctrl[0].on_file_rename()

    mock_rename_cmd.assert_called_once()

    # 2.6 check overwrite dialog
    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    # recreate file for file usage in root pkg folder
    (pkg_root_path / config_path.name).write_text("TEST")

    mock_copy_cmd = mocker.patch("package_explorer.file_controller.copy_path_with_overwrite")

    lpe._pkg_tabs_ctrl[0].paste_path(config_path, pkg_root_path / config_path.name)

    mock_copy_cmd.assert_called_with(config_path, pkg_root_path / config_path.name)
    
    # select no in dialog
    mock_copy_cmd = mocker.patch("package_explorer.file_controller.copy_path_with_overwrite")
    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.Cancel)
    
    lpe._pkg_tabs_ctrl[0].paste_path(config_path, pkg_root_path / config_path.name)

    mock_copy_cmd.assert_not_called()

    # 2.7 check auto renaming 
    mock_copy_cmd = mocker.patch("package_explorer.file_controller.copy_path_with_overwrite")
    renamed_file = pkg_root_path / "app_config_empty_refs (2).json"
    assert (pkg_root_path / config_path.name).exists()
    try:
        os.remove(renamed_file) # ensure file does not exist
    except: # nothing to do here
        pass
    lpe._pkg_tabs_ctrl[0].paste_path(pkg_root_path / config_path.name, pkg_root_path / config_path.name)
    mock_copy_cmd.assert_called_with(pkg_root_path / config_path.name, renamed_file)

    # 2.8 check delete
    Logger().debug("delete")
    sel_idx = lpe._pkg_tabs_ctrl[0]._model.index(
        str(pkg_root_path / config_path.name), 0)  # (0, 0, QtCore.QModelIndex())
    lpe._ui.package_file_view.selectionModel().select(sel_idx, SelFlags.ClearAndSelect)
    sleep(1)

    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    lpe._pkg_tabs_ctrl[0].on_file_delete()  # check new file?
    check.is_false((pkg_root_path / config_path.name).exists())

    pkgs = app.conan_api.get_local_pkgs_from_ref(cfr)
    print(f"Found packages: {str(pkgs)}")
    assert len(pkgs)
    another_id = ""
    for pkg in pkgs:
        if pkg.get("id") != id:
            another_id = pkg.get("id")
    assert another_id
    another_pkg_path = app.conan_api.get_package_folder(cfr, another_id)
    assert lpe.select_local_package_from_ref(TEST_REF + ":" + another_id)
    assert Path(lpe._pkg_tabs_ctrl[0]._model.rootPath()) == another_pkg_path


@pytest.mark.conanv2
def test_delete_package_dialog(qtbot, mocker, ui_config_fixture, base_fixture):
    """ Test, that the delete package dialog deletes a reference with id, 
    without id and cancel does nothing"""
    from pytestqt.plugin import _qapp_instance

    cfr = ConanRef.loads(TEST_REF)
    conan_install_ref(TEST_REF)

    # precheck, that the package is found
    found_pkg = app.conan_api.get_local_pkgs_from_ref(cfr)
    assert found_pkg

    pkg_id_to_remove = ""
    if conan_version.minor == 2: # 2 works only with id, 1 can work without
        pkg_id_to_remove = found_pkg.get("id", "")

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.load()
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    lpe = main_gui.page_widgets.get_page_by_type(LocalConanPackageExplorer)

    main_gui.page_widgets.get_button_by_type(type(lpe)).click()   # changes to local explorer page
    lpe._pkg_sel_ctrl._loader.wait_for_finished()
    app.conan_worker.finish_working()

    # check cancel does nothing
    dialog = ConanRemoveDialog(None, TEST_REF, pkg_id_to_remove, None)
    dialog.show()
    dialog.button(dialog.StandardButton.Cancel).clicked.emit()

    found_pkg = app.conan_api.find_best_matching_local_package(cfr)
    assert found_pkg.get("id", "")

    # check without pkg id
    dialog.button(dialog.StandardButton.Yes).clicked.emit()
    lpe._pkg_sel_ctrl._loader.wait_for_finished()

    # check, that the package is deleted
    found_pkg = app.conan_api.find_best_matching_local_package(cfr)
    assert not found_pkg.get("id", "")

    # check with pkg id
    conan_install_ref(TEST_REF)
    dialog = ConanRemoveDialog(None, TEST_REF, found_pkg.get("id", ""), None)
    dialog.show()
    dialog.button(dialog.StandardButton.Yes).clicked.emit()

    lpe._pkg_sel_ctrl._loader.wait_for_finished()

    found_pkg = app.conan_api.find_best_matching_local_package(cfr)
    assert not found_pkg.get("id", "")
