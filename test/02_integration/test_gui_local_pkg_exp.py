"""
Test the self written qt gui components, which can be instantiated without
using the whole application (standalone).
"""
from test.conftest import TEST_REF
from PyQt5 import QtWidgets
from pathlib import Path
import os
import time
import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher.ui import main_window
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets
from conan_app_launcher.ui.modules.app_grid.tab import AppEditDialog

Qt = QtCore.Qt
# For debug:
# from pytestqt.plugin import _qapp_instance
# while True:
#    _qapp_instance.processEvents()


def wait_for_loading_pkgs(main_gui: main_window.MainWindow):
    from pytestqt.plugin import _qapp_instance

    # wait for loading thread
    main_gui.local_package_explorer._pkg_sel_model_loader.load_thread
    while not main_gui.local_package_explorer._pkg_sel_model_loader.load_thread:
        time.sleep(1)
    while not main_gui.local_package_explorer._pkg_sel_model_loader.load_thread.isFinished():
        _qapp_instance.processEvents()


def test_pkgs_sel_view(ui_no_refs_config_fixture, qtbot, mocker):
    from pytestqt.plugin import _qapp_instance
    cfr = ConanFileReference.loads(TEST_REF)
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)
    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    main_gui.ui.main_toolbox.setCurrentIndex(1)  # changes to local explorer page
    wait_for_loading_pkgs(main_gui)

    model = main_gui.local_package_explorer.pkg_sel_model
    assert model
    assert main_gui.ui.package_select_view.model().columnCount() == 1

    # check, that the ref + pkg is in the list
    found_tst_pkg = False
    for pkg in model.root_item.child_items:
        if pkg.item_data[0] == str(cfr):
            found_tst_pkg = True
            # check it's child
            assert model.get_quick_profile_name(pkg.child(0)) in [
                "Windows_x64_vs16_release", "Linux_x64_gcc9_release"]
    assert found_tst_pkg

    # select package (ref, not profile)
    index = model.index(0, 0, QtCore.QModelIndex())
    item = index.internalPointer()
    for i in range(model.root_item.child_count()):
        index = model.index(i, 0, QtCore.QModelIndex())
        item = model.index(i, 0, QtCore.QModelIndex()).internalPointer()
        if item.item_data[0] == str(cfr):
            break
    view_model = main_gui.ui.package_select_view.model()

    main_gui.local_package_explorer.select_local_package_from_ref(
        TEST_REF)
    assert not main_gui.local_package_explorer.fs_model  # view not changed

    # select pkg to check file view initalizes at the correct path and path got written in label
    main_gui.ui.package_select_view.expand(view_model.mapFromSource(index))
    # ensure, that we select the pkg with the correct options
    main_gui.local_package_explorer.select_local_package_from_ref(
        TEST_REF + ":" + id)
    assert main_gui.local_package_explorer.fs_model  # view selected -> fs_model is set
    assert Path(main_gui.local_package_explorer.fs_model.rootPath()) == pkg_path

    ### Test pkg reference context menu functions ###
    # test copy ref
    main_gui.local_package_explorer.on_copy_ref_requested()
    assert QtWidgets.QApplication.clipboard().text() == str(cfr)
    conanfile = app.conan_api.get_conanfile_path(cfr)
    # test open export folder
    import conan_app_launcher.ui.modules.package_explorer.local_packages as lp
    mocker.patch.object(lp, 'open_in_file_manager')
    main_gui.local_package_explorer.on_open_export_folder_requested()
    lp.open_in_file_manager.assert_called_once_with(conanfile)
    # test show conanfile
    mocker.patch.object(lp, 'open_file')
    main_gui.local_package_explorer.on_show_conanfile_requested()
    lp.open_file.assert_called_once_with(conanfile)

    #### Test file context menu functions ###
    # select a file
    root_path = Path(main_gui.local_package_explorer.fs_model.rootPath())
    file = root_path / "conaninfo.txt"
    sel_idx = main_gui.local_package_explorer.fs_model.index(str(file), 0)
    main_gui.ui.package_file_view.selectionModel().select(sel_idx, QtCore.QItemSelectionModel.ClearAndSelect)

    # check copy as path
    cp_text = main_gui.local_package_explorer.on_copy_file_as_path()
    assert Path(cp_text) == file

    # check open terminal
    pid = main_gui.local_package_explorer.on_open_terminal_in_dir()
    assert pid > 0
    import signal
    # TODO check pid is running
    os.kill(pid, signal.SIGTERM)
    # Check copy
    main_gui.local_package_explorer.on_file_copy()
    # tODO mock call
    assert "file://" in QtWidgets.QApplication.clipboard().text() and cp_text in QtWidgets.QApplication.clipboard().text()

    # check paste
    config_path: Path = ui_no_refs_config_fixture  # use the config file as test data to be pasted
    data = QtCore.QMimeData()
    url = QtCore.QUrl.fromLocalFile(str(config_path))
    data.setUrls([url])
    QtWidgets.QApplication.clipboard().setMimeData(data)
    main_gui.local_package_explorer.on_file_paste()  # check new file
    assert (root_path / config_path.name).exists()

    # check "open in file manager"
    main_gui.local_package_explorer.on_open_file_in_file_manager(None)
    lp.open_in_file_manager.assert_called_with(Path(cp_text))

    # check "Add AppLink to AppGrid"
    mocker.patch.object(QtWidgets.QInputDialog, 'exec_',
                        return_value=QtWidgets.QInputDialog.Accepted)
    mocker.patch.object(QtWidgets.QInputDialog, 'textValue',
                        return_value="Basics")
    mocker.patch.object(AppEditDialog, 'exec_', return_value=QtWidgets.QDialog.Accepted)

    main_gui.local_package_explorer.on_add_app_link_from_file()
    # assert that the link has been created
    last_app_link = main_gui.app_grid.model.tabs[0].apps[-1]
    assert last_app_link.executable == "conaninfo.txt"
    assert str(last_app_link.conan_file_reference) == str(cfr)

    # check delete
    sel_idx = main_gui.local_package_explorer.fs_model.index(
        str(root_path / config_path.name), 0)  # (0, 0, QtCore.QModelIndex())
    main_gui.ui.package_file_view.selectionModel().select(sel_idx, QtCore.QItemSelectionModel.ClearAndSelect)
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)
    main_gui.local_package_explorer.on_file_delete()  # check new file?
    assert not (root_path / config_path.name).exists()


def test_delete_package_dialog(base_fixture, ui_config_fixture, qtbot, mocker):
    """ Test, that the delete package dialog deletes a reference with id, 
    without id and cancel does nothing"""
    cfr = ConanFileReference.loads(TEST_REF)
    os.system(f"conan install {TEST_REF}")

    # precheck, that the package is found
    found_pkg = app.conan_api.get_local_pkgs_from_ref(cfr)
    assert found_pkg

    main_gui = main_window.MainWindow()
    main_gui.load()
    main_gui.show()
    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    # check cancel does nothing
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Cancel)
    main_gui.local_package_explorer.delete_conan_package_dialog(TEST_REF, None)
    found_pkg = app.conan_api.find_best_local_package(cfr)
    assert found_pkg.get("id", "")

    # check without pkg id
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)
    main_gui.local_package_explorer.delete_conan_package_dialog(TEST_REF, None)

    wait_for_loading_pkgs(main_gui)

    # check, that the package is deleted
    found_pkg = app.conan_api.find_best_local_package(cfr)
    assert not found_pkg.get("id", "")

    # check with pkg id
    os.system(f"conan install {TEST_REF}")
    main_gui.local_package_explorer.delete_conan_package_dialog(TEST_REF, None)

    wait_for_loading_pkgs(main_gui)

    found_pkg = app.conan_api.find_best_local_package(cfr)
    assert not found_pkg.get("id", "")

# def test_refresh_pkg_list_button
