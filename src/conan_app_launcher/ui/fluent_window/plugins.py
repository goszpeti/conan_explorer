import configparser
import os
from dataclasses import dataclass
from distutils.util import strtobool
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

import conan_app_launcher.app as app
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.settings import PLUGINS_SECTION_NAME
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QSizePolicy

from .fluent_window import ThemedWidget

if TYPE_CHECKING:
    from conan_app_launcher.ui.fluent_window import FluentWindow
    from conan_app_launcher.ui.main_window import BaseSignals

@dataclass
class PluginDescription():
    name: str
    version: str
    author: str
    icon: str
    import_path: str
    plugin_class: str
    description: str
    side_menu: bool

class PluginFile():

    @staticmethod
    def register(name: str, path: str):
        app.active_settings.add(name, path, PLUGINS_SECTION_NAME)


    @staticmethod
    def read_file(path: str) -> List[PluginDescription]:
        if not os.path.exists(path):
            pass # error
        plugins = []
        parser = configparser.ConfigParser()
        parser.read(path, encoding="UTF-8")
        for section in parser.keys():
            if parser.default_section == section:
                continue
            plugin_info = parser[section]
            try:
                name = plugin_info.get("name")
                assert name, "field 'name' is required"
                version = plugin_info.get("version", "None")

                icon_str = plugin_info.get("icon")
                assert icon_str, "field 'icon' is required"
                if version == "built-in":
                    icon = icon_str
                else:
                    icon = str(Path(path).parent / icon_str)

                import_path = str(Path(path).parent / plugin_info.get("import_path"))
                assert import_path, "field 'import_path' is required"
                # import_path =  / import_path_str
                # assert import_path.exists(), f"import_path {str(import_path)} does not exist"
                # if import_path.is_dir(): # needs an __init__.py
                #     import_path = import_path / "__init__.py"
                #     assert import_path.exists(), f"import_path {str(import_path)} does not exist"

                plugin_class = plugin_info.get("plugin_class")
                assert plugin_class, "field 'plugin_class' is required"
                description = plugin_info.get("description", "")
                author = plugin_info.get("author", "Unknown")

                side_menu = strtobool(plugin_info.get("side_menu", "False"))
                desc = PluginDescription(name, version, author, icon, import_path, plugin_class, description, side_menu)
                plugins.append(desc)
            except Exception as e:
                Logger().error(f"Can't read {section} plugin information from {path}: {str(e)}.")

        return plugins

    @staticmethod
    def write(path: str, infos: List[PluginDescription]):
        parser = configparser.ConfigParser()

        for i in range(len(infos)):
            section_name = "PluginDescription" + str(i)
            parser.add_section(section_name)
            for setting, value in infos[i].__dict__.items():
                parser[section_name][setting] = value
        with open(path, 'w', encoding="utf8") as fd:
            parser.write(fd)



class PluginInterface(ThemedWidget):
    """
    Class to extend the application with custom views.
    """
    # Return a signal, which will be called, when the Ui should load.
    # Connect this to your actual load method.
    # This is used for asynchronous loading.
    load_signal = Signal()

    def __init__(self, parent: QWidget, base_signals: Optional["BaseSignals"]=None, page_widgets: Optional["FluentWindow.PageStore"]=None) -> None:
        ThemedWidget.__init__(self, parent)
        self._base_signals = base_signals
        self._page_widgets = page_widgets
        #self._base_signals.page_size_changed.emit(self)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, a0) -> None:
        # handles maximum size on resize
        if not self._base_signals:
            return
        self._base_signals.page_size_changed.emit(self)

