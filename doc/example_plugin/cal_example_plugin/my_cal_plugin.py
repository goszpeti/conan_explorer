from pathlib import Path
from typing import Optional
import sys

from conan_app_launcher.ui import BaseSignals, PluginInterfaceV1, FluentWindow, compile_ui_file_if_newer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

current_dir = Path(__file__).parent

# For standalone execution with no package installed (cna be removed depending on workflow)
sys.path.append(str(current_dir.parent))

# Generates examplu_ui.py, so UI variables resolve in IDE
compile_ui_file_if_newer(current_dir / "example.ui")

class SamplePluginView(PluginInterfaceV1):

    def __init__(self, parent: QWidget, base_signals: Optional["BaseSignals"] = None,
                 page_widgets: Optional["FluentWindow.PageStore"] = None):
        super().__init__(parent, base_signals, page_widgets)
        self._base_signals # access to global Qt signals
        self._page_widgets # access to other views (Caution!)

        # load compiled ui file
        from cal_example_plugin.example_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        # apply an icon which is inverted, when turning on dark mode
        self.set_themed_icon(self._ui.icon_label, str(current_dir / "about.png"), size=(20, 20))
       
        # register load method for load signal (runs when GUI is starting and displays loading screen) 
        self.load_signal.connect(self.load)

    def load(self):
        self._ui.push_button.setText("LoadedText")
        # Page specific right settings menu
        self._init_right_menu()


    def _init_right_menu(self):
        if self._page_widgets is None:
            return
        menu = self._page_widgets.get_side_menu_by_type(type(self))
        assert menu
        menu.reset_widgets()
        menu.add_button_menu_entry(
            "My Button", self.on_option_button, "icons/opened_folder.png")
        menu.add_menu_line()
        menu.add_toggle_menu_entry(
            "My Toggle", self.on_option_toggled, True)

    def on_option_button(self):
        pass

    def on_option_toggled(self):
        pass

if __name__ == "__main__":
    # Standalone execution
    app = QApplication([])
    window = QMainWindow()
    pl = SamplePluginView(window)
    window.setGeometry(pl.geometry())
    pl.load_signal.emit()
    window.show()
    app.exec()
