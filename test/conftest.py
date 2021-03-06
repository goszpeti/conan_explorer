import os
from pathlib import Path

import pytest
import tempfile
from PyQt5 import QtCore, QtWidgets

from conan_app_launcher.settings import *
import conan_app_launcher.base as logger
import conan_app_launcher as app


class PathSetup():
    def __init__(self):
        self.test_path = Path(os.path.dirname(__file__))
        self.base_path = self.test_path.parent
        self.testdata_path = self.test_path / "testdata"


@pytest.fixture
def base_fixture(request):

    paths = PathSetup()
    app.base_path = paths.base_path / "src" / "conan_app_launcher"
    app.asset_path: Path = app.base_path / "assets"
    yield paths

    # teardown
    if app.conan_worker:
        app.conan_worker.finish_working()
        del(app.conan_worker)
    # reset singletons
    del(app.qt_app)
    app.qt_app = None
    del(logger.Logger._instance)

    # delete cache file
    if (app.base_path / app.CACHE_FILE_NAME).exists():
        os.remove(app.base_path / app.CACHE_FILE_NAME)

    logger.Logger._instance = None
    app.base_path = None
    app.conan_worker = None
    app.cache = None
    app.settings = None
    app.tab_configs = []


@pytest.fixture
def settings_fixture(base_fixture):
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    app.settings = Settings(ini_file=Path(temp_ini_path))
    config_file_path = base_fixture.testdata_path / "app_config.json"
    app.settings.set(LAST_CONFIG_FILE, str(config_file_path))
    yield config_file_path
