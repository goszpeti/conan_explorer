import json
import threading
from typing import Optional
import conan_explorer.app as app
from pyqttoast import Toast, ToastPreset
from PySide6.QtCore import QRect, Signal, SignalInstance, Qt, QObject
from conan_explorer import user_save_path
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import delete_path

class NotifierService(QObject):
    conan_pkg_available: SignalInstance = Signal(str, str)  # type: ignore

    queries = ["*stable", "*integration"]
    UPDATE_TIME_s = 3 * 60
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.conan_pkg_available.connect(self.show_notification)
        self._ticker_event = threading.Event()
        self._update_thread: Optional[threading.Thread] = None
        self._update_thread = threading.Thread(name=self.__class__.__name__,
                                               target=self._update_loop,
                                            #    args=[init_func, update_func, ],
                                               daemon=True)
        self._update_thread.start()

    def _update_loop(self):
        # first search
        notifier_journal = user_save_path / "notifier_journal.json"
        if not notifier_journal.exists():
            notifier_journal.touch()
        json_data = {"refs": []}
        try:
            with open(notifier_journal, "r") as json_file:
                content = json_file.read()
                if len(content) > 0:
                    json_data = json.loads(content)
                else:
                    json_data["refs"] = app.conan_api.info_cache.get_all_remote_refs()
                    self._save(notifier_journal, json_data)
        except Exception:  # possibly corrupt, delete cache file
            Logger().debug("ConanCache: Can't read speedup-cache file, deleting it.")
            delete_path(notifier_journal)
            # create file anew
            notifier_journal.touch()
        while not self._ticker_event.wait(self.UPDATE_TIME_s):
            if self._ticker_event.is_set():
                self._ticker_event.clear()
                return
            for remote in app.conan_api.get_remotes():
                for query in self.queries:
                    stables = app.conan_api.search_recipes_in_remotes(
                        query, remote_name=remote.name)
                    for ref in  stables:
                        if ref not in json_data.get("refs", []):
                            json_data.get("refs", []).append(ref)
                            self.conan_pkg_available.emit(str(ref), remote.name)
                            self._save(notifier_journal, json_data)
            #integrations = app.conan_api.search_recipes_in_remotes("*integration", remote_name="all")
            # get new ones

    def _save(self, notifier_journal, json_data):
        try:
            with open(notifier_journal, "w") as json_file:
                    json.dump(json_data, json_file)
        except Exception:
            Logger().debug("ConanCache: Can't save speedup-cache file.")

    def show_notification(self, ref: str, server: str):
        self.toast = Toast(self.parent())
        self.toast.setDuration(10000)  # Hide after 5 seconds
        self.toast.applyPreset(ToastPreset.INFORMATION_DARK)  # Apply style preset
        self.toast.setMinimumWidth(600)
        self.toast.setMinimumHeight(50)
        self.toast.setMaximumWidth(1000)
        self.toast.setTitle('New release availabe!')
        self.toast.setText(f"{ref} was just released on remote {server}")
        self.toast.show()
