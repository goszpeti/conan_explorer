"""
Entrypoint of Conan App Launcher
"""

from conan_app_launcher.app import run_application as run_conan_app_launcher
# use main with conan_search=True as a function alias for conan_searcher entrypoint
from functools import partial

run_conan_searcher = partial(run_conan_app_launcher, conan_search=True)

if __name__ == "__main__":
    run_conan_app_launcher()
