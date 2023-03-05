import os
import platform
import stat
import subprocess
import sys
import tempfile
import time
from distutils.dir_util import remove_tree
from pathlib import Path
from subprocess import check_output
from test.conftest import check_if_process_running, get_window_pid, is_ci_job

import conan_app_launcher  # for mocker
import psutil
from conan_app_launcher import INVALID_PATH, PKG_NAME
from conan_app_launcher.core.system import (calc_paste_same_dir_name,
                                            copy_path_with_overwrite,
                                            delete_path, execute_app, find_program_in_windows,
                                            open_file, open_in_file_manager,
                                            run_file)


def test_choose_run_file(tmp_path, mocker):
    """
    Tests, that the function call is propagated correctly
    Existing path with a filesize > 0 expected
    """
    # Mock away the calls
    mocker.patch('conan_app_launcher.core.system.open_file')
    mocker.patch('conan_app_launcher.core.system.execute_app')

    # test with nonexistant path - nothing should happen (no exception raising)

    run_file(Path(INVALID_PATH), False, "")
    conan_app_launcher.core.system.open_file.assert_not_called()
    conan_app_launcher.core.system.execute_app.assert_not_called()

    # test with existing path
    test_file = Path(tmp_path) / "test.txt"
    with open(test_file, "w") as f:
        f.write("test")

    run_file(test_file, False, "")

    conan_app_launcher.core.system.open_file.assert_called_once_with(test_file)


def test_open_in_file_manager(mocker):
    """ Test, that on calling open_in_file_manager a file explorer actually opens """
    current_file_path = Path(__file__)

    if platform.system() == "Windows":
        if is_ci_job():
            mocker.patch('subprocess.Popen')
            ret = open_in_file_manager(current_file_path)
            subprocess.Popen.assert_called_once_with("explorer /select," + str(current_file_path), creationflags=subprocess.CREATE_NO_WINDOW)
            ret.kill()
        else:
            open_in_file_manager(current_file_path)
            time.sleep(2)
            # Does not work in CI :( - On Windows the window title is that of the opened directory name, so we can easily test, if it opened
            pid = get_window_pid(str(current_file_path.parent))
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
        os.system("pkill nautilus")


def test_choose_run_script(tmp_path, mocker):
    """
    Tests, that the function call is propagated correctly
    Existing path with a filesize > 0 expected
    """

    # Mock away the calls
    mocker.patch('conan_app_launcher.core.system.execute_app')

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

    conan_app_launcher.core.system.execute_app.assert_called_once_with(test_file, False, "")


def test_choose_run_exe(tmp_path, mocker):
    """
    Test, that run_file will call execute_app with the correct argumnenst.
    Mock away the actual calls.
    """
    mocker.patch('conan_app_launcher.core.system.execute_app')
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

    conan_app_launcher.core.system.execute_app.assert_called_once_with(test_file, False, "")


def test_start_cli_option_app():
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
        proc = psutil.Process(pid)
        assert proc.name() == "x-terminal-emulator"
        assert PKG_NAME in proc.cmdline()[2]
        os.system("pkill --newest terminal")
    elif platform.system() == "Windows":
        assert pid > 0
        time.sleep(1)
        ret = check_output(f'tasklist /fi "PID eq {str(pid)}"')
        assert "cmd.exe" in ret.decode("utf-8")
        os.system("taskkill /PID " + str(pid))


def test_start_app_with_args_non_cli():
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
    args = f"-c \"f=open(r'{str(test_file)}','w');f.write('test');f.close()\""
    execute_app(executable, is_console_app, args)

    time.sleep(5)  # wait for terminal to spawn
    assert test_file.is_file()

    os.remove(test_file)


def test_start_script(tmp_path):
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


def test_open_file():
    """ Test file opener by opening a text file and checking for the app to spawn"""
    test_file = Path(tempfile.gettempdir(), "test.inf")
    with open(str(test_file), "w") as f:
        f.write("test")
    assert (test_file.exists())

    if platform.system() == "Linux":
        # set default app for textfile
        check_output(["xdg-mime", "default", "mousepad.desktop", "text/plain"]).decode("utf-8")
        time.sleep(1)
    open_file(test_file)

    if platform.system() == "Linux":
        # check pid of created process
        assert check_if_process_running("mousepad", kill=True)
    elif platform.system() == "Windows":
        assert check_if_process_running("notepad.exe", kill=True)
    os.remove(test_file)


def test_copy_paste():
    """ 
    1. Copy file in same dir (renaming)
    2. Copy non-empty dir in same dir (renaming)
    3. Copy file in other dir (non-overwrite)
    4. Copy file in other dir (overwrite)
    5. Copy non-empty dir in other dir (non-overwrite)
    6. Copy non-empty dir in other dir (overwrite)
    """
    # setup a test file
    test_file = Path(tempfile.mkdtemp()) / "test.inf"
    test_file_content = "test"
    with open(str(test_file), "w") as f:
        f.write(test_file_content)

    # 1. Copy file in same dir(renaming)
    new_path = calc_paste_same_dir_name(test_file)
    assert new_path != test_file
    assert "(2)" in new_path.stem

    copy_path_with_overwrite(test_file, new_path)
    assert new_path.exists()
    assert test_file_content == new_path.read_text()
    os.remove(new_path)

    # setup a test dir with a file
    test_dir = Path(tempfile.mkdtemp()) / "test_dir"
    os.makedirs(test_dir)
    test_dir_file = test_dir / "test.inf"
    with open(str(test_dir_file), "w") as f:
        f.write(test_file_content)

    # 2. Copy non-empty dir in same dir(renaming)
    new_path = calc_paste_same_dir_name(test_dir)
    assert new_path != test_dir
    assert "(2)" in new_path.stem
    copy_path_with_overwrite(test_dir, new_path)
    assert new_path.exists()
    assert test_file_content == (new_path / test_file.name).read_text()
    remove_tree(str(new_path), verbose=1)

    # 3. Copy file in other dir(non-overwrite)
    new_dir_path = Path(tempfile.mkdtemp())
    copy_path_with_overwrite(test_file, new_dir_path)
    new_file_path = new_dir_path / test_file.name
    assert new_file_path.exists()
    assert test_file_content == new_file_path.read_text()

    # 4. Copy file in other dir(overwrite)
    # Use the previously copied file
    test_file_overwrite_content = "test2"
    assert test_file_overwrite_content != test_file_content
    with open(str(test_file), "w") as f:
        f.write(test_file_overwrite_content)
    copy_path_with_overwrite(test_file, new_dir_path)
    assert test_file_overwrite_content == new_file_path.read_text()

    # 5. Copy non-empty dir in other dir(non-overwrite)
    new_dir_path = Path(tempfile.mkdtemp()) / test_dir.name
    copy_path_with_overwrite(test_dir, new_dir_path)
    assert new_dir_path.exists()
    assert test_file_content == (new_dir_path / test_file.name).read_text()

    # 6. Copy non-empty dir in other dir(overwrite)
    # Use the previously copied dir
    with open(str(test_dir_file), "w") as f:
        f.write(test_file_overwrite_content)
    copy_path_with_overwrite(test_dir, new_dir_path)
    assert test_file_overwrite_content == (new_dir_path / test_file.name).read_text()
    
def test_delete():
    """ 
    1. Delete file
    2. Delete non-empty directory
    """
    # 1. Delete file
    test_file = Path(tempfile.mkdtemp()) / "test.inf"
    test_file_content = "test"
    with open(str(test_file), "w") as f:
        f.write(test_file_content)
    delete_path(test_file)
    assert not test_file.exists()

    # 2. Delete non-empty directory
    test_dir = Path(tempfile.mkdtemp()) / "test_dir"
    os.makedirs(test_dir)
    test_dir_file = test_dir / "test.inf"
    with open(str(test_dir_file), "w") as f:
        f.write("test")
    delete_path(test_dir)
    assert not test_dir.exists()


def test_find_program_in_registry():

    found_path = find_program_in_windows("Git", True)
    if platform.system() == "Linux":
        assert not found_path
    else:
        assert os.path.exists(found_path)
 