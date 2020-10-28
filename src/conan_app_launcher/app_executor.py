import platform
import subprocess

from conan_app_launcher.config_file import AppEntry


def execute_app(app_info: AppEntry):
    """ Executes an application with args and optionally spawns a new shell as specified in the app entry."""
    if app_info.executable.absolute().is_file():
        cmd = [str(app_info.executable)]
        # Linux call errors on creationflags argument, so the calls must be separated
        if platform.system() == "Windows":
            creationflags = 0
            if app_info.is_console_application:
                creationflags = subprocess.CREATE_NEW_CONSOLE
            if app_info.args:
                cmd += app_info.args.strip().split(" ")
                # don't use 'executable' arg of Popen, because then shell scripts won't execute correctly
            subprocess.Popen(cmd, creationflags=creationflags)
        elif platform.system() == "Linux":
            if app_info.is_console_application:
                # Sadly, there is no default way to do this, because of the miriad terminal emulators available
                # Use the default distro emulator, with x-terminal-emulator
                # (sudo update-alternatives --config x-terminal-emulator)
                # This works only on debian distros.
                cmd = ["x-terminal-emulator", "-e", str(app_info.executable)]
            if app_info.args:
                cmd += app_info.args.strip().split(" ")
            subprocess.Popen(cmd)
