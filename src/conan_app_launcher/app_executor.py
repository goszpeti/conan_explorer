import platform
import subprocess

from conan_app_launcher.config_file import AppEntry


def execute_app(app_info: AppEntry):
    if app_info.executable.absolute().is_file():
        # Linux call errors on creationflags argument, so the calls must be separated
        if platform.system() == "Windows":
            creationflags = 0
            if app_info.is_console_application:
                creationflags = subprocess.CREATE_NEW_CONSOLE
            subprocess.Popen(executable=str(app_info.executable),
                             args=app_info.args.strip().split(" "), creationflags=creationflags)
        elif platform.system() == "Linux":
            if app_info.is_console_application:
                # Sadly, there is no default way to do this, because of the miriad terminal emulators available
                # Use the default distro emulator, with x-terminal-emulator (sudo update-alternatives --config x-terminal-emulator)
                # This works only on debian distros.
                cmd = ["x-terminal-emulator", "-e", str(app_info.executable)]
            else:
                cmd = [str(app_info.executable)]
            if app_info.args:
                cmd += app_info.args.strip().split(" ")
            subprocess.Popen(cmd)
