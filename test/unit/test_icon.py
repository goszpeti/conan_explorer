import os
import platform
import sys
import tempfile
import time
import pytest
from pathlib import Path
from subprocess import check_output

from conan_app_launcher.components.icon import extract_icon


def testExtractIconFromExe(base_fixture):
    if platform.system() == "Linux":
        pass
        # assert Error
    elif platform.system() == "Windows":
        pass


def testExtractIconFromGenericFile(base_fixture, tmp_path):
    test_file = Path(tmp_path) / "test.txt"
    with open(test_file, "w") as f:
        f.write("test")
    wrong_path = extract_icon(test_file, tmp_path)
