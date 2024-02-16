import sys
from setuptools import setup

class BForm:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

if not 'sdist' in sys.argv: # emit deprecation notice on installation
    depr_notice = f"""
    {BForm.FAIL}conan-app-launcher is now{BForm.ENDC} {BForm.HEADER}conan-explorer{BForm.ENDC}
    This package has been renamed. Use {BForm.OKGREEN}pip install conan-explorer instead.{BForm.ENDC}
    New package: {BForm.OKBLUE}https://pypi.org/project/conan-explorer/{BForm.ENDC} \n"""
    sys.exit(depr_notice)

setup(name="conan-app-launcher",
    version="2.2.0a0",
)
