import os

from conan_app_launcher.layout_file import parse_layout_file


def testCorrectFile(base_fixture):

    tabs = parse_layout_file(base_fixture.testdata_path / "app_config.json")
    assert tabs[0].name == "Basics"
    assert tabs[1].name == "Extra"


def testIncorrectFilename(base_fixture):
    parse_layout_file(base_fixture.testdata_path / "nofile.json")


def testInvalidContent(base_fixture):
    pass
