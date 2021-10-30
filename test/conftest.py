import os
import tempfile
from pathlib import Path
from shutil import copy

import conan_app_launcher as app
import conan_app_launcher.base as logger
import pytest
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
    app.base_path = paths.base_path / "src" / "conan_app_launcher"
    app.asset_path: Path = app.base_path / "assets"
    app.DEBUG_LEVEL = 1
    yield paths

    # teardown
    app.DEBUG_LEVEL = 0

    if app.conan_worker:
        app.conan_worker.finish_working()
    # reset singletons
    app.qt_app = None

    # delete cache file
    if (app.base_path / app.CACHE_FILE_NAME).exists():
        os.remove(app.base_path / app.CACHE_FILE_NAME)

    logger.Logger._instance = None
    app.base_path = None
    app.conan_worker = None
    app.cache = None
    app.active_settings = None
    app.tab_configs = []


@pytest.fixture
def settings_fixture(base_fixture):
    """ Use temporary settings based on testdata/app_config.json """
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    app.active_settings = Settings(ini_file=Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "app_config.json"
    temp_config_file_path = copy(config_file_path, temp_dir)
    app.active_settings.set(LAST_CONFIG_FILE, str(temp_config_file_path))
    yield Path(temp_config_file_path)
