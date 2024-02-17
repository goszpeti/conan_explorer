#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the "upload" functionality of this file, you must:
#   $ pipenv install twine --dev

import os
from glob import glob
from os.path import basename, splitext
from pathlib import Path
import tempfile

from setuptools import find_packages, setup


# Package meta-data.
NAME = "cal-example-plugin"
VERSION = "0.1.0"
DESCRIPTION = "Example Plugin"
URL = "https://github.com/goszpeti/conan_explorer"
AUTHOR = "Péter Gosztolya and Contributors"
PYTHON_REQUIRES = ">=3.8.0"

# What packages are required for this module to be executed?
REQUIRES = [
    "conan_explorer>=2.2.0"
]

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    python_requires=PYTHON_REQUIRES,
    url=URL,
    packages=find_packages("."),
    py_modules=[splitext(basename(path))[0] for path in glob("*.py")],
    install_requires=REQUIRES,
    include_package_data=True,
)

# Register plugin
from conan_explorer.ui import PluginFile, PluginDescription
import cal_example_plugin
# cd away, so that not the current cwd module will be registered, but the site-packages one
os.chdir(tempfile.gettempdir())
plugin_dir_path = Path(cal_example_plugin.__file__).parent
plugin_file_path = str(plugin_dir_path / "plugin.ini")
plugin_descr = PluginDescription("My Example Plugin", VERSION, AUTHOR, f"{plugin_dir_path}/about.svg",
                                ".", "SamplePluginView", DESCRIPTION, True, "<2")
PluginFile.write(plugin_file_path, [plugin_descr])
PluginFile.register(plugin_file_path)
