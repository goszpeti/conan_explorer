""" QT Loading dialog. Placed outside of ui, becauseit is needed to boostrap the loading of all uis. """

import os
from time import sleep
from typing import Any, Callable, Optional, Tuple

from conan_app_launcher import DEBUG_LEVEL
from conan_app_launcher.app.logger import Logger
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt, Signal, SignalInstance

from conan_app_launcher.app.system import str2bool

class Worker(QtCore.QObject):
    """ Generic worker for Qt, which can call any function with args """
    finished: SignalInstance = Signal()  # type: ignore

    def __init__(self, func, args: Tuple[Any, ...] = ()):
        super().__init__()
        self.func = func
        self.args = args

    def work(self):
        if DEBUG_LEVEL > 1:  # pragma: no cover
            try:
                import debugpy  # - debug with this the Qt Thread
                debugpy.debug_this_thread()
            except Exception:
                Logger().debug("Debugger not loaded!")
        self.func(*self.args)
        self.finished.emit()


class AsyncLoader(QtCore.QObject):

    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)
        self.progress_dialog: Optional[QtWidgets.QProgressDialog] = None
        self.worker: Optional[Worker] = None
        self.load_thread: Optional[QtCore.QThread] = None
        self.finished = True

    def async_loading(self, dialog_parent: QtWidgets.QWidget, work_task: Callable, worker_args: Tuple[Any, ...] = (),
                      finish_task: Optional[Callable] = None,
                      loading_text: str = "Loading", cancel_button=True):
        self.finished = False

        self.progress_dialog = QtWidgets.QProgressDialog(dialog_parent)
        self.progress_dialog.setLabelText(loading_text)
        # Window flags to disable close button
        self.progress_dialog.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint)
        self.progress_dialog.setWindowTitle("Loading...")
        self.progress_dialog.setCancelButton(None)  # type: ignore
        self.progress_dialog.setModal(True)  # otherwise user can trigger it twice -> crash
        self.progress_dialog.setRange(0, 0)
        self.progress_dialog.setMinimumDuration(1000)
        self.progress_dialog.setMinimumWidth(500)
        self.progress_dialog.setMaximumWidth(600)
        if cancel_button:
            self.cancel_button = QtWidgets.QPushButton("Cancel")
            self.progress_dialog.setCancelButton(self.cancel_button)

        # set position in middle of window
        qapp: QtWidgets.QApplication = QtWidgets.QApplication.instance()  # type: ignore
        rectangle = self.progress_dialog.frameGeometry()
        if dialog_parent:
            while not qapp.activeWindow():
                QtWidgets.QApplication.processEvents()
            if qapp.activeWindow():
                rectangle.moveCenter(qapp.activeWindow().frameGeometry().center())
                self.progress_dialog.move(rectangle.topLeft())
        self.progress_dialog.show()

        if str2bool(os.getenv("DISABLE_ASYNC_LOADER", "")):
            work_task(*worker_args)
            self.thread_finished()
            self.progress_dialog.hide()
            if finish_task:
                finish_task()
            return

        self.worker = Worker(work_task, worker_args)
        self.load_thread = QtCore.QThread(dialog_parent)
        self.load_thread.setObjectName(f"loader_thread_{str(self)}")
        self.worker.moveToThread(self.load_thread)
        self.load_thread.started.connect(self.worker.work)

        if finish_task:
            self.load_thread.finished.connect(finish_task)
        self.load_thread.finished.connect(self.thread_finished)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.load_thread.quit)

        self.load_thread.finished.connect(self.load_thread.deleteLater)
        self.load_thread.finished.connect(self.progress_dialog.hide)

        Logger().debug(f"Start async loading thread for {str(work_task)}")
        self.load_thread.start()
        if cancel_button:
            self.cancel_button.clicked.connect(self.load_thread.quit)

    def thread_finished(self):
        self.finished = True

    def wait_for_finished(self):
        Logger().debug("Wait for loading thread...")
        # execute once
        while not self.finished:
            sleep(0.01)
            QtWidgets.QApplication.processEvents()
