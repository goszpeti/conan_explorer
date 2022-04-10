"""
Test the self written qt gui base, which can be instantiated without
using the whole application (standalone).
"""
import os
import sys
import traceback
from test.conftest import TEST_REF
from time import sleep

import conan_app_launcher  # for mocker
import conan_app_launcher.app as app
from conan_app_launcher.ui.main_window import MainWindow
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt


def test_conan_search_dialog(base_fixture, qtbot, mock_clipboard, mocker):
    """ Tests, that the Conan search dialog:
    - search button does not work under 3 characters
    - can find the test packages from the name
    - installed packages/pkgs have the correct internal flag
    - After item expansion, the pkgs are shown
    Context menu actions work:
    - Copy ref and pkg
    - Install dialog call
    - Show conanfile call
    - Show in Local Package Explorer
    """
    cfr = ConanFileReference.loads(TEST_REF)
    # first with ref + id in constructor
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)
    from pytestqt.plugin import _qapp_instance
    main_window = MainWindow(_qapp_instance)
    search_dialog = main_window.search_dialog  # ConanSearchDialog(root_obj, main_window.conan_pkg_installed,
    # main_window.conan_pkg_removed, main_window.page_widgets)

    qtbot.addWidget(main_window)
    main_window.show()
    qtbot.waitExposed(main_window)

    # enter short search term -> search button disabled
    search_dialog._ui.search_line.setText("ex")
    assert not search_dialog._ui.search_button.isEnabled()

    # search for the test ref name: example -> 2 versions
    search_dialog._ui.search_line.setText("example")
    assert search_dialog._ui.search_button.isEnabled()
    search_dialog._ui.search_button.clicked.emit()

    # wait for loading
    search_dialog._pkg_result_loader.wait_for_finished()

    # assert basic view
    model = search_dialog._pkg_result_model
    assert model
    assert search_dialog._ui.search_results_tree_view.findChildren(QtCore.QObject)
    assert search_dialog._ui.search_results_tree_view.model().columnCount() == 3  # fixed 3 coloumns

    assert model.root_item.item_data[0] == "Packages"
    assert model.root_item.child_count() == 3

    # expand package -> assert number of packages and itemdata
    # check installed ref ist highlighted

    ref_item = model.get_item_from_ref(TEST_REF)
    assert ref_item
    assert ref_item.is_installed
    index = model.get_index_from_item(ref_item)
    proxy_view_model = search_dialog._ui.search_results_tree_view.model()
    ref_view_index = proxy_view_model.mapFromSource(index)
    search_dialog._ui.search_results_tree_view.expand(ref_view_index)

    while not ref_item.child_items:
        _qapp_instance.processEvents()
    # check in child items that installed pkg id is highlighted
    pkg_found = False
    for child_item in ref_item.child_items:
        if child_item.get_conan_ref() == TEST_REF + ":" + id:
            pkg_found = True
            assert child_item.is_installed
            break
    assert pkg_found
    pkg_view_index = proxy_view_model.mapFromSource(model.get_index_from_item(child_item))

    # check context menu actions
    # check copy recipe ref
    # select ref
    sel_model = search_dialog._ui.search_results_tree_view.selectionModel()
    sel_model.select(ref_view_index, QtCore.QItemSelectionModel.ClearAndSelect)
    search_dialog.on_copy_ref_requested()
    mock_clipboard.setText.assert_called_with(TEST_REF)

    # check copy id ref
    # select id
    sel_model.select(pkg_view_index, QtCore.QItemSelectionModel.ClearAndSelect)
    search_dialog.on_copy_ref_requested()
    mock_clipboard.setText.assert_called_with(TEST_REF + ":" + id)

    # check install
    mock_install_dialog = mocker.patch(
        "conan_app_launcher.ui.views.conan_search.conan_search.ConanInstallDialog")
    search_dialog.on_install_pkg_requested()
    mock_install_dialog.assert_called_with(search_dialog, TEST_REF + ":" + id, main_window.conan_pkg_installed)

    # check show conanfile
    mock_open_file = mocker.patch(
        "conan_app_launcher.ui.views.conan_search.conan_search.open_file")
    search_dialog.on_show_conanfile_requested()
    conanfile = app.conan_api.get_export_folder(cfr) / "conanfile.py"
    mock_open_file.assert_called_with(conanfile)

    # check check open in local pkg explorer
    search_dialog.on_show_in_pkg_exp()
    assert id == main_window.local_package_explorer.get_selected_conan_pkg_info().get("id", "")

    search_dialog.hide()
