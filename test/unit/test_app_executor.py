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
    elif platform.system() == "Windows":
        cmd_path = os.getenv("COMSPEC")
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",
                            Path(cmd_path), "", "", True, Path("."))
        execute_app(app_info)
        time.sleep(1)
        ret = check_output('tasklist /fi "WINDOWTITLE eq %s"' % cmd_path)
        assert "cmd.exe" in ret.decode("utf-8")
        lines = ret.decode("utf-8").splitlines()
        line = lines[3].replace(" ", "")
        pid = line.split("cmd.exe")[1].split("Console")[0]
        os.system("taskkill /PID " + pid)


def testRunAppWithArgsNonCli(base_fixture):
    test_file = Path(tempfile.gettempdir(), "test.txt")

    if platform.system() == "Linux":
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",  Path("/usr/bin/python3"),
                            "-c f=open('%s','w');f.write('test');f.close()" % str(test_file), "", False, Path("."))
        execute_app(app_info)
        time.sleep(1)
        assert test_file.is_file()
        os.remove(test_file)
    elif platform.system() == "Windows":
        cmd_path = r"C:\Windows\System32\cmd.exe"  # currently hardcoded...
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",
                            Path(cmd_path), "/c echo test > " + str(test_file), "", False, Path("."))
        execute_app(app_info)
        time.sleep(1)
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
