from contextlib import contextmanager
from datetime import datetime, timedelta
import configparser
import ctypes
import os
import platform
import shutil
import sys
import tempfile
import time
from pathlib import Path
from subprocess import CalledProcessError, check_output
from threading import Thread
from typing import Generator
from unittest import mock

import psutil
import pytest
import conan_explorer.app as app  # resolve circular dependencies
from conan_explorer import SETTINGS_FILE_NAME, base_path, user_save_path
from conan_explorer.app.system import str2bool
from conan_explorer.conan_wrapper import ConanInfoCache, ConanWorker
from conan_explorer.conan_wrapper import ConanApiFactory as ConanApi

from conan_explorer.ui.common import remove_qt_logger
from conan_explorer.ui.main_window import MainWindow
from conan_explorer.settings import *
from conan_explorer.conan_wrapper.types import ConanRef
from conan_explorer import conan_version

exe_ext = ".exe" if platform.system() == "Windows" else ""
conan_server_thread = None
# setup conan test server
TEST_REF = "example/9.9.9@local/testing"
TEST_REF_OFFICIAL = "example/1.0.0@_/_"
SKIP_CREATE_CONAN_TEST_DATA = str2bool(os.getenv("SKIP_CREATE_CONAN_TEST_DATA", "False"))
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


def check_if_process_running(process_name, cmd_contains=[], kill=False, cmd_narg=1, timeout_s=10) -> bool:
    start_time = datetime.now()
    while datetime.now() - start_time < timedelta(seconds=timeout_s) or timeout_s == 0:
        for process in psutil.process_iter():
            try:
                if process_name.lower() in process.name().lower():
                    matches = 0
                    cmdline = ""
                    for cmd_contain in cmd_contains:
                        cmdline = process.cmdline()
                        if cmd_contain in cmdline[cmd_narg]:
                            matches += 1
                    if matches == len(cmd_contains):
                        if kill:
                            try:
                                # or parent.children() for recursive=False
                                for child in process.children(recursive=True):
                                    child.terminate()
                                process.terminate()
                            except:
                                process.kill()
                        return True
                    else:
                        print(f"Not matching arguments: {cmd_contains} in cmdline {cmdline} arg nr. {cmd_narg}")

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, IndexError):
                pass
        print(f"Not found process {process_name}, keep looking...")
        if timeout_s == 0:
            return False
        time.sleep(1)
    return False


def conan_install_ref(ref, args="", profile=None):
    paths = PathSetup()
    profiles_path = paths.testdata_path / "conan" / "profile"
    extra_cmd = ""
    if conan_version.major == 2:
        extra_cmd = "--requires"
        if not profile:
            profile = platform.system().lower()
        profile = "windowsV2" if profile == "windows" else "linuxV2"
    if profile:
        args += " -pr " + str(profiles_path / profile)
    assert os.system(f"conan install {extra_cmd} {ref} {args}") == 0

def conan_remove_ref(ref):
    if conan_version.major == 2:
        os.system(f"conan remove {ref} -c")
    else:
        os.system(f"conan remove {ref} -f")

def conan_add_editables(conanfile_path: str, reference: ConanRef): # , path: str
    if conan_version.major == 2:
        os.system(f"conan editable add --version {reference.version} "
                  f"--channel {reference.channel} --user {reference.user}  {conanfile_path}")
    else:
        os.system(f"conan editable add {conanfile_path} {str(reference)}")

def conan_create_and_upload(conanfile: str, ref: str, create_params=""):
    if conan_version.major == 1:
        os.system(f"conan create {conanfile} {ref} {create_params}")
        os.system(f"conan upload {ref} -r {TEST_REMOTE_NAME} --force --all")
    elif conan_version.major == 2:
        ref = ref.replace("@_/_", "") # does not work anymore...
        cfr = ConanRef.loads(ref)
        extra_args = ""
        if cfr.user:
            extra_args = f"--user={cfr.user} "
        if cfr.channel:
            extra_args += f"--channel={cfr.channel} "
        os.system(
            f"conan create {conanfile} --name={cfr.name} --version={cfr.version} {extra_args} {create_params}")
        os.system(f"conan upload {ref} -r {TEST_REMOTE_NAME} --force")


def create_test_ref(ref, paths, create_params=[""], update=False):
    if conan_version.major == 2:
        ref = ref.replace("@_/_", "") # does not work anymore...
    native_ref = str(ConanRef.loads(ref))
    conan = ConanApi()
    conan.init_api()

    pkgs = conan.search_recipes_in_remotes(native_ref)

    if not update:
        for pkg in pkgs:
            if str(pkg) == native_ref:
                return
    conanfile = str(paths.testdata_path / "conan" / "conanfile.py")
    if conan_version.major == 2:
        conanfile = str(paths.testdata_path / "conan" / "conanfileV2.py")

    for param in create_params:
        conan_create_and_upload(conanfile, ref, param)

def add_remote(remote_name, url):
    if conan_version.major == 1:
        os.system(f"conan remote add {remote_name} {url} false")
    elif conan_version.major == 2:
        os.system(f"conan remote add {remote_name} {url} --insecure")

def remove_remote(remote_name):
    os.system(f"conan remote remove {remote_name}")

def login_test_remote(remote_name):
    if conan_version.major == 1:
        os.system(f"conan user demo -r {remote_name} -p demo")

    elif conan_version.major == 2:
        os.system(f"conan remote login {remote_name} demo -p demo")

def logout_all_remotes():
    if conan_version.major == 1:
        os.system("conan user --clean")
    elif conan_version.major == 2:
        os.system('conan remote logout "*"') # need " for linux

def clean_remotes_on_ci():
    if not is_ci_job():
        return
    if conan_version.major == 1:
        os.system("conan remote clean")
    elif conan_version.major == 2:
        os.system("conan remote remove conancenter")

def get_profiles():
    profiles = ["windows", "linux"]
    if conan_version.major == 2:
        profiles = ["windowsV2", "linuxV2"]
    return profiles

def get_current_profile():
    profiles = get_profiles()
    for profile in profiles:
        if platform.system().lower() in profile:
            return profile


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
    with config_path.open('w', encoding="utf8") as fd:
        cp.write(fd)

    # Setup default profile
    paths = PathSetup()
    profiles_path = paths.testdata_path / "conan" / "profile"
    if conan_version.major == 1:
        conan = ConanApi()
        conan.init_api()
        os.makedirs(conan._client_cache.profiles_path, exist_ok=True)
        shutil.copy(str(profiles_path / platform.system().lower()),  conan._client_cache.default_profile_path)
    elif conan_version.major == 2:
        os.system("conan profile detect")

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
    clean_remotes_on_ci()
    add_remote(TEST_REMOTE_NAME, TEST_REMOTE_URL)
    login_test_remote(TEST_REMOTE_NAME)
    os.system(f"conan remote enable {TEST_REMOTE_NAME}")
    # Create test data
    if SKIP_CREATE_CONAN_TEST_DATA:
        return
    print("CREATING TESTDATA FOR LOCAL CONAN SERVER")

    for profile in get_profiles():
        profile_path = profiles_path / profile
        create_test_ref(TEST_REF, paths, [f"-pr {str(profile_path)}",
                         f"-o shared=False -pr {str(profile_path)}"], update=True)
        create_test_ref(TEST_REF_OFFICIAL, paths, [f"-pr {str(profile_path)}"], update=True)
        if not conan_version.major == 2:
            paths = PathSetup()
            conanfile = str(paths.testdata_path / "conan" / "conanfile_no_settings.py")
            conan_create_and_upload(conanfile,  "nocompsettings/1.0.0@local/no_sets")


@pytest.fixture(scope="session", autouse=True)
def ConanServer():
    os.environ["CONAN_NON_INTERACTIVE"] = "True"  # don't hang is smth. goes wrong
    started = False
    if not check_if_process_running("conan_server", timeout_s=0):
        started = True
        print("STARTING CONAN SERVER")
        start_conan_server()
    yield
    if started:
        print("\nKILLING CONAN SERVER\n ")
        check_if_process_running("conan_server", timeout_s=0, kill=True)
        conan_server_thread.join()


@pytest.fixture(autouse=True)
def test_output():
    print("\n********************** Starting TEST ********************************")
    yield
    print("\n********************** Finished TEST ********************************")


@pytest.fixture
def app_qt_fixture(qtbot):
    yield qtbot
    import conan_explorer.app as app
    # remove logger, so the logger doesn't log into nonexistant qt gui
    remove_qt_logger(app.Logger(), MainWindow.qt_logger_name)
    # finish worker - otherwise errors and crashes will occur!
    if app.conan_worker:
        app.conan_worker.finish_working(3)


@pytest.fixture
def base_fixture()-> Generator[PathSetup, None, None]:
    """
    Set up the global variables to be able to start the application.
    Needs to be used, if the tested component uses the global Logger.
    Clean up all instances after the test.
    """
    paths = PathSetup()
    os.environ["CONAN_REVISIONS_ENABLED"] = "1"
    os.environ["DISABLE_ASYNC_LOADER"] = "True"  # for code coverage to work
    import conan_explorer.app as app

    settings_ini_path = user_save_path / (SETTINGS_FILE_NAME + "." + SETTINGS_INI_TYPE)
    os.remove(str(settings_ini_path))
    app.active_settings = settings_factory(SETTINGS_INI_TYPE, settings_ini_path)
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
    import conan_explorer.app as app
    app.active_settings.set(GUI_MODE, GUI_MODE_LIGHT)
    app.active_settings.set(GUI_STYLE, GUI_STYLE_MATERIAL)


def temp_ui_config(config_file_path: Path):
    temp_config_file_path = shutil.copy(config_file_path, tempfile.gettempdir())
    tmp_file = tempfile.mkstemp()
    import conan_explorer.app as app

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

@contextmanager
def escape_venv():
    # don't do this while testing! if it errors or the gui is closed, while this is running,
    #  the whole testrun will be compromised!
    if os.getenv("PYTEST_CURRENT_TEST"):
        yield
    if os.getenv("PYTEST_CURRENT_TEST"):
        return
    path_var = os.environ.get("PATH", "")
    bin_path = Path(sys.executable).parent
    import re
    path_regex = re.compile(re.escape(str(bin_path)), re.IGNORECASE)
    new_path_var = path_regex.sub('', path_var)
    apply_vars = {"PATH": new_path_var}
    old_env = dict(os.environ)
    os.environ.update(apply_vars)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_env)