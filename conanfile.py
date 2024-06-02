from conans import ConanFile, CMake

class MyConanFile(ConanFile):
    name = "conan_explorer"
    version = "1.0"
    license = "<insert license here>"
    author = "<insert author name here>"
    url = "<insert URL here>"
    description = "<insert description here>"
    topics = ("<insert topics here>", "<insert topics here>")
    settings = "os", "compiler", "build_type", "arch"
    generators = "txt", "CMakeDeps", "virtualrunenv"
    tool_requires = "cmake/3.29.0"
    default_options = {
        "cpython:shared": True,
        "qt:shared": True,
        "qt:qtdeclarative": False,
        "qt:qtdoc": False,
        "qt:qttools": False,
        "qt:qttranslations": False,
        "qt:with_sqlite3": False
    }

    def requirements(self):
        self.requires("sqlite3/3.45.2", override=True)
        self.requires("cpython/3.11.9")
        self.requires("pybind11/2.12.0")
        self.requires("qt/6.6.3")


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include", src="src")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = [self.name]