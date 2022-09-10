
import os
from pathlib import Path
from time import sleep
import conan_app_launcher
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
    """
    from conan_app_launcher.app.logger import Logger
    from pytestqt.plugin import _qapp_instance

    # add 2 more remotes
    os.system("conan remote add local2 http://127.0.0.1:9301/ false")
    os.system("conan remote add local3 http://127.0.0.1:9302/ false")
    # remove potentially created remotes from this testcase
    os.system("conan remote remove local4")
    os.system("conan remote remove New")
    os.system("conan remote remove Edited")

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    app.conan_worker.finish_working()
    conan_conf_view = main_gui.conan_config

    # changes to conan conf page
    main_gui.page_widgets.get_button_by_type(type(conan_conf_view)).click()
    remotes_model = conan_conf_view._remotes_controller.model
    assert remotes_model

    #### 1. check, that the test remotes are in the list
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

    #### 2. Select new remote
    assert conan_conf_view._remotes_controller._select_remote("local3")

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
    last_item = remotes_model.root_item.child_items[-1]
    assert conan_conf_view._remotes_controller._select_remote(last_item.remote.name)
    
    conan_conf_view._ui.remote_move_up_button.click()
    sleep(1)
    remotes_model = conan_conf_view._remotes_controller.model
    second_last_item = remotes_model.root_item.child_items[-2]

    assert second_last_item.remote.name == last_item.remote.name

    # 5. Move this remote down, check order
    conan_conf_view._ui.remote_move_down_button.click()
    sleep(1)
    remotes_model = conan_conf_view._remotes_controller.model
    last_item = remotes_model.root_item.child_items[-1]
    assert second_last_item.remote.name == last_item.remote.name

    # 6. Add a new remote via cli -> push refresh -> new remote should appear
    os.system("conan remote add local4 http://127.0.0.1:9303/ false")
    conan_conf_view._ui.remote_refresh_button.click()
    assert conan_conf_view._remotes_controller._select_remote("local4")

    # 7. Delete the new remote
    # mock cancel -> nothing should change
    # mock OK
    remotes_count = conan_conf_view._remotes_controller.model.root_item.child_count()
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Cancel)
    conan_conf_view._ui.remote_remove.click()
    assert conan_conf_view._remotes_controller._select_remote("local4")
    assert conan_conf_view._remotes_controller.model.root_item.child_count() == remotes_count

    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Yes)
    conan_conf_view._ui.remote_remove.click()
    assert conan_conf_view._remotes_controller.model.root_item.child_count()  == remotes_count - 1

    # 8. Add a new remote via button/dialog -> save
    # mock cancel -> nothing should change
    # mock OK
    remotes_count = conan_conf_view._remotes_controller.model.root_item.child_count()
    mocker.patch.object(conan_app_launcher.ui.views.conan_conf.dialogs.RemoteEditDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Rejected)
    conan_conf_view._ui.remote_add.click()
    assert conan_conf_view._remotes_controller.model.root_item.child_count() == remotes_count

    mocker.patch.object(conan_app_launcher.ui.views.conan_conf.dialogs.RemoteEditDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Accepted)
    conan_conf_view._ui.remote_add.click()
    # can't easily call this, while dialog is opened - so call it on the saved, but now hidden dialog manually
    conan_conf_view.remote_edit_dialog.save()
    conan_conf_view.remote_edit_dialog.save() # save a second time (errors under the hood), to see if Exception from conan is handled
    conan_conf_view._remotes_controller.update()
    assert conan_conf_view._remotes_controller.model.root_item.child_count() == remotes_count + 1

    # 9. Edit the remote -> changes should be reflected in the model
    assert conan_conf_view._remotes_controller._select_remote("New")
    mock_diag = mocker.patch.object(conan_app_launcher.ui.views.conan_conf.dialogs.RemoteEditDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Accepted)
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
    assert edited_remote_item.remote.url == "http://127.0.0.1:9305/"
    assert edited_remote_item.remote.verify_ssl == False

    os.system("conan remote remove Edited")

def test_conan_config_view_remote_login(base_fixture, ui_no_refs_config_fixture, qtbot, mocker):
    # Test login with the local remote
    from pytestqt.plugin import _qapp_instance
    os.system(f"conan user demo -r {TEST_REMOTE_NAME} -p demo")  # todo autogenerate and config

    main_gui = main_window.MainWindow(_qapp_instance)
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    app.conan_worker.finish_working()
    conan_conf_view = main_gui.conan_config

    # changes to conan conf page
    main_gui.page_widgets.get_button_by_type(type(conan_conf_view)).click()
    # select local, invoke dialog, click cancel -> remote user info should not change
    assert conan_conf_view._remotes_controller._select_remote(TEST_REMOTE_NAME)
    mocker.patch.object(conan_app_launcher.ui.views.conan_conf.dialogs.RemoteLoginDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Rejected)
    conan_conf_view._ui.remote_login.click()
    assert app.conan_api.get_remote_user_info(TEST_REMOTE_NAME) == ("demo", True)  # still logged in

    # evaluate dialog, after it closed
    assert conan_conf_view.remote_login_dialog._ui.remote_list.count() == 1
    assert conan_conf_view.remote_login_dialog._ui.password_line_edit.text() == ""
    assert conan_conf_view.remote_login_dialog._ui.name_line_edit.text() == "demo"

    # now enter a wrong password and call save
    conan_conf_view.remote_login_dialog._ui.name_line_edit.setText("wrong")
    conan_conf_view.remote_login_dialog._ui.password_line_edit.setText("wrong")
    conan_conf_view.remote_login_dialog.save()
    # throws error on console, but still logged in
    assert app.conan_api.get_remote_user_info("local") == ("demo", True)
    
    # log out with cli
    os.system("conan user --clean")
    assert app.conan_api.get_remote_user_info("local") == ("None", False)

    # now enter the correct password and call save
    conan_conf_view.remote_login_dialog._ui.name_line_edit.setText("demo")
    conan_conf_view.remote_login_dialog._ui.password_line_edit.setText("demo")
    conan_conf_view.remote_login_dialog.save()

    # logged in
    assert app.conan_api.get_remote_user_info("local") == ("demo", True)
    # assert password is empty (does not really test, if it worked correctly)
    assert conan_conf_view.remote_login_dialog._ui.password_line_edit.text() == ""
