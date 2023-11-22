
import sys
import traceback
from types import TracebackType

from conan_explorer import user_save_path

def bug_dialog_exc_hook(exctype: "type[BaseException]", excvalue: BaseException, 
                        tracebock: TracebackType):
    """ App crash handling:
    print, write log and if the GUI still works show crash dialog """

    print("Application crashed")
    error_text = f"ERROR: {str(exctype)} {excvalue}"
    with open(user_save_path / "crash.log", "w") as fd:
        fd.write(error_text + "\n")
        traceback.print_tb(tracebock, limit=10, file=fd)
    # print it too the console too
    print(error_text)
    traceback.print_tb(tracebock, limit=10)
    try:
        from conan_explorer.ui.dialogs import show_bug_reporting_dialog
        show_bug_reporting_dialog(excvalue, tracebock)
    except Exception as e:
        print(str(e))
        # gui does not work anymore - nothing to do
        sys.exit(2)
    sys.exit(1)
