import os
import platform
import sys
import time
from pathlib import Path
from subprocess import check_output
import tempfile
from conan_app_launcher.config_file import AppEntry
from conan_app_launcher.file_runner import execute_app, open_file


def testStartCliOptionApp(base_fixture):
    if platform.system() == "Linux":
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",  Path("/usr/bin/python3"), "",
                            "", True, Path("."))
        execute_app(app_info.executable, app_info.is_console_application, app_info.args)
        time.sleep(5)  # wait for terminal to spawn
        # check pid of created process
        ret = check_output(["xwininfo", "-name", "Terminal"]).decode("utf-8")
        assert "Terminal" in ret
        os.system("pkill --newest terminal")
    elif platform.system() == "Windows":

        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",
                            Path(sys.executable), "", "", True, Path("."))
        pid = execute_app(app_info.executable, app_info.is_console_application, app_info.args)
        assert pid > 0
        time.sleep(1)
        ret = check_output(f'tasklist /fi "PID eq {str(pid)}"')
        assert "python.exe" in ret.decode("utf-8")
        os.system("taskkill /PID " + str(pid))


def testRunAppWithArgsNonCli(base_fixture):
    test_file = Path(tempfile.gettempdir(), "test.txt")

    if platform.system() == "Linux":
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",  Path("/usr/bin/python3"),
                            "-c f=open('%s','w');f.write('test');f.close()" % str(test_file), "", False, Path("."))
        execute_app(app_info.executable, app_info.is_console_application, app_info.args)
        time.sleep(1)
        assert test_file.is_file()
        os.remove(test_file)
    elif platform.system() == "Windows":
        cmd_path = os.getenv("COMSPEC")
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",
                            Path(cmd_path), "/c echo test > " + str(test_file), "", False, Path("."))
        execute_app(app_info.executable, app_info.is_console_application, app_info.args)
        time.sleep(1)
        assert test_file.is_file()
        os.remove(test_file)


def testRunAppWithArgsCliOption(base_fixture):
    if platform.system() == "Linux":
        test_file = Path(tempfile.gettempdir(), "test.txt")
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",  Path("/usr/bin/python3"),
                            "-c f=open('%s','w');f.write('test');f.close()" % str(test_file), "", True, Path("."))
        execute_app(app_info.executable, app_info.is_console_application, app_info.args)
        time.sleep(5)  # wait for terminal to spawn
        assert test_file.is_file()
    elif platform.system() == "Windows":
        cmd_path = os.getenv("COMSPEC")
        test_file = Path(tempfile.gettempdir(), "test.txt")
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",
                            Path(cmd_path), "/c echo test > " + str(test_file), "", True, Path("."))
        execute_app(app_info.executable, app_info.is_console_application, app_info.args)
        time.sleep(1)  # wait for terminal to spawn
        assert test_file.is_file()
    os.remove(test_file)


def testOpenFile(base_fixture):
    """ Test file opener by opening a text file and checking for the app to spawn"""
    test_file = Path(tempfile.gettempdir(), "test.txt")
    with open(str(test_file), "w") as f:
        f.write("test")
    open_file(test_file)
    time.sleep(3)  # wait for program to start

    if platform.system() == "Linux":
        # set for textfile
        ret = check_output(["xdg-mime", "default", "org.gnome.Terminal.desktop",
                            "text/plain"]).decode("utf-8")

        ret = check_output(["xdg-mime", "query", "default", "text/plain"]).decode("utf-8")
        # check pid of created process
        ret = check_output(["xwininfo", "-name", "Terminal"]).decode("utf-8")
        assert "Terminal" in ret
        os.system("pkill --newest terminal")
    elif platform.system() == "Windows":
        default_app = "notepad.exe"
        # this is application specific
        ret = check_output(f'tasklist /fi "IMAGENAME eq {default_app}"')
        assert default_app in ret.decode("utf-8")
        lines = ret.decode("utf-8").splitlines()
        line = lines[3].replace(" ", "")
        pid = line.split(default_app)[1].split("Console")[0]
        os.system("taskkill /PID " + pid)
    os.remove(test_file)
