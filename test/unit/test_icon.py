import os
import platform
import sys
import tempfile
import time
import pytest
from pathlib import Path
from subprocess import check_output

from conan_app_launcher.components.icon import extract_icon


def testExtractIconFromExeOnWindows(base_fixture):
    """
    Tests, that an icon is extracted.
    Existant path with a filesize > 0 expected
    """
    if platform.system() == "Windows":
        pass


def testExtractIconFromGenericFile(base_fixture, tmp_path):
    """ 
    Generic files have no icon embedded.
    Nonexistant path expected.
    """
    test_file = Path(tmp_path) / "test.txt"
    with open(test_file, "w") as f:
        f.write("test")
    wrong_path = extract_icon(test_file, tmp_path)


def testExtractIconWrapper(base_fixture, tmp_path):
    """
    Tests, that only for windows the fct is called.
    Nonexistant path / fct call expected.
    """
    test_file = Path(tmp_path) / "test.txt"
    with open(test_file, "w") as f:
        f.write("test")
    wrong_path = extract_icon(test_file, tmp_path)
    # TODO
