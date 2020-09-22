import os
import sys
from pathlib import Path

import pytest

import conan_app_launcher.logger
from conan_app_launcher import config


class PathSetup():
    def __init__(self):
        self.test_path = Path(os.path.dirname(__file__))
        self.base_path = self.test_path.parent
        self.testdata_path = self.test_path / "testdata"


@pytest.fixture
def target_mockup_fixture():
    paths = PathSetup()

    config.resource_path = paths.base_path.parent / "resources"
    mockup_path = paths.test_path / "mock"
    sys.path.append(str(mockup_path))


@pytest.fixture
def base_fixture(request):
    # yield "base_fixture"  # return after setup
    paths = PathSetup()

    def teardown():
        # reset singletons
        conan_app_launcher.logger.Logger._instance = None

    request.addfinalizer(teardown)

    return paths
