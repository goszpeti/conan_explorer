from typing import Optional
from conan import ConanFile

import platform
import sys
import os
from pathlib import Path
from conan.tools.files import copy

class Example(ConanFile):
    name = "example"
    #default_user = "user"
    #default_channel = "very_long_channel_name_you_should_not_do_this"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    def package(self):
        # repackage some executable
        copy(self, Path(sys.executable).name, src=os.path.dirname(sys.executable), dst="bin")
