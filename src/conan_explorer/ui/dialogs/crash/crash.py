"""
On catching an uncaught execution show a dialog with a link to post an issue,
with prefilled text and stacktrace.
"""
import platform
import traceback
from types import TracebackType

from conan_explorer import REPO_URL, __version__
from PySide6.QtWidgets import QStyle


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


def show_bug_reporting_dialog(excvalue: BaseException, tb: TracebackType):
    import urllib.parse  # late import hopefully we don't need this
    error_text = f"{excvalue}\n" + "\n".join(traceback.format_tb(tb, limit=None))
    title = urllib.parse.quote("Application Crash on <>")
    body = urllib.parse.quote(f"{bug_dialog_text}\n**Stacktrace**:\n" + error_text)
    new_issue_with_info_text = f"{REPO_URL}/issues/new?title={title}&body={body}&labels=bug"
    html_crash_text = f'\
        <html><head/><body><p> \
        Oops, something went wrong!\
        To help improve the program, please post a <a href="{new_issue_with_info_text}"> \
        <span style=" text-decoration: underline color:  # 0000ff;" \
        >new github issue</span></a> and describe, how the crash occured!'

    from .crash_ui import Ui_Dialog, QDialog
    dialog = QDialog()
    dialog_ui = Ui_Dialog()
    dialog_ui.setupUi(dialog)
    dialog_ui.crash_message_label.setText(html_crash_text)
    dialog_ui.error_text_browser.setText(error_text)
    pixmapi = QStyle.StandardPixmap.SP_MessageBoxCritical
    icon = dialog.style().standardIcon(pixmapi)
    dialog.setWindowIcon(icon)
    dialog.setMinimumWidth(800)
    dialog.exec()
    return dialog  # for testing
