""" OS Abstraction Layer for all file based functions """

import os
import platform
import shutil
import subprocess
import tempfile

from pathlib import Path
from typing import List

from jinja2 import Template

from conan_explorer import INVALID_PATH, PKG_NAME, asset_path
from conan_explorer.app.logger import Logger

WIN_EXE_FILE_TYPES = [".cmd", ".com", ".bat", ".ps1", ".exe"]


def str2bool(value: str) -> bool:
    """ Own impl. isntead of distutils.util.strtobool
      because distutils will be deprecated """
    value = value.lower()
    if value in {'yes', 'true', 'y', '1'}:
        return True
    if value in {'no', 'false', 'n', '0'}:
        return False
    return False


def is_windows_11():
    """ Main version number is still 10 - thanks MS! """
    from packaging import version
    if platform.system() == "Windows" and \
            version.parse(platform.version()) >= version.parse("10.0.22000"):
        return True
    return False


def run_file(file_path: Path, is_console_app: bool, args: str):
    " Decide, if a file should be opened or executed and call the appropriate method "
    if not file_path.is_file():
        return
    try:
        if is_file_executable(file_path):
            execute_app(file_path, is_console_app, args)
        else:
            open_file(file_path)
    except Exception:
        Logger().error(
            f"Error while executing {str(file_path)} with args: {args}.")


def open_in_file_manager(file_path: Path):
    """ Show file in file manager. """
    try:
        if platform.system() == "Linux":
            # no standardized select functionailty.
            # xdg-open on a dir will open the folder in the default file explorer.
            dir_to_view = file_path.parent if file_path.is_file() else file_path
            return subprocess.Popen(("xdg-open", str(dir_to_view)))
        elif platform.system() == "Windows":
            # select switch for highlighting
            creationflags = subprocess.CREATE_NO_WINDOW  # available since 3.7
            return subprocess.Popen("explorer /select," + str(file_path),
                                    creationflags=creationflags)
    except Exception as e:
        Logger().error(f"Can't show path in file-manager: {str(e)}")


def open_cmd_in_path(file_path: Path) -> int:
    """ Open a terminal in the selected folder. """
    try:
        if platform.system() == "Linux":
            return execute_cmd(["x-terminal-emulator", "-e", '"', 
                                "cd", f"{str(file_path)}", "&&", "bash", '"'], True)
        elif platform.system() == "Windows":
            cmd_path = shutil.which("cmd")
            if cmd_path:
                return execute_app(Path(cmd_path), True, f"/k cd {str(file_path)}")
        return 0
    except Exception as e:
        Logger().error(f"Can't open cmd in path: {str(e)}")
        return 0


def is_file_executable(file_path: Path) -> bool:
    """ Checking execution mode is ok on linux, but not enough on windows, 
    since every file with an associated program has this flag. 
    Use custom pathext like list to determine executable file extensions. """
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
    Executes an application with args and optionally spawns a new shell.
    Returns the pid of the new process.
    """
    if executable.absolute().is_file():
        cmd = [str(executable)]
        if args:
            cmd += args.strip().split(" ")
        return execute_cmd(cmd, is_console_app)
    Logger().warning(f"No executable {str(executable)} to start.")
    return 0


def execute_cmd(cmd: List[str], is_console_app: bool) -> int:  # pid
    """ Generic process execute method. Returns pid. """
    command_path = Path(cmd[0]).parent
    try:
        # Linux call errors on creationflags argument, so the calls must be separated
        if platform.system() == "Windows":
            creationflags = 0
            if is_console_app:
                creationflags = subprocess.CREATE_NEW_CONSOLE
                cmd = [generate_launch_script(cmd)]
            # don't use 'executable' arg of Popen, because shell scripts won't execute correctly
            proc = subprocess.Popen(
                cmd, creationflags=creationflags, cwd=str(command_path))
            return proc.pid
        elif platform.system() == "Linux":
            if is_console_app:
                # Sadly, there is no default way to do this, because of the miriad terminal
                # emulators available. Use the default distro emulator through x-terminal-emulator
                # This works only on debian distros.
                cmd = ["x-terminal-emulator", "-e"] + [generate_launch_script(cmd)]
            proc = subprocess.Popen(cmd, cwd=str(command_path))
            return proc.pid
        return 0
    except Exception as e:
        Logger().error(f"Can't execute cmd: {str(e)}")
        return 0


def generate_launch_script(cmd: List[str]) -> str:
    """
    Generate a launch script for shell cmd, which will halt on error and not close
    the terminal.
    """
    launch_templ_file = ""

    if platform.system() == 'Windows':
        launch_templ_file = "launch.bat.in"
        temp_fd, temp_path_str = tempfile.mkstemp(
            ".bat", prefix=PKG_NAME, text=True)
    elif platform.system() == "Linux":
        launch_templ_file = "launch.sh.in"
        temp_fd, temp_path_str = tempfile.mkstemp(
            ".sh", prefix=PKG_NAME, text=True)
    else:
        Logger().warning("Not supported OS.")
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
    try:
        if file.absolute().is_file():
            if platform.system() == 'Windows':
                os.startfile(str(file))
            elif platform.system() == "Linux":
                subprocess.Popen(("xdg-open", str(file)))
    except Exception as e:
        Logger().error(f"Can't open file: {str(e)}")
        return 0


def delete_path(dst: Path):
    """
    Delete file or (non-empty) folder recursively.
    Exceptions will be caught and message logged to stdout.
    """
    from shutil import rmtree
    try:
        if dst.is_file():
            os.remove(dst)
        elif dst.is_dir():
            rmtree(str(dst), ignore_errors=True)
    except Exception as e:
        Logger().warning(f"Can't delete {str(dst)}: {str(e)}")


def copy_path_with_overwrite(src: Path, dst: Path):
    """
    Copy files/directories while overwriting possible files and adding missing ones.
    Directories will be copied from under source, so you may need to add the original
    folder name, if you want that!
    Exceptions will be caught and message logged to stdout.
    """
    from shutil import copytree, copy2
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            copy2(str(src), str(dst))
        else:
            copytree(str(src), str(dst), dirs_exist_ok=True)
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
        if possible_path == Path(INVALID_PATH):
            return new_path
        else:
            return dst
    else:
        if index == 1:  # if file does not exist
            return dst
        return Path(INVALID_PATH)


def get_default_file_editor():
    if platform.system() == "Windows":
        editor_executable = find_program_in_windows(
            "Notepad++", partial_match=True, key_to_find="DisplayIcon")
        if Path(editor_executable).exists():
            return editor_executable
        return "notepad.exe"
    else:
        return "gedit"  # distro dependent, but make something


def find_program_in_windows(app_name: str, partial_match=False, 
                                                key_to_find="InstallLocation") -> str:
    if platform.system() != "Windows":
        return ""

    import winreg
    arch_keys = {winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY}
    for arch_key in arch_keys:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 
            0, winreg.KEY_READ | arch_key)
        for i in range(0, winreg.QueryInfoKey(key)[0]):
            sub_key_name = winreg.EnumKey(key, i)
            sub_key = winreg.OpenKey(key, sub_key_name)
            try:
                current_app_name = winreg.QueryValueEx(
                    sub_key, "DisplayName")[0]
                if partial_match:
                    if app_name in current_app_name:
                        location = winreg.QueryValueEx(sub_key, key_to_find)[0]
                        return location
                if app_name == current_app_name:
                    location = winreg.QueryValueEx(sub_key, key_to_find)[0]
                    return location
            except OSError:
                pass
            finally:
                sub_key.Close()
    return ""


def check_for_wayland() -> bool:
    if platform.system() != "Linux":
        return False
    if os.getenv("XDG_SESSION_TYPE", "").lower() == "wayland" or \
       os.getenv("WAYLAND_DISPLAY"):
        Logger().debug("Found XDG_SESSION_TYPE==wayland or WAYLAND_DISPLAY")
        return True
    return False
