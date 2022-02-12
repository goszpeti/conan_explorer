""" Common ui classes and functions """
from conan_app_launcher.logger import Logger
from PyQt5 import QtCore, QtWidgets
from typing import Optional, Tuple, Callable

from PyQt5.QtCore import Qt
ASYNC_LOADING = True  # For debug purposes: errors in Qt Threads are not debuggable


class Worker(QtCore.QObject):
    """ Generic worker for Qt, which can call any function with args """
    finished = QtCore.pyqtSignal()

    def __init__(self, func, args: Tuple = ()):
        super().__init__()
        self.func = func
        self.args = args

    def work(self):
        self.func(*self.args)
        self.finished.emit()


class QtLoaderObject(QtCore.QObject):
    def __init__(self) -> None:
        self.progress_dialog: Optional[QtWidgets.QProgressDialog] = None
        self.worker: Optional[Worker] = None
        self.load_thread: Optional[QtCore.QThread] = None

    def async_loading(self, parent, work_task: Callable, finish_task: Optional[Callable], loading_text: str):
        # TODO check if init_model_thread exists and wait for join
        self.progress_dialog = QtWidgets.QProgressDialog(parent)
        self.progress_dialog.setLabelText(loading_text)
        # Window flags to disable close button
        self.progress_dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.progress_dialog.setWindowTitle("Loading...")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setModal(True)  # otherwise user can trigger it twice -> crash
        self.progress_dialog.setRange(0, 0)
        self.progress_dialog.setMinimumDuration(1000)
        self.progress_dialog.show()

        if ASYNC_LOADING:
            self.worker = Worker(work_task)
            self.load_thread = QtCore.QThread()
            self.worker.moveToThread(self.load_thread)
            self.load_thread.started.connect(self.worker.work)

            if finish_task:
                self.worker.finished.connect(finish_task)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.load_thread.quit)

            self.load_thread.finished.connect(self.load_thread.deleteLater)
            self.load_thread.finished.connect(self.progress_dialog.hide)
            Logger().debug(f"Start async loading thread for {str(work_task)}")
            self.load_thread.start()
        else:
            work_task()
            if finish_task:
                finish_task()
                self.progress_dialog.hide()
