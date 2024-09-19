
import os
from pathlib import Path
from time import sleep

import pytest
import conan_explorer
from conan_explorer.app.system import delete_path
from conan_explorer.conan_wrapper import ConanApiFactory as ConanApi
from conan_explorer.conan_wrapper.types import ConanRef
from conan_explorer.ui.views.conan_conf.dialogs.editable_edit_dialog import EditableEditDialog
from conan_explorer.ui.views.conan_conf.editable_model import EditableModel, EditableModelItem
from test.conftest import (TEST_REMOTE_NAME, TEST_REMOTE_URL, TEST_REF, PathSetup, 
                    login_test_remote, logout_all_remotes, add_remote, remove_remote)
from conan_explorer import conan_version

import conan_explorer.app as app  # using global module pattern
from conan_explorer.ui import main_window
from PySide6 import QtCore, QtWidgets
from conan_explorer.ui.views.conan_conf import ConanConfigView

Qt = QtCore.Qt

def start_main_and_switch_to_config_view(ui_no_refs_config_fixture, qtbot):
    from pytestqt.plugin import _qapp_instance
    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    app.conan_worker.finish_working()
    conan_conf_view = main_gui.page_widgets.get_page_by_type(ConanConfigView)
    main_gui.page_widgets.get_button_by_type(type(conan_conf_view)).click()
    return conan_conf_view, main_gui


@pytest.mark.conanv2
def test_conan_config_view_remotes(qtbot, base_fixture: PathSetup, ui_no_refs_config_fixture, mocker):
    """
    Test Local Pacakge Explorer functions.
    Add 2 remotes in addition to the local one.
    1. Change to page, check if the remotes are in the list.
    2. Select a new remote, nothing should change.
    3. Disable/Enable remote, check with conan API
    4. Move last remote up, check order
    5. Move this remote down, check order
    5a. Move last remote to top
    5b. Move top remote to last
    6. Add a new remote via cli -> push refresh -> new remote should appear
    7. Delete the new remote
    8. Add a new remote via button/dialog -> save
    9. Edit the remote -> changes should be reflected in the model
    10. Delete the remote
    """
    from pytestqt.plugin import _qapp_instance
    # add 2 more remotes
    add_remote("local2", "http://127.0.0.1:9301/")
    add_remote("local3", "http://127.0.0.1:9302/")

    # remove potentially created remotes from this testcase
    remove_remote("local4")
    remove_remote("New")
    remove_remote("Edited")

    sleep(1)

    try:
        conan_conf_view, main_gui = start_main_and_switch_to_config_view(ui_no_refs_config_fixture, qtbot)

        # test revisions
        # Revisions are on via env-var
        assert conan_conf_view._ui.revision_enabled_checkbox.checkState()

        # changes to conan conf page
        main_gui.page_widgets.get_button_by_type(type(conan_conf_view)).click()
        conan_conf_view._remotes_controller.update()
        remotes_model = conan_conf_view._remotes_controller._model
        assert remotes_model

        #### 1. check, that the test remotes are in the list
        assert len(remotes_model.items()) >= 3
        for remote_item in remotes_model.items():
            if remote_item.item_data[0] == TEST_REMOTE_NAME:
                assert remote_item.item_data[1] in TEST_REMOTE_URL
                assert remote_item.item_data[2] == "False"
                assert remote_item.item_data[3] == "demo"
                assert remote_item.item_data[4] == "True"
            if remote_item.item_data[0] in ["local2", "local3"]:
                assert "http://127.0.0.1:930" in remote_item.item_data[1]
                assert remote_item.item_data[2] == "False"
                assert str(remote_item.item_data[3]) == "None"
                assert remote_item.item_data[4] == "False"

        #### 2. Select new remote
        assert conan_conf_view._remotes_controller._select_remote("local3")

        #### 3. Test Disable/Enable
        conan_conf_view._ui.remote_toggle_disabled_button.click()

        remotes = app.conan_api.get_remotes(include_disabled=True)
        for remote in remotes:
            if remote.name == "local3":
                assert remote.disabled

        conan_conf_view._ui.remote_toggle_disabled_button.click()

        remotes = app.conan_api.get_remotes()
        for remote in remotes:
            if remote.name == "local3":
                assert not remote.disabled

        # 4. Move last remote up, check order
        last_item = remotes_model.items()[-1]
        assert conan_conf_view._remotes_controller._select_remote(last_item.name)
        
        conan_conf_view._ui.remote_move_up_button.click()
        sleep(1)
        remotes_model = conan_conf_view._remotes_controller._model
        second_last_item = remotes_model.items()[-2]

        assert second_last_item.name == last_item.name

        # 5. Move this remote down, check order
        conan_conf_view._ui.remote_move_down_button.click()
        sleep(1)
        remotes_model = conan_conf_view._remotes_controller._model
        last_item = remotes_model.items()[-1]
        assert second_last_item.name == last_item.name

        # 5a. Move last remote to top
        last_item = remotes_model.items()[-1]
        assert conan_conf_view._remotes_controller._select_remote(last_item.name)
        conan_conf_view._ui.remote_move_top_button.click()
        sleep(1)
        remotes_model = conan_conf_view._remotes_controller._model
        first_item = remotes_model.items()[0]

        assert first_item.name == last_item.name

        # 5b. Move top remote to last
        assert conan_conf_view._remotes_controller._select_remote(first_item.name)
        conan_conf_view._ui.remote_move_bottom_button.click()
        sleep(1)
        remotes_model = conan_conf_view._remotes_controller._model
        last_item = remotes_model.items()[-1]
        assert first_item.name == last_item.name

        # 6. Add a new remote via cli -> push refresh -> new remote should appear
        add_remote("local4", "http://127.0.0.1:9303/ ")
        conan_conf_view._ui.remote_refresh_button.click()
        assert conan_conf_view._remotes_controller._select_remote("local4")

        # 7. Delete the new remote
        # mock cancel -> nothing should change
        # mock OK
        remotes_count = conan_conf_view._remotes_controller._model.root_item.child_count()
        mocker.patch.object(QtWidgets.QDialog, 'exec',
                            return_value=QtWidgets.QDialog.DialogCode.Rejected)
        conan_conf_view._ui.remote_remove_button.click()
        assert conan_conf_view._remotes_controller._model.root_item.child_count() == remotes_count

        mocker.patch.object(QtWidgets.QDialog, 'exec',
                            return_value=QtWidgets.QDialog.DialogCode.Accepted)
        conan_conf_view._ui.remote_remove_button.click()
        assert conan_conf_view._remotes_controller._model.root_item.child_count()  == remotes_count - 1

        # 8. Add a new remote via button/dialog -> save
        # mock cancel -> nothing should change
        # mock OK
        remotes_count = conan_conf_view._remotes_controller._model.root_item.child_count()
        mocker.patch.object(QtWidgets.QDialog, 'exec',
                            return_value=QtWidgets.QDialog.DialogCode.Rejected)
        conan_conf_view._ui.remote_add_button.click()
        assert conan_conf_view._remotes_controller._model.root_item.child_count() == remotes_count

        mocker.patch.object(QtWidgets.QDialog, 'exec',
                            return_value=QtWidgets.QDialog.DialogCode.Accepted)
        conan_conf_view._ui.remote_add_button.click()
        # can't easily call this, while dialog is opened - so call it on the saved, but now hidden dialog manually
        conan_conf_view.remote_edit_dialog.save()
        conan_conf_view.remote_edit_dialog.save() # save a second time (errors under the hood), to see if Exception from conan is handled
        conan_conf_view._remotes_controller.update()
        assert conan_conf_view._remotes_controller._model.root_item.child_count() == remotes_count + 1

        # 9. Edit the remote -> changes should be reflected in the model
        assert conan_conf_view._remotes_controller._select_remote("New")
        mock_diag = mocker.patch.object(QtWidgets.QDialog, 'exec',
                            return_value=QtWidgets.QDialog.DialogCode.Accepted)
        conan_conf_view.on_remote_edit(None)
        mock_diag.assert_called_once()

        # now call directly to gain access to the dialog
        assert conan_conf_view.remote_edit_dialog._ui.name_line_edit.text() == "New"
        assert conan_conf_view.remote_edit_dialog._ui.url_line_edit.text() == ""
        assert conan_conf_view.remote_edit_dialog._ui.verify_ssl_checkbox.isChecked()
        
        conan_conf_view.remote_edit_dialog._ui.name_line_edit.setText("Edited")
        conan_conf_view.remote_edit_dialog._ui.url_line_edit.setText("http://127.0.0.1:9305/")
        conan_conf_view.remote_edit_dialog._ui.verify_ssl_checkbox.setChecked(False)
        conan_conf_view.remote_edit_dialog.save()
        conan_conf_view._ui.remote_refresh_button.click()
        assert conan_conf_view._remotes_controller._select_remote("Edited")
        edited_remote_item = conan_conf_view._remotes_controller.get_selected_remote()
        assert edited_remote_item
        assert edited_remote_item.url == "http://127.0.0.1:9305/"
        assert edited_remote_item.verify_ssl == False
    finally:
        remove_remote("Edited")
        remove_remote("local2")
        remove_remote("local3")
        remove_remote("local4")
        main_gui.close()

@pytest.mark.conanv2
def test_conan_config_view_remote_login(qtbot, base_fixture, ui_no_refs_config_fixture, mocker):
    """ Test login with the local remote """
    login_test_remote(TEST_REMOTE_NAME)
    conan_conf_view, main_gui = start_main_and_switch_to_config_view(ui_no_refs_config_fixture, qtbot)

    conan = ConanApi().init_api()

    # changes to conan conf page
    main_gui.page_widgets.get_button_by_type(type(conan_conf_view)).click()
    # select local, invoke dialog, click cancel -> remote user info should not change
    assert conan_conf_view._remotes_controller._select_remote(TEST_REMOTE_NAME)

    mocker.patch.object(QtWidgets.QDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Rejected)
    conan_conf_view._ui.remote_login_button.click()
    assert conan.get_remote_user_info(TEST_REMOTE_NAME) == ("demo", True)  # still logged in

    # evaluate dialog, after it closed
    assert conan_conf_view.remote_login_dialog._ui.remote_list.count() == 1
    assert conan_conf_view.remote_login_dialog._ui.password_line_edit.text() == ""
    assert conan_conf_view.remote_login_dialog._ui.name_line_edit.text() == "demo"

    # now enter a wrong password and call save
    conan_conf_view.remote_login_dialog._ui.name_line_edit.setText("wrong")
    conan_conf_view.remote_login_dialog._ui.password_line_edit.setText("wrong")
    conan_conf_view.remote_login_dialog.on_ok()
    # throws error on console, but still logged in
    assert conan.get_remote_user_info("local") == ("demo", True)
    
    # log out with cli
    logout_all_remotes()
    assert conan.get_remote_user_info("local") == ("None", False)

    # now enter the correct password and call save
    conan_conf_view.remote_login_dialog._ui.name_line_edit.setText("demo")
    conan_conf_view.remote_login_dialog._ui.password_line_edit.setText("demo")
    conan_conf_view.remote_login_dialog.on_ok()

    # logged in
    assert conan.get_remote_user_info("local") == ("demo", True)
    # assert password is empty (does not really test, if it worked correctly)
    assert conan_conf_view.remote_login_dialog._ui.password_line_edit.text() == ""

@pytest.fixture
def profile_fixture():
    """ Delete all created profiles in case of errors for test_conan_config_view_profiles"""
    profiles_path = app.conan_api.get_profiles_path()
    delete_path(profiles_path / "new_profile_add")
    delete_path(profiles_path / "new_profile_rename")
    delete_path(profiles_path / "new_profile_test")
    yield
    delete_path(profiles_path / "new_profile_add")
    delete_path(profiles_path / "new_profile_rename")
    delete_path(profiles_path / "new_profile_test")


@pytest.mark.conanv2
def test_conan_config_view_profiles(qtbot, base_fixture: PathSetup, profile_fixture, ui_no_refs_config_fixture, mocker):
    """ Test all profile related functions """
    conan_conf_view, main_gui = start_main_and_switch_to_config_view(ui_no_refs_config_fixture, qtbot)

    main_gui.page_widgets.get_button_by_type(type(conan_conf_view)).click()

    # check, that all conan profiles are displayed
    model = conan_conf_view._ui.profiles_list_view.model()
    profiles_path = app.conan_api.get_profiles_path()
    default_profile_path = profiles_path / "default"

    profile_model_count = model.rowCount(0)

    assert profile_model_count == len(app.conan_api.get_profiles())
    index = model.get_index_from_profile("default")

    # check, that selecting a profile displays it in the bottom pane
    sel_model = conan_conf_view._ui.profiles_list_view.selectionModel()
    sel_model.select(index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
   
    assert conan_conf_view._ui.profiles_text_browser.toPlainText() == default_profile_path.read_text()
    
    # add a new profile
    mocker.patch.object(QtWidgets.QInputDialog, 'getText', return_value=["new_profile_add", True])
    conan_conf_view._ui.profile_add_button.click()
    #model = conan_conf_view._ui.profiles_list_view.model()
    assert profile_model_count +1 == model.rowCount(0)

    # select and rename the profile
    index = model.get_index_from_profile("new_profile_add")
    sel_model.select(index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)

    mocker.patch.object(QtWidgets.QInputDialog, 'getText', return_value=["new_profile_rename", True])
    conan_conf_view._ui.profile_rename_button.click()
    assert "new_profile_rename" in model._profiles

    # enter some content
    index = model.get_index_from_profile("new_profile_rename")
    sel_model.select(index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
    new_profile_content = "[settings]\nos=Linux\n"
    conan_conf_view._ui.profiles_text_browser.setText(new_profile_content)

    # save and reload
    conan_conf_view._ui.profile_save_button.click()
    sleep(1) # wait for file being created
    new_profile_path = profiles_path / "new_profile_rename"

    # check, that content is changed
    assert new_profile_path.read_text() == new_profile_content

    # remove profile
    index = model.get_index_from_profile("new_profile_rename")
    sel_model.select(index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    conan_conf_view._ui.profile_remove_button.click()
    sleep(1) # wait for file being deleted
    assert not new_profile_path.exists()

    # check, that reload button works
    ## create new profile file
    new_profile_path = profiles_path / "new_profile_test"
    new_profile_path.touch()

    ## click reload
    conan_conf_view._ui.profile_refresh_button.click()

    ## check model
    assert "new_profile_test" in model._profiles

@pytest.mark.conanv2
def test_conan_config_view_editables(qtbot, base_fixture: PathSetup, profile_fixture, 
                                     ui_no_refs_config_fixture, mocker):
    # delete potentially already added test editable before starting the gui
    new_ref_obj = ConanRef.loads(TEST_REF + "INT")
    assert app.conan_api.remove_editable(new_ref_obj)
    assert app.conan_api.remove_editable(ConanRef.loads(TEST_REF + "INT2"))

    conan_conf_view, main_gui = start_main_and_switch_to_config_view(ui_no_refs_config_fixture, qtbot)
    model: EditableModel = conan_conf_view._ui.editables_ref_view.model()
    new_editable_path = base_fixture.testdata_path / "conan"
    if conan_version.major == 2:
        new_editable_path /= "conanfileV2.py"

    def editable_dialog_actions():
        conan_conf_view.remote_edit_dialog._ui.name_line_edit.setText(TEST_REF + "int")
        conan_conf_view.remote_edit_dialog._ui.path_line_edit.setText(str(new_editable_path))
        conan_conf_view.remote_edit_dialog._ui.button_box.accepted.emit()
    # add a new ref via dialog
    mocker.patch.object(QtWidgets.QDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Accepted,
                        side_effect=editable_dialog_actions)
    conan_conf_view._ui.editables_add_button.click()

    index = model.get_index_from_ref(TEST_REF + "int")
    assert index.internalPointer() # index is existing

    # edit the ref 
    # select it
    sel_model = conan_conf_view._ui.editables_ref_view.selectionModel()
    sel_model.select(index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)

    def editable_dialog_actions():
        conan_conf_view.remote_edit_dialog._ui.name_line_edit.setText(TEST_REF + "int2")
        conan_conf_view.remote_edit_dialog._ui.button_box.accepted.emit()
    # add a new ref via dialog
    mocker.patch.object(QtWidgets.QDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Accepted,
                        side_effect=editable_dialog_actions)
    conan_conf_view._ui.editables_edit_button.click()

    index = model.get_index_from_ref(TEST_REF + "int2")
    assert index.internalPointer()  # index is existing
    assert model.get_index_from_ref(TEST_REF + "int") is None

    # delete it
    sel_model.select(index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    conan_conf_view._ui.editables_remove_button.click()
    model: EditableModel = conan_conf_view._ui.editables_ref_view.model()

    assert model.get_index_from_ref(TEST_REF + "int2") is None

@pytest.mark.conanv2
def test_conan_config_save_config(qtbot, base_fixture: PathSetup, profile_fixture,
                                  ui_no_refs_config_fixture, mocker):

    conan_conf_view, main_gui = start_main_and_switch_to_config_view(
        ui_no_refs_config_fixture, qtbot)
    config_text = conan_conf_view._ui.config_file_text_browser.toPlainText()
    assert app.conan_api.get_config_file_path().read_text() == config_text

    conan_conf_view._ui.config_file_text_browser.setText(config_text + "\n#TEST_STRING")
    conan_conf_view.on_save_config_file()

    config_text_changed = conan_conf_view._ui.config_file_text_browser.toPlainText()
    # write back original text
    app.conan_api.get_config_file_path().write_text(config_text)
    assert "TEST_STRING" in config_text_changed

