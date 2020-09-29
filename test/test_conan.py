import os

from conans.model.ref import ConanFileReference

from conan_app_launcher.conan import get_conan_package_folder


def testConanApi():
    ref = "m4_installer/1.4.18@bincrafters/stable"
    os.system("conan remove %s -f" % ref)
    # Gets package path / installs the package
    package_folder = get_conan_package_folder(ConanFileReference.loads(ref))
    assert (package_folder / "bin").is_dir()
    # check again for already installed package
    package_folder = get_conan_package_folder(ConanFileReference.loads(ref))
    assert (package_folder / "bin").is_dir()
