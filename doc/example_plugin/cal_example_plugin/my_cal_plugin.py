from pathlib import Path
from typing import Optional
import sys

import conan_explorer.app as app
from conan_explorer.app.logger import Logger # for global singletons
from conan_explorer.ui import (BaseSignals, PluginInterfaceV1, FluentWindow, 
                                   PluginDescription, compile_ui_file_if_newer)
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

current_dir = Path(__file__).parent

# For standalone execution with no package installed (can be removed depending on workflow)
sys.path.append(str(current_dir.parent))

### Generates example_ui.py, so UI variables resolve in IDE
# NOTE: You can edit the .ui file in a GUI editor with the Qt Designer application!
# You can install it via the PySide6-Addons pip package.
# It will be beside the python entry point scripts called pyside6-designer
# Then this will automatically recreate the .py representation of it, if the application is started.
compile_ui_file_if_newer(current_dir / "example.ui")

class SamplePluginView(PluginInterfaceV1):

    def __init__(self, parent: QWidget, plugin_description: PluginDescription,
                 base_signals: Optional["BaseSignals"] = None,
                 page_widgets: Optional["FluentWindow.PageStore"] = None):
        super().__init__(parent, plugin_description, base_signals, page_widgets)
        self._base_signals # access to global Qt signals
        self._page_widgets # access to other views (Caution!)

        # load compiled ui file
        from cal_example_plugin.example_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        # apply an icon which is inverted, when turning on dark mode
        self.set_themed_icon(self._ui.icon_label, str(current_dir / "about.svg"), 
                             size=(20, 20))
       
        # register load method for load signal
        # runs when GUI is starting and displays loading screen
        self.load_signal.connect(self.load)


    def load(self):
        self._ui.push_button.setText("LoadedText")
        # Page specific right settings menu
        self._init_right_menu()
        self._ui.tree_widget.expandAll()
        self._resize_columns()

    def _init_right_menu(self):
        """ Sets up the right side menu """
        if self._page_widgets is None:  # only available, when running embedded
            return
        # retrieve it's own empty menu from the page store
        menu = self._page_widgets.get_side_menu_by_type(type(self))
        assert menu
        menu.reset_widgets()
        menu.add_button_menu_entry("My Button", self.on_option_button, 
                                                            "icons/opened_folder.svg")
        menu.add_menu_line()
        menu.add_toggle_menu_entry("My Toggle", self.on_option_toggled, True)

    def on_option_button(self):
        """ Callback of side menu option button"""
        Logger().info(str(app.conan_api.get_all_local_refs()))

    def on_option_toggled(self):
        """ Callback of side menu toggle button"""
        pass

    def _resize_columns(self):
        """ Resizes every coloumnm to contents, with the first coloumn being last """
        count = self._ui.tree_widget.columnCount()
        for i in reversed(range(count-1)):
            self._ui.tree_widget.resizeColumnToContents(i)

if __name__ == "__main__":
    # Standalone execution
    qapp = QApplication([])
    window = QMainWindow()
    pl = SamplePluginView(window, {})
    window.setGeometry(pl.geometry())
    pl.load_signal.emit()
    window.show()
    qapp.exec()
