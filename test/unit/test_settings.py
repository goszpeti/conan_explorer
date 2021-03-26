import os
import tempfile
import shutil
import configparser
from pathlib import Path
from conan_app_launcher.settings import *


def testReadFromFile(base_fixture):
    """
    Tests, that the settings file is read by using a string setting.
    Correct setting value expected.
    """
    sets = Settings(ini_file=base_fixture.testdata_path / "settings/read/config.ini")
    assert sets.get(LAST_CONFIG_FILE) == "C:/work/app_config.json"
    assert sets.get(CONAN_USER_ALIASES) == {"myuser" : "user1",
                                            "myuser2" : "user2"}


def testSaveToFile(base_fixture):
    """
    Tests, that writing a value works and untouched entries remain.
    Correctly read back setting value expected.
    """
    # copy testdata to temp
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")
    shutil.copy(base_fixture.testdata_path / "settings/write/config.ini", temp_dir)
    sets = Settings(ini_file=Path(temp_ini_path))

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
