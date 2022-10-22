from pathlib import Path
from typing import Optional

from conan_app_launcher.ui import BaseSignals, PluginInterface
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget

current_dir = Path(__file__).parent


class SamplePluginView(PluginInterface):

    def __init__(self, parent: QWidget, base_signals: "BaseSignals", 
                 page_widgets: Optional["FluentWindow.PageStore"] = None):
        # Add minimize and maximize buttons
        super().__init__(parent, base_signals, page_widgets)
        self._base_signals
        self._page_widgets
        self.ui = uic.loadUi(str(current_dir / "example.ui"), self)
        self.add_themed_icon(self.ui.icon_label, str(current_dir / "about.png"), size=(20, 20))
        self.load_signal.connect(self.load)

    def load(self):
        self.ui.push_button.setText("LoadedText")

if __name__ == "__main__":
    app = QApplication([])
    window = QMainWindow()
    pl = SamplePluginView(window, BaseSignals(None, None, None))
    window.show()
    app.exec()
