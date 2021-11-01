import json
import jsonschema
from distutils.version import StrictVersion
from pathlib import Path
from typing import Any, Dict, List, TYPE_CHECKING, Optional, Type, TypeVar, Union

from conan_app_launcher.data.ui_config import AppLinkConfig, TabConfig, UiConfigInterface

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypedDict
else:
    try:
        from typing import TypedDict
    except ImportError:
        from typing_extensions import TypedDict

from conan_app_launcher import PathLike, asset_path, user_save_path
from conan_app_launcher.base import Logger

### Internal represantation of JSON save format


class JsonAppConfig(TypedDict):
    version: str
    tabs: List[Dict]


class JsonUiConfig(UiConfigInterface):

    def __init__(self, json_file_path: PathLike):
        self._json_file_path = Path(json_file_path)
        
        # create file, if not available for first start
        if not self._json_file_path.is_file():
            Logger().debug('UiConfig: Creating json file')
            self._json_file_path.touch()
        else:
            Logger().debug(f'Settings: Using {self._json_file_path}')

    T = TypeVar('T', bound=Union[TabConfig, AppLinkConfig])

    @staticmethod
    def _convert_to_dict(config: T) -> Dict[str, Any]:
        result_dict = {}
        for attr in vars(config):
            result_dict[attr] = getattr(config, attr)
        return result_dict


    @staticmethod
    def _convert_to_config_type(dict: Dict[str, Any], config_type: Type[T]) -> T:
        result_config = config_type()
        for key in dict: # matches 1-1
            setattr(result_config, key, dict[key])
        return result_config

    def load(self) -> List[TabConfig]:
        """ Parse the json config file, validate and convert to object structure """
        app_config: JsonAppConfig = {"version": "0.0.0", "tabs": []}
        Logger().info(f"Loading file '{self._json_file_path}'...")

        with open(str(self._json_file_path)) as fp:
            try:
                app_config = json.load(fp)
                with open(asset_path / "config_schema.json") as schema_file:
                    json_schema = json.load(schema_file)
                    jsonschema.validate(instance=app_config, schema=json_schema)
            except BaseException as error:
                Logger().error(f"Config file:\n{str(error)}")
                return []

        # implement subsequent migration functions
        self.migrate_to_0_3_0(app_config)
        self.migrate_to_0_4_0(app_config)

        # build the object abstraction and update
        tabs_result: List[TabConfig] = []
        for tab in app_config.get("tabs", {}):
            tab_entry = self._convert_to_config_type(tab, TabConfig)
            for app in tab.get("apps", {}):
                app_entry = self._convert_to_config_type(app, AppLinkConfig)
                tab_entry.apps.append(app_entry)
            tabs_result.append(tab_entry)

        # auto update version to last version:
        app_config["version"] = json_schema.get("properties").get("version").get("enum")[-1]

        # write it back with updates
        with open(str(self._json_file_path), "w") as config_file:
            json.dump(app_config, config_file, indent=4)
        return tabs_result

    def save(self, tabs: List[TabConfig]):
        """ Create json dict from model and write it to path. """
        tabs_data = []
        for tab in tabs:
            apps_data = []
            for app_entry in tab.apps:
                apps_data.append(self._convert_to_dict(app_entry))
            tab_data = {"name": tab.name, "apps": apps_data}
            tabs_data.append(tab_data)

        # get last version
        with open(asset_path / "config_schema.json") as schema_file:
            json_schema = json.load(schema_file)
        version = json_schema.get("properties").get("version").get("enum")[-1]
        app_config: JsonAppConfig = {"version": version, "tabs": tabs_data}

        with open(str(self._json_file_path), "w") as config_file:
            json.dump(app_config, config_file, indent=2)

    def migrate_to_0_3_0(self, app_config: JsonAppConfig):
        """ Compatiblity function to update schema version. """
        if StrictVersion(app_config["version"]) >= StrictVersion("0.3.0"):
            return
        for tab in app_config["tabs"]:
            for app in tab["apps"]:
                if app.get("package_id"):
                    value = app.pop("package_id")
                    app["conan_ref"] = value

    def migrate_to_0_4_0(self, app_config: JsonAppConfig):
        """ Compatiblity function to update schema version. """
        if StrictVersion(app_config["version"]) >= StrictVersion("0.4.0"):
            return
        for tab in app_config["tabs"]:
            for app in tab["apps"]:
                if app.get("console_application"):
                    value = app.pop("console_application")
                    app["is_console_application"] = value
