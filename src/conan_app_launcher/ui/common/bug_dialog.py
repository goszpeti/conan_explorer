"""
On catching an uncaught execution show a dialog with a link to post an issue,
with prefilled text and stacktrace.
"""
import platform
import sys
import traceback

from conan_app_launcher import REPO_URL, __version__, base_path
from PyQt5 import QtCore, QtWidgets

bug_dialog_text = f"""
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
 - Version: {__version__}

**Additional context**
Add any other context about the problem here.
"""


def bug_reporting_dialog(excvalue, tb):
    import urllib.parse # late import hopefully we don't need this
    error_text = f"{excvalue}\n" + "\n".join(traceback.format_tb(tb, limit=None))
    title = urllib.parse.quote("Application Crash on <>")
    body = urllib.parse.quote(f"{bug_dialog_text}\n**Stacktrace**:\n" + error_text)
    new_issue_with_info_text = f"{REPO_URL}/issues/new?title={title}&body={body}&labels=bug"
    html_crash_text = f'<html><head/><body><p> \
        Oops, something went wrong!\
        To help improve the program, please post a <a href="{new_issue_with_info_text}"> \
        <span style=" text-decoration: underline color:  # 0000ff;" \
        >new github issue</span></a> and describe, how the crash occured.'
    dialog = QtWidgets.QMessageBox(parent=None)
    dialog.setWindowTitle("Application Crash - Bug Report")
    dialog.setText(html_crash_text)
    dialog.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
    dialog.setDetailedText(error_text)
    dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
    dialog.setIcon(QtWidgets.QMessageBox.Warning)
    dialog.exec_()
    return dialog # for testing

def show_bug_dialog_exc_hook(exctype, excvalue, tb):
    print("Application crashed")
    error_text = f"ERROR: {excvalue}"
    with open(base_path / "crash.log", "w") as fd:
        fd.write(error_text + "\n")
        traceback.print_tb(tb, limit=10, file=fd)
    # print it too the console too
    print(error_text)
    traceback.print_tb(tb, limit=10)
    try:
        bug_reporting_dialog(excvalue, tb)
    except Exception:
        # gui does not work anymore - nothing to do
        sys.exit(2)
    sys.exit(1)
