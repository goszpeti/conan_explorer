from threading import Thread
from typing import Callable, List

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.settings import GUI_STYLE, GUI_STYLE_DARK
from conans.model.ref import ConanFileReference, PackageReference
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QLineEdit, QCompleter


class ConanRefLineEdit(QLineEdit):
    """ Adds completions for Conan references and a validator. """
    completion_finished = pyqtSignal()
    MINIMUM_CHARS_FOR_QUERY = 4
    INVALID_COLOR = "LightCoral"
    VALID_COLOR_LIGHT = "#37efba"  # light green
    VALID_COLOR_DARK = "#007b50"  # dark green

    def __init__(self, parent, validator_enabled=True):
        super().__init__(parent)
        self.validator_enabled = validator_enabled
        self.is_valid = False
        completer = QCompleter([], self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self._completion_thread = None
        self._loading_cbk = None
        self._remote_refs = app.conan_api.info_cache.get_all_remote_refs()  # takes a while to get

        self.setCompleter(completer)
        combined_refs = set()
        combined_refs.update(app.conan_api.info_cache.get_all_local_refs())
        combined_refs.update(self._remote_refs)
        self.completer().model().setStringList(list(combined_refs))
        self.textChanged.connect(self.on_text_changed)

    def __del__(self):
        if self._completion_thread:
            self._completion_thread.join(1)

    def set_loading_callback(self, loading_cbk: Callable):
        self._loading_cbk = loading_cbk

    def on_text_changed(self, text: str):
        self.validate(text)
        self.search_query(text)

    def validate(self, conan_ref: str):
        """ Validate ConanFileReference or PackageReference. Empty text is invalid. """
        if not self.validator_enabled:
            return
        if not conan_ref:
            self.is_valid = False
        else:
            try:
                if ":" in conan_ref:
                    PackageReference.loads(conan_ref)
                else:
                    ConanFileReference.loads(conan_ref)
                self.is_valid = True
            except Exception:
                self.is_valid = False

        # color background
        if self.is_valid:
            if app.active_settings.get_string(GUI_STYLE).lower() == GUI_STYLE_DARK:
                self.setStyleSheet(f"background: {self.VALID_COLOR_DARK};")
            else:
                self.setStyleSheet(f"background: {self.VALID_COLOR_LIGHT};")
        else:  # if it does error it's invalid format, thus red
            self.setStyleSheet(f"background: {self.INVALID_COLOR};")

    def search_query(self, conan_ref: str):
        if len(conan_ref) < self.MINIMUM_CHARS_FOR_QUERY:  # skip searching for such broad terms
            return
        # start a query for all similar packages with conan search by starting a new thread for it
        if not any([entry.startswith(conan_ref) for entry in self._remote_refs]) or not self.is_valid:
            if self._completion_thread and self._completion_thread.is_alive():  # one query at a time
                return
            self._completion_thread = Thread(target=self.load_completion, args=[conan_ref, ])
            self._completion_thread.start()
            if self._loading_cbk:
                self._loading_cbk()

    def load_completion(self, text: str):
        recipes = app.conan_api.search_query_in_remotes(f"{text}*")  # can take very long time
        if app.conan_api:
            app.conan_api.info_cache.update_remote_package_list(recipes)  # add to cache
            self.completion_finished.emit()
            self._remote_refs = app.conan_api.info_cache.get_all_remote_refs()
            current_completions: List[str] = self.completer().model().stringList() # add two list together -> filter is applied later
            new_completions = set(self._remote_refs + current_completions)
            self.completer().model().setStringList(list(new_completions))
