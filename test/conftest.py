import configparser
import os
import platform
import subprocess
import sys
import tempfile
import time
import ctypes
from pathlib import Path
from shutil import copy
from threading import Thread

import conan_app_launcher.app as app
import conan_app_launcher.logger as logger
import pytest
from conan_app_launcher import (SETTINGS_FILE_NAME, asset_path, base_path,
                                user_save_path)
from conan_app_launcher.components import ConanApi, ConanInfoCache, ConanWorker
from conan_app_launcher.settings import *

conan_server_thread =  None
# setup conan test server
character_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&'()*+,-./:;<=>?@[\]^_`{|}~"

def run_conan_server():
    if platform.system() == "Windows":
        # alow server port for private connections
        args=f' advfirewall firewall add rule name="conan_server" program="{sys.executable}" dir= in action=allow protocol=TCP localport=9300'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "netsh", args, None, 1)

    proc = subprocess.Popen("conan_server")
    proc.communicate()

@pytest.fixture # (scope="session", autouse=True)
def start_conan_server():
    config_path = Path.home() / ".conan_server" / "server.conf"
    os.makedirs(str(config_path.parent), exist_ok=True)
    #password = "".join(random.sample(character_string, 12))
    os.system("conan_server --migrate") # call server once to create a config file
    # configre server config file
    cp = configparser.ConfigParser()
    cp.read(str(config_path))
    # add write permissions
    if "write_permissions" not in cp:
        cp.add_section("write_permissions")
    cp["write_permissions"]["*/*@*/*"] = "*"
    with config_path.open('w', encoding="utf8") as fd:
        cp.write(fd)
    global conan_server_thread
    if not conan_server_thread:
        conan_server_thread = Thread(name="ConanServer", daemon=True, target=run_conan_server)
        conan_server_thread.start()
    time.sleep(1)
    os.system("conan remote add local http://0.0.0.0:9300/ false")
    os.system("conan user demo -r local -p demo") # todo autogenerate and config

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

    app.conan_api = ConanApi()
    app.conan_worker = ConanWorker(app.conan_api)
    app.active_settings = settings_factory(SETTINGS_INI_TYPE, user_save_path / SETTINGS_FILE_NAME)

    yield paths
    # Teardown

    # remove logger, so the logger doesn't log into nonexistant qt gui
    logger.Logger.remove_qt_logger()
    # finish worker - otherwise errors and crashes will occur!
    if app.conan_worker:
        app.conan_worker.finish_working()

    # delete cache file
    if (base_path / ConanInfoCache.CACHE_FILE_NAME).exists():
        os.remove(base_path / ConanInfoCache.CACHE_FILE_NAME)

    # reset singletons
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
