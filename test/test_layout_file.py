import os

from conan_app_launcher.config_file import parse_config_file


def testCorrectFile(base_fixture):

    tabs = parse_config_file(base_fixture.testdata_path / "app_config.json")
    assert tabs[0].name == "Basics"
    tab0_entries = tabs[0].get_app_entries()
    assert str(tab0_entries[0].package_id) == "m4_installer/1.4.18@bincrafters/stable"
    assert tab0_entries[0].executable.as_posix() == "bin/m4"
    assert tab0_entries[0].icon.name == "default_app_icon.png"
    assert tab0_entries[0].name == "App1 with spaces"

    assert str(tab0_entries[1].package_id) == "boost_functional/1.69.0@bincrafters/stable"
    assert tab0_entries[1].executable.as_posix() == "bin/app2"
    assert tab0_entries[1].icon.name == "default_app_icon.png"
    assert tab0_entries[1].name == "App2"

    assert tabs[1].name == "Extra"
    tab1_entries = tabs[1].get_app_entries()
    assert str(tab1_entries[0].package_id) == "app2/1.0.0@user/stable"
    assert tab1_entries[0].executable.as_posix() == "bin/app2.exe"
    assert tab1_entries[0].icon.name == "default_app_icon.png"
    assert tab1_entries[0].name == "App2"


def testIncorrectFilename(base_fixture):
    parse_config_file(base_fixture.testdata_path / "nofile.json")


def testInvalidContent(base_fixture):
    pass
