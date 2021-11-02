import platform
import sys
from pathlib import Path

from conan_app_launcher.components.icon import (
    extract_icon, extract_icon_from_win_executable)


def test_extract_icon_from_exe_windows(tmp_path):
    """
    Tests, that an icon is extracted.
    Existant path with a filesize > 0 expected
    """
    if platform.system() == "Windows":
        ret_path = extract_icon_from_win_executable(Path(sys.executable), tmp_path)
        assert ret_path.suffix == ".img"
        assert ret_path.is_file()
    elif platform.system() == "Linux":
        pass


def test_extract_icon_from_generic_file(tmp_path):
    """ 
    Generic files have no icon embedded.
    Nonexistant path expected.
    """
    test_file = Path(tmp_path) / "test.cmd"
    with open(test_file, "w") as f:
        f.write("test")
    wrong_path = extract_icon(test_file, tmp_path)
    assert not wrong_path.is_file()


def test_extract_icon_wrapper(tmp_path):
    """
    Tests, that only for windows the fct is called.
    Nonexistant path / fct call expected.
    """
    ret_path = extract_icon(Path(sys.executable), tmp_path)
    if platform.system() == "Linux":
        assert not ret_path.is_file()
    if platform.system() == "Windows":
        assert ret_path.is_file()
