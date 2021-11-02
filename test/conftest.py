import os
import tempfile
from pathlib import Path
from shutil import copy

import conan_app_launcher
import conan_app_launcher.app as app
import conan_app_launcher.logger as logger
import pytest
from conan_app_launcher import asset_path, base_path
from conan_app_launcher.settings import *


class PathSetup():
    """ Get the important paths form the source repo. """
    def __init__(self):
        self.test_path = Path(os.path.dirname(__file__))
        self.base_path = self.test_path.parent
        self.testdata_path = self.test_path / "testdata"


@pytest.fixture
def base_fixture(request):
    """
    Set up the global variables to be able to start the application.
    Needs to be used, if the tested component uses the global Logger.
    Clean up all instances after the test.
    """
    paths = PathSetup()
    conan_app_launcher.base_path = paths.base_path / "src" / "conan_app_launcher"
    conan_app_launcher.asset_path = base_path / "assets"
    yield paths

    # teardown

    if app.conan_worker:
        app.conan_worker.finish_working()
    # reset singletons

    # delete cache file
    # if (app.base_path / app.CACHE_FILE_NAME).exists():
    #     os.remove(app.base_path / app.CACHE_FILE_NAME)

    logger.Logger._instance = None
    conan_app_launcher.base_path = None
    app.conan_worker = None
    app.conan_api = None
    app.active_settings = None


@pytest.fixture
def ui_config_fixture(base_fixture):
    """ Use temporary default settings and config file based on testdata/app_config.json """
    config_file_path = base_fixture.testdata_path / "app_config.json"
    temp_config_file_path = copy(config_file_path, tempfile.gettempdir())
    app.active_settings = SettingsFactory(SETTINGS_INI_TYPE, Path(tempfile.mktemp()))
    app.active_settings.set(LAST_CONFIG_FILE, str(temp_config_file_path))
    yield Path(temp_config_file_path)
