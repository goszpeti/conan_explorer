# <img src="https://raw.githubusercontent.com/goszpeti/conan_app_launcher/master/src/conan_app_launcher/icon.ico" width="128">

# Conan App Launcher

![https://pypi.org/project/conan-app-launcher/](https://img.shields.io/pypi/v/conan-app-launcher)
![PyPI Python versions](https://img.shields.io/pypi/pyversions/conan-app-launcher)
![Python tests](https://github.com/goszpeti/conan_app_launcher/workflows/Python%20tests/badge.svg)


## Quick Overview

The goal of this project is to provide a frontend to start executable contained in packages of the package manager conan. It is intented to be used on Windows and Linux x64 platforms.


# <img src="https://raw.githubusercontent.com/goszpeti/conan_app_launcher/master/doc/screenshot.png" width="1024">

Features:
- configurable layout (tabs and applications) with json file
- installs all referenced packages automatically
- automatic settings resolution for your platform
- integrated console for information an packages and config file
- installable with pip

## How to install?

### Prequisites on Linux
Qt for Python must be installed with the native package manager, like:

    sudo apt install python3-pyqt5

Ubuntu 16.04 is currently not supported, because of Python 3.5 syntax.

### With pip from Pypi
`pip install conan-app-launcher`

### From source

After checkout use the command:
`pip install .`

## Running
Execute `conan_app_launcher`, if the Python "scripts" folder is on your system path, or look it up manually in the site-packages folder.

## Config File

The config file uses the following exemplary schema:

    {
        "version": "0.2.0", // please update the schema manually, no auto update available
        "tabs": [
            {
                "name": "Basics",
                "apps": [
                    {
                        "name": "App1 with spaces", 
                        "package_id": "app1/0.1.0@user1/stable", // full conan reference
                        "executable": "bin/app1", // relative to conan "package folder"
                        "icon": "MyIcon.png" // relative to this config file,
                        "console_application": true, // start console application in extra window
                        "args": "--version" // args to start the application with
                    },
                    {
                        "name": "App2",
                        "package_id": "app2/0.2.0@user2/testing",
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
                        "package_id": "app3/0.3.0@user3/stable",
                        "console_application": true, // starts in a new console window
                        "executable": "bin/app3", // extension (.exe) can be ommited for windows
                        // Icon can be ommitted
                    }
                ]
            }
        ]
    }

## Toolchain

This project uses Python with Qt as a frontend using the PyQt integration.
The IDE integration is done for VsCode.
