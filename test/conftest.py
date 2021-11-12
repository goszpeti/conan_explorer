import os
import tempfile
from pathlib import Path
from shutil import copy

import conan_app_launcher.app as app
from conan_app_launcher.components.conan import ConanApi
from conan_app_launcher.components.conan_worker import ConanWorker
import conan_app_launcher.logger as logger
import pytest
from conan_app_launcher import SETTINGS_FILE_NAME, asset_path, base_path, user_save_path
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
    logger.Logger.remove_qt_logger()

    app.conan_api = ConanApi()
    app.conan_worker = ConanWorker(app.conan_api)
    app.active_settings = settings_factory(SETTINGS_INI_TYPE, user_save_path / SETTINGS_FILE_NAME)

    yield paths

    # teardown

    if app.conan_worker:
        app.conan_worker.finish_working()
    # reset singletons

    # delete cache file
    # if (app.base_path / app.CACHE_FILE_NAME).exists():
    #     os.remove(app.base_path / app.CACHE_FILE_NAME)

    logger.Logger._instance = None
    app.conan_worker = None
    app.conan_api = None
    app.active_settings = None


def temp_ui_config(config_file_path: Path):
    temp_config_file_path = copy(config_file_path, tempfile.gettempdir())
    tmp_file = tempfile.mkstemp()
    app.active_settings = settings_factory(SETTINGS_INI_TYPE, Path(tmp_file[1]))
    app.active_settings.set(LAST_CONFIG_FILE, str(temp_config_file_path))
    return Path(temp_config_file_path)

@pytest.fixture
def ui_config_fixture(base_fixture):
    """ Use temporary default settings and config file based on testdata/app_config.json """
    config_file_path = base_fixture.testdata_path / "app_config.json"
    yield temp_ui_config(config_file_path)


@pytest.fixture
def ui_no_refs_config_fixture(base_fixture):
    """ Use temporary default settings and config file based on testdata/app_config_empty_refs.json """
    config_file_path = base_fixture.testdata_path / "app_config_empty_refs.json"
    yield temp_ui_config(config_file_path)
