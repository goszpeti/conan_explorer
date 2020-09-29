from conan_app_launcher.conan import get_conan_package_folder
from conans.model.ref import ConanFileReference


def testConanApi(base_fixture):
    # Gets package path / installs the package
    package_folder = get_conan_package_folder(
        ConanFileReference.loads("m4_installer/1.4.18@bincrafters/stable"))
    assert (package_folder / "bin").is_dir()
    # check again for already installed package
    package_folder = get_conan_package_folder(
        ConanFileReference.loads("m4_installer/1.4.18@bincrafters/stable"))
    assert (package_folder / "bin").is_dir()
