from conans import ConanFile


class Example(ConanFile):
    name = "example"
    version = "1.0.0"
    default_user = "user"
    default_channel = "stable"

    settings = "os", "arch", "compiler", "build_type"

    def package_id(self):
        self.info.settings.build_type = "Any"
        self.info.settings.compiler.runtime = "ANY"
