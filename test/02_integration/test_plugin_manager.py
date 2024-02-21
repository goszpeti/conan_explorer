
from conan_explorer.ui.views.plugins_manager.plugins import PluginsPage

import conan_explorer  # for mocker
import conan_explorer.app as app
from conan_explorer.ui.main_window import MainWindow
from PySide6 import QtCore, QtWidgets

Qt = QtCore.Qt


def test_plugin_page(qtbot, base_fixture, mocker):
    """
    Test plugin view basic functionality, but only with mocked functionality
    1. Display model 
    2. Add plugin
    3. Remove plugin
    """

    from pytestqt.plugin import _qapp_instance
    # first with ref + id in constructor
    main_window = MainWindow(_qapp_instance)
    main_window.load()
    qtbot.addWidget(main_window)
    main_window.show()
    qtbot.waitExposed(main_window)
    plugins_page = main_window.plugins_page
    conan_conf_view = main_window.page_widgets.get_page_by_type(PluginsPage)
    main_window.page_widgets.get_button_by_type(type(conan_conf_view)).click()

    # check default plugins in model
    model = plugins_page._ui.plugins_tree_view.model()
    assert model.rowCount(QtCore.QModelIndex()) == 3

    # check add button
    # mock _plugin_handler.add_plugin(plugin_path)
    plugin_file_path = base_fixture.testdata_path / "plugin" / "plugins_minimal_valid.ini"

    mocker.patch.object(QtWidgets.QFileDialog, 'exec', return_value=QtWidgets.QDialog.DialogCode.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles', return_value=[str(plugin_file_path)])
    # mock_add_func = mocker.patch("conan_explorer.ui.plugin.handler.PluginHandler.add_plugin")

    plugins_page._ui.add_plugin_button.click()

    # mock_add_func.assert_called_with(str(plugin_file_path))
    model = plugins_page._ui.plugins_tree_view.model()
    assert model.rowCount(QtCore.QModelIndex()) == 4

    # check remove button
    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    mock_remove_func = mocker.patch("conan_explorer.ui.plugin.handler.PluginHandler.remove_plugin")
    sel_model = plugins_page._controller._view.selectionModel()
    # select built-in plugin
    sel_model.select(model.index(0, 0, QtCore.QModelIndex()), QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)

    plugins_page._ui.remove_plugin_button.click()
    
    mock_remove_func.assert_not_called()

    # select external plugin
    sel_model.select(model.index(3, 0, QtCore.QModelIndex()), QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
    
    plugins_page._ui.remove_plugin_button.click()

    mock_remove_func.assert_called_with(str(plugin_file_path.resolve()))

    main_window.close()
