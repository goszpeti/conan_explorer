"""
This test starts the application.
It is called z_integration, so that it launches last.
"""

import os
import sys
import threading
import time


def testDebugDisabledForRelease(base_fixture):
    from conan_app_launcher import DEBUG_LEVEL
    assert DEBUG_LEVEL == 0  # debug level should be 0 for release


def testMinimalUseCase(base_fixture):
    # Start the gui and check if it runs and does not throw errors
    pass
    # import conan_app_launcher as app
    # from conan_app_launcher.main import main
    # sys.argv = ["main", "-f", str(base_fixture.testdata_path / "app_config.json")]
    # main_thread = threading.Thread(target=main)
    # main_thread.start()

    # time.sleep(7)

    # try:
    #     print("Start quit")
    #     app.qt_app.quit()
    #     time.sleep(3)
    # finally:
    #     if main_thread:
    #         print("Join test thread")
    #         main_thread.join()

    # def testOpenMenu(base_fixture):
    #     pass

    # def testClickApp(base_fixture):
    #     pass
