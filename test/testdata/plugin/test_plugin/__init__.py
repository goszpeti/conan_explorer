

from typing import Optional
from conan_explorer.ui import BaseSignals, PluginInterfaceV1, PageStore, PluginDescription
from PySide6.QtWidgets import QWidget, QDialog

class TestPlugin(PluginInterfaceV1):

    def __init__(self, parent: QWidget, plugin_description: PluginDescription,
                 base_signals: Optional["BaseSignals"] = None,
                 page_widgets: Optional["PageStore"] = None):
        super().__init__(parent, plugin_description, base_signals, page_widgets)
        self._dialog = QDialog(self)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

    # Standalone execution
    app = QApplication([])
    window = QMainWindow()
    pl = TestPlugin(window, {})
    window.setGeometry(pl.geometry())
    pl.load_signal.emit()
    window.show()
    app.exec()