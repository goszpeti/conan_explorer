import os
import platform
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from subprocess import check_output
from test.conftest import get_window_pid, is_ci_job

import conan_app_launcher  # for mocker
import psutil
from conan_app_launcher.core.system import (execute_app, open_file,
                                                 open_in_file_manager,
                                                 run_file)


def test_choose_run_file(base_fixture, tmp_path, mocker):
    """
    Tests, that the function call is propagated correctly
    Existing path with a filesize > 0 expected
    """
    # Mock away the calls
    mocker.patch('conan_app_launcher.core.file_runner.open_file')
    mocker.patch('conan_app_launcher.core.file_runner.execute_app')

    # test with nonexistant path - nothing should happen (no exception raising)

    run_file(Path("NULL"), False, "")
    conan_app_launcher.core.file_runner.open_file.assert_not_called()
    conan_app_launcher.core.file_runner.execute_app.assert_not_called()

    # test with existing path
    test_file = Path(tmp_path) / "test.txt"
    with open(test_file, "w") as f:
        f.write("test")

    run_file(test_file, False, "")

    conan_app_launcher.core.file_runner.open_file.assert_called_once_with(test_file)


def test_open_in_file_manager(base_fixture, mocker):
    """ Test, that on calling open_in_file_manager a file explorer actually opens """
    current_file_path = Path(__file__)

    if platform.system() == "Windows":
        if is_ci_job():
            mocker.patch('subprocess.Popen')
            ret = open_in_file_manager(current_file_path)
            subprocess.Popen.assert_called_once_with("explorer /select," + str(current_file_path), creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            open_in_file_manager(current_file_path)
            time.sleep(2)
            # Does not work in CI :( - On Windows the window title is that of the opened directory name, so we can easily test, if it opened
            pid = get_window_pid(current_file_path.parent.name)
            assert pid > 0
            proc = psutil.Process(pid)
            proc.kill()
    else:
        ret = open_in_file_manager(current_file_path)
        assert ret.pid > 0
        time.sleep(3)
        proc = psutil.Process(ret.pid)
        assert len(proc.children()) == 1
        # list a few candidates
        assert proc.children()[0].name() in ["nautilus", "chrome", "thunar", "dolphin", "pcmanfm"]
    ret.kill()



def test_choose_run_script(base_fixture, tmp_path, mocker):
    """
    Tests, that the function call is propagated correctly
    Existing path with a filesize > 0 expected
    """

    # Mock away the calls
    mocker.patch('conan_app_launcher.core.file_runner.execute_app')

    if platform.system() == "Windows":
        test_file = Path(tmp_path) / "test.bat"
    else:
        test_file = Path(tmp_path) / "test.sh"

    with open(test_file, "w") as f:
        f.write("test")

    if platform.system() == "Linux":
        st = os.stat(str(test_file))
        os.chmod(str(test_file), st.st_mode | stat.S_IEXEC)

    run_file(test_file, False, "")

    conan_app_launcher.core.file_runner.execute_app.assert_called_once_with(test_file, False, "")


def test_choose_run_exe(base_fixture, tmp_path, mocker):
    """
    Test, that run_file will call execute_app with the correct argumnenst.
    Mock away the actual calls.
    """
    mocker.patch('conan_app_launcher.core.file_runner.execute_app')
    test_file = Path()
    if platform.system() == "Linux":
        test_file = Path(tmp_path) / "test"
        with open(test_file, "w") as f:
            f.write("test")
        # use chmod to set as executable
        st = os.stat(str(test_file))
        os.chmod(str(test_file), st.st_mode | stat.S_IEXEC)
    elif platform.system() == "Windows":
        test_file = Path(tmp_path) / "test.exe"
        with open(test_file, "w") as f:
            f.write("test")

    run_file(test_file, False, "")

    conan_app_launcher.core.file_runner.execute_app.assert_called_once_with(test_file, False, "")


def test_start_cli_option_app(base_fixture):
    """
    Test, that starting with the option is_console_app
    will spawn a terminal.
    """
    executable = Path(sys.executable)
    is_console_app = True
    test_file = Path(tempfile.gettempdir(), "test.txt")
    args = ""  # no args os it stays open
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


def test_start_app_with_args_non_cli(base_fixture):
    """
    Test that the CLI args will be correctly passed to a non-console app, 
    by writing out a file in a shell cmd and check, if the file has been created.
    """
    test_file = Path(tempfile.gettempdir(), "test.txt")
    executable = Path(sys.executable)
    is_console_app = False
    args = f"-c f=open(r'{str(test_file)}','w');f.write('test');f.close()"

    execute_app(executable, is_console_app, args)

    time.sleep(1)
    assert test_file.is_file()
    os.remove(test_file)


def test_start_app_with_args_cli_option(base_fixture):
    """
    Test that the CLI args will be correctly passed to a console app, 
    by writing out a file in a shell cmd and check, if the file has been created.
    """
    test_file = Path(tempfile.gettempdir(), "test.txt")

    executable = Path(sys.executable)
    is_console_app = True
    args = f"-c f=open(r'{str(test_file)}','w');f.write('test');f.close()"
    execute_app(executable, is_console_app, args)

    time.sleep(5)  # wait for terminal to spawn
    assert test_file.is_file()

    os.remove(test_file)


def test_start_script(base_fixture, tmp_path):
    """
    Test, that calling a batch script will be actually execute,
    by checking if it will write a file. Windows only!
    """
    if platform.system() != "Windows":
        return
    res_file = Path(tmp_path) / "res.txt"
    assert not res_file.is_file()
    test_file = Path(tmp_path) / "test.bat"
    with open(test_file, "w") as f:
        f.write("echo test > " + str(res_file))

    execute_app(test_file, False, "")

    time.sleep(2)  # wait for command to be executed

    assert res_file.is_file()


def test_open_file(base_fixture):
    """ Test file opener by opening a text file and checking for the app to spawn"""
    test_file = Path(tempfile.gettempdir(), "test.inf")
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
        assert default_app in ret.decode("utf-8").lower()
        lines = ret.decode("utf-8").splitlines()
        line = lines[3].replace(" ", "").lower()
        pid = line.split(default_app)[1].split("console")[0]
        os.system("taskkill /PID " + pid)
    os.remove(test_file)
