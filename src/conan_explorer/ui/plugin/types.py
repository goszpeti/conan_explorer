
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Signal, SignalInstance, Qt
from PySide6.QtWidgets import QWidget, QSizePolicy


from ..fluent_window.fluent_window import ThemedWidget

if TYPE_CHECKING:
    from conan_explorer.ui.fluent_window import FluentWindow
    from conan_explorer.ui.main_window import BaseSignals

@dataclass
class PluginDescription():
    """ Plugin meta information for runtime """
    name: str  # Display name, also used as page title
    version: str
    author: str
    icon: str  # left menu icon
    import_path: str  # this path will be placed on python path or a file directly
    plugin_class: str  # class to be loaded from module
    description: str
    side_menu: bool  # will create a side menu, which can be accessed by page_widgets
    conan_versions: str  # spec to restrict the plugin to a conan version (will be greyed out)


class PluginInterfaceV1(ThemedWidget):
    """
    Class to extend the application with custom views.
    """
    # Return a signal, which will be called, when the Ui should load.
    # Connect this to your actual load method.
    # This is used for asynchronous loading.
    load_signal: SignalInstance = Signal()  # type: ignore

    def __init__(self, parent: QWidget, plugin_description: PluginDescription,
                 base_signals: Optional["BaseSignals"] = None,
                 page_widgets: Optional["FluentWindow.PageStore"] = None) -> None:
        ThemedWidget.__init__(self, parent)
        self._base_signals = base_signals
        self._page_widgets = page_widgets
        # save PluginDescription to query data from outside
        self.plugin_description = plugin_description
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        size_policy.setVerticalStretch(0)
        self.setSizePolicy(size_policy)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def resizeEvent(self, a0) -> None:
        # handles maximum size on resize
        if not self._base_signals:
            super().resizeEvent(a0)
            return
        self._base_signals.page_size_changed.emit(self)
        super().resizeEvent(a0)

