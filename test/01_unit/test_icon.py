import sys
from pathlib import Path

from conan_app_launcher.ui.common.icon import extract_icon


def test_extract_icon_from_exe(tmp_path, qtbot):
    """
    Tests, that an icon is extracted from different file types
    """

    # executable
    icon = extract_icon(Path(sys.executable))
    assert not icon.isNull()

    # textfile
    test_file = Path(tmp_path) / "test.txt"
    with open(test_file, "w") as f:
        f.write("test")
    icon = extract_icon(Path(tmp_path) / "test.txt")
    assert not icon.isNull()

    # non existant file -> null pointer icon
    icon = extract_icon(Path(tmp_path) / "nonexistant")
    assert icon.isNull()
