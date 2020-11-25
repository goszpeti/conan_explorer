import json
import platform
import jsonschema
import tempfile

from pathlib import Path
from typing import List, Dict
from conans.model.ref import ConanFileReference

import conan_app_launcher as this
from conan_app_launcher.base import Logger
from conan_app_launcher.components.icon import extract_icon


class AppEntry():
    """ Representation of an app entry of the config schema """

    def __init__(self, name, conan_ref: str, conan_options: Dict[str, str], executable: Path, args: str, icon: str,
                 console_application: bool, config_file_path: Path):
        self.name = name
        self.executable = executable
        self.icon = Path("NULL")
        self.package_folder = Path()
        self.is_console_application = console_application
        self.args = args
        self.conan_options = conan_options  # user specified, can differ from the actual installation
        # validate package id early
        try:
            self.conan_ref = ConanFileReference.loads(conan_ref)
        except Exception as error:
            # errors happen fairly often, keep going
            self.conan_ref = ConanFileReference.loads("YouGaveA/0.0.1@Wrong/Reference")
            Logger().error(f"Conan ref id invalid {str(error)}")

        # validate icon path
        if icon.startswith("//"):
            Logger().warning("Icon relative to package currently not implemented")
        elif icon and not Path(icon).is_absolute():
            # relative path is calculated from config file path
            self.icon = config_file_path.parent / icon
            if not self.icon.is_file():
                Logger().error(f"Can't find icon {str(self.icon)} for '{name}")
        elif not icon:
            # try to find icon in temp
            self.icon = extract_icon(executable, Path(tempfile.gettempdir()))
        else:
            self.icon = Path(icon)
        if not self.icon.is_file():
            self.icon = this.base_path / "assets" / "default_app_icon.png"

    def validate_with_conan_info(self, package_folder: Path):
        """ Callback when conan operation is done and paths can be validated"""
        self.package_folder = package_folder
        # adjust path on windows, if no file extension is given
        if platform.system() == "Windows" and not self.executable.suffix:
            self.executable = self.executable.with_suffix(".exe")
        full_path = Path(self.package_folder / self.executable)
        if self.package_folder.is_dir() and not full_path.is_file():
            Logger().error(
                f"Can't find file in package {str(self.conan_ref)}:\n    {str(full_path)}")

        self.executable = full_path
        # try to extract, if it is still the default
        if self.icon == this.base_path / "assets" / "default_app_icon.png":
            icon = extract_icon(self.executable, Path(tempfile.gettempdir()))
            if icon.is_file():
                self.icon = icon


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


def update_app_info(app: dict):
    # change from 0.2.0 to 0.3.0
    if app.get("package_id"):
        value = app.pop("package_id")
        app["conan_ref"] = value


def parse_config_file(config_file_path: Path) -> List[TabEntry]:
    """ Parse the json config file, validate and convert to object structure """
    app_config = None
    Logger().info(f"Loading file '{config_file_path}'...")

    if not config_file_path.is_file():
        Logger().error(f"Config file '{config_file_path}' does not exist.")
        return []
    with open(config_file_path) as config_file:
        try:
            app_config = json.load(config_file)
            with open(this.base_path / "assets" / "config_schema.json") as schema_file:
                json_schema = json.load(schema_file)
                jsonschema.validate(instance=app_config, schema=json_schema)
        except BaseException as error:
            Logger().error(f"Config file:\n{str(error)}")
            return []

    # build the object model and update
    tabs = []
    for tab in app_config.get("tabs"):
        tab_entry = TabEntry(tab.get("name"))
        for app in tab.get("apps"):
            # TODO: not very robust, but enough for small changes
            update_app_info(app)
            # convert key-value pairs from options to list of dicts
            conan_opts = app.get("conan_options", [])
            conan_options = {}
            for opt in conan_opts:
                conan_options[opt.get("name", "")] = opt.get("value", "")

            app_entry = AppEntry(name=app.get("name"), conan_ref=app.get("conan_ref"),
                                 executable=Path(app.get("executable")), icon=app.get("icon", ""),
                                 console_application=app.get("console_application", False),
                                 args=app.get("args", ""), config_file_path=config_file_path,
                                 conan_options=conan_options)
            tab_entry.add_app_entry(app_entry)
        tabs.append(tab_entry)
    # auto Update version to next version:
    app_config["version"] = json_schema.get("properties").get("version").get("enum")[-1]
    # write it back with updates
    with open(config_file_path, "w") as config_file:
        json.dump(app_config, config_file, indent=4)
    return tabs
