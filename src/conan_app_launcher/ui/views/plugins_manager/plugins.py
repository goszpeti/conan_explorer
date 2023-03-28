from typing import TYPE_CHECKING, Optional
from conan_app_launcher import __version__
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox
from conan_app_launcher.ui.plugin.plugins import PluginHandler, ThemedWidget, PluginInterfaceV1

from .controller import PluginController


if TYPE_CHECKING:
    from conan_app_launcher.ui.fluent_window import FluentWindow
    from conan_app_launcher.ui.main_window import BaseSignals


class PluginsPage(PluginInterfaceV1):

    def __init__(self, parent: QWidget, plugin_handler: PluginHandler, base_signals: Optional["BaseSignals"] = None,
                 page_widgets: Optional["FluentWindow.PageStore"] = None):
        super().__init__(parent)
        from .plugins_ui import Ui_Form
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.setObjectName("plugin_manager")
        self._controller = PluginController(self._ui.plugins_tree_view, plugin_handler)
        self._controller.update()
        self.set_themed_icon(self._ui.add_plugin_button, "icons/plus_rounded.svg")
        self.set_themed_icon(self._ui.remove_plugin_button, "icons/delete.svg")

        # self.set_themed_icon(self._ui.search_icon, "icons/search_packages.svg", size=(20,20))
        self._ui.plugins_tree_view.selectionModel().selectionChanged.connect(self.on_plugin_selected)
        self._ui.add_plugin_button.clicked.connect(self.on_add)
        self._ui.remove_plugin_button.clicked.connect(self.on_remove)

    def on_plugin_selected(self):
        """ Show path of plugin and disable remove for builtins """
        plugin = self._controller.get_selected_source_item()
        if not plugin:
            return
        self._ui.path_label.setText(plugin.plugin_path)
        if plugin.data(1) == "built-in":
            self._ui.remove_plugin_button.setEnabled(False)
        else:
            self._ui.remove_plugin_button.setEnabled(True)

    def on_add(self):
        """ Open File dialog with filter for ini files, then load the plugin"""
        dialog = QFileDialog(parent=self, caption="Select Plugin description file",
                             filter="Plugin files (*.ini)")
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
        if selected_item.data(1) == "built-in":
            return
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Remove plugin?")
        message_box.setText(f"Are you sure, you want to remove the plugin {selected_item.data(0)}?")
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setIcon(QMessageBox.Icon.Question)
        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
         
            self._controller.remove_plugin(selected_item.plugin_path)
            self._controller.update()

