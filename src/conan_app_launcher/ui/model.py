
from pathlib import Path
from typing import List

from conan_app_launcher.components.conan_worker import ConanWorkerElement
from conan_app_launcher.ui.data import (UI_CONFIG_JSON_TYPE,
                                        UiApplicationConfig, UiConfigFactory,
                                        UiConfigInterface)


class UiApplicationModel(UiApplicationConfig):
    CONFIG_TYPE = UI_CONFIG_JSON_TYPE

    def __init__(self, *args, **kwargs):
        """ Create an empty AppModel on init, so we can load it later"""
        super().__init__(*args, **kwargs)
        self._ui_config_data: UiConfigInterface

    def load(self, ui_config=UiApplicationConfig):
        super().__init__(ui_config.tabs)

    def save(self):
        self._ui_config_data.save(self)

    def loadf(self, config_file_path):
        self._ui_config_data = UiConfigFactory(self.CONFIG_TYPE, config_file_path)
        ui_config = self._ui_config_data.load()

        self.load(ui_config)

    #     self_config = ui_config.load()
    #     # initalite default config
    #     if not tab_configs:
    #         app_config = UiApplicationConfig()
    #         tab_configs.append(UiTabConfig())
    #         tab_configs[0].apps.append(UiAppLinkConfig())
    #         app_config.tabs = tab_configs
    #         ui_config.save(app_config)

    #     for tab in tab_configs:
    #         model_tab = UiTabModel()
    #         model_tab.load(tab)
    #         self.tabs.append(model_tab)
    #     return config_file_setting

    def get_all_conan_refs(self):
        conan_refs: List[ConanWorkerElement] = []
        for tab in self.tabs:
            for app in tab.apps:
                ref_dict: ConanWorkerElement = {"reference": str(app.conan_ref),
                                                "options": app.conan_options}
                if ref_dict not in conan_refs:
                    conan_refs.append(ref_dict)
        return conan_refs
