import json
import platform
import jsonschema
import tempfile

from pathlib import Path
from typing import Callable, List, Dict, Optional, TYPE_CHECKING

from conans.model.ref import ConanFileReference

if TYPE_CHECKING:
    from typing import TypedDict
else:
    try:
        from typing import TypedDict
    except ImportError:
        from typing_extensions import TypedDict

import conan_app_launcher as this
from conan_app_launcher.base import Logger
from conan_app_launcher.settings import LAST_CONFIG_FILE
from conan_app_launcher.components.icon import extract_icon
from conan_app_launcher.components.conan import ConanApi

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


class AppConfigEntry():
    """ Representation of an app link entry of the config schema """
    INVALID_DESCR = "NA"
    OFFICIAL_RELEASE = "<official release>" # to be used for "_" channel
    OFFICIAL_USER = "<official user>" # to be used for "_" user

    def __init__(self, app_data: Optional[AppType] = None):
        if app_data is None:
            app_data = {"name": "", "conan_ref": this.INVALID_CONAN_REF, 
                        "executable": "", "icon": "", "console_application": False,
                        "args": "", "conan_options": []}

        self.app_data: AppType = app_data # underlying format for json
        self.package_folder = Path("NULL")

        # internal repr for vars which have other types or need to be manipulated
        self._executable = Path("NULL")
        self._icon = Path("NULL")

        # Init values with validation, which can be preloaded
        self.icon = self.app_data.get("icon", "")
        self.conan_ref = app_data.get("conan_ref", this.INVALID_CONAN_REF)
        # can be regsistered from external function to notify when conan infos habe been fetched asynchronnaly
        self._update_cbk_func: Optional[Callable] = None
        self._available_refs: List[ConanFileReference] = [self.conan_ref] # holds all conan refs for name/user
        self.update_from_cache()

    def update_from_cache(self):
        if this.cache: # get all info from cache
            self.set_available_packages(this.cache.get_similar_pkg_refs(
                self._conan_ref.name, self._conan_ref.user))
            if this.USE_LOCAL_INTERNAL_CACHE:
                self.set_package_info(this.cache.get_local_package_path(str(self._conan_ref)))
            elif not this.USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH:  # last chance to get path
                conan = ConanApi()
                package_folder = conan.get_path_or_install(self.conan_ref, self.conan_options)
                self.set_package_info(package_folder)

    def register_update_callback(self, update_func: Callable):
        self._update_cbk_func = update_func

    @property
    def name(self):
        """ Name to be displayed on the link. """
        return self.app_data["name"]

    @name.setter
    def name(self, new_value: str):
        self.app_data["name"] = new_value

    @property
    def conan_ref(self) -> ConanFileReference:
        """ The conan reference to be used for the link. """
        return self._conan_ref

    @conan_ref.setter
    def conan_ref(self, new_value: str):
        try:
            self._conan_ref = ConanFileReference.loads(new_value)

            # add conan ref to worker
            if (self.app_data.get("conan_ref", "") != new_value and new_value != this.INVALID_CONAN_REF
                    and self._conan_ref.version != self.INVALID_DESCR
                    and self._conan_ref.channel != self.INVALID_DESCR):  # don't put it for init
                if this.conan_worker:
                    this.conan_worker.put_ref_in_queue(str(self._conan_ref), self.conan_options)
            # invalidate old entries, which are dependent on the conan ref
            self.app_data["conan_ref"] = new_value
            self._executable = Path("NULL")
            self.icon = self.app_data.get("icon", "")

        except Exception as error:
            # errors happen fairly often, keep going
            self._conan_ref = ConanFileReference.loads(this.INVALID_CONAN_REF)
            Logger().warning(f"Conan reference invalid {str(error)}")

    @property
    def version(self) -> str:
        """ Version, as specified in the conan ref """
        return self.conan_ref.version

    @version.setter
    def version(self, new_value: str):
        user = self.conan_ref.user
        channel = self.conan_ref.channel
        if not self.conan_ref.user or not self.conan_ref.channel:
            user = "_"
            channel = "_"  # both must be unset if channel is official
        self.conan_ref = f"{self.conan_ref.name}/{new_value}@{user}/{channel}"

    @classmethod
    def convert_to_disp_channel(cls, channel: str) -> str:
        """ Substitute _ for official channel string """
        if not channel:
            return cls.OFFICIAL_RELEASE
        return channel

    @property
    def channel(self) -> str:
        """ Channel, as specified in the conan ref"""
        return self.convert_to_disp_channel(self.conan_ref.channel)

    @channel.setter
    def channel(self, new_value: str):
        user = self.conan_ref.user
        if new_value == self.OFFICIAL_RELEASE or not new_value:
            new_value = "_"
            user = "_" # both must be unset if channel is official
        self.conan_ref = f"{self.conan_ref.name}/{self.conan_ref.version}@{user}/{new_value}"

    @property
    def versions(self) -> List[str]:
        """ All versions for the current name and user"""
        versions = set()
        for ref in self._available_refs:
            versions.add(ref.version)
        return list(versions)

    @property
    def channels(self) -> List[str] :
        """ Channels, for the current version only """
        channels = set()
        for ref in self._available_refs:
            if ref.version == self.version:
                channels.add(self.convert_to_disp_channel(ref.channel))
        return list(channels)

    @property
    def executable(self) -> Path:
        """ The executabel for this link to trigger """
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
        """ Icon to display on the link"""
        return self._icon

    @icon.setter
    def icon(self, new_value: str):
        # validate icon path
        emit_warning = False
        if new_value.startswith("//"):  # relative to package
            self._icon = self.package_folder / new_value.replace("//", "")
        elif new_value and not Path(new_value).is_absolute():
            # relative path is calculated from config file path
            self._icon = Path(this.settings.get_string(LAST_CONFIG_FILE)).parent / new_value
            emit_warning = True
        elif not new_value:  # try to find icon in temp
            self._icon = extract_icon(self.executable, Path(tempfile.gettempdir()))
        else:  # absolute path
            self._icon = Path(new_value)
            emit_warning = True
        # default icon, until package path is updated
        if not self._icon.is_file():
            self._icon = this.asset_path / "icons" / "app.png"
            if new_value and emit_warning:  # user input given -> warning
                Logger().error(f"Can't find icon {str(new_value)} for '{self.name}'")

        # default icon, until package path is updated
        if not self._icon.is_file():
            self._icon = this.asset_path / "icons" / "app.png"
            if new_value:  # user input given -> warning
                Logger().error(f"Can't find icon {str(new_value)} for '{self.name}")
        else:
            self._icon = self._icon.resolve()
            self.app_data["icon"] = new_value

    @property
    def is_console_application(self) -> bool:
        return bool(self.app_data.get("console_application"))

    @is_console_application.setter
    def is_console_application(self, new_value: bool):
        self.app_data["console_application"] = new_value

    @property
    def args(self) -> str:
        """ Args to launch the executable with """
        return self.app_data.get("args", "")

    @args.setter
    def args(self, new_value: str):
        self.app_data["args"] = new_value

    @property
    def conan_options(self) -> Dict[str, str]: 
        """ User specified conan options, can differ from the actual installation """
        conan_options: Dict[str, str] = {}
        for option_entry in self.app_data.get("conan_options", {}):
            conan_options[option_entry["name"]] = option_entry.get("value", "")
        return conan_options

    @conan_options.setter
    def conan_options(self, new_value: Dict[str, str]):
        conan_options: List[OptionType] = []
        for opt in new_value:
            conan_options.append({"name": opt, "value": new_value[opt]})
        self.app_data["conan_options"] = conan_options

    def set_package_info(self, package_folder: Path):
        """
        Sets package path and all dependent paths.
        Use, when conan operation is done and paths can be validated.
        Usually to be called from conan worker.
        """

        if this.USE_LOCAL_INTERNAL_CACHE:
            if self.package_folder != package_folder and this.cache:
                this.cache.update_local_package_path(str(self.conan_ref), package_folder)
        self.package_folder = package_folder

        # use setter to reevaluate
        self.executable = self.app_data.get("executable", "")
        # icon needs executable
        self.icon = self.app_data.get("icon", "")

        # call registered update callback
        if self._update_cbk_func:
            self._update_cbk_func()

    def set_available_packages(self, available_refs: List[ConanFileReference]):
        """
        Set all other available packages.
        Usually to be called from conan worker.
        """
        if self._available_refs != available_refs and this.cache:
            this.cache.update_remote_package_list(available_refs)
        self._available_refs = available_refs

        # call registered update callback
        if self._update_cbk_func:
            self._update_cbk_func()


class TabConfigEntry():
    """ Representation of a tab entry of the config schema """

    def __init__(self, name):
        self.name = name
        self._app_entries: List[AppConfigEntry] = []
        Logger().debug(f"Adding tab {name}")

    def add_app_entry(self, app_entry: AppConfigEntry):
        """ Add an AppConfigEntry object to the tabs layout """
        self._app_entries.append(app_entry)

    def remove_app_entry(self, app_entry: AppConfigEntry):
        """ Remove an AppConfigEntry object from the tabs layout """
        self._app_entries.remove(app_entry)

    def get_app_entries(self) -> List[AppConfigEntry]:
        """ Get all app entries on the tab layout """
        return self._app_entries

    def get_app_entry(self, name: str) -> Optional[AppConfigEntry]:
        """ Get one app entry of the tab layout based on it's name"""
        app = None
        for app in self.tab.get_app_entries():
            if name == app.name:
                break
        return app


def update_app_info(app: dict):
    """ Compatiblity function to convert entries of older json schema version. """
    # change from 0.2.0 to 0.3.0
    if app.get("package_id"):
        value = app.pop("package_id")
        app["conan_ref"] = value


def parse_config_file(config_file_path: Path) -> List[TabConfigEntry]:
    """ Parse the json config file, validate and convert to object structure """
    app_config = None
    Logger().info(f"Loading file '{config_file_path}'...")

    if not config_file_path.is_file():
        Logger().error(f"Config file '{config_file_path}' does not exist.")
        return []
    with open(str(config_file_path)) as fp:
        try:
            app_config = json.load(fp)
            with open(this.asset_path / "config_schema.json") as schema_file:
                json_schema = json.load(schema_file)
                jsonschema.validate(instance=app_config, schema=json_schema)
        except BaseException as error:
            Logger().error(f"Config file:\n{str(error)}")
            return []

    # build the object model and update
    tabs = []
    for tab in app_config.get("tabs"):
        tab_entry = TabConfigEntry(tab.get("name"))
        for app in tab.get("apps"):
            update_app_info(app)
            app_entry = AppConfigEntry(app)
            tab_entry.add_app_entry(app_entry)
        tabs.append(tab_entry)
    # auto update version to next version:
    app_config["version"] = json_schema.get("properties").get("version").get("enum")[-1]
    # write it back with updates
    with open(str(config_file_path), "w") as config_file:
        json.dump(app_config, config_file, indent=4)
    return tabs


def write_config_file(config_file_path: Path, tab_entries: List[TabConfigEntry]):
    """ Create json dict from model and write it to path. """
    tabs_data: List[TabType] = []
    for tab in tab_entries:
        apps_data: List[AppType] = []
        for app_entry in tab.get_app_entries():
            apps_data.append(app_entry.app_data)
        tab_data: TabType = {"name": tab.name, "apps": apps_data}
        tabs_data.append(tab_data)

    # get last version
    with open(this.asset_path / "config_schema.json") as schema_file:
        json_schema = json.load(schema_file)
    version = json_schema.get("properties").get("version").get("enum")[-1]
    app_config: AppConfigType = {"version": version, "tabs": tabs_data}

    with open(str(config_file_path), "w") as config_file:
        json.dump(app_config, config_file, indent=2)
