from dataclasses import asdict
import json
from conans.model.ref import ConanFileReference
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
    tabs: List[Dict] # same as ConfogTypes, but as dict

class ConanOptionConfig(TypedDict):
    name: str
    value: str

class JsonUiConfig(UiConfigInterface):

    def __init__(self, json_file_path: PathLike):
        self._json_file_path = Path(json_file_path)
        
        # create file, if not available for first start
        if not self._json_file_path.is_file():
            Logger().debug('UiConfig: Creating json file')
            self._json_file_path.touch()
        else:
            Logger().debug(f'UiConfig: Using {self._json_file_path}')

    T = TypeVar('T', bound=Union[TabConfig, AppLinkConfig])
    @staticmethod
    def _convert_to_config_type(dict: Dict[str, Any], config_type: Type[T]) -> T:
        result_config = config_type()
        for key in dict.keys(): # matches 1-1
            value = dict[key]
            if key == "apps":
                value = []
                for dict_val in dict[key]:
                    app = JsonUiConfig._convert_to_config_type(dict_val, AppLinkConfig)
                    value.append(app)
            elif key == "conan_options":
                options: List[ConanOptionConfig] = dict[key]
                value = {}
                for option in options:
                    value[option["name"]] = option.get("value", "")
            if key == "conan_ref":
                value = ConanFileReference.loads(value)
            setattr(result_config, key, value)
        return result_config

    def load(self) -> List[TabConfig]:
        """ Parse the json config file, validate and convert to object structure """
        app_json_config: JsonAppConfig = {"version": "0.0.0", "tabs": []}
        Logger().info(f"Loading file '{self._json_file_path}'...")

        with open(str(self._json_file_path)) as fp:
            try:
                app_json_config = json.load(fp)
                with open(asset_path / "config_schema.json") as schema_file:
                    json_schema = json.load(schema_file)
                    jsonschema.validate(instance=app_json_config, schema=json_schema)
            except Exception as error:
                Logger().error(f"Config file:\n{str(error)}")
                return []

        # implement subsequent migration functions
        self.migrate_to_0_3_0(app_json_config)
        self.migrate_to_0_4_0(app_json_config)

        # build the object abstraction and update
        tabs_result: List[TabConfig] = []
        for tab_dict in app_json_config.get("tabs", {}):
            tab_result = self._convert_to_config_type(tab_dict, TabConfig)
            tabs_result.append(tab_result)

        # auto update version to last version
        app_json_config["version"] = json_schema.get("properties").get("version").get("enum")[-1]

        # write it back with updates
        with open(str(self._json_file_path), "w") as config_file:
            json.dump(app_json_config, config_file, indent=4)
        return tabs_result

    def save(self, tabs: List[TabConfig]):
        """ Create json dict from model and write it to path. """
        tabs_data = []
        for tab in tabs:
            tab_dict = asdict(tab)
            # convert options
            for app_dict in tab_dict.get("apps", {}):
                opt_list = []
                for opt_key in app_dict.get("conan_options", {}):
                    opt_list.append({"name": opt_key, "value": app_dict["conan_options"][opt_key]})
                app_dict["conan_options"] = opt_list
            tabs_data.append(tab_dict)

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
