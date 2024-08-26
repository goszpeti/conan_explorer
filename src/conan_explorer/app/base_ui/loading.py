""" Qt Loading dialog. Placed outside of ui, because 
it is needed to boostrap the loading of all uis. """

import os
from datetime import datetime
from time import sleep
import time
from typing import Any, Callable, Optional, Tuple

from conan_explorer import DEBUG_LEVEL, asset_path
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import str2bool

from PySide6.QtCore import Qt, QObject, QThread, Signal, SignalInstance
from PySide6.QtWidgets import QApplication, QProgressDialog, QPushButton, QWidget
from PySide6 import QtGui


class Worker(QObject):
    """ Generic worker for Qt, which can call any function with args """
    finished: SignalInstance = Signal(object)  # type: ignore

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
        start = time.time()
        ret = self.func(*self.args)
        end = time.time()
        Logger().debug("Waited: " + str(end - start) + " s")
        self.finished.emit(ret)


class LoaderGui(QObject):
    # Reuse the same progress_dialog instance for every loading dialog - 
    # there can only be one at a time
    __progress_dialog: Optional[QProgressDialog] = None
    loading_string_signal: SignalInstance = Signal(str)  # type: ignore
    loading_gui_signal: SignalInstance = Signal(SignalInstance)  # type: ignore
    loading_finished_signal: SignalInstance = Signal()  # type: ignore

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent)
        # initial setup
        if LoaderGui.__progress_dialog is None: # implicit check for init
            wt = Qt.WindowType
            progress_dialog = QProgressDialog()
            progress_dialog.setAttribute(Qt.WidgetAttribute.WA_ShowModal)
            progress_dialog.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop)
            # Window flags to disable close button
            progress_dialog.setWindowFlags(wt.FramelessWindowHint |
                wt.Window | wt.WindowTitleHint | wt.CustomizeWindowHint)
            progress_dialog.setCancelButton(None)  # type: ignore
            progress_dialog.setModal(True)  # user could trigger it twice -> crash
            progress_dialog.setRange(0, 0)
            progress_dialog.setMinimumDuration(1000)
            progress_dialog.setMinimumWidth(500)
            progress_dialog.setMaximumWidth(600)
            progress_dialog.setWindowIcon(QtGui.QIcon(str(asset_path / "icons" / "icon.ico")))

            LoaderGui.__progress_dialog = progress_dialog
        self.progress_dialog = LoaderGui.__progress_dialog
        self.loading_string_signal.connect(self.progress_dialog.setLabelText)
        self.loading_finished_signal.connect(self.thread_finished)
        self.worker: Optional[Worker] = None
        self.load_thread: Optional[QThread] = None
        self.finished = True
        self.return_value = None
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)

    def load_with_finish_hook(self, dialog_parent: Optional[QWidget], work_task: Callable,
                                 worker_args: Tuple[Any, ...] = (),
                                 finish_task: Optional[Callable] = None,
                                 loading_text: str = "Loading...", cancel_button=True):
        self.load(dialog_parent, work_task, 
                           worker_args, finish_task, loading_text, cancel_button)

    def load_for_blocking(self, dialog_parent: Optional[QWidget], work_task: Callable,
                             worker_args: Tuple[Any, ...] = (),
                             loading_text: str = "Loading...", cancel_button=True):
        self.load(dialog_parent, work_task, worker_args,
                           loading_text=loading_text, cancel_button=cancel_button)


    def load(self, dialog_parent: Optional[QWidget], work_task: Callable, 
                      worker_args: Tuple[Any, ...] = (),
                      finish_task: Optional[Callable] = None,
                      loading_text: str = "Loading...", cancel_button=True):
        self.finished = False
        self.return_value = None
        self.progress_dialog.setLabelText(loading_text)

        if cancel_button:
            self.progress_dialog.setCancelButton(self.cancel_button)
        else:
            self.progress_dialog.setCancelButton(None) # type: ignore

        # set position in middle of window
        qapp: QApplication = QApplication.instance()  # type: ignore
        rectangle = self.progress_dialog.frameGeometry()
        if dialog_parent:
            # wait for active window to center
            start_time = datetime.now()
            while not qapp.activeWindow():
                QApplication.processEvents()
                time_delta = datetime.now() - start_time
                if time_delta.total_seconds() >= 2:
                    break
            if qapp.activeWindow(): 
                rectangle.moveCenter(qapp.activeWindow().frameGeometry().center())
                self.progress_dialog.move(rectangle.topLeft())
        else:
            rectangle.moveCenter(qapp.primaryScreen().geometry().center())
            self.progress_dialog.move(rectangle.topLeft())
        self.progress_dialog.show()
        self.progress_dialog.activateWindow()

        # for debug purposes only
        if str2bool(os.getenv("DISABLE_ASYNC_LOADER", "")):
            ret = work_task(*worker_args)
            self.thread_finished()
            self.progress_dialog.hide()
            if finish_task:
                try: # difficult to handle without Qt signals - so just try
                    finish_task(ret)
                except Exception:
                    finish_task()
            self.on_finished(ret)
            return

        self.worker = Worker(work_task, worker_args)
        self.load_thread = QThread(dialog_parent)
        self.load_thread.setObjectName(f"loader_thread_{str(self)}")
        self.worker.moveToThread(self.load_thread)
        self.load_thread.started.connect(self.worker.work)

        if finish_task:
            self.worker.finished.connect(finish_task)
        self.load_thread.finished.connect(self.thread_finished)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.load_thread.quit)
        self.worker.finished.connect(self.on_finished)

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
            QApplication.processEvents()

    def on_cancel(self):
        self.finished = True

    def on_finished(self, return_value=None):
        # save return value to get after wait_for_finished
        self.return_value = return_value
