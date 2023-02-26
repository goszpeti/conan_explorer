import configparser
import os
import shutil
import tempfile
from pathlib import Path

from conan_app_launcher.settings import *
from conan_app_launcher.settings.ini_file import IniSettings, PLUGINS_SECTION_NAME
from test.conftest import PathSetup


def test_read_from_file():
    """
    Tests, that the settings file is read by using a string setting.
    Correct setting value expected.
    """
    paths = PathSetup()

    sets = IniSettings(paths.testdata_path / "settings/read/config.ini")
    assert sets.get(LAST_CONFIG_FILE) == "C:/work/app_config.json"
    assert sets.get(AUTO_INSTALL_QUICKLAUNCH_REFS) == False
    assert sets.get(GUI_MODE) == GUI_MODE_DARK
    assert sets.get(GUI_STYLE) == GUI_STYLE_MATERIAL
    assert "local_package_explorer" in sets.get_settings_from_node(PLUGINS_SECTION_NAME)
    assert "conan_search" in sets.get_settings_from_node(PLUGINS_SECTION_NAME)


def test_save_to_file():
    """
    Tests, that writing a value works and untouched entries remain.
    Correctly read back setting value expected.
    """
    paths = PathSetup()

    # copy testdata to temp
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")
    shutil.copy(paths.testdata_path / "settings/write/config.ini", temp_dir)
    sets = IniSettings(Path(temp_ini_path))

    last_config_file = "D:/file.ini"

    sets.set(LAST_CONFIG_FILE, last_config_file)

    # read file
    parser = configparser.ConfigParser()
    parser.read(temp_ini_path, encoding="utf-8")

    # assert set settings
    assert parser.get("General", LAST_CONFIG_FILE) == last_config_file

    # assert, that original entries remain untouched
    assert parser.get("MyCustomSection", "MyCustomKey") == "123"
    assert parser.get("General", "MyCustomKey2") == "abcd"
    # delete tempfile
    os.remove(temp_ini_path)
