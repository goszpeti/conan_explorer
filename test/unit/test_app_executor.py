import os
import platform
import time
from pathlib import Path
from subprocess import check_output
import tempfile
from conan_app_launcher.config_file import AppEntry
from conan_app_launcher.app_executor import execute_app


def testStartCliOptionApp(base_fixture):
    if platform.system() == "Linux":
        test_file = Path(tempfile.gettempdir(), "test.txt")
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",  Path("/usr/bin/python3"), "",
                            "", True, Path("."))
        execute_app(app_info)
        time.sleep(5)  # wait for terminal to spawn
        # check pid of created process
        ret = check_output(["xwininfo", "-name", "Terminal"]).decode("utf-8")
        assert "Terminal" in ret
        os.system("pkill --newest terminal")


def testRunAppWithArgsNonCli(base_fixture):
    if platform.system() == "Linux":
        test_file = Path(tempfile.gettempdir(), "test.txt")
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",  Path("/usr/bin/python3"),
                            "-c f=open('%s','w');f.write('test');f.close()" % str(test_file), "", False, Path("."))
        execute_app(app_info)
        time.sleep(1)  # wait for terminal to spawn
        assert test_file.is_file()
        os.remove(test_file)
    elif platform.system() == "Windows":
        cmd_path = r"C:\Windows\System32\cmd.exe"  # currently hardcoded...
        test_file = Path(tempfile.gettempdir(), "test.txt")
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",
                            Path(cmd_path), "/c echo test > " + str(test_file), "", False, Path("."))
        execute_app(app_info)
        time.sleep(1)  # wait for terminal to spawn
        assert test_file.is_file()
        os.remove(test_file)


def testRunAppWithArgsCliOption(base_fixture):
    if platform.system() == "Linux":
        test_file = Path(tempfile.gettempdir(), "test.txt")
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",  Path("/usr/bin/python3"),
                            "-c f=open('%s','w');f.write('test');f.close()" % str(test_file), "", True, Path("."))
        execute_app(app_info)
        time.sleep(5)  # wait for terminal to spawn
        assert test_file.is_file()
        os.remove(test_file)
    elif platform.system() == "Windows":
        cmd_path = r"C:\Windows\System32\cmd.exe"  # currently hardcoded...
        test_file = Path(tempfile.gettempdir(), "test.txt")
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",
                            Path(cmd_path), "/c echo test > " + str(test_file), "", True, Path("."))
        execute_app(app_info)
        time.sleep(1)  # wait for terminal to spawn
        assert test_file.is_file()
        os.remove(test_file)
