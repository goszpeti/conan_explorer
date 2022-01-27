import configparser
import ctypes
import os
import platform
import sys
import tempfile
import time
from pathlib import Path
from shutil import copy
from subprocess import check_output
from threading import Thread

import conan_app_launcher.app as app
import conan_app_launcher.logger as logger
import psutil
import pytest
from conan_app_launcher import SETTINGS_FILE_NAME, base_path, user_save_path
from conan_app_launcher.components import ConanApi, ConanInfoCache, ConanWorker
from conan_app_launcher.settings import *
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets

conan_server_thread =  None

# setup conan test server
TEST_REF =  "example/9.9.9@local/testing" #"zlib/1.2.8@_/_#74ce22a7946b98eda72c5f8b5da3c937"
TEST_REF_OFFICIAL = "example/1.0.0@_/_"
SETUP_TEST_DATA = True
class PathSetup():
    """ Get the important paths form the source repo. """
    def __init__(self):
        self.test_path = Path(os.path.dirname(__file__))
        self.base_path = self.test_path.parent
        self.testdata_path = self.test_path / "testdata"

def check_if_process_running(process_name):
    for process in psutil.process_iter():
        try:
            if process_name.lower() in process.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def create_test_ref(ref, paths, create_params=[""], update=False):
    native_ref = ConanFileReference.loads(ref).full_str()
    pkgs = app.conan_api.search_query_in_remotes(native_ref)

    if not update:
        for pkg in pkgs:
            if pkg.full_str() == native_ref:
                return
    conanfile = str(paths.testdata_path / "conan" / "conanfile.py")
    for param in create_params:
        conan_create_and_upload(conanfile, ref, param)

def conan_create_and_upload(conanfile:str, ref:str, create_params=""):
    os.system(f"conan create {conanfile} {ref} {create_params}")
    os.system(f"conan upload {ref} -r local --force --all")

def run_conan_server():
    if platform.system() == "Windows":
        # check if firewall was set
        out = check_output("netsh advfirewall firewall show rule conan_server").decode("cp850")
        print(out)
        if not "Enabled" in out:
            # allow server port for private connections
            args=f'advfirewall firewall add rule name="conan_server" program="{sys.executable}" dir= in action=allow protocol=TCP localport=9300'
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "netsh", args, None, 1)
            print("Adding firewall rule for conan_server")
    os.system("conan_server")
    #proc = subprocess.Popen()
    #proc.communicate()

def start_conan_server():
    config_path = Path.home() / ".conan_server" / "server.conf"
    os.makedirs(str(config_path.parent), exist_ok=True)
    #character_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
    #password = "".join(random.sample(character_string, 12))
    os.system("conan_server --migrate") # call server once to create a config file
    # configre server config file
    cp = configparser.ConfigParser()
    cp.read(str(config_path))
    # add write permissions
    if "write_permissions" not in cp:
        cp.add_section("write_permissions")
    cp["write_permissions"]["*/*@*/*"] = "*"
    cp["read_permissions"]["*/*@*/*"] = "*"
    with config_path.open('w', encoding="utf8") as fd:
        cp.write(fd)
    global conan_server_thread
    if not conan_server_thread:
        conan_server_thread = Thread(name="ConanServer", daemon=True, target=run_conan_server)
        conan_server_thread.start()
        time.sleep(3)
    os.system("conan remote add local http://127.0.0.1:9300/ false")
    # add the same remote twice to be able to test multiremote views - TODO does not work
#    os.system("conan remote add local2 http://127.0.0.1:9300/ false")
    os.system("conan user demo -r local -p demo")  # todo autogenerate and config
#    os.system("conan user demo -r local2 -p demo")  # todo autogenerate and config

    if SETUP_TEST_DATA:
        paths = PathSetup()
        profiles_path = paths.testdata_path / "conan" / "profile"
        for profile in ["windows", "linux"]:
            profile_path = profiles_path / profile
            create_test_ref(TEST_REF, paths, [f"-pr {str(profile_path)}",
                            f"-o shared=False -pr {str(profile_path)}"], update=True)
            create_test_ref(TEST_REF_OFFICIAL, paths, [f"-pr {str(profile_path)}"], update=True)

@pytest.fixture(scope="session", autouse=True)
def ConanServer():
    if not check_if_process_running("conan_server"):
        start_conan_server()

@pytest.fixture
def base_fixture(request):  # TODO , autouse=True?
    """
    Set up the global variables to be able to start the application.
    Needs to be used, if the tested component uses the global Logger.
    Clean up all instances after the test.
    """
    paths = PathSetup()
    os.environ["CONAN_REVISIONS_ENABLED"] = "1"
    app.conan_api = ConanApi()
    app.conan_worker = ConanWorker(app.conan_api)
    app.active_settings = settings_factory(SETTINGS_INI_TYPE, user_save_path / SETTINGS_FILE_NAME)
    app.active_settings.set(ENABLE_APP_COMBO_BOXES, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

    yield paths
    # Teardown

    # remove logger, so the logger doesn't log into nonexistant qt gui
    logger.Logger.remove_qt_logger()
    # finish worker - otherwise errors and crashes will occur!
    if app.conan_worker:
        app.conan_worker.finish_working(3)

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
