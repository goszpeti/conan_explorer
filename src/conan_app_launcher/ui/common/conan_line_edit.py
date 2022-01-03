from threading import Thread
from typing import Callable

import conan_app_launcher.app as app  # using gobal module pattern
from PyQt5 import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt


class ConanRefLineEdit(QtWidgets.QLineEdit):
    """ Adds completions for Conan references and a validator. """
    completion_finished = QtCore.pyqtSignal()
    MINIMUM_CHARS_FOR_QUERY = 4

    def __init__(self, parent):
        super().__init__(parent)
        completer = QtWidgets.QCompleter([], self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._validator = QtGui.QRegExpValidator(self)
        self._validator_thread = None
        self._loading_cbk = None
        self._remote_refs = app.conan_api.info_cache.get_all_remote_refs() # takes a while to get
        # setup range
        part_regex = r"[a-zA-Z0-9_][a-zA-Z0-9_\+\.-]{1,50}"
        recipe_regex = f"{part_regex}/{part_regex}(@({part_regex}|_)/({part_regex}|_))?"
        self._validator.setRegExp(QtCore.QRegExp(recipe_regex))
        self.setCompleter(completer)
        combined_refs = set()
        combined_refs.update(app.conan_api.info_cache.get_all_local_refs())
        combined_refs.update(self._remote_refs)
        self.completer().model().setStringList(list(combined_refs))
        self.textChanged.connect(self.validate_text)

    def __del__(self):
        if self._validator_thread:
            self._validator_thread.join(1)

    def set_loading_callback(self, loading_cbk: Callable):
        self._loading_cbk = loading_cbk

    def validate_text(self, text):
        valid = False
        if self._validator.validate(text, 0)[0] < self._validator.Acceptable:
            self.setStyleSheet("background: LightCoral;")
        else:
            valid = True
            self.setStyleSheet("background: PaleGreen;")
        
        if len(text) < self.MINIMUM_CHARS_FOR_QUERY:  # skip seraching for such broad terms
            return

        if not any([entry.startswith(text) for entry in self._remote_refs]) or not valid:
            if self._validator_thread and self._validator_thread.is_alive(): # one query at a time
                return
            self._validator_thread = Thread(target=self.load_completion, args=[text, ])
            self._validator_thread.start()
            if self._loading_cbk:
                self._loading_cbk()

    def load_completion(self, text: str):
        recipes = app.conan_api.search_query_in_remotes(f"{text}*") # can take very long time
        if app.conan_api:
            app.conan_api.info_cache.update_remote_package_list(recipes)  # add to cache
            self.completion_finished.emit()
            self._remote_refs = app.conan_api.info_cache.get_all_remote_refs()  # takes a while to get
            self.completer().model().setStringList(self._remote_refs)
