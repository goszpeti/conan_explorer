import json
from pathlib import Path
from typing import List

import jsonschema
from conans.model.ref import ConanFileReference

from conan_app_launcher.config import base_path, config_path
from conan_app_launcher.logger import Logger

# format specifier for config file
json_schema = {
    "type": "object",
    "tabs": [
        {
            "name": {"type": "string"},
            "apps": [
                {
                    "name": {"type": "string"},
                    "package_id": {"type": "string"},
                    "executable": {"type": "string"},
                    "icon": {"type": "string"}
                }
            ]
        }
    ]
}


class AppEntry():
    """ Representation of an app entry of the config schema """

    def __init__(self, name, package_id:str, executable:Path, icon:str):
        self.conan_info = None
        self.name = name
        try:
            self.package_id = ConanFileReference.loads(package_id)
            # TODO conan install?
        except RuntimeError as error:
            # errors happen fairly often, keep going
            Logger().error("Conan ref id invalid %s", str(error))
            return
        self.executable = executable

        self.icon = Path()
        if icon.startswith("//"):
            Logger().info("Icon relative to package currently not implemented")
            # self.icon = self.conan_info.package_path / icon
        elif not Path(icon).is_absolute():
            self.icon = config_path / icon
        else:
            self.icon = Path(icon)
        if not self.icon.is_file():
            Logger().error("Icon %s for %s not found", str(self.icon), name)
            self.icon = base_path / "ui" / "qt" / "default_app_icon.png"
        Logger().debug("Adding entry %s, %s, %s, %s", name, package_id, str(self.executable), str(self.icon))


class TabEntry():
    """ Representation of a tab entry of the config schema """
    def __init__(self, name):
        self.name = name
        self._app_entries: List[AppEntry] = []
        Logger().debug("Adding tab %s", name)

    def add_app_entry(self, app_entry: AppEntry):
        self._app_entries.append(app_entry)

    def get_app_entries(self) -> List[AppEntry]:
        return self._app_entries


def parse_layout_file(grid_file_path) -> List[TabEntry]:
    app_config = None
    with open(grid_file_path) as f:
        try:
            app_config = json.load(f)
            jsonschema.validate(app_config, json_schema)
        except BaseException as error:
            Logger().error("Config file %s :\n%s", grid_file_path, str(error))
            return []

    tabs = []
    for tab in app_config.get("tabs"):
        tab_entry = TabEntry(tab.get("name"))
        for app in tab.get("apps"):
            tab_entry.add_app_entry(AppEntry(app.get("name"), app.get(
                "package_id"), Path(app.get("executable")), app.get("icon")))
        tabs.append(tab_entry)

    return tabs
