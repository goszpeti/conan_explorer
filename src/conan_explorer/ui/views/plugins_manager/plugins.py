from typing import TYPE_CHECKING, Optional
from conan_explorer import AUTHOR, BUILT_IN_PLUGIN, DEBUG_LEVEL
from conan_explorer import base_path

from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PySide6.QtGui import QShowEvent
from conan_explorer.ui.plugin import PluginDescription, PluginHandler, PluginInterfaceV1
from conan_explorer.ui.views.plugins_manager.model import PluginModelItem

from .controller import PluginController


if TYPE_CHECKING:
    from conan_explorer.ui.fluent_window import FluentWindow
    from conan_explorer.ui.main_window import BaseSignals


class PluginsPage(PluginInterfaceV1):
    """ GUI representation of plugin_handler """

    def __init__(self, parent: QWidget, plugin_handler: PluginHandler, base_signals: Optional["BaseSignals"] = None,
                 page_widgets: Optional["FluentWindow.PageStore"] = None):
        plugin_descr = PluginDescription("Plugin Manager", BUILT_IN_PLUGIN, AUTHOR, "", "", "", " ", False, "")
        super().__init__(parent, plugin_descr)
        from .plugins_ui import Ui_Form
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.setObjectName("plugin_manager")
        self._controller = PluginController(self._ui.plugins_tree_view, plugin_handler)
        self._controller.update()
        self.set_themed_icon(self._ui.add_plugin_button, "icons/plus_rounded.svg")
        self.set_themed_icon(self._ui.remove_plugin_button, "icons/delete.svg")
        self.set_themed_icon(self._ui.reload_plugin_button, "icons/refresh.svg")

        # self.set_themed_icon(self._ui.search_icon, "icons/search_packages.svg", size=(20,20))
        self._ui.plugins_tree_view.selectionModel().selectionChanged.connect(self.on_plugin_selected)
        self._ui.add_plugin_button.clicked.connect(self.on_add)
        self._ui.remove_plugin_button.clicked.connect(self.on_remove)
        self._ui.reload_plugin_button.clicked.connect(self.on_reload)

        if DEBUG_LEVEL < 1: # only in dev mode
            self._ui.reload_plugin_button.hide()

    def showEvent(self, a0: QShowEvent) -> None:
        self.resize_file_columns()
        return super().showEvent(a0)

    def resize_file_columns(self):
        if not self._ui.plugins_tree_view:
            return
        for i in reversed(range(5 - 1)):
            self._ui.plugins_tree_view.resizeColumnToContents(i)

    def on_plugin_selected(self):
        """ Show path of plugin and disable remove for builtins """
        plugin = self._controller.get_selected_source_item()
        if not plugin:
            return
        self._ui.path_label.setText(plugin.plugin_path)
        if plugin.data(1) == BUILT_IN_PLUGIN:
            self.set_themed_icon(self._ui.remove_plugin_button, "icons/delete.svg", 
                                 force_light_mode=True)
            self._ui.remove_plugin_button.setEnabled(False)
        else:
            self.set_themed_icon(self._ui.remove_plugin_button, "icons/delete.svg")
            self._ui.remove_plugin_button.setEnabled(True)

    def on_add(self):
        """ Open File dialog with filter for ini files, then load the plugin"""
        dialog = QFileDialog(parent=self, caption="Select Plugin description file",
                             filter="Plugin files (*.ini)", directory=str(base_path))
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            new_file = dialog.selectedFiles()[0]
            self._controller.add_plugin(new_file)
        self._controller.update()

    def on_remove(self):
        """ Unload plugin and deregister from ini"""
        selected_item = self._controller.get_selected_source_item()
        if not selected_item:
            return
        if selected_item.data(1) == BUILT_IN_PLUGIN:
            return
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Remove plugin?")
        message_box.setText(f"Are you sure, you want to remove the plugin {selected_item.data(0)}?")
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
        message_box.setIcon(QMessageBox.Icon.Question)
        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            self._controller.remove_plugin(selected_item.plugin_path)
            self._controller.update()

    def on_reload(self):
        selected_item: Optional[PluginModelItem] = self._controller.get_selected_source_item()
        if not selected_item:
            return
        self._controller.reload_plugin(selected_item.data(0))
