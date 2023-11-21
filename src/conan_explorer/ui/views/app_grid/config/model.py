
from pathlib import Path
from typing import Optional

import conan_explorer.app as app  # using global module pattern
from conan_explorer import (DEFAULT_UI_CFG_FILE_NAME,
                                LEGACY_UI_CFG_FILE_NAME, legacy_user_save_path,
                                user_save_path)
from conan_explorer.settings import AUTO_INSTALL_QUICKLAUNCH_REFS, LAST_CONFIG_FILE
from . import (UI_CONFIG_JSON_TYPE, UiConfig,
                        UiConfigInterface, get_ui_config_file_ext, ui_config_factory)

from ..model import UiAppGridModel


class UiApplicationModel(UiConfig):
    CONFIG_TYPE = UI_CONFIG_JSON_TYPE

    def __init__(self, conan_pkg_installed=None, conan_pkg_removed=None, *args, **kwargs):
        """ Create an empty AppModel on init, so we can load it later"""
        UiConfig.__init__(self, *args, **kwargs)
        self.app_grid: UiAppGridModel
        self._ui_config_data: Optional[UiConfigInterface] = None
        self.conan_pkg_installed = conan_pkg_installed
        self.conan_pkg_removed = conan_pkg_removed

    def save(self):
        """ Save configuration """
        if self._ui_config_data:
            self._ui_config_data.save(self)

    def load(self, ui_config: UiConfig) -> "UiApplicationModel":
        """ Load the model and submodels from the config object """
        # update conan info
        self.app_grid = UiAppGridModel()
        self.app_grid.load(ui_config.app_grid, self)
        if app.conan_worker and app.active_settings.get_bool(AUTO_INSTALL_QUICKLAUNCH_REFS):
            app.conan_worker.finish_working(3)
            app.conan_worker.update_all_info(self.app_grid.get_all_conan_worker_elements(),
                                             self.emit_conan_pkg_signal_callback)

        return self

    def emit_conan_pkg_signal_callback(self, conan_ref: str, pkg_id: str):
        if not self.conan_pkg_installed:
            return
        self.conan_pkg_installed.emit(conan_ref, pkg_id)

    def loadf(self, config_source: str) -> "UiApplicationModel":
        """ Load model and submodels from specified file source """
        # empty ui config, create it in user path
        file_ext = get_ui_config_file_ext(self.CONFIG_TYPE)
        default_config_file_path = user_save_path / (DEFAULT_UI_CFG_FILE_NAME + file_ext)
        if not config_source or legacy_user_save_path / (LEGACY_UI_CFG_FILE_NAME) == Path(config_source):
            config_source = str(default_config_file_path)
            app.active_settings.set(LAST_CONFIG_FILE, str(config_source))

        self._ui_config_data = ui_config_factory(self.CONFIG_TYPE, config_source)
        ui_config = self._ui_config_data.load()

        self.load(ui_config)
        return self

