import json
import platform
from pathlib import Path
from typing import List

import jsonschema
from conans.model.ref import ConanFileReference

import conan_app_launcher as app
from conan_app_launcher.logger import Logger


class AppEntry():
    """ Representation of an app entry of the config schema """

    def __init__(self, name, package_id: str, executable: Path, icon: str,
                 config_file_path: Path, base_path: Path):
        # TODO getter/setter
        self.name = name
        self.executable = executable
        self.icon = Path()
        self.package_folder = Path()
        # validate package id
        try:
            self.package_id = ConanFileReference.loads(package_id)
        except RuntimeError as error:
            # errors happen fairly often, keep going
            Logger().error("Conan ref id invalid %s", str(error))
            return

        # validate icon path
        if icon.startswith("//"):
            Logger().info("Icon relative to package currently not implemented")
        elif icon and not Path(icon).is_absolute():
            self.icon = config_file_path.parent / icon
        else:
            self.icon = Path(icon)
        if not self.icon.is_file():
            Logger().error("Icon %s for '%s' not found", str(self.icon), name)
            self.icon = base_path / "ui" / "qt" / "default_app_icon.png"

        # add this object to the conan worker to get a package info / install the package
        # TODO: not the optimal place to call this
        if app.conan_worker:
            app.conan_worker.app_queue.put(self)
            app.conan_worker.start_working()

    def on_conan_info_available(self):
        """ Callback when conan operation is done and paths can be validated"""
        # adjust path on windows, if no file extension is given
        if platform.system() == "Windows" and not self.executable.suffix:
            self.executable = self.executable.with_suffix(".exe")
        full_path = Path(self.package_folder / self.executable)
        if not full_path.is_file():
            Logger().error("Cannot find " + str(self.executable) + " in package " + str(self.package_id))
        self.executable = full_path


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


def parse_config_file(config_file_path: Path, ) -> List[TabEntry]:
    """ Parse the json config file, validate and convert to object structure """
    app_config = None
    if not config_file_path.is_file():
        Logger().error("Config file '%s' does not exist.", config_file_path)
        return []
    base_path = Path(__file__).parent
    with open(config_file_path) as grid_file:
        try:
            app_config = json.load(grid_file)
            with open(base_path / "config_schema.json") as schema_file:
                json_schema = json.load(schema_file)
                jsonschema.validate(instance=app_config, schema=json_schema)
            assert app_config.get(
                "version") == "0.1.0", "Unknown schema version '%s'" % app_config.get("version")
        except BaseException as error:
            Logger().error("Config file:\n%s", str(error))
            return []

    # build the object model
    tabs = []
    for tab in app_config.get("tabs"):
        tab_entry = TabEntry(tab.get("name"))
        for app in tab.get("apps"):
            tab_entry.add_app_entry(AppEntry(app.get("name"), app.get("package_id"),
                                             Path(app.get("executable")), app.get("icon", ""),
                                             config_file_path, base_path))
        tabs.append(tab_entry)

    return tabs
