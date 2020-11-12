import platform
import subprocess
import os
from pathlib import Path
from conan_app_launcher.logger import Logger


def execute_app(executable: Path, is_console_app: bool, args: str) -> int:
    """ Executes an application with args and optionally spawns a new shell as specified in the app entry."""
    if executable.absolute().is_file():
        cmd = [str(executable)]
        # Linux call errors on creationflags argument, so the calls must be separated
        if platform.system() == "Windows":
            creationflags = 0
            if is_console_app:
                creationflags = subprocess.CREATE_NEW_CONSOLE
            if args:
                cmd += args.strip().split(" ")
                # don't use 'executable' arg of Popen, because then shell scripts won't execute correctly
            proc = subprocess.Popen(cmd, creationflags=creationflags)
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
    else:
        Logger().warning(f"No executable {str(executable)} to start.")
        return 0


def open_file(file_path: Path):
    """ Open files with their assocoiated programs """
    if file_path.absolute().is_file():
        if platform.system() == 'Windows':
            os.startfile(str(file_path))
        elif platform.system() == "Linux":
            subprocess.call(('xdg-open', str(file_path)))
