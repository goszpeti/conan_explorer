from tempfile import gettempdir, tempdir
from typing import Optional
from conans import ConanFile
import platform
import sys
import os
from pathlib import Path
from distutils.file_util import copy_file

class Example(ConanFile):
    name = "example"
    #default_user = "user"
    #default_channel = "very_long_channel_name_you_should_not_do_this"
    options = {"shared": [True, False], "fPIC": [True, False], "variant": [None, "ANY"]}
    default_options = {"shared": True, "fPIC": True, "variant": "var1"}
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    def package(self):
        # repackage some executable
        python_path = Path(sys.executable)
        renamed_executable = Path(gettempdir()) / ("python" + python_path.suffix)
        copy_file(str(python_path), str(renamed_executable))
        self.copy(renamed_executable.name, src=str(renamed_executable.parent), dst="bin")
