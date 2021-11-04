
from typing import List

import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher import (DEFAULT_UI_CFG_FILE_NAME, PathLike,
                                user_save_path)
from conan_app_launcher.components.conan_worker import ConanWorkerElement
from conan_app_launcher.settings import LAST_CONFIG_FILE
from conan_app_launcher.ui.data import (UI_CONFIG_JSON_TYPE,
                                        UiApplicationConfig, UiConfigFactory,
                                        UiConfigInterface)
from conan_app_launcher.ui.modules.app_grid.model import UiTabModel


class UiApplicationModel(UiApplicationConfig):
    CONFIG_TYPE = UI_CONFIG_JSON_TYPE

    def __init__(self, *args, **kwargs):
        """ Create an empty AppModel on init, so we can load it later"""
        super().__init__(*args, **kwargs)
        self.tabs: List[UiTabModel]
        self._ui_config_data: UiConfigInterface

    def load(self, ui_config=UiApplicationConfig) -> "UiApplicationModel":
        super().__init__(ui_config.tabs)
        # load all submodels
        tabs_model = []
        for tab_config in self.tabs:
            tabs_model.append(UiTabModel().load(tab_config, self))
        self.tabs = tabs_model
        return self

    def save(self):
        self._ui_config_data.save(self)

    def loadf(self, config_source: str) -> "UiApplicationModel":
        # empty ui config, create it in user path
        default_config_file_path = user_save_path / DEFAULT_UI_CFG_FILE_NAME
        if not config_source or not default_config_file_path.exists():
            config_source = str(default_config_file_path)
        app.active_settings.set(LAST_CONFIG_FILE, str(config_source))

        self._ui_config_data = UiConfigFactory(self.CONFIG_TYPE, config_source)
        ui_config = self._ui_config_data.load()

        self.load(ui_config)
        return self

    def get_all_conan_refs(self):
        conan_refs: List[ConanWorkerElement] = []
        for tab in self.tabs:
            for app in tab.apps:
                ref_dict: ConanWorkerElement = {"reference": str(app.conan_ref),
                                                "options": app.conan_options}
                if ref_dict not in conan_refs:
                    conan_refs.append(ref_dict)
        return conan_refs
