"""
A simple setup script to create an executable using PySide6. This also
demonstrates the method for creating a Windows executable that does not have
an associated console.
# RUN: python setup_standalone.py build
"""

import platform
import sys
from setup import AUTHOR, URL, VERSION
from cx_Freeze import Executable, setup
include_files = []

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"
build_exe_options = {
    "includes": "conan_explorer",
    "excludes": ["debugpy", "pywin32", "pywin32_system32"],
    "bin_excludes": ['Qt6dbus.dll', 'Qt6Network.dll', 'Qt6Qml.dll', "Qt6QmlModels.dll",
        'Qt6Quick.dll', 'Qt6WebSockets.dll',  "Qt6QuickTemplates2.dll", "Qt6QmlCompiler.dll",
         "Qt6QuickDialogs2QuickImpl.dll", "Qt6LanguageServer.dll", "d3dcompiler_47.dll", 
                     "QtOpenGL.pyi", "Qt6DesignerComponents.dll", "Qt6Designer.dll", 
                     "Qt6VirtualKeyboard.dll",  "Qt6Pdf.dll",
        "opengl32sw.dll", "lupdate.exe", "QtOpenGL.pyd", "icudtl.dat", "qmlls.exe",
        "assistant.exe", "designer.exe", "linguist.exe", "qmlformat.exe",
        # examples, qml dir, lupdate.exe QtOpenGL.pyd
        "libicudata.so.66", "libgtk-3.so.0", "libQt6Quick.so.5", 
        "libQt6Qml.so.5", "libicui18n.so.66", "libicui18n.so.66", 
        "libQt6Network.so.5", "libQt6QmlModels.so.5"],
    "include_files": include_files,
    "zip_include_packages" : ['PySide6', "conans"]
}

icon = "src/conan_explorer/assets/icons/icon.ico"
app_name = "Conan Explorer"

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
    #"target_name": "conan_explorer_setup",
    "data": msi_data,
    "install_icon": icon}

if platform.system() == "Windows":
    conan_main = ".venv/Lib/site-packages/conans/conan.py"
else:
    conan_main = f".venv/lib/python3.{sys.version_info.minor}/site-packages/conans/conan.py"

executables = [Executable("./src/conan_explorer/__main__.py",
                          base=base, target_name="Conan Explorer",
                          icon=icon, shortcut_name=app_name,
                          shortcut_dir="DesktopFolder",
                          ),
               Executable(conan_main, target_name="conan")]

setup(
    name=app_name,
    author=AUTHOR,
    version=VERSION,
    description=app_name,
    url=URL,
    options={
        "build_exe": build_exe_options,
        "bdist_mac": bdist_mac_options,
        "bdist_dmg": bdist_dmg_options,
        "bdist_msi": bdist_msi_options
    },
    executables=executables,
    optimize="2"
)
