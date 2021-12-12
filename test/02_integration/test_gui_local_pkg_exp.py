"""
Test the self written qt gui components, which can be instantiated without
using the whole application (standalone).
"""
from PyQt5 import QtWidgets
from pathlib import Path
import os
import time
import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher.ui import main_window
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt
TEST_REF = "zlib/1.2.11@_/_"

# For debug:
# from pytestqt.plugin import _qapp_instance
# while True:
#    _qapp_instance.processEvents()


def wait_for_loading_pkgs(main_gui):
    from pytestqt.plugin import _qapp_instance

    # wait for loading thread
    main_gui.local_package_explorer._init_model_thread
    while not main_gui.local_package_explorer._init_model_thread:
        time.sleep(1)
    while not main_gui.local_package_explorer._init_model_thread.isFinished():
        _qapp_instance.processEvents()


def test_pkgs_sel_view(ui_no_refs_config_fixture, qtbot, mocker):
    cfr = ConanFileReference.loads(TEST_REF)
    pkg_path = app.conan_api.get_path_or_install(cfr)
    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    main_gui.ui.main_toolbox.setCurrentIndex(1)  # changes to local explorer page
    wait_for_loading_pkgs(main_gui)

    model = main_gui.local_package_explorer.pkg_sel_model
    assert model
    assert main_gui.ui.package_select_view.findChildren(QtCore.QObject)
    assert main_gui.ui.package_select_view.model().columnCount() == 1

    model.root_item.item_data[0] == "Packages"
    model.root_item.child_count() == main_gui.ui.package_select_view.model().rowCount()

    found_tst_pkg = False
    for pkg in model.root_item.child_items:
        if pkg.item_data[0] == str(cfr):
            found_tst_pkg = True
            # check it's child
            assert pkg.child(0).data(0) in ["Windows_x64_vs16_release", "Linux_x64_gcc9_release"]
    assert found_tst_pkg
    # select package (ref, not profile)
    index = model.index(0, 0, QtCore.QModelIndex())
    item = index.internalPointer()
    for i in range(model.root_item.child_count()):
        index = model.index(i, 0, QtCore.QModelIndex())
        item = model.index(i, 0, QtCore.QModelIndex()).internalPointer()
        print(item.item_data[0])
        if item.item_data[0] == str(cfr):
            break
    view_model = main_gui.ui.package_select_view.model()
    sel_model = main_gui.ui.package_select_view.selectionModel()
    sel_model.select(view_model.mapFromSource(
        index), QtCore.QItemSelectionModel.ClearAndSelect)
    sel_model.currentIndex()
    assert not main_gui.local_package_explorer.fs_model  # view not changed

    # check right view initialized at the correct path and path got written in label
    main_gui.ui.package_select_view.expand(view_model.mapFromSource(index))
    chi = index.child(0, 0)
    item = chi.internalPointer()
    sel_model.select(view_model.mapFromSource(chi), QtCore.QItemSelectionModel.ClearAndSelect)
    main_gui.ui.package_select_view.selectionModel().currentRowChanged.emit(index, chi)
    assert main_gui.local_package_explorer.fs_model  # view selected
    assert Path(main_gui.local_package_explorer.fs_model.rootPath()) == pkg_path

    # Test Context menu functions
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

    # select a file


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

# def test_add_app_link_from_local_explorer

# def test_file_in_pkg_cntx_menu
