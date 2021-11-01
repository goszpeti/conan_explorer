import os
import tempfile
import shutil
import configparser
from pathlib import Path
from conan_app_launcher.data.settings import *
from conan_app_launcher.data.settings.ini_file import IniSettings


def test_read_from_file(base_fixture):
    """
    Tests, that the settings file is read by using a string setting.
    Correct setting value expected.
    """
    sets = IniSettings(base_fixture.testdata_path / "settings/read/config.ini")
    assert sets.get(LAST_CONFIG_FILE) == "C:/work/app_config.json"
    assert sets.get_bool(DISPLAY_APP_CHANNELS) == False
    assert sets.get_bool(DISPLAY_APP_VERSIONS) == False
    assert sets.get_bool(DISPLAY_APP_USERS) == False
    assert sets.get_int(GRID_COLUMNS) == 10
    assert sets.get_int(GRID_ROWS) == 30

def test_save_to_file(base_fixture):
    """
    Tests, that writing a value works and untouched entries remain.
    Correctly read back setting value expected.
    """
    # copy testdata to temp
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")
    shutil.copy(base_fixture.testdata_path / "settings/write/config.ini", temp_dir)
    sets = IniSettings(Path(temp_ini_path))

    last_config_file = "D:/file.ini"

    sets.set(LAST_CONFIG_FILE, last_config_file)

    # read file
    parser = configparser.ConfigParser()
    parser.read(temp_ini_path, encoding="utf-8")

    # assert set settings
    assert parser.get(sets._GENERAL_SECTION_NAME, LAST_CONFIG_FILE) == last_config_file

    # assert, that original entries remain untouched
    assert parser.get("MyCustomSection", "MyCustomKey") == "123"
    assert parser.get(sets._GENERAL_SECTION_NAME, "MyCustomKey2") == "abcd"
    # delete tempfile
    os.remove(temp_ini_path)
