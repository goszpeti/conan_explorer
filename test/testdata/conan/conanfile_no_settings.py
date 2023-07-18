from typing import Optional
from conans import ConanFile
import platform
import sys
import os
from pathlib import Path

class Example(ConanFile):
    name = "nocompsettings"
    #default_user = "user"
    #default_channel = "very_long_channel_name_you_should_not_do_this"
    options = {"shared": [True, False], "fPIC2": [True, False]}
    default_options = {"shared": True, "fPIC2": True}
    no_copy_source = True
    short_paths = True
    requires = "example/9.9.9@local/testing"

    def package(self):
        # repackage some executable
        self.copy(Path(sys.executable).name, src=os.path.dirname(sys.executable), dst="bin")
