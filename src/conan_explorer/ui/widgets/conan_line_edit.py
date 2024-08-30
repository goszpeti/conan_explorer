from threading import Thread
from typing import Callable, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCompleter, QLineEdit, QListView
from typing_extensions import override

import conan_explorer.app as app  # using global module pattern
from conan_explorer.app.logger import Logger
from conan_explorer.conan_wrapper.types import ConanPkgRef, ConanRef
from conan_explorer.ui.common.theming import get_gui_dark_mode


class ConanRefLineEdit(QLineEdit):
    """ Adds completions for Conan references and a validator. """
    completion_finished = Signal()
    MINIMUM_CHARS_FOR_QUERY = 6
    INVALID_COLOR = "LightCoral"
    VALID_COLOR_LIGHT = "#37efba"  # light green
    VALID_COLOR_DARK = "#007b50"  # dark green

    def __init__(self, parent, validator_enabled=True):
        super().__init__(parent)
        self.validator_enabled = validator_enabled
        self.is_valid = False
        completer = QCompleter([], self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setMaxVisibleItems(10)
        completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        self._first_show = True # don't call completer on first show
        self._completion_thread = None
        self._loading_cbk = None
        completer_popup = QListView(self)
        completer_popup.setLayoutMode(QListView.LayoutMode.Batched)
        completer_popup.setUniformItemSizes(True)
        completer.setPopup(completer_popup)
        self.setCompleter(completer)

        self.completion_finished.connect(self.completer().complete)
        self.textChanged.connect(self.on_text_changed)

    @override
    def setEnabled(self, enabled: bool):
        # apply grey color to text, when disabled manually
        if enabled:
            self.setStyleSheet("") # remove grey color
        else:
            self.setStyleSheet("color: grey;")
        super().setEnabled(enabled)

    @override
    def showEvent(self, event):
        self.load_completion_refs()
        if self._first_show:
            self.completer().popup().hide()
            self._first_show = True
        super().showEvent(event)

    def load_completion_refs(self):
        combined_refs = set()
        combined_refs.update(app.conan_api.info_cache.get_all_local_refs())
        combined_refs.update(app.conan_api.info_cache.get_all_remote_refs())
        self.completer().model().setStringList(sorted(combined_refs, reverse=True))  # type: ignore

    def cleanup(self):
        if self._completion_thread:
            self._completion_thread.join(1)

    def set_loading_callback(self, loading_cbk: Callable):
        self._loading_cbk = loading_cbk

    def on_text_changed(self, text: str):
        self.validate(text)
        self.search_query(text)

    def validate(self, conan_ref: str):
        """ Validate ConanRef or PackageReference. Empty text is invalid. """
        if not self.validator_enabled:
            return
        if not conan_ref:
            self.is_valid = False
        else:
            try:
                if ":" in conan_ref:
                    ConanPkgRef.loads(conan_ref)
                else:
                    ConanRef.loads(conan_ref)
                self.is_valid = True
            except Exception:
                self.is_valid = False

        # color background
        if self.is_valid:
            if get_gui_dark_mode():
                self.setStyleSheet(f"background: {self.VALID_COLOR_DARK};")
            else:
                self.setStyleSheet(f"background: {self.VALID_COLOR_LIGHT};")
        else:  # if it does error it's invalid format, thus red
            self.setStyleSheet(f"background: {self.INVALID_COLOR};")

    def search_query(self, conan_ref: str):
        if len(conan_ref) < self.MINIMUM_CHARS_FOR_QUERY:  # skip searching for such broad terms
            return
        # start a query for all similar packages with conan search by starting a new thread for it
        if self._completion_thread and self._completion_thread.is_alive():  # one query at a time
            return
        self._completion_thread = Thread(target=self.load_completion, args=[conan_ref, ])
        self._completion_thread.start()
        if self._loading_cbk:
            self._loading_cbk()

    def load_completion(self, text: str):
        if any([entry.startswith(text) for entry in app.conan_api.info_cache.get_all_remote_refs()]) or self.is_valid:
            return
        recipes = app.conan_api.search_recipes_in_remotes(f"{text}*")  # can take very long time
        if app.conan_api:  # program can shut down and conan_api destroyed
            try:
                app.conan_api.info_cache.update_remote_package_list(recipes)  # add to cache
                remote_refs = app.conan_api.info_cache.get_all_remote_refs()
                # add two list together -> filter is applied later
                current_completions: List[str] = self.completer().model().stringList()  # type: ignore
                new_completions = set(remote_refs + current_completions)
                if len(new_completions) > len(current_completions):
                    self.completer().model().setStringList(sorted(new_completions))  # type: ignore
                    self.completion_finished.emit()

            except Exception as e:
                Logger().error(f"Failed load completion: {str(e)}")
