#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the "upload" functionality of this file, you must:
#   $ pipenv install twine --dev

import os
from glob import glob
from os.path import basename, splitext

# Force Conan version from envvar CONAN_VERSION
from setuptools import find_packages, setup
from pkg_resources import Requirement
conan_version_env = os.getenv("CONAN_VERSION", "").strip()
conan_major_version = ""
if conan_version_env: # eval as spec
    specs = Requirement.parse("conan" + conan_version_env)
    if "2.0.0" in specs:
        conan_major_version = "2"
    else:
        conan_major_version = "1"
    print(f"Using Conan version {conan_major_version} from spec: {conan_version_env}")

# Package meta-data.
NAME = "conan-app-launcher"
VERSION = "2.0.0"
DESCRIPTION = "App Launcher and Package Explorer for Conan"
URL = "https://github.com/goszpeti/conan_app_launcher"
AUTHOR = "Péter Gosztolya and Contributors"
PYTHON_REQUIRES = ">=3.7.0"

# What packages are required for this module to be executed?
conan_req_spec = "conan>=1.24, <2.1"
if conan_major_version == "1":
    conan_req_spec = "conan>=1.24, <2.0"
if conan_major_version == "2":
    conan_req_spec = "conan>=2.0, <2.1"
REQUIRES = [
    'PySide6-Essentials>=6.3.0', # LGPLv3
    conan_req_spec,  # MIT License
    "jsonschema>=3.2.0, <4",  # MIT License
    'importlib-metadata>=4.8.2, <5; python_version<"3.8"',  # Apache Software License (Apache)
    'typing-extensions>=3.10.0.2, <5; python_version<="3.10"',  # Python Software Foundation License(PSF)
    "packaging",  # use the built-in, or get latest if there is some issue with pip
    "Jinja2>=2.3, <4"  # BSD License (BSD-3-Clause) (restriction from conan 1.24, since it is included there)
]

TEST_REQUIRES = [
    "pytest==6.2.5",
    "pytest-cov==4.0.0",
    "pytest-mock==3.9.0",
    "pytest-qt==4.1.0",
    "pytest-check==1.0.10",
    "psutil",
    "pywin32; sys_platform=='win32'",
]

if conan_major_version.startswith("2"):
    TEST_REQUIRES.append("conan-server")

DEV_REQUIRES = [
    "autopep8", # formatter
    "rope", # refactoring
    "debugpy", # Qt thread debugging
]

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Replace image links at release to point to this tag instead of master, so they do not change with new releases
try:
    with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
    # replace links
    temp = []
    if os.getenv("GITHUB_REF"):
        print(f"GITHUB_REF: {str(os.getenv('GITHUB_REF'))}")
        branch = os.getenv("GITHUB_REF", "").split("refs/heads/")
        if len(branch) == 1:
            branch = os.getenv("GITHUB_REF", "").split("tags")
        if len(branch) > 1:
            link = "conan_app_launcher" + branch[1].replace(" ", "")
            master_link = "conan_app_launcher/master"
            for line in long_description.splitlines():
                if master_link in line:
                    line = line.replace(master_link, link)
                    print(f"replaced {master_link} with {link}")
                temp.append(line)
            long_description = "\n".join(temp)
    else:
        print("No GITHUB_REF envvar found!")
except FileNotFoundError:
    long_description = DESCRIPTION


# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    python_requires=PYTHON_REQUIRES,
    url=URL,
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    install_requires=REQUIRES,
    extras_require={
        "dev": DEV_REQUIRES + TEST_REQUIRES,
        "test": TEST_REQUIRES
    },
    include_package_data=True,
    license="LGPL v3",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)"
    ],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        "gui_scripts": [
            "conan_app_launcher=conan_app_launcher.__main__:run_conan_app_launcher",
            "conan_explorer=conan_app_launcher.__main__:run_conan_app_launcher",
        ]
    },
)
