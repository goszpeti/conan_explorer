"""
A simple setup script to create an executable using PyQt5. This also
demonstrates the method for creating a Windows executable that does not have
an associated console.
PyQt5app.py is a very simple type of PyQt5 application
Run the build process by running the command 'python setup.py build'
If everything works well you should find a subdirectory in the build
subdirectory that contains the files needed to run the application
"""

import sys
from setup import AUTHOR, DESCRIPTION, URL, VERSION
from cx_Freeze import Executable, setup
try:
    from cx_Freeze.hooks import get_qt_plugins_paths
except ImportError:
    include_files = []
else:
    # Inclusion of extra plugins (new in cx_Freeze 6.8b2)
    # cx_Freeze imports automatically the following plugins depending of the
    # use of some modules:
    # imageformats - QtGui
    # platforms - QtGui
    # mediaservice - QtMultimedia
    # printsupport - QtPrintSupport
    include_files = get_qt_plugins_paths("PyQt5", "platforms") + get_qt_plugins_paths("PyQt5", "styles")

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"
build_exe_options = {
    "includes": "conan_app_launcher",
    "excludes": ["debugpy"],
    "bin_excludes": ['Qt5dbus.dll', 'Qt5Network.dll', 'Qt5Qml.dll', "Qt5QmlModels.dll",
                     'Qt5Quick.dll', 'Qt5Svg.dll', 'Qt5WebSockets.dll', "d3dcompiler_47.dll", "opengl32sw.dll",
    "libicudata.so.66", "libgtk-3.so.0", "libQt5Quick.so.5", "libQt5Qml.so.5", "libicui18n.so.66", "libicui18n.so.66",
    "libQt5Network.so.5", "libQt5QmlModels.so.5"],
    "include_files": include_files,
    "zip_include_packages" : ['PyQt5', "conans"]
}

icon = "src/conan_app_launcher/assets/icons/icon.ico"
app_name = "Conan App Launcher"

bdist_mac_options = {
    "bundle_name": app_name,
}

bdist_dmg_options = {
    "volume_label": app_name,
}

directory_table = [
   # ("ProgramMenuFolder", "TARGETDIR", "."),
   # ("Conan App Launcher", "ProgramMenuFolder", "MYPROG~1|My Program"),
]

msi_data = {
    "Directory": directory_table,
    "ProgId": [
        ("Prog.Id", None, None, "This is a description", "IconId", None),
    ],
    "Icon": [
        ("IconId", icon)
    ],
    # "summary_data": {
    #     "author": "Peter Gosztolya and Contributors",
    # },
}

bdist_msi_options = {
    #"target_name": "conan_app_launcher_setup",
    "data": msi_data,
    "install_icon": icon}

executables = [Executable("./src/conan_app_launcher/__main__.py",
                          base=base, target_name="conan_app_launcher",
                          icon=icon, shortcut_name=app_name,
                          shortcut_dir="DesktopFolder",
                          ),
               Executable(".venv/Lib/site-packages/conans/conan.py",
                          target_name="conan",
                          )]

setup(
    name=app_name,
    author=AUTHOR,
    version=VERSION,
    description=DESCRIPTION,
    url=URL,
    options={
        "build_exe": build_exe_options,
        "bdist_mac": bdist_mac_options,
        "bdist_dmg": bdist_dmg_options,
        "bdist_msi": bdist_msi_options
    },
    executables=executables,
    optimize="-O2"
)
