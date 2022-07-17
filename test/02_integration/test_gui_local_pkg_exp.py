
import os
from pathlib import Path
from test.conftest import TEST_REF, TEST_REF_OFFICIAL

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.dialogs.conan_remove import ConanRemoveDialog
from conan_app_launcher.ui.views.app_grid.tab import AppEditDialog
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt
# For debug:
# from pytestqt.plugin import _qapp_instance
# while True:
#    _qapp_instance.processEvents()


def test_delete_package_dialog(base_fixture, ui_config_fixture, qtbot, mocker):
    """ Test, that the delete package dialog deletes a reference with id, 
    without id and cancel does nothing"""
    from pytestqt.plugin import _qapp_instance

    cfr = ConanFileReference.loads(TEST_REF_OFFICIAL)
    os.system(f"conan install {TEST_REF_OFFICIAL}")

    # precheck, that the package is found
    found_pkg = app.conan_api.get_local_pkgs_from_ref(cfr)
    assert found_pkg

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.load()
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    lpe = main_gui.local_package_explorer

    main_gui.page_widgets.get_button_by_type(type(lpe)).click()   # changes to local explorer page
    lpe._pkg_sel_model_loader.wait_for_finished()
    app.conan_worker.finish_working()

    # check cancel does nothing
    dialog = ConanRemoveDialog(None, TEST_REF_OFFICIAL, "", None)
    dialog.show()
    dialog.button(dialog.Cancel).clicked.emit()

    found_pkg = app.conan_api.find_best_local_package(cfr)
    assert found_pkg.get("id", "")

    # check without pkg id
    dialog.button(dialog.Yes).clicked.emit()
    lpe._pkg_sel_model_loader.wait_for_finished()

    # check, that the package is deleted
    found_pkg = app.conan_api.find_best_local_package(cfr)
    assert not found_pkg.get("id", "")

    # check with pkg id
    os.system(f"conan install {TEST_REF_OFFICIAL}")
    dialog = ConanRemoveDialog(None, TEST_REF_OFFICIAL, found_pkg.get("id", ""), None)
    dialog.show()
    dialog.button(dialog.Yes).clicked.emit()

    lpe._pkg_sel_model_loader.wait_for_finished()


    found_pkg = app.conan_api.find_best_local_package(cfr)
    assert not found_pkg.get("id", "")


def test_local_package_explorer(base_fixture, ui_no_refs_config_fixture, qtbot, mocker):
    """
    Test Local Pacakge Explorer functions.
    1. Change to Page, check if the installed package is in the list.
    2. Select a ref, nothing should change.
    3. Expand ref and select the pkg, fileview should open.
    Test context menu functions of Pkg Selection View
    1. Copy ref - Copy conan reference to clipboard (no pkg id!)
    2. Open export folder - Opens in file manager
    3. Show Conanfile - Opens in default texteditor
    Test context menu functions of File View
    1. Copy file as path - on clipboard
    2. Open terminal - in the same folder as file or the selected folder
    3. Open in File Manager
    4. Copy - copy file to clipboard (MIME)
    5. Paste - paste file from  clipboard (MIME)
    6. Delete file
    """
    from conan_app_launcher.app.logger import Logger
    from pytestqt.plugin import _qapp_instance

    cfr = ConanFileReference.loads(TEST_REF)
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)
    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)
    app.conan_worker.finish_working()
    lpe = main_gui.local_package_explorer

    main_gui.page_widgets.get_button_by_type(type(lpe)).click()   # changes to local explorer page   
    lpe._pkg_sel_model_loader.wait_for_finished()

    # restart reload (check for thread safety)
    lpe._ui.refresh_button.clicked.emit()
    lpe._pkg_sel_model_loader.wait_for_finished()

    pkg_sel_model = lpe.pkg_sel_model
    assert pkg_sel_model
    assert lpe._ui.package_select_view.model().columnCount() == 1

    # check, that the ref + pkg is in the list
    found_tst_pkg = False
    for pkg in pkg_sel_model.root_item.child_items:
        if pkg.item_data[0] == TEST_REF:
            found_tst_pkg = True
            # check it's child
            assert pkg_sel_model.get_quick_profile_name(pkg.child(0)) in [
                "Windows_x64_vs16_release", "Linux_x64_gcc9_release"]
    assert found_tst_pkg

    # select package (ref, not profile)
    assert lpe.select_local_package_from_ref(TEST_REF, refresh=True)
    Logger().debug("Selected ref")
    assert not lpe.fs_model  # view not changed

    # ensure, that we select the pkg with the correct options
    Logger().debug("Select pkg")
    assert lpe.select_local_package_from_ref(TEST_REF + ":" + id, refresh=True)

    assert lpe.fs_model  # view selected -> fs_model is set
    assert Path(lpe.fs_model.rootPath()) == pkg_path

    ### Test pkg reference context menu functions ###
    # test copy ref
    Logger().debug("test copy ref")
    lpe.on_copy_ref_requested()
    assert QtWidgets.QApplication.clipboard().text() == str(cfr)
    conanfile = app.conan_api.get_conanfile_path(cfr)

    # test open export folder
    Logger().debug("open export folder")
    import conan_app_launcher.ui.views.package_explorer.local_packages as lp
    mocker.patch.object(lp, 'open_in_file_manager')
    lpe.on_open_export_folder_requested()
    lp.open_in_file_manager.assert_called_once_with(conanfile)

    # test show conanfile
    Logger().debug("open show conanfile")
    mocker.patch.object(lp, 'open_file')
    lpe.on_show_conanfile_requested()
    lp.open_file.assert_called_once_with(conanfile)

    #### Test file context menu functions ###
    # select a file
    Logger().debug("select a file")

    root_path = Path(lpe.fs_model.rootPath())
    file = root_path / "conaninfo.txt"
    sel_idx = lpe.fs_model.index(str(file), 0)
    lpe._ui.package_file_view.selectionModel().select(sel_idx, QtCore.QItemSelectionModel.ClearAndSelect)

    # check copy as path - don't check the clipboard, it has issues in windows with qtbot
    cp_text = lpe.on_copy_file_as_path()
    assert Path(cp_text) == file

    # check open terminal
    Logger().debug("open terminal")

    pid = lpe.on_open_terminal_in_dir()
    assert pid > 0
    import signal
    os.kill(pid, signal.SIGTERM)

    # check "open in file manager"
    Logger().debug("open in file manager")
    lpe.on_open_file_in_file_manager(None)
    lp.open_in_file_manager.assert_called_with(Path(cp_text))

    # check "Add AppLink to AppGrid"
    mocker.patch.object(QtWidgets.QInputDialog, 'exec_',
                        return_value=QtWidgets.QInputDialog.Accepted)
    mocker.patch.object(QtWidgets.QInputDialog, 'textValue',
                        return_value="Basics")
    mocker.patch.object(AppEditDialog, 'exec_', return_value=QtWidgets.QDialog.Accepted)

    lpe.on_add_app_link_from_file()
    # assert that the link has been created
    last_app_link = main_gui.app_grid.model.tabs[0].apps[-1]
    assert last_app_link.executable == "conaninfo.txt"
    assert str(last_app_link.conan_file_reference) == str(cfr)

    # Check copy
    mime_file = lpe.on_file_copy()
    mime_file_text = mime_file.toString()
    assert "file://" in mime_file_text and cp_text in mime_file_text

    # check paste
    Logger().debug("check paste")
    config_path: Path = ui_no_refs_config_fixture  # use the config file as test data to be pasted
    data = QtCore.QMimeData()
    url = QtCore.QUrl.fromLocalFile(str(config_path))
    data.setUrls([url])
    _qapp_instance.clipboard().setMimeData(data)
    lpe.on_file_paste()  # check new file
    assert (root_path / config_path.name).exists()

    # check delete
    Logger().debug("delete")
    sel_idx = lpe.fs_model.index(
        str(root_path / config_path.name), 0)  # (0, 0, QtCore.QModelIndex())
    lpe._ui.package_file_view.selectionModel().select(sel_idx, QtCore.QItemSelectionModel.ClearAndSelect)
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)
    lpe.on_file_delete()  # check new file?
    assert not (root_path / config_path.name).exists()
