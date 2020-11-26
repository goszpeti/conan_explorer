import json
import platform
import jsonschema
import tempfile

from pathlib import Path
from typing import List, Dict, TypedDict
from conans.model.ref import ConanFileReference

import conan_app_launcher as this
from conan_app_launcher.base import Logger
from conan_app_launcher.components.icon import extract_icon

# TODO: remove json validation, when user edit will be removed.
# maybe remove versioning, but keep parsing for all versions?
# Create it like a database, where evrything is synchronized?
# Write out package folder for caching?
# Create setters with validation for everything.


class OptionType(TypedDict):
    name: str
    value: str


class AppType(TypedDict):
    name: str
    conan_ref: str
    executable: str
    icon: str
    console_application: bool
    args: str
    conan_options: List[OptionType]


class TabType(TypedDict):
    name: str
    apps: List[AppType]


class AppConfigType(TypedDict):
    version: str
    tabs: List[TabType]


class AppEntry():
    """ Representation of an app entry of the config schema """

    @property
    def name(self):
        return self.app_data["name"]

    @property
    def conan_ref(self):
        return self._conan_ref

    @conan_ref.setter
    def conan_ref(self, new_value: str):
        try:
            self._conan_ref = ConanFileReference.loads(new_value)
            self.app_data["conan_ref"] = new_value
        except Exception as error:
            # errors happen fairly often, keep going
            self._conan_ref = ConanFileReference.loads("YouGaveA/0.0.1@Wrong/Reference")
            Logger().error(f"Conan ref id invalid {str(error)}")

    @property
    def executable(self):
        return self._executable

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, new_value):
        icon = self.app_data.get("icon", "")
        # validate icon path
        if icon and not Path(icon).is_absolute():
            # relative path is calculated from config file path
            self._icon = self._config_file_path.parent / icon
            if not self._icon.is_file():
                Logger().error(f"Can't find icon {str(self.icon)} for '{self.name}")
        elif not icon:  # try to find icon in temp
            self._icon = extract_icon(self._executable, Path(tempfile.gettempdir()))
        else:  # absolute path
            self._icon = Path(icon)
        # default icon, until package path is updated
        if not self._icon.is_file():
            self._icon = this.base_path / "assets" / "default_app_icon.png"

    @property
    def is_console_application(self):
        return self.app_data.get("is_console_application")

    @property
    def args(self):
        return self.app_data.get("args", "")

    @property
    def conan_options(self):  # user specified, can differ from the actual installation
        return self.app_data.get("conan_options", {})

    def __init__(self, app_data: AppType, config_file_path: Path):
        self.app_data: AppType = app_data
        self._config_file_path = config_file_path  # TODO will be removed later, when no relative icon paths allowed
        self.package_folder = Path("NULL")
        # internal repr for vars which have other types or need to be manipulated
        self._icon = Path("NULL")
        self._conan_ref = None
        self.conan_ref = app_data["conan_ref"]
        self._executable = Path("NULL")

    def validate_with_conan_info(self, package_folder: Path):
        """ Callback when conan operation is done and paths can be validated"""
        self.package_folder = package_folder
        # adjust path on windows, if no file extension is given
        if platform.system() == "Windows" and not self._executable.suffix:
            self._executable = self._executable.with_suffix(".exe")
        full_path = Path(self.package_folder / self.executable)
        if self.package_folder.is_dir() and not full_path.is_file():
            Logger().error(
                f"Can't find file in package {str(self.conan_ref)}:\n    {str(full_path)}")

        self._executable = full_path
        # try to extract, if it is still the default
        if self._icon == this.base_path / "assets" / "default_app_icon.png":
            if self._icon.startswith("//"):  # relative to package
                icon = self.package_folder / self.icon
                Logger().error(f"Can't find icon {str(self.icon)} for '{self.name}")
            else:
                icon = extract_icon(self.executable, Path(tempfile.gettempdir()))
            if icon.is_file():
                self._icon = icon


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
            app_entry = AppEntry(app, config_file_path)
            tab_entry.add_app_entry(app_entry)
        tabs.append(tab_entry)
    # auto Update version to next version:
    app_config["version"] = json_schema.get("properties").get("version").get("enum")[-1]
    # write it back with updates
    with open(config_file_path, "w") as config_file:
        json.dump(app_config, config_file, indent=4)
    return tabs


def write_config_file(config_file_path: Path, tab_entries: List[TabEntry]):
    # create json dict from model
    tabs_data: List[TabType] = []
    for tab in tab_entries:
        apps_data: List[AppType] = []
        for app_entry in tab.get_app_entries():
            apps_data.append(app_entry.app_data)
        tab_data: TabType = {"name": tab.name, "apps": apps_data}
        tabs_data.append(tab_data)

    # get last version
    with open(this.base_path / "assets" / "config_schema.json") as schema_file:
        json_schema = json.load(schema_file)
    version = json_schema.get("properties").get("version").get("enum")[-1]
    app_config: AppConfigType = {"version": version, "tabs": tabs_data}

    with open(config_file_path, "w") as config_file:
        json.dump(app_config, config_file, indent=4)
