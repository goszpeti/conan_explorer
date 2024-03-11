
import pytest
from conan_explorer.settings import FILE_EDITOR_EXECUTABLE
from test.conftest import TEST_REF

import conan_explorer  # for mocker
import conan_explorer.app as app
from conan_explorer.ui.main_window import MainWindow
from conan_explorer.conan_wrapper.types import ConanRef
from PySide6 import QtCore, QtWidgets
from conan_explorer.ui.views import ConanSearchView
from conan_explorer.ui.views import LocalConanPackageExplorer

Qt = QtCore.Qt

@pytest.mark.conanv2
def test_conan_search_view(qtbot, base_fixture, mock_clipboard, mocker):
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
    # disable editor to force open file
    app.active_settings.set(FILE_EDITOR_EXECUTABLE, "UNKNOWN")
    from pytestqt.plugin import _qapp_instance
    cfr = ConanRef.loads(TEST_REF)
    # first with ref + id in constructor
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)
    assert id
    main_window = MainWindow(_qapp_instance)
    main_window.conan_remotes_updated.emit()
    main_window.load()
    qtbot.addWidget(main_window)
    main_window.show()
    qtbot.waitExposed(main_window)
    search_dialog = main_window.page_widgets.get_page_by_type(ConanSearchView)
    main_window.page_widgets.get_button_by_type(ConanSearchView).click()

    # expand and collapse remotes list, simply to see if it does not crash
    search_dialog._ui.remote_toggle_button.click()
    search_dialog._ui.remote_toggle_button.click() # collapse again

    # enter short search term -> search button disabled
    search_dialog._ui.search_line.setText("ex")
    assert not search_dialog._ui.search_button.isEnabled()

    # search for the test ref name: example -> 2 versions
    search_dialog._ui.search_line.setText("example")
    assert search_dialog._ui.search_button.isEnabled()
    search_dialog._ui.search_button.clicked.emit()

    # wait for loading
    search_dialog._search_controller._loader.wait_for_finished()

    # assert basic view
    model = search_dialog._search_controller._model
    assert model
    assert search_dialog._ui.search_results_tree_view.model().columnCount() == 3  # fixed 3 coloumns
    # while True:
    #     _qapp_instance.processEvents()

    assert model.root_item.item_data[0] == "Packages"
    assert model.root_item.child_count() == 2

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
    sel_model.select(ref_view_index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
    search_dialog._search_controller.on_copy_ref_requested()
    mock_clipboard.setText.assert_called_with(TEST_REF)

    # check copy id ref
    # select id
    sel_model.select(pkg_view_index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
    search_dialog._search_controller.on_copy_ref_requested()
    mock_clipboard.setText.assert_called_with(TEST_REF + ":" + id)

    # check install
    mock_install_dialog = mocker.patch("conan_search.controller.ConanInstallDialog")
    search_dialog._search_controller.on_install_pkg_requested()
    mock_install_dialog.assert_called_with(search_dialog._search_controller._view, 
                                           TEST_REF + ":" + id, search_dialog._search_controller.conan_pkg_installed)

    # check show conanfile
    mock_open_file = mocker.patch("conan_explorer.ui.common.open_file")
    search_dialog._search_controller.on_show_conanfile_requested()
    conanfile = app.conan_api.get_export_folder(cfr) / "conanfile.py"
    mock_open_file.assert_called_with(conanfile)

    # check check open in local pkg explorer
    search_dialog.on_show_in_pkg_exp()
    lpe = main_window.page_widgets.get_page_by_type(LocalConanPackageExplorer)

    assert id == lpe._pkg_sel_ctrl.get_selected_conan_pkg_info().get("id", "")

    # select 3 packages and compare them
    main_window.page_widgets.get_button_by_type(ConanSearchView).click()
    index = model.get_index_from_item(ref_item.child_items[0])
    ref_view_index_ch1 = proxy_view_model.mapFromSource(index)
    sel_model.select(
        ref_view_index_ch1, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
    index = model.get_index_from_item(ref_item.child_items[1])
    ref_view_index_ch2 = proxy_view_model.mapFromSource(index)
    sel_model.select(
        ref_view_index_ch2, QtCore.QItemSelectionModel.SelectionFlag.Select)
    index = model.get_index_from_item(ref_item.child_items[2])
    ref_view_index_ch3 = proxy_view_model.mapFromSource(index)
    sel_model.select(
        ref_view_index_ch3, QtCore.QItemSelectionModel.SelectionFlag.Select)
    
    mock_diff_dialog = mocker.patch("conan_search.controller.PkgDiffDialog")
    search_dialog.diff_pkgs_action.trigger()
    mock_diff_dialog.assert_called_once()
    assert mock_diff_dialog.mock_calls[1][0] == "().add_diff_item"
    assert mock_diff_dialog.mock_calls[2][0] == "().add_diff_item"
    assert mock_diff_dialog.mock_calls[3][0] == "().add_diff_item"
    assert mock_diff_dialog.mock_calls[4][0] == "().show"

    # check greyyed out context menu elements
    elem_pos = search_dialog._ui.search_results_tree_view.visualRect(ref_view_index_ch2)
    mocker.patch.object(search_dialog.select_cntx_menu, 'exec')
    search_dialog.on_pkg_context_menu_requested(elem_pos.center())
    assert search_dialog.diff_pkgs_action.isEnabled()
    assert search_dialog.show_in_pkg_exp_action.isEnabled()

    search_dialog.hide()
    main_window.close()
