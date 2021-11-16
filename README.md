# <img src="https://raw.githubusercontent.com/goszpeti/conan_app_launcher/master/src/conan_app_launcher/assets/icons/icon.ico" width="128">

# Conan App Launcher and Local Package Explorer

![https://pypi.org/project/conan-app-launcher/](https://img.shields.io/pypi/v/conan-app-launcher)
![PyPI Python versions](https://img.shields.io/pypi/pyversions/conan-app-launcher)
![MilestoneProgress](https://img.shields.io/github/milestones/progress-percent/goszpeti/conan_app_launcher/9)
![Python tests](https://github.com/goszpeti/conan_app_launcher/workflows/Python%20tests/badge.svg)
![Alerts](https://sonarcloud.io/api/project_badges/measure?project=goszpeti_conan_app_launcher&metric=alert_status)
![Violations](https://img.shields.io/sonar/violations/goszpeti_conan_app_launcher?server=https%3A%2F%2Fsonarcloud.io)
![Downloads](https://img.shields.io/pypi/dm/conan_app_launcher)

## Quick Overview

The goal of this project is to provide a frontend to start executables contained in packages of the package manager [Conan](https://conan.io/). It also contains a local package explorer view, which is handy on Windows to browse short paths annd navigate quickly.

It is more end-user oriented and focuses on using packages. It can be used on Windows and Linux x64 platforms.

#### Application Link Grid:
# <img src="https://raw.githubusercontent.com/goszpeti/conan_app_launcher/master/doc/screenshot.png" width="1024">

#### Local Package Manager:
# <img src="https://raw.githubusercontent.com/goszpeti/conan_app_launcher/master/doc/screenshot_pkg_explorer.png" width="1024">


**Main Features**
- compatible with a wide range of conan versions (from 1.24 onwards)
- integrated console for information an packages and config file
- installable with pip

App Grid:
- configurable layout (tabs and applications) in the GUI
- can also open files with their associated default program
- installs all referenced packages automatically
- automatic conan settings resolution for your platform
- uses the default icons of files or can be configured to use custom ones
- quick controls to switch between versions and channels

Local Package Explorer:
- view for browsing through installed packages
- understand package settings at a glance from a shortened representation, e.g. Linux_x64_ggc7
- supports copy/paste on file, open in file explorer, copy reference, etc. functions which are often needed in daily Conan workflow


## How to install?

### Prequisites on Linux
Qt for Python must be installed with the native package manager, like:

    sudo apt install python3-pyqt5

Ubuntu 16.04 is not supported due to its native Python version (3.5).

### With pip from PyPi
`pip install conan-app-launcher`

### From source

After checkout use the command:
`pip install .`

## Running
Execute `conan-app-launcher`, if the Python "scripts" folder is on your system path, or look it up manually in the site-packages folder. 
You can also assign its icon to it from the site packages folder in conan_app_launcher/assets/icons/icon.ico.

### Main dependencies

* PyQt5 >= 5.13.0 
* conan >= 1.24.0

## Toolchain

This project uses Python with Qt as a frontend using the PyQt integration.
An IDE configuration is available for VsCode.

## Licenses of used libraries and code

#### Resources
* Using icons by https://icons8.com under [Universal Multimedia Licensing
Agreement for Icons8](https://icons8.com/vue-static/landings/pricing/icons8-license.pdf)
* Using Conan Package Manager Icon by Conan.io developers under [MIT License](<http://opensource.org/licenses/mit-license.php>), via Wikimedia Commons

##### PyPi runtime dependencies
* PyQt5 by Riverbank Computing Limited, [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)
* Conan by JFrog LTD under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)
* jsonschema by Julian Berman under [MIT License](<http://opensource.org/licenses/mit-license.php>)

##### PyPi backports for older Python versions
* importlib-metadata by Jason R. Coombs under [ Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)
* typing-extensions by Guido van Rossum, Jukka Lehtosalo, Łukasz Langa, Michael Lee under [Python Software Foundation License(PSF)](https://docs.python.org/3/license.html)
* dataclasses by Eric V. Smith under [ Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)
    'dataclasses>=0.8 ; python_version<"3.7"'  # Apache Software License (Apache)


