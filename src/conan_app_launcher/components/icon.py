import platform
from pathlib import Path

from conan_app_launcher.base import Logger
from conan_app_launcher.components.file_runner import is_file_executable

if platform.system() == "Windows":
    import win32con
    import win32api


def extract_icon(file_path: Path, output_dir: Path) -> Path:
    """
    Extract icons from a file and save them to specified dir.
    Since we don't know the format (png or ico), the function returns the generated filepath.
    """

    if platform.system() == "Linux":
        Logger().info("Automatic icon extraction is not available on Linux.")
    if platform.system() == "Windows":
        if file_path.is_file():
            if is_file_executable(file_path):
                return extract_icon_from_win_executable(file_path, output_dir)
            Logger().info("Automatic icon extraction is not available for non executable files.")
        else:
            Logger().debug("File for icon extraction does not exist.")
    return Path("NULL")


def extract_icon_from_win_executable(executable_path: Path, output_dir: Path) -> Path:
    # Currently only pngs supported
    # cache files
    output_path = output_dir / (executable_path.name + ".png")
    if output_path.is_file():
        return output_path
    try:
        hlib = win32api.LoadLibrary(str(executable_path))
        icon_names = win32api.EnumResourceNames(hlib, win32con.RT_ICON)
        for icon_name in icon_names:
            rec = win32api.LoadResource(hlib, win32con.RT_ICON, icon_name)
            if rec.startswith(b"\x89PNG"):  # binary file header for pngs
                with open(output_path, "wb") as extract_file:
                    extract_file.write(bytearray(rec))
                return output_path
    except Exception as error:
        # user needs not know this
        Logger().debug(str(error))
    return Path("NULL")
