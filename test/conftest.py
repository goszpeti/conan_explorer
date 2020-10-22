import os
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
def base_fixture(request):
    paths = PathSetup()
    app.base_path = paths.base_path / "src" / "conan_app_launcher"

    def teardown():
        # reset singletons
        del(app.qt_app)
        app.qt_app = None
        del(logger.Logger._instance)
        logger.Logger._instance = None
        app.base_path = None
        if app.conan_worker:
            app.conan_worker.finish_working()
            del(app.conan_worker)
        app.conan_worker = None
        app.config_file_path = None

    request.addfinalizer(teardown)

    return paths  # ensures that paths can be used in testcases
