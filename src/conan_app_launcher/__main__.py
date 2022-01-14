"""
Entrypoint of Conan App Launcher
"""

from conan_app_launcher.app import main
# use main with conan_search=True as a function alias for conan_searcher entrypoint
from functools import partial
main_conan_search = partial(main, True)

if __name__ == "__main__":
    main()
