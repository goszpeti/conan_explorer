from shutil import copyfile
from tempfile import gettempdir
from conan import ConanFile

import sys
from pathlib import Path
from conan.tools.files import copy
class Example(ConanFile):
    name = "example"
    #default_user = "user"
    #default_channel = "very_long_channel_name_you_should_not_do_this"
    # fPIC does not work in Conan 2 because it will be removed and setting the option will error...
    options = {"shared": [True, False], "fPIC2": [True, False], "variant": ["ANY"]}
    default_options = {"shared": True, "fPIC2": True, "variant": "var1"}
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    def package(self):
        # repackage some executable
        python_path = Path(sys.executable)
        renamed_executable = Path(gettempdir()) / ("python" + python_path.suffix)
        copyfile(str(python_path), str(renamed_executable))
        copy(self, renamed_executable.name, src=str(renamed_executable.parent), dst=self.package_folder + "/bin")

    def package_info(self) -> None:
        pass
