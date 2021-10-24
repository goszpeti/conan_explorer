from threading import Thread
from typing import Callable

import conan_app_launcher as this
from conan_app_launcher.components.conan import ConanApi
from PyQt5 import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt


class ConanRefLineEdit(QtWidgets.QLineEdit):
    """ Adds completions for Conan references and a validator. """
    completion_finished = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        completer = QtWidgets.QCompleter([], self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._validator = QtGui.QRegExpValidator(self)
        self._validator_thread = None
        self._loading_cbk = None
        # setup range
        part_regex = r"[a-zA-Z0-9_][a-zA-Z0-9_\+\.-]{1,50}"
        recipe_regex = f"{part_regex}/{part_regex}(@{part_regex}/{part_regex})?"
        self._validator.setRegExp(QtCore.QRegExp(recipe_regex))
        self.setCompleter(completer)
        self.textChanged.connect(self.validate_text)

    def set_loading_callback(self, loading_cbk: Callable):
        self._loading_cbk = loading_cbk

    def validate_text(self, text):
        valid = False
        if self._validator.validate(text, 0)[0] < self._validator.Acceptable:
            self.setStyleSheet("background: LightCoral;")
        else:
            valid = True
            self.setStyleSheet("background: PaleGreen;")
        
        if this.cache:
            local_refs, remote_refs = this.cache.search(text)
            combined_refs = set()
            combined_refs.update(local_refs)
            combined_refs.update(remote_refs)
    
            self.completer().model().setStringList(combined_refs)
            if not any([entry.startswith(text) for entry in remote_refs]) or not valid:
                if self._validator_thread and self._validator_thread.is_alive(): # one query at a time
                    return
                self._validator_thread = Thread(target=self.load_completion, args=[text, ])
                self._validator_thread.start()
                if self._loading_cbk:
                    self._loading_cbk()

    def load_completion(self, text):
        if this.cache:
            conan = ConanApi()
            recipes = conan.search_query_in_remotes(f"{text}*")
            this.cache.update_remote_package_list(recipes)  # add to cache
            self.completion_finished.emit()

