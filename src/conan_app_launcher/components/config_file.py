import json
import platform
import jsonschema
import tempfile

from pathlib import Path
from typing import List, Dict, Optional
from conans.model.ref import ConanFileReference

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

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
    INVALID_DESCR = "NA"
    INVALID_REF = "Invalid/NA@NA/NA"

    def __init__(self, app_data: AppType = None, config_file_path: Path = None):
        if app_data is None:
            app_data = {"name": "", "conan_ref": self.INVALID_REF, "executable": "", "icon": "",
                        "console_application": False, "args": "", "conan_options": []}
        self.app_data: AppType = app_data
        self._config_file_path = config_file_path  # TODO will be removed later, when no relative icon paths allowed
        self.package_folder = Path("NULL")
        # internal repr for vars which have other types or need to be manipulated
        self._conan_ref = None
        self._conan_options = {}
        self._executable = Path("NULL")
        self._icon = Path("NULL")

        # Init values with validation, which can be preloaded
        self.icon = self.app_data.get("icon", "")
        self.conan_options = self.app_data.get("conan_options", [])
        self.conan_ref = app_data.get("conan_ref", "")

        self._available_refs: List[str] = [self.conan_ref]

    @property
    def name(self):
        return self.app_data["name"]

    @name.setter
    def name(self, new_value: str):
        self.app_data["name"] = new_value

    @property
    def conan_ref(self) -> ConanFileReference:
        return self._conan_ref

    @conan_ref.setter
    def conan_ref(self, new_value: str):
        try:
            self._conan_ref = ConanFileReference.loads(new_value)

            # add conan ref to worker
            if (self.app_data["conan_ref"] != new_value and new_value != self.INVALID_REF
                    and self._conan_ref.version != self.INVALID_DESCR
                    and self._conan_ref.channel != self.INVALID_DESCR):  # don't put it for init
                this.conan_worker.put_ref_in_queue(str(self._conan_ref), self.conan_options)
            self.app_data["conan_ref"] = new_value
        except Exception as error:
            # errors happen fairly often, keep going
            self._conan_ref = ConanFileReference.loads(self.INVALID_REF)
            Logger().error(f"Conan ref id invalid {str(error)}")

    @property
    def version(self):
        return self.conan_ref.version

    @version.setter
    def version(self, new_value: str):
        self.conan_ref = f"{self.conan_ref.name}/{new_value}@{self.conan_ref.user}/{self.conan_ref.channel}"

    @property
    def channel(self):
        return self.conan_ref.channel

    @channel.setter
    def channel(self, new_value: str):
        self.conan_ref = f"{self.conan_ref.name}/{self.conan_ref.version}@{self.conan_ref.user}/{new_value}"

    @property
    def versions(self):
        versions = []
        for ref in self._available_refs:
            versions.append(ref.version)
        return list(set(versions))

    @property
    def channels(self):  # for the current version only
        channels = []
        for ref in self._available_refs:
            if ref.version == self.version:
                channels.append(ref.channel)
        return list(set(channels))

    @property
    def executable(self):
        return self._executable

    @executable.setter
    def executable(self, new_value: str):
        if not new_value:
            Logger().error(f"No file/executable specified for {str(self.name)}")
            return

        # adjust path on windows, if no file extension is given
        path = Path(new_value)
        if platform.system() == "Windows" and not path.suffix:
            path = path.with_suffix(".exe")

        full_path = Path(self.package_folder / path)
        if self.package_folder.is_dir() and not full_path.is_file():
            Logger().error(
                f"Can't find file in package {str(self.conan_ref)}:\n    {str(full_path)}")
        self.app_data["executable"] = new_value
        self._executable = full_path

    @property
    def icon(self) -> Path:
        return self._icon

    @icon.setter
    def icon(self, new_value: str):
        # validate icon path
        if new_value.startswith("//"):  # relative to package
            self._icon = self.package_folder / new_value.replace("//", "")
        elif new_value and not Path(new_value).is_absolute():
            # relative path is calculated from config file path
            self._icon = self._config_file_path.parent / new_value
        elif not new_value:  # try to find icon in temp
            self._icon = extract_icon(self.executable, Path(tempfile.gettempdir()))
        else:  # absolute path
            self._icon = Path(new_value)

        # default icon, until package path is updated
        if not self._icon.is_file():
            self._icon = this.default_icon
            if new_value:  # user input given -> warning
                Logger().error(f"Can't find icon {str(new_value)} for '{self.name}")
        else:
            self._icon = self._icon.resolve()
            self.app_data["icon"] = new_value

    @property
    def is_console_application(self) -> bool:
        return bool(self.app_data.get("console_application"))

    @is_console_application.setter
    def is_console_application(self, new_value):
        self.app_data["console_application"] = new_value

    @property
    def args(self):
        return self.app_data.get("args", "")

    @args.setter
    def args(self, new_value):
        self.app_data["args"] = new_value

    @property
    def conan_options(self) -> Dict[str, str]:  # user specified, can differ from the actual installation
        return self._conan_options

    @conan_options.setter
    def conan_options(self, new_value: List[OptionType]):
        # convert key-value pairs from options to list of dicts
        conan_options = {}
        for opt in new_value:
            conan_options[opt.get("name", "")] = opt.get("value", "")
        self._conan_options = conan_options
        self.app_data["conan_options"] = new_value

    def set_package_info(self, package_folder: Path):
        """ Callback when conan operation is done and paths can be validated"""
        self.package_folder = package_folder

        # use setter to reevaluate
        self.icon = self.app_data.get("icon", "")
        self.executable = self.app_data.get("executable", "")

    def set_available_packages(self, available_refs: List[ConanFileReference]):
        """ Callback when conan operation is done and paths can be validated"""
        self._available_refs = available_refs


class TabEntry():
    """ Representation of a tab entry of the config schema """

    def __init__(self, name):
        self.name = name
        self._app_entries: List[AppEntry] = []
        Logger().debug(f"Adding tab {name}")

    def add_app_entry(self, app_entry: AppEntry):
        """ Add an AppConfigEntry object to the tabs layout """
        self._app_entries.append(app_entry)

    def remove_app_entry(self, app_entry: AppEntry):
        self._app_entries.remove(app_entry)

    def get_app_entries(self) -> List[AppEntry]:
        """ Get all app entries on the tab layout """
        return self._app_entries

    def get_app_entry(self, name: str) -> Optional[AppEntry]:
        """ Get one app entry of the tab layout based on it's name"""
        app = None
        for app in self.tab.get_app_entries():
            if name == app.name:
                break
        return app


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
    with open(str(config_file_path)) as fp:
        try:
            app_config = json.load(fp)
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
            app_entry = AppEntry(app, config_file_path)
            tab_entry.add_app_entry(app_entry)
        tabs.append(tab_entry)
    # auto Update version to next version:
    app_config["version"] = json_schema.get("properties").get("version").get("enum")[-1]
    # write it back with updates
    with open(str(config_file_path), "w") as config_file:
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

    with open(str(config_file_path), "w") as config_file:
        json.dump(app_config, config_file, indent=4)
