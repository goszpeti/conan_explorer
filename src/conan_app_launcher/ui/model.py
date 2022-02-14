
from typing import Optional

import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher import (DEFAULT_UI_CFG_FILE_NAME, user_save_path)
from conan_app_launcher.settings import LAST_CONFIG_FILE
from conan_app_launcher.ui.data import (UI_CONFIG_JSON_TYPE, UiConfig,
                                        ui_config_factory, UiConfigInterface)
from conan_app_launcher.ui.views.app_grid.model import UiAppGridModel


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
        if app.conan_worker:
            app.conan_worker.finish_working(3)
            app.conan_worker.update_all_info(self.app_grid.get_all_conan_worker_elements(), self.conan_pkg_installed)
    
        return self

    def loadf(self, config_source: str) -> "UiApplicationModel":
        """ Load model and submodels from specified file source """
        # empty ui config, create it in user path
        default_config_file_path = user_save_path / DEFAULT_UI_CFG_FILE_NAME
        if not config_source or not default_config_file_path.exists():
            config_source = str(default_config_file_path)
        app.active_settings.set(LAST_CONFIG_FILE, str(config_source))

        self._ui_config_data = ui_config_factory(self.CONFIG_TYPE, config_source)
        ui_config = self._ui_config_data.load()

        self.load(ui_config)
        return self

