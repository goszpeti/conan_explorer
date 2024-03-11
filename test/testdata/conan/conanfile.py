from tempfile import gettempdir
from conans import ConanFile
import sys
import os
from pathlib import Path
from shutil import copyfile
from conans.client.output import ScopedOutput, ConanOutput

class Example(ConanFile):
    name = "example"
    #default_user = "user"
    #default_channel = "very_long_channel_name_you_should_not_do_this"
    options = {"shared": [True, False], "fPIC2": [True, False], "variant": "ANY"}
    default_options = {"shared": True, "fPIC2": True, "variant": "var1"}
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True
    generators = "txt", "cmake"

    def package(self):
        # repackage some executable
        python_path = Path(sys.executable)
        renamed_executable = Path(gettempdir()) / ("python" + python_path.suffix)
        copyfile(str(python_path), str(renamed_executable))
        self.copy(renamed_executable.name, src=str(renamed_executable.parent), dst="bin")
        
    def package_info(self):
        self.cpp_info.includedirs = ['include']  # Ordered list of include paths
        self.env_info.path.append("ANOTHER VALUE") # Append "ANOTHER VALUE" to the path variable
        self.env_info.othervar = "OTHER VALUE" # Assign "OTHER VALUE" to the othervar variable
        self.user_info.var1 = 2
        out = ScopedOutput("111", ConanOutput(sys.stdout, sys.stderr))
        out.highlight("test logging")

    def layout(self):
        self.folders.source = "src"
        build_type = str(self.settings.build_type).lower()
        self.folders.build = "cmake-build-{}".format(build_type)
        self.folders.generators = os.path.join(self.folders.build, "conan")

        self.cpp.package.libs = ["say"]
        self.cpp.package.includedirs = ["include"] # includedirs is already set to this value by
                                                   # default, but declared for completion

        # this information is relative to the source folder
        self.cpp.source.includedirs = ["include"]  # maps to ./src/include

        # this information is relative to the build folder
        self.cpp.build.libdirs = ["."]             # maps to ./cmake-build-<build_type>
        self.cpp.build.bindirs = ["bin"]           # maps to ./cmake-build-<build_type>/bin