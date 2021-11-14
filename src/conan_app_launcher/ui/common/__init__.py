""" Common ui classes and functions """
from PyQt5 import QtCore
from typing import Tuple
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
