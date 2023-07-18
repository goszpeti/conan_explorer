from typing import Optional
from conans import ConanFile
import platform
import sys
import os
from pathlib import Path

class Example(ConanFile):
    name = "example"
    #default_user = "user"
    #default_channel = "very_long_channel_name_you_should_not_do_this"
    options = {"shared": [True, False], "fPIC2": [True, False]}
    default_options = {"shared": False, "fPIC2": True}
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    def package(self):
        # repackage some executable
        self.copy(Path(sys.executable).name, src=os.path.dirname(sys.executable), dst="bin")

    def package_id(self):
        self.info.settings.build_type = "Any"
        self.info.settings.compiler = "ANYCOMPILER"
        self.info.settings.compiler.runtime = "ANY"
