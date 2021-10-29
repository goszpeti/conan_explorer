"""
On catching an uncaught execution show a dialog with a link to post an issue, with prefilled text and stacktrace.
"""
import platform
import sys
import traceback

import conan_app_launcher as this
from conan_app_launcher.base import Logger
from PyQt5 import QtCore, QtWidgets

BUG_REPORT = f"""
**Describe the bug**
Application crash.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Desktop:**
 - OS: {platform.platform(terse=True)}
 - Python Version: {platform.python_version()}
 - Version: {this.VERSION}

**Additional context**
Add any other context about the problem here.
"""


def custom_exception_hook(exctype, value, tb):
    Logger().error("Application crashed:")
    with open(this.base_path / "crash.log", "w") as fd:
        traceback.print_tb(tb, limit=10, file=fd)
    if this.qt_app:
        import urllib.parse
        title = urllib.parse.quote("Application Crash on <>")
        body = urllib.parse.quote(f"{BUG_REPORT}\n**Stacktrace**:\n" +
                                  "\n".join(traceback.format_tb(tb, limit=None)))
        new_issue_with_info_text = f"https://github.com/goszpeti/conan_app_launcher/issues/new?title={title}&body={body}&labels=bug"
        html_crash_text = f'<html><head/><body><p> \
        Oops, something went wrong!\
        To help improve the program, please post a <a href="{new_issue_with_info_text}"><span style=" text-decoration: underline \
        color:  # 0000ff;">new github issue</span></a> and describe, how the crash occured.'
        msg = QtWidgets.QMessageBox(parent=None)
        msg.setWindowTitle("Application Crash - Bug Report")
        msg.setText(html_crash_text)
        msg.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        msg.setDetailedText("\n".join(traceback.format_tb(tb, limit=None)))
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.exec_()
    if this.conan_worker:  # cancel conan worker tasks on exit
        this.conan_worker.finish_working()
    sys.exit(1)
