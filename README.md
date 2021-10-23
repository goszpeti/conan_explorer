# <img src="https://raw.githubusercontent.com/goszpeti/conan_app_launcher/master/src/conan_app_launcher/assets/icons/icon.ico" width="128">

# Conan App Launcher

![https://pypi.org/project/conan-app-launcher/](https://img.shields.io/pypi/v/conan-app-launcher)
![PyPI Python versions](https://img.shields.io/pypi/pyversions/conan-app-launcher)
![Python tests](https://github.com/goszpeti/conan_app_launcher/workflows/Python%20tests/badge.svg)


## Quick Overview

The goal of this project is to provide a frontend to start executables contained in packages of the package manager conan. It is intented to be used on Windows and Linux x64 platforms.


# <img src="https://raw.githubusercontent.com/goszpeti/conan_app_launcher/master/doc/screenshot.png" width="1024">

Features:
- configurable layout (tabs and applications) in GUI itself
- can also open files with their associated default program
- installs all referenced packages automatically
- automatic conan settings resolution for your platform
- compatible with a wide range of conan versions (from 1.19 onwards)
- integrated console for information an packages and config file
- installable with pip

## How to install?

### Prequisites on Linux
Qt for Python must be installed with the native package manager, like:

    sudo apt install python3-pyqt5

Ubuntu 16.04 is not supported duw to its native Python 3.5.

### With pip from Pypi
`pip install conan-app-launcher`

### From source

After checkout use the command:
`pip install .`

## Running
Execute `conan_app_launcher`, if the Python "scripts" folder is on your system path, or look it up manually in the site-packages folder.

### Main dependencies

* PyQt5 >= 5.13.0 
* conan >= 1.19.4

## Config File layout

It is not needed to edit this by hand, since (almost) every option is available in the GUI.
The config file uses the following exemplary schema:

    {
        "version": "0.3.0",
        "tabs": [
            {
                "name": "Basics",
                "apps": [
                    {
                        "name": "App1 with spaces", 
                        "conan_ref": "app1/0.1.0@user1/stable", // full conan reference
                        "package_id": "app1/0.1.0@user1/stable" // DEPRECATED - will converted to conan_ref automatically
                        "executable": "bin/app1", // relative to conan "package folder" - can also be a file to open
                        "icon": "MyIcon.png" // relative to this config file,
                        "console_application": true, // start console application in extra window
                        "args": "--version" // args to start the application with
                    },
                    {
                        "name": "App2",
                        "conan_ref": "app2/0.2.0@user2/testing",
                        "executable": "bin/app2", // forward slashes are preferred
                        "icon": "C:\\CustomIcon.ico" // but escaped backslashes also work
                    }
                ]
            },
            {
                "name": "Extra",
                "apps": [
                    {
                        "name": "App3",
                        "conan_ref": "app3/0.3.0@user3/stable",
                        "console_application": true, // starts in a new console window
                        "executable": "bin/app3", // extension (.exe) can be ommited for windows
                        // Icon can be ommitted, then it will try on Windows to use the applications own icon
                    }
                ]
            }
        ]
    }

## Toolchain

This project uses Python with Qt as a frontend using the PyQt integration.
The IDE integration is done for VsCode.


## Licenses of used libraries and code

* Using source code of modified ExtractIcon class from https://github.com/firodj/extract-icon-py, Copyright(c) 2015-2016 Fadhil Mandaga, MIT license
* Using icons by https://icons8.com, Universal Multimedia Licensing
Agreement for Icons8, https://icons8.com/vue-static/landings/pricing/icons8-license.pdf

