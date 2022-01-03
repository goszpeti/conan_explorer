import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import List

from conan_app_launcher.logger import Logger


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
    if platform.system() == "Linux":
        return # TODO how to implement this?
    elif platform.system() == "Windows":
        # select switch for highlighting
        # TODO: spawns an empty visible shell on some/slower? systems
        os.system("explorer /select," + str(file_path))


def open_cmd_in_path(file_path: Path) -> int:
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
        path_exts = [".cmd", ".com", ".bat", ".ps1", ".exe"]
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
        if platform.system() == "Windows":
            return execute_cmd(cmd, is_console_app)
        elif platform.system() == "Linux":
            if is_console_app:
                # Sadly, there is no default way to do this, because of the miriad terminal emulators available
                # Use the default distro emulator, with x-terminal-emulator
                # (sudo update-alternatives --config x-terminal-emulator)
                # This works only on debian distros.
                cmd = ["x-terminal-emulator", "-e", str(executable)]
            if args:
                cmd += args.strip().split(" ")
            proc = subprocess.Popen(cmd)
            return proc.pid
    Logger().warning(f"No executable {str(executable)} to start.")
    return 0

def execute_cmd(cmd: List[str], is_console_app: bool) -> int:
    # Linux call errors on creationflags argument, so the calls must be separated
    if platform.system() == "Windows":
        creationflags = 0
        if is_console_app:
            creationflags = subprocess.CREATE_NEW_CONSOLE
        # don't use 'executable' arg of Popen, because then shell scripts won't execute correctly
        proc = subprocess.Popen(cmd, creationflags=creationflags)
        return proc.pid
    elif platform.system() == "Linux":
        proc = subprocess.Popen(cmd)
        return proc.pid
    return 0

def open_file(file: Path):
    """ Open files with their associated programs """
    if file.absolute().is_file():
        if platform.system() == 'Windows':
            os.startfile(str(file))
        elif platform.system() == "Linux":
            subprocess.call(('xdg-open', str(file)))
