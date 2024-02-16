#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the "upload" functionality of this file, you must:
#   $ pipenv install twine --dev

import os
from glob import glob
from os.path import basename, splitext
from setuptools import find_packages, setup
from pkg_resources import Requirement

# Package meta-data.
NAME = "conan-explorer"
VERSION = "2.2.0a6"
DESCRIPTION = "Package Explorer and App Launcher for Conan"
URL = "https://github.com/goszpeti/conan_explorer"
AUTHOR = "Péter Gosztolya and Contributors"
PYTHON_REQUIRES = ">=3.8.0"


# Force Conan version from envvar CONAN_VERSION

conan_version_env = os.getenv("CONAN_VERSION", "").strip()
conan_major_version = ""
if conan_version_env: # eval as spec
    specs = Requirement.parse("conan" + conan_version_env)
    if "2.0.0" in specs:
        conan_major_version = "2"
    else:
        conan_major_version = "1"
    print(f"Using Conan version {conan_major_version} from spec: {conan_version_env}")

# What packages are required for this module to be executed?
conan_req_spec = "conan>=1.48, <2.1"
if conan_major_version == "1":
    conan_req_spec = "conan>=1.48, <2.0"
if conan_major_version == "2":
    conan_req_spec = "conan>=2.0, <2.1"
REQUIRES = [
    conan_req_spec,  # MIT License
    "PySide6-Essentials>=6.4.0", # LGPLv3
    "jsonschema>=3.2.0, <5", # MIT License
    "dictdiffer==0.9.0",  # MIT License
    # compatibility
    'contextlib-chdir==1.0.2; python_version<"3.11"',  # BSD License (BSD-3-Clause)
    'typing-extensions>=3.10.0.2, <5; python_version<="3.10"',  # Python Software Foundation License(PSF)
    "packaging",  # use the built-in, or get latest if there is some issue with pip
    # transitive compatibility
    "Jinja2>=2.3, <4"  # BSD License (BSD-3-Clause) (restriction from conan 1.24, since it is included there)
]

TEST_REQUIRES = [
    "pytest==8.0.0",
    "pytest-cov==4.1.0",
    "pytest-mock==3.12.0",
    "pytest-qt==4.4.0",
    "psutil==5.9.8",
    "pytest-check==2.3.1",
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
        if len(branch) > 1:
            # is feature branch - don't adjust for prerelease
            pass
        else:
            if len(branch) == 1:
                branch = os.getenv("GITHUB_REF", "").split("tags")
            if len(branch) > 1:
                link = "conan_explorer" + branch[1].replace(" ", "")
                master_link = "conan_explorer/master"
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)"
    ],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        "gui_scripts": [
            "conan_explorer=conan_explorer.__main__:run_conan_explorer",
        ]
    },
)
