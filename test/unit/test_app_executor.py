import os
import platform
import sys
import tempfile
import time
from pathlib import Path
from subprocess import check_output

from conan_app_launcher.components.file_runner import (execute_app, open_file,
                                                       run_file)


def testRunFile(base_fixture):
    # Mock away the calls
    pass


def testRunAppWithArgsNonCli(base_fixture):
    test_file = Path(tempfile.gettempdir(), "test.txt")

    executable = Path(sys.executable)
    is_console_app = False
    args = f"-c f=open(r'{str(test_file)}','w');f.write('test');f.close()"
    pid = execute_app(executable, is_console_app, args)
    time.sleep(1)

    assert test_file.is_file()
    os.remove(test_file)


def testRunAppWithArgsCliOption(base_fixture):
    test_file = Path(tempfile.gettempdir(), "test.txt")

    executable = Path(sys.executable)
    is_console_app = True
    args = f"-c f=open(r'{str(test_file)}','w');f.write('test');f.close()"
    pid = execute_app(executable, is_console_app, args)

    time.sleep(5)  # wait for terminal to spawn
    assert test_file.is_file()

    os.remove(test_file)


def testStartCliOptionApp(base_fixture):
    executable = Path(sys.executable)
    is_console_app = True
    args = ""
    pid = execute_app(executable, is_console_app, args)

    if platform.system() == "Linux":
        time.sleep(5)  # wait for terminal to spawn
        # check pid of created process
        ret = check_output(["xwininfo", "-name", "Terminal"]).decode("utf-8")
        assert "Terminal" in ret
        os.system("pkill --newest terminal")
    elif platform.system() == "Windows":
        assert pid > 0
        time.sleep(1)
        ret = check_output(f'tasklist /fi "PID eq {str(pid)}"')
        assert "python.exe" in ret.decode("utf-8")
        os.system("taskkill /PID " + str(pid))


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
