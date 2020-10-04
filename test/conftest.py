import os
import sys
import time
from pathlib import Path

import pytest

import conan_app_launcher.logger as logger
import conan_app_launcher as app


class PathSetup():
    def __init__(self):
        self.test_path = Path(os.path.dirname(__file__))
        self.base_path = self.test_path.parent
        self.testdata_path = self.test_path / "testdata"


@pytest.fixture
def target_mockup_fixture():
    paths = PathSetup()
    #mockup_path = paths.test_path / "mock"
    # sys.path.append(str(mockup_path))


@pytest.fixture
def base_fixture(request):
    paths = PathSetup()

    def teardown():
        # reset singletons
        # if app.qt_app:
        #    app.qt_app = None
        logger.Logger._instance = None
        app.base_path = None
        if app.conan_worker:
            app.conan_worker.finish_working(5)
        app.conan_worker = None
        app.config_file_path = None

    request.addfinalizer(teardown)

    return paths
