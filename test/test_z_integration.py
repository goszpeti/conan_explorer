"""
This test starts the application.
It is called z_integration, so that it launches last.
"""

import os
import sys
import threading
import time


def testDebugDisabledForRelease(base_fixture):
    from piweather import config
    assert config.DEBUG_LEVEL == 0  # debug level should be 0 for release


def testMinimalUseCase(base_fixture):
    import conan_app_launcher as app
    from conan_app_launcher.main import main
    sys.argv = ["main", "-f", str(base_fixture.testdata_path / "app_config.json")]
    main_thread = threading.Thread(target=main)
    main_thread.start()

    time.sleep(5)

    try:
        app.qt_app.quit()
        time.sleep(5)
    finally:
        if main_thread:
            main_thread.join(5)
        if app.qt_app:
            app.qt_app.quit()
