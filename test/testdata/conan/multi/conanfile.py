from conans import ConanFile
import platform
import sys
import os

class Example(ConanFile):
    # no name and version, so this can be used to generate more packages

    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    def package(self):
        pass
        # repackage some executable
        # if platform.system() == "Windows":
        #     self.copy("python.exe", src=os.path.dirname(sys.executable), dst="bin")

    def package_id(self):
        self.info.settings.build_type = "Any"
        self.info.settings.compiler = "ANYCOMPILER"
        self.info.settings.compiler.runtime = "ANY"
