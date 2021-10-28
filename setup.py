#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'conan-app-launcher'
DESCRIPTION = 'App Launcher for quick starting applications with conan'
URL = 'https://github.com/goszpeti/conan_app_launcher'
AUTHOR = 'Peter Gosztolya'
REQUIRES_PYTHON = '>=3.6.0'

# What packages are required for this module to be executed?
REQUIRED = [
    "PyQt5>=5.13.0",
    "conan>=1.24",
    "jsonschema>=3.2.0",
    "pefile==2021.9.3",
    "typing-extensions ; python_version<'3.8'",
]

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
    # replace links
    temp = []
    if os.getenv("GITHUB_REF"):
        print(f"GITHUB_REF: {str(os.getenv("GITHUB_REF"))}")
        branch = os.getenv("GITHUB_REF").split("refs/heads/")
        if len(branch) == 1:
            branch = os.getenv("GITHUB_REF").split("tags")
        link = "conan_app_launcher/" + branch[1]
        master_link = "conan_app_launcher/master"
        for line in long_description.splitlines():
            if master_link in line:
                line.replace(master_link, link)
            temp.append(line)
        long_description = "\n".join(temp)
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, "src", "conan_app_launcher", '__version__.py')) as f:
    exec(f.read(), about)


# Where the magic happens:
setup(
    name=NAME,
    version=about['VERSION'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages("src"),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)"
    ],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'gui_scripts': [
            'conan-app-launcher=conan_app_launcher.__main__:main',
        ]
    },
)
