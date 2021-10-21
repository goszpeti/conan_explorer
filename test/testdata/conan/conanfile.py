from conans import ConanFile
import platform
import os


class Example(ConanFile):
    name = "example"
    version = "1.0.0"
    default_user = "user"
    default_channel = "very_long_channel_name_you_should_not_do_this"

    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    def package(self):
        # repackage some executable
        if platform.system() == "Windows":
            self.copy("procexp.exe", dst="bin")  # "notepad.exe", src=os.getenv("WINDIR"), dst="bin")

    def package_id(self):
        self.info.settings.build_type = "Any"
        self.info.settings.compiler = "ANYCOMPILER"
        self.info.settings.compiler.runtime = "ANY"
