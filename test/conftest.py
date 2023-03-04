import distutils.sysconfig
import configparser
import ctypes
import os
import platform
import shutil
import sys
import tempfile
import time
from distutils.util import strtobool
from pathlib import Path
from shutil import copy
from subprocess import CalledProcessError, check_output
from threading import Thread
from unittest import mock

import psutil
import pytest
import conan_app_launcher.app as app # resolve circular dependencies
from conan_app_launcher import SETTINGS_FILE_NAME, base_path, user_save_path
from conan_app_launcher.core import ConanApi, ConanInfoCache, ConanWorker
from conan_app_launcher.ui.common import remove_qt_logger
from conan_app_launcher.ui.main_window import MainWindow
from conan_app_launcher.settings import *
from conan_app_launcher.core.conan_common import ConanFileReference

def get_scripts_path():
    return Path(sys.executable).parent


exe_ext = ".exe" if platform.system() == "Windows" else ""
conan_server_thread = None
conan_path_str = str(get_scripts_path() / ("conan" + exe_ext))
assert os.path.exists(conan_path_str)
# setup conan test server
TEST_REF = "example/9.9.9@local/testing"
TEST_REF_OFFICIAL = "example/1.0.0@_/_"
SKIP_CREATE_CONAN_TEST_DATA = strtobool(os.getenv("SKIP_CREATE_CONAN_TEST_DATA", "False"))
TEST_REMOTE_NAME = "local"
TEST_REMOTE_URL = "http://127.0.0.1:9300/"

def is_ci_job():
    """ Test runs in CI environment """
    if os.getenv("GITHUB_WORKSPACE"):
        return True
    return False


def get_window_pid(title):
    import win32process
    import win32gui
    hwnd = win32gui.FindWindow(None, title)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid


class PathSetup():
    """ Get the important paths form the source repo. """

    def __init__(self):
        self.test_path = Path(os.path.dirname(__file__))
        self.core_path = self.test_path.parent
        self.testdata_path = self.test_path / "testdata"


def check_if_process_running(process_name, cmd_contains=[], kill=False) -> bool:
    for process in psutil.process_iter():
        print(process)
        try:
            if process_name.lower() in process.name().lower():
                for cmd_contain in cmd_contains:
                    matches = 0
                    if cmd_contain in process.cmdline()[1]:
                        matches += 1
                    if matches == len(cmd_contains):
                        if kill:
                            process.kill()
                        return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def create_test_ref(ref, paths, create_params=[""], update=False):
    native_ref = ConanFileReference.loads(ref).full_str()
    conan = ConanApi()
    conan.init_api()
    pkgs = conan.search_query_in_remotes(native_ref)

    if not update:
        for pkg in pkgs:
            if pkg.full_str() == native_ref:
                return
    conanfile = str(paths.testdata_path / "conan" / "conanfile.py")
    for param in create_params:
        conan_create_and_upload(conanfile, ref, param)


def conan_create_and_upload(conanfile: str, ref: str, create_params=""):
    os.system(f"conan create {conanfile} {ref} {create_params}")
    os.system(f"conan upload {ref} -r {TEST_REMOTE_NAME} --force --all")


def run_conan_server():
    os.system("conan_server")


def start_conan_server():
    # Setup Server config
    os.system("conan_server --migrate")  # call server once to create a config file
    config_path = Path.home() / ".conan_server" / "server.conf"
    os.makedirs(str(config_path.parent), exist_ok=True)
    # configre server config file
    cp = configparser.ConfigParser()
    cp.read(str(config_path))
    # add write permissions
    if "write_permissions" not in cp:
        cp.add_section("write_permissions")
    cp["write_permissions"]["*/*@*/*"] = "*"
    # if "read_permissions" not in cp:
    #     cp.add_section("read_permissions")
    # cp["read_permissions"]["*/*@*/*"] = "*"
    # if "users" not in cp:
    #     cp.add_section("read_permissions")
    # cp["read_permissions"]["*/*@*/*"] = "*"
    with config_path.open('w', encoding="utf8") as fd:
        cp.write(fd)

    # Setup default profile
    paths = PathSetup()
    profiles_path = paths.testdata_path / "conan" / "profile"
    conan = ConanApi()
    conan.init_api()
    os.makedirs(conan.client_cache.profiles_path, exist_ok=True)
    shutil.copy(str(profiles_path / platform.system().lower()),  conan.client_cache.default_profile_path)

    # Add to firewall
    if platform.system() == "Windows":
        # check if firewall was set
        try:
            check_output("netsh advfirewall firewall show rule conan_server").decode("cp850")
        except CalledProcessError:
            # allow server port for private connections
            args = f'advfirewall firewall add rule name="conan_server" program="{sys.executable}" dir= in action=allow protocol=TCP localport=9300'
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "netsh", args, None, 1)
            print("Adding firewall rule for conan_server")

    # Start Server
    global conan_server_thread
    if not conan_server_thread:
        conan_server_thread = Thread(name="ConanServer", daemon=True, target=run_conan_server)
        conan_server_thread.start()
        time.sleep(3)
        print("ADDING CONAN REMOTE")
        if is_ci_job():
            os.system("conan remote clean")
        os.system(f"conan remote add {TEST_REMOTE_NAME} http://127.0.0.1:9300/ false")
        os.system(f"conan user demo -r {TEST_REMOTE_NAME} -p demo")  # todo autogenerate and config
        os.system(f"conan remote enable {TEST_REMOTE_NAME}")
    # Create test data
    if SKIP_CREATE_CONAN_TEST_DATA:
        return
    print("CREATING TESTDATA FOR LOCAL CONAN SERVER")
    for profile in ["windows", "linux"]:
        profile_path = profiles_path / profile
        create_test_ref(TEST_REF, paths, [f"-pr {str(profile_path)}",
                        f"-o shared=False -pr {str(profile_path)}"], update=True)
        create_test_ref(TEST_REF_OFFICIAL, paths, [f"-pr {str(profile_path)}"], update=True)


@pytest.fixture(scope="session", autouse=True)
def ConanServer():
    started = False
    if not check_if_process_running("conan_server"):
        started = True
        print("STARTING CONAN SERVER")
        start_conan_server()
    yield
    if started:
        print("\nKILLING CONAN SERVER\n ")
        check_if_process_running("conan_server", kill=True)


@pytest.fixture
def app_qt_fixture(qtbot):
    yield qtbot
    import conan_app_launcher.app as app
    # remove logger, so the logger doesn't log into nonexistant qt gui
    remove_qt_logger(app.Logger(), MainWindow.qt_logger_name)
    # finish worker - otherwise errors and crashes will occur!
    if app.conan_worker:
        app.conan_worker.finish_working(3)


@pytest.fixture
def base_fixture():
    """
    Set up the global variables to be able to start the application.
    Needs to be used, if the tested component uses the global Logger.
    Clean up all instances after the test.
    """
    paths = PathSetup()
    os.environ["CONAN_REVISIONS_ENABLED"] = "1"
    os.environ["DISABLE_ASYNC_LOADER"] = "True"  # for code coverage to work
    import conan_app_launcher.app as app

    app.active_settings = settings_factory(SETTINGS_INI_TYPE, user_save_path / (SETTINGS_FILE_NAME + "." + SETTINGS_INI_TYPE))
    app.conan_api = ConanApi()
    app.conan_api.init_api()
    app.conan_worker = ConanWorker(app.conan_api, app.active_settings)

    yield paths
    # Teardown

    # remove logger, so the logger doesn't log into nonexistant qt gui
    remove_qt_logger(app.Logger(), MainWindow.qt_logger_name)
    # finish worker - otherwise errors and crashes will occur!
    if app.conan_worker:
        app.conan_worker.finish_working(3)

    # delete cache file
    if (base_path / ConanInfoCache.CACHE_FILE_NAME).exists():
        try:
            os.remove(base_path / ConanInfoCache.CACHE_FILE_NAME)
        except PermissionError:  # just Windows things...
            time.sleep(5)
            os.remove(base_path / ConanInfoCache.CACHE_FILE_NAME)

    # reset singletons
    app.conan_worker = None
    app.conan_api = None
    app.active_settings = None


@pytest.fixture
def light_theme_fixture(base_fixture):
    import conan_app_launcher.app as app
    app.active_settings.set(GUI_MODE, GUI_MODE_LIGHT)
    app.active_settings.set(GUI_STYLE, GUI_STYLE_MATERIAL)


def temp_ui_config(config_file_path: Path):
    temp_config_file_path = copy(config_file_path, tempfile.gettempdir())
    tmp_file = tempfile.mkstemp()
    import conan_app_launcher.app as app

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


@pytest.fixture
def mock_clipboard(mocker):
    from PySide6.QtWidgets import QApplication
    mocker.patch.object(QApplication, 'clipboard')
    clipboard = mock.MagicMock()
    clipboard.supportsSelection.return_value = True
    QApplication.clipboard.return_value = clipboard
    return clipboard
