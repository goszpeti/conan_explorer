# <img src="https://raw.githubusercontent.com/goszpeti/conan_explorer/main/src/conan_explorer/assets/icons/icon.ico" width="128">

# Conan Explorer: Local Package Explorer and App Launcher

![https://pypi.org/project/conan-explorer/](https://img.shields.io/pypi/v/conan-explorer?logo=pypi)
![PyPI Python versions](https://img.shields.io/pypi/pyversions/conan-explorer?logo=python)
![Windows](https://custom-icon-badges.demolab.com/badge/Windows-0078D6?logo=windows11&logoColor=white)
![Linux](
https://img.shields.io/badge/Linux-purple?logo=linux&logoColor=white)
![MilestoneProgress](https://img.shields.io/github/milestones/progress-percent/goszpeti/conan_explorer/25?logo=conan)
[![Python Tests](https://github.com/goszpeti/conan_explorer/actions/workflows/test.yml/badge.svg)](https://github.com/goszpeti/conan_explorer/actions/workflows/test.yml)
![SonarStatus](https://sonarcloud.io/api/project_badges/measure?project=goszpeti_conan_explorer&metric=alert_status)
![Downloads](https://img.shields.io/pypi/dm/conan_explorer)


## 🛈 conan-app-launcher is now conan-explorer 🚀

This package has been renamed from version 2.2.0 onwards. Use `pip install conan-explorer` instead.

New package: https://pypi.org/project/conan-explorer/

## 📋 Quick Overview

The goal of this project is to provide a standalone Graphical User Interface (GUI) to
* Start executables contained in packages of the package manager [Conan](https://conan.io/)
* Browse the local package cache
* Search Packages in remotes
* Configure Remotes and Profiles

It is end-user oriented and focuses on using packages, rather then developing them. It can be used on Windows and Linux x64 platforms.

#### Quicklaunch for Applications in Conan Packages
# <img src="https://raw.githubusercontent.com/goszpeti/conan_explorer/main/doc/screenshot.png" width="512">

#### Local Package Manager
# <img src="https://raw.githubusercontent.com/goszpeti/conan_explorer/main/doc/screenshot_pkg_explorer.png" width="512">

#### Conan Search
# <img src="https://raw.githubusercontent.com/goszpeti/conan_explorer/main/doc/screenshot_conan_search.png" width="512">

#### Conan Config
# <img src="https://raw.githubusercontent.com/goszpeti/conan_explorer/main/doc/screenshot_conan_conf.png" width="512">

**Main Features**
- compatible with a wide range of conan versions (from 1.24 onwards)
- integrated console for information an packages and config file
- installable with pip

**📑 Quicklaunch**

- configurable layout (tabs and applications) in the GUI
- list and grid view
- can also open files with their associated default program
- installs all referenced packages automatically
- automatic conan settings resolution for your platform
- uses the default icons of files or can be configured to use custom ones
- quick controls to switch between versions and channels

**📦 Local Package Explorer**

- tabbed view for browsing through installed packages
- understand package settings at a glance from a shortened representation, e.g. Linux_x64_ggc7
- supports rename/copy/cut/paste on file, open in file explorer, copy reference, etc. functions which are often needed in daily Conan workflow

**🔍 Conan Search**

- search for references in selected remotes
- show all existing packages for a reference and their infos
- install package directly via right-click menu

**📝 Conan Config**

- view and edit your profiles
- view and edit your remotes - with multi-login to the same artifactory server for multiple remotes
- see the most important paths and config at one glance

**🔌 Plugin Mechanism**

- All views are now plugins, which can be extended by the user

## 💻 Installation

### 🐧 Prerequisites on Linux

Currently testing and compatibility is only ensured for Debian based distros, see the section distros, although if Qt6 is working for the plaftorm there should be no problems.

1. Pip must be updated to at least pip 20.3, so using a venv like this is recommended:

```bash
sudo apt-get install python3-venv
python3 -m venv .venv 
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install conan_explorer --use-pep517
```

2. An x-terminal emulator must be available for "Open Files in cmd" and console based programs for the App Grid. Type `x-terminal-emulator` to get a list of available terminals.

3. To open files with its associated program xdg-open is used: `sudo apt install xdg-utils` or `sudo dnf install xdg-utils`

#### Distros

[![Debian](https://img.shields.io/badge/Debian-A81D33?logo=debian&logoColor=fff)](#)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?logo=ubuntu&logoColor=white)](#)
[![Fedora](https://img.shields.io/badge/Fedora-51A2DA?logo=fedora&logoColor=fff)](#)

Not all Qt6 versions support the Wayland lib of the operating system.
Generally the solution is to match the qt6 platform packages to the ones deployed with Pyside6. Minor version match is enough, because patch versions are ABI compatible.

  * **Ubuntu 18** was last supported in the 1.4.3 release, due to the Qt dependency.
  Recompiling Qt6 would be necessary.
  * For **Ubuntu 20.04** please execute `pip install PySide6-Essentials==6.4.3` in the same environment as conan_explorer and update pip to latest version!
  * For **Ubuntu 22.04** please ensure that the system Qt6 packages are available. Simply execute `sudo apt-get install qt6-wayland` on a wayland system, or `sudo apt-get install qt6-base-dev` for an X11 based system.
  * For **Ubuntu 24.04** the wayland platform is currently unknown how to get work with PySide6. To force X11 mode on wayland start it with `--platform=xbc` and make sure  "libxcb-cursor0" is installed.
  * **Fedora 28** (base for RedHat 8.4) - No information
  * **Fedora 34** (base for RedHat 9.4) and **Fedora 40** - runs natively on X11 and wayland without problems with a desktop environment. 

#### Scaling on X11

If the window displays with very small scaling you can increase it by setting the environment variable QT_SCALE_FACTOR to a higher value, e.g. `QT_SCALE_FACTOR=2 conan_explorer`

### With pip from PyPi

    pip install conan-explorer --use-pep517

### From source

After checkout use the command:

    pip install . --use-pep517

## 🏃 Running

Execute `conan_explorer` if the Python "scripts" or "bin" folder is on your system path, or look it up manually in the site-packages folder. 
You can also assign its icon to it from the site packages folder in **conan_explorer/assets/icons/icon.ico**.

### Main dependencies

* Pyside6 >= 6.4.3
* 1.48.0 <= conan < 2.8

> ⚠ **Warning** - **Deprecation of Python 3.X**  
> From version 2.0.0 Python 3.6 support will be dropped, having reached end-of-life.    
> From version 2.2.0 Python 3.7 support will be dropped, having reached end-of-life.    

## 🛠 Toolchain

[![Visual Studio Code](https://custom-icon-badges.demolab.com/badge/Visual%20Studio%20Code-0078d7.svg?logo=vsc&logoColor=white)](#)

This project uses Python with Qt as a frontend using the PySide6 integration.
An IDE configuration is available for VsCode.

The .ui files are created with Qt Designer and automatically converted to .py code when starting the application. The Designer can be installed via the PySide6-Addons pip package.

See https://sonarcloud.io/project/overview?id=goszpeti_conan_explorer for Static Code Analysis.

## 📒 Licenses of used libraries and code

> **Warning** - **Change of License to LGPL**
> From version 2.0.0 the project will use the [LGPL 3.0](https://www.gnu.org/licenses/lgpl-3.0.en.html) license to cleanly comply with PySide6.

#### Resources
* Conan Package Manager Icon by Conan.io developers under [MIT License](http://opensource.org/licenses/mit-license.php), via Wikimedia Commons
* [Noto Sans and Noto Sans Mono fonts](https://fonts.google.com/) by Google under [SIL Open Font License](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL)
* [Material icons](https://fonts.google.com/) by Google  under [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
* [Linux icon](https://www.svgrepo.com/svg/340563/linux-alt) by Carbon Design  under [Apache License](https://opensource.org/licenses/Apache-1.1)
* [Apple icon](https://www.svgrepo.com/svg/488495/apple) by Klever Space  under [MIT License](http://opensource.org/licenses/mit-license.php)
* [Windows icon](https://www.svgrepo.com/svg/488736/windows) by Klever Space under [MIT License](http://opensource.org/licenses/mit-license.php)
* Modified [Package icon](https://www.svgrepo.com/svg/487645/package) by Neuicons [MIT License](http://opensource.org/licenses/mit-license.php)
* Modified [Open Box icon](https://www.svgrepo.com/svg/383786/open-box-parcel) by wishforge.gamesunder [CC Attribution License](https://creativecommons.org/licenses/by/4.0/legalcode)</li>

##### PyPi runtime dependencies
* PySide6 by Qt, [LGPL V3](https://www.gnu.org/licenses/lgpl-3.0.en.html)
* Conan by JFrog LTD under [MIT License](<http://opensource.org/licenses/mit-license.php>)
* jsonschema by Julian Berman under [MIT License](<http://opensource.org/licenses/mit-license.php>)
* dictdiffer by Invenio Collaboration under [MIT License](<http://opensource.org/licenses/mit-license.php>)
* Using a modified version of Toggle Widget from QtWidgets (https://github.com/pythonguis/python-qtwidgets) under [MIT License](<http://opensource.org/licenses/mit-license.php>)

##### PyPi backports for older Python versions
* contextlib-chdir by Álvaro Mondéjar Rubio under [BSD License (BSD-3-Clause) ](https://opensource.org/license/BSD-3-clause/)
* typing-extensions by Guido van Rossum, Jukka Lehtosalo, Łukasz Langa, Michael Lee under [Python Software Foundation License(PSF)](https://docs.python.org/3/license.html)
