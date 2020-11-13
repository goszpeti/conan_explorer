import json
import platform
import jsonschema

from pathlib import Path
from typing import List
from conans.model.ref import ConanFileReference

import conan_app_launcher as this
from conan_app_launcher.base import Logger


class AppEntry():
    """ Representation of an app entry of the config schema """

    def __init__(self, name, package_id: str, executable: Path, args: str, icon: str,
                 console_application: bool, config_file_path: Path):
        self.name = name
        self.executable = executable
        self.icon = Path()
        self.package_folder = Path()
        self.is_console_application = console_application
        self.args = args
        # validate package id
        try:
            self.package_id = ConanFileReference.loads(package_id)
        except Exception as error:
            # errors happen fairly often, keep going
            self.package_id = ConanFileReference.loads("YouGaveA/0.0.1@Wrong/Reference")
            Logger().error(f"Conan ref id invalid {str(error)}")

        # validate icon path
        if icon.startswith("//"):
            Logger().warning("Icon relative to package currently not implemented")
        elif icon and not Path(icon).is_absolute():
            self.icon = config_file_path.parent / icon
        else:
            self.icon = Path(icon)
        if not self.icon.is_file():
            Logger().error(f"Icon {str(self.icon)} for '{name}' not found")
            self.icon = this.base_path / "assets" / "default_app_icon.png"

    def validate_with_conan_info(self, package_folder: Path):
        """ Callback when conan operation is done and paths can be validated"""
        self.package_folder = package_folder
        # adjust path on windows, if no file extension is given
        if platform.system() == "Windows" and not self.executable.suffix:
            self.executable = self.executable.with_suffix(".exe")
        full_path = Path(self.package_folder / self.executable)
        if not full_path.is_file():
            Logger().error(f"Cannot find {str(self.executable)} in package {str(self.package_id)}")
        self.executable = full_path


class TabEntry():
    """ Representation of a tab entry of the config schema """

    def __init__(self, name):
        self.name = name
        self._app_entries: List[AppEntry] = []
        Logger().debug(f"Adding tab {name}")

    def add_app_entry(self, app_entry: AppEntry):
        """ Add an AppEntry object to the tabs layout """
        self._app_entries.append(app_entry)

    def get_app_entries(self) -> List[AppEntry]:
        """ Get all app entries on the tab layout """
        return self._app_entries


def parse_config_file(config_file_path: Path) -> List[TabEntry]:
    """ Parse the json config file, validate and convert to object structure """
    app_config = None
    Logger().info(f"Loading file '{config_file_path}'...")

    if not config_file_path.is_file():
        Logger().error(f"Config file '{config_file_path}' does not exist.")
        return []
    with open(config_file_path) as grid_file:
        try:
            app_config = json.load(grid_file)
            with open(this.base_path / "assets" / "config_schema.json") as schema_file:
                json_schema = json.load(schema_file)
                jsonschema.validate(instance=app_config, schema=json_schema)
        except BaseException as error:
            Logger().error(f"Config file:\n{str(error)}")
            return []

    # build the object model
    tabs = []
    for tab in app_config.get("tabs"):
        tab_entry = TabEntry(tab.get("name"))
        for app in tab.get("apps"):
            app_entry = AppEntry(name=app.get("name"), package_id=app.get("package_id"),
                                 executable=Path(app.get("executable")), icon=app.get("icon", ""),
                                 console_application=app.get("console_application", False),
                                 args=app.get("args", ""), config_file_path=config_file_path)
            tab_entry.add_app_entry(app_entry)
        tabs.append(tab_entry)
    return tabs
