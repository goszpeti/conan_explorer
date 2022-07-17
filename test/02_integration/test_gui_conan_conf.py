
import os
from pathlib import Path
from test.conftest import TEST_REF, TEST_REF_OFFICIAL, TEST_REMOTE_NAME, TEST_REMOTE_URL

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.views.app_grid.tab import AppEditDialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QItemSelectionModel, QModelIndex

Qt = QtCore.Qt
# For debug:
# from pytestqt.plugin import _qapp_instance
# while True:
#    _qapp_instance.processEvents()



def test_conan_config_view_remotes(base_fixture, ui_no_refs_config_fixture, qtbot, mocker):
    """
    Test Local Pacakge Explorer functions.
    Add 2 remotes in addition to the local one.
    1. Change to page, check if the remotes are in the list.
    2. Select a new remote, nothing should change.
    3. Disable/Enable remote, check with conan API
    4. Move last remote up, check order
    5. Move this remote down, check order
    6. Add a new remote via cli -> push refresh -> new remote should appear
    7. Delete the new remote
    8. Add a new remote via button/dialog -> save
    9. Edit the remote -> changes should be reflected in the model
    10. Delete the remote
    11. Test login with the local remote TODO???
    """
    from conan_app_launcher.app.logger import Logger
    from pytestqt.plugin import _qapp_instance

    # add 2 more remotes
    os.system("conan remote add local2 http://127.0.0.1:9301/ false")
    os.system("conan remote add local3 http://127.0.0.1:9302/ false")

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    app.conan_worker.finish_working()
    conan_conf_view = main_gui.conan_config

    # changes to conan conf page
    main_gui.page_widgets.get_button_by_type(type(conan_conf_view)).click()
    from pytestqt.plugin import _qapp_instance
    # while True:
    #    _qapp_instance.processEvents()
    remotes_model = conan_conf_view._remotes_model
    assert remotes_model

    #### 1. check, that the test remotes are in the list
    row_remote_to_test = 0
    row = 0
    for remote_item in remotes_model.root_item.child_items:
        if remote_item.item_data[0] == TEST_REMOTE_NAME:
            assert remote_item.item_data[1] in TEST_REMOTE_URL
            assert remote_item.item_data[2] == "False"
            assert remote_item.item_data[3] == "demo"
            assert remote_item.item_data[4] == "True"
        if remote_item.item_data[0] in ["local2", "local3"]:
            assert "http://127.0.0.1:930" in remote_item.item_data[1]
            assert remote_item.item_data[2] == "False"
            assert remote_item.item_data[3] == "None"
            assert remote_item.item_data[4] == "False"
            row_remote_to_test = row

    #### 2. Select new remote
    sel_model = conan_conf_view._ui.remotes_tree_view.selectionModel()
    index = remotes_model.index(row_remote_to_test, 0, QModelIndex())
    assert index.data(0) == "local3"
    sel_model.select(index, QItemSelectionModel.ClearAndSelect)

    #### 3. Test Disable/Enable
    conan_conf_view._ui.remote_toggle_disabled.click()

    remotes = app.conan_api.get_remotes(include_disabled=True)
    for remote in remotes:
        if remote.name == "local3":
            assert remote.disabled

    conan_conf_view._ui.remote_toggle_disabled.click()

    remotes = app.conan_api.get_remotes()
    for remote in remotes:
        if remote.name == "local3":
            assert not remote.disabled
    # 4. Move last remote up, check order
    # 5. Move this remote down, check order
    # 6. Add a new remote via cli -> push refresh -> new remote should appear
    # 7. Delete the new remote
    # 8. Add a new remote via button/dialog -> save
    # 9. Edit the remote -> changes should be reflected in the model
    # 10. Delete the remote
    # 11. Test login with the local remote TODO???
    return


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


def test_conan_config_view_profiles(base_fixture, ui_no_refs_config_fixture, qtbot, mocker):
    pass