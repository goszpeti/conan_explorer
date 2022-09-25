""" OS Abstraction Layer for all file based functions """

import os
import platform
import shutil
import subprocess
import sys
from contextlib import contextmanager
# TODO find replacements for deprecated distutils functions
from distutils.dir_util import copy_tree, remove_tree
from distutils.file_util import copy_file
from pathlib import Path
from typing import List

from conan_app_launcher import PKG_NAME, asset_path
from conan_app_launcher.app.logger import Logger
from jinja2 import Template
from packaging import version

WIN_EXE_FILE_TYPES = [".cmd", ".com", ".bat", ".ps1", ".exe"]


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


def is_windows_11():
    """ Main version number is still 10 - thanks MS! """
    if platform.system() == "Windows" and version.parse(platform.version()) >= version.parse("10.0.22000"):
        return True
    return False


def run_file(file_path: Path, is_console_app: bool, args: str):
    """ Decide, if a file should be opened or executed and call the appropriate method """
    if not file_path.is_file():
        return
    try:
        if is_file_executable(file_path):
            execute_app(file_path, is_console_app, args)
        else:
            open_file(file_path)
    except Exception:
        Logger().error(f"Error while executing {str(file_path)} with args: {args}.")


def open_in_file_manager(file_path: Path):
    """ Show file in file manager. """
    if platform.system() == "Linux":
        # no standardized select functionailty.
        # However xdg-open on a dir will open the folder in the default file explorer.
        dir_to_view = file_path.parent if file_path.is_file() else file_path
        return subprocess.Popen(("xdg-open", str(dir_to_view)))
    elif platform.system() == "Windows":
        # select switch for highlighting
        creationflags = 0
        if version.parse(platform.python_version()) >= version.parse("3.7.0"):
            creationflags = subprocess.CREATE_NO_WINDOW  # available since 3.7
        return subprocess.Popen("explorer /select," + str(file_path), creationflags=creationflags)


def open_cmd_in_path(file_path: Path) -> int:
    """ Open a terminal in the selected folder. """
    if platform.system() == "Linux":
        return execute_cmd(["x-terminal-emulator", "-e", "cd", f"{str(file_path)}", "bash"], True)
    elif platform.system() == "Windows":
        cmd_path = shutil.which("cmd")
        if cmd_path:
            return execute_app(Path(cmd_path), True, f"/k cd {str(file_path)}")
    return 0


def is_file_executable(file_path: Path) -> bool:
    """ Checking execution mode is ok on linux, but not enough on windows, since every file with an associated
     program has this flag. Use custom pathext lists to determine executable file extensions. """
    is_executable = False
    if platform.system() == "Linux":
        if os.access(str(file_path), os.X_OK):
            is_executable = True
    elif platform.system() == "Windows":
        # don't use PATHEXT - some programs write other filetypes like .py in it...
        path_exts = WIN_EXE_FILE_TYPES
        if file_path.suffix in path_exts:
            is_executable = True
    return is_executable


def execute_app(executable: Path, is_console_app: bool, args: str) -> int:
    """
    Executes an application with args and optionally spawns a new shell
    as specified in the app entry.
    Returns the pid of the new process.
    """
    if executable.absolute().is_file():
        cmd = [str(executable)]
        if args:
            cmd += args.strip().split(" ")
        return execute_cmd(cmd, is_console_app)
    Logger().warning(f"No executable {str(executable)} to start.")
    return 0


def execute_cmd(cmd: List[str], is_console_app: bool) -> int:
    """ Generic process execute method. Returns pid. """
    # Linux call errors on creationflags argument, so the calls must be separated
    if platform.system() == "Windows":
        creationflags = 0
        if is_console_app:
            creationflags = subprocess.CREATE_NEW_CONSOLE
            cmd = [generate_launch_script(cmd)]
        # don't use 'executable' arg of Popen, because then shell scripts won't execute correctly
        proc = subprocess.Popen(cmd, creationflags=creationflags)
        return proc.pid
    elif platform.system() == "Linux":
        if is_console_app:
            # Sadly, there is no default way to do this, because of the miriad terminal emulators available
            # Use the default distro emulator, with x-terminal-emulator
            # (sudo update-alternatives --config x-terminal-emulator)
            # This works only on debian distros.
            cmd = [generate_launch_script(cmd)]
            cmd = ["x-terminal-emulator", "-e"] + cmd
        proc = subprocess.Popen(cmd)
        return proc.pid
    return 0


def generate_launch_script(cmd: List[str]) -> str:
    import tempfile
    launch_templ_file = ""

    if platform.system() == 'Windows':
        launch_templ_file = "launch.bat.in"
        temp_fd, temp_path_str = tempfile.mkstemp(".bat", prefix=PKG_NAME, text=True)
    elif platform.system() == "Linux":
        launch_templ_file = "launch.sh.in"
        temp_fd, temp_path_str = tempfile.mkstemp(".sh", prefix=PKG_NAME, text=True)
    else:
        Logger().warning(f"Not supported OS.")
        return ""
    launch_templ_path = asset_path / launch_templ_file
    with open(launch_templ_path, "r") as fd:
        launch_template = Template(fd.read())
    launch_content = launch_template.render(COMMAND=" ".join(cmd))
    with os.fdopen(temp_fd, 'w') as f:
        f.write(launch_content)
    if platform.system() == 'Linux':
        os.system(f"chmod +x {temp_path_str}")
    return temp_path_str


def open_file(file: Path):
    """ Open files with their associated programs """
    if file.absolute().is_file():
        if platform.system() == 'Windows':
            os.startfile(str(file))
        elif platform.system() == "Linux":
            subprocess.Popen(("xdg-open", str(file)))


def delete_path(dst: Path):
    """
    Delete file or (non-empty) folder recursively. 
    Exceptions will be caught and message logged to stdout.
    """
    try:
        if dst.is_file():
            os.remove(dst)
        elif dst.is_dir():
            remove_tree(str(dst), verbose=1)
    except Exception as e:
        Logger().warning(f"Can't delete {str(dst)}: {str(e)}")


def copy_path_with_overwrite(src: Path, dst: Path):
    """
    Copy files/directories while overwriting possible files and adding missing ones.
    Directories will be copied from under source, so you may need to add the orig. folder name, if you want that!
    Exceptions will be caught and message logged to stdout.
    """
    try:
        if src.is_file():
            copy_file(str(src), str(dst))
        else:
            copy_tree(str(src), str(dst))
    except Exception as e:
        Logger().warning(f"Can't copy {str(src)} to {str(dst)}: {str(e)}")


def calc_paste_same_dir_name(dst: Path, index=1):
    """
    Create a name for a file like /file.txt -> /file (2).txt.
    It will find the next empty number.
    If a file with a higher number exists it will ignore it.
    """
    if dst.exists():
        new_path = dst.with_name(f"{dst.stem} ({str(index+1)}){dst.suffix}")
        possible_path = calc_paste_same_dir_name(new_path, index+1)
        if possible_path == Path("NULL"):
            return new_path
        else:
            return dst
    else:
        if index == 1:  # if file does not exist
            return dst
        return Path("NULL")
