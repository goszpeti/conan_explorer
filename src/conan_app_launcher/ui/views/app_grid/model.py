import platform

from pathlib import Path
from typing import Callable, List, Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher import (
    INVALID_CONAN_REF, USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH_AND_INSTALL,
    USE_LOCAL_CACHE_FOR_LOCAL_PKG_PATH)
from conan_app_launcher.core.conan_worker import ConanWorkerElement
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.ui.common import extract_icon, get_icon_from_image_file, get_themed_asset_image
from conan_app_launcher.ui.data import UiAppGridConfig, UiAppLinkConfig, UiTabConfig
from conans.model.ref import ConanFileReference

from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt, QObject
from PyQt5.QtGui import QIcon

class UiAppGridModel(UiAppGridConfig, QObject):

    def __init__(self, *args, **kwargs):
        UiAppGridConfig.__init__(self, *args, **kwargs)
        QObject.__init__(self)
        self.tabs: List[UiTabModel]

    def save(self):
        if self.parent:
            self.parent.save()

    def load(self, ui_config: UiAppGridConfig, parent) -> "UiAppGridModel":
        super().__init__(ui_config.tabs)
        self.parent = parent
        # load all submodels
        tabs_model = []
        for tab_config in self.tabs:
            tabs_model.append(UiTabModel().load(tab_config, self))
        self.tabs = tabs_model
        return self

    def get_all_conan_worker_elements(self) -> List[ConanWorkerElement]:
        """ Helper function to generate a unique list of all ConanWorkerElements """
        conan_refs: List[ConanWorkerElement] = []
        for tab in self.tabs:
            for app in tab.apps:
                conan_worker_element: ConanWorkerElement = {"ref_pkg_id": app.conan_ref, "settings": {},
                                                            "options": app.conan_options, "update": False,
                                                            "auto_install": True}
                if conan_worker_element not in conan_refs:
                    conan_refs.append(conan_worker_element)
        return conan_refs


class UiTabModel(UiTabConfig, QAbstractListModel):
    """ Representation of a tab entry of the config schema """

    def __init__(self, *args, **kwargs):
        """ Create an empty AppModel on init, so we can load it later"""
        UiTabConfig.__init__(self, *args, **kwargs)
        QAbstractListModel.__init__(self)
        self.parent: UiAppGridModel
        self.apps: List[UiAppLinkModel]

    def load(self, config: UiTabConfig, parent: "UiAppGridModel") -> "UiTabModel":
        super().__init__(config.name, config.apps)
        self.parent = parent
        # load all submodels
        apps_model = []
        for app_config in self.apps:
            apps_model.append(UiAppLinkModel().load(app_config, self, trigger_update=False))
        self.apps = apps_model
        return self

    def save(self):
        if self.parent:  # delegate to top
            self.parent.save()

    # override QAbstractListModel methods - used for rearrange functions
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.apps[index.row()].name
        if role == Qt.UserRole:
            return self.apps[index.row()]

    def setData(self, index, value, role):
        if role == Qt.UserRole:
            self.apps[index.row()] = value

    def rowCount(self, parent=None) -> int:
        return len(self.apps)

    def insertRow(self, row: int, parent=QModelIndex()) -> bool:
        self.apps.insert(row, UiAppLinkModel())
        return super().insertRow(row, parent=parent)

    def removeRow(self, row: int, parent=QModelIndex()) -> bool:
        self.apps.pop(row)
        return super().removeRow(row, parent=parent)

    def moveRow(self, source_parent: QModelIndex, source_row: int, destination_parent: QModelIndex, destination_child: int) -> bool:
        app_to_move = self.apps[source_row]
        self.apps.insert(destination_child, app_to_move)
        if source_row < destination_child:
            self.apps.pop(source_row)
        else:
            self.apps.pop(source_row+1)
        return super().moveRow(source_parent, source_row, destination_parent, destination_child)


class UiAppLinkModel(UiAppLinkConfig):
    """ Representation of an app link entry of the config """
    INVALID_DESCR = "NA"
    OFFICIAL_RELEASE = "<official release>"  # to be used for "_" channel
    OFFICIAL_USER = "<official user>"  # to be used for "_" user

    def __init__(self, *args, **kwargs):
        """ Create an empty AppModel on init, so we can load it later"""
        # internal repr for vars which have other types or need to be manipulated
        self.conan_options = {}
        self.package_folder = Path("NULL")
        self._executable_path = Path("NULL")
        self._conan_ref = INVALID_CONAN_REF
        self._conan_file_reference = ConanFileReference.loads(self._conan_ref)
        self._available_refs: List[ConanFileReference] = []
        self._executable = ""
        self._icon: str = ""
        self.lock_changes = True  # values do not emit events. used when multiple changes are needed
        self.parent = UiTabModel("default")
        # can be registered from external function to notify when conan infos habe been fetched asynchronnaly
        self._update_cbk_func: Optional[Callable] = None
        # calls public functions, every internal variable needs to initialitzed
        super().__init__(*args, **kwargs)  # empty init

    def load(self, config: UiAppLinkConfig, parent: UiTabModel, trigger_update=True) -> "UiAppLinkModel":
        self.parent = parent
        if trigger_update:
            self.lock_changes = False  # don't trigger updates to worker - will be done in batch

        super().__init__(config.name, config.conan_ref, config.executable, config.icon,
                         config.is_console_application, config.args, config.conan_options)
        self.lock_changes = False  # unlock for futher use now that everything is loaded
        return self

    def save(self):
        if self.parent:  # delegate to top
            self.parent.save()

    def update_from_cache(self):
        if not app.conan_api:
            return
        # get all info from cache
        self.set_available_packages(app.conan_api.info_cache.get_similar_pkg_refs(
            self._conan_file_reference.name, user="*"))
        if USE_LOCAL_CACHE_FOR_LOCAL_PKG_PATH:
            self.set_package_info(app.conan_api.info_cache.get_local_package_path(self._conan_file_reference))
        elif not USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH_AND_INSTALL:  # last chance to get path
            _, package_folder = app.conan_api.get_path_or_auto_install(self._conan_file_reference, self.conan_options)
            self.set_package_info(package_folder)

    def register_update_callback(self, update_func: Callable):
        """ This callback can be used to update the gui after new conan info was received """
        self._update_cbk_func = update_func

    @property
    def conan_file_reference(self) -> ConanFileReference:
        return self._conan_file_reference

    @property
    def conan_ref(self) -> str:
        """ The conan reference to be used for the link. """
        return self._conan_ref

    @conan_ref.setter
    def conan_ref(self, new_value: str):
        try:
            self._conan_file_reference = ConanFileReference.loads(new_value)
        except Exception:  # invalid ref
            Logger().debug(f"Invalid ref: {new_value}")
            return
        # add conan ref to worker
        if (self._conan_ref != new_value and new_value != INVALID_CONAN_REF
                and self._conan_file_reference.version != self.INVALID_DESCR
                and self._conan_file_reference.channel != self.INVALID_DESCR):  # don't put it for init
            # invalidate old entries, which are dependent on the conan ref - only for none invalid refs
            self._conan_ref = new_value
            self.update_from_cache()
            if self.parent and self.parent.parent and not self.lock_changes:
                self.trigger_conan_update()
        self._conan_ref = new_value

    def trigger_conan_update(self):
        try:
            conan_worker_element: ConanWorkerElement = {"ref_pkg_id": str(self._conan_ref), "settings": {},
                                                        "options": self.conan_options, "update": True, "auto_install": True}
            app.conan_worker.put_ref_in_install_queue(
                conan_worker_element, self.emit_conan_pkg_signal_callback)
            app.conan_worker.put_ref_in_version_queue(
                conan_worker_element,  self.emit_conan_pkg_signal_callback)
        except Exception as error:
            # errors happen fairly often, keep going
            Logger().warning(f"Conan reference invalid {str(error)}")

    def emit_conan_pkg_signal_callback(self, conan_ref, pkg_id):
        if not self.parent.parent.parent.conan_pkg_installed:
            return
        self.parent.parent.parent.conan_pkg_installed.emit(conan_ref, pkg_id)

    @property
    def version(self) -> str:
        """ Version, as specified in the conan ref """
        return self._conan_file_reference.version

    @version.setter
    def version(self, new_value: str):
        user = self._conan_file_reference.user
        channel = self._conan_file_reference.channel
        if not self._conan_file_reference.user or not self._conan_file_reference.channel:
            user = "_"
            channel = "_"  # both must be unset if channel is official
        self.conan_ref = str(ConanFileReference(self._conan_file_reference.name, new_value, user, channel))

    @classmethod
    def convert_to_disp_channel(cls, channel: str) -> str:
        """ Substitute _ for official channel string """
        if not channel:
            return cls.OFFICIAL_RELEASE
        return channel

    @property
    def user(self) -> str:
        """ User, as specified in the conan ref """
        return self._convert_to_disp_user(self._conan_file_reference.user)

    @user.setter
    def user(self, new_value: str):
        channel = self._conan_file_reference.channel
        if new_value == self.OFFICIAL_USER or not new_value:
            new_value = "_"
            channel = "_"  # both must be unset if channel is official
        if not channel:
            channel = "NA"
        self.conan_ref = str(ConanFileReference(
            self._conan_file_reference.name, self._conan_file_reference.version, new_value, channel))

    @classmethod
    def _convert_to_disp_user(cls, user: str) -> str:
        """ Substitute _ for official user string """
        if not user:
            return cls.OFFICIAL_USER
        return user

    @property
    def channel(self) -> str:
        """ Channel, as specified in the conan ref"""
        return self.convert_to_disp_channel(self._conan_file_reference.channel)

    @channel.setter
    def channel(self, new_value: str):
        user = self._conan_file_reference.user
        # even when changig to another channel, it will reset, user or whole ref has to be changed
        if new_value == self.OFFICIAL_RELEASE or not new_value or not user:
            new_value = "_"
            user = "_"  # both must be unset if channel is official
        self.conan_ref = str(ConanFileReference(
            self._conan_file_reference.name, self._conan_file_reference.version, user, new_value))

    @property
    def versions(self) -> List[str]:
        """ All versions (sorted) for the current name and user"""
        versions = set()
        for ref in self._available_refs:
            versions.add(ref.version)
        versions_list = list(versions)
        versions_list.sort()
        return versions_list

    @property
    def users(self) -> List[str]:
        """ All users (sorted) for the current name and verion """
        users = set()
        # users.add(self.user)
        for ref in self._available_refs:
            if ref.version == self.version:
                users.add(self._convert_to_disp_user(ref.user))
        users_list = list(users)
        users_list.sort()
        return users_list

    @property
    def channels(self) -> List[str]:
        """ All channels (sorted) for the current version and user only """
        channels = set()
        channels.add(self.channel)
        for ref in self._available_refs:
            if ref.version == self.version and self._convert_to_disp_user(ref.user) == self.user:
                channels.add(self.convert_to_disp_channel(ref.channel))
        # extra handling for only one existing channel found
        if len(channels) == 2 and self.INVALID_DESCR in channels:
            channels.remove(self.INVALID_DESCR)
        channels_list = list(channels)
        channels_list.sort()
        return channels_list

    @property
    def executable(self) -> str:
        """ The executabel for this link to trigger """
        return self._executable

    @executable.setter
    def executable(self, new_value: str):
        self._executable = new_value

    def get_executable_path(self) -> Path:
        if not self._executable or not self.package_folder.exists():
            Logger().debug(f"No file/executable specified for {str(self.name)}")
            return Path("NULL")
        path = Path(self._executable)
        full_path = self.resolve_executable_path(path)
        self._executable_path = full_path

        return self._executable_path

    def resolve_executable_path(self, exe_rel_path: Path) -> Path:
        # adjust path on windows, if no file extension is given
        if platform.system() == "Windows":
            possible_matches = self.package_folder.glob(str(exe_rel_path) + "*")
            match_found = False
            match = Path("NULL")
            try:
                for match in possible_matches:
                    # don't allow for ambiguity!
                    if match_found:
                        Logger().error(f"Multiple candidates found for {exe_rel_path} in {self.name}: e.g. {str(match.name)}")
                    match_found = True
                if not match_found:
                    Logger().debug(f"Can't find file in package {self.conan_ref}:\n    {str(exe_rel_path)}")
                else:
                    return match
            except NotImplementedError:
                Logger().error(f"Absolute path not allowed!")
            return Path("NULL")
        else:
            return self.package_folder / exe_rel_path

    @property
    def icon(self) -> str:
        """ Internal representation of Icon to display on the link"""
        return self._icon

    @icon.setter
    def icon(self, new_value: str):
        self._icon = new_value

    def _eval_icon_path(self) -> Path:
        icon_path = Path("NULL")
        # relative to package - migrate from old setting
        # config path will be deprecated
        if self._icon.startswith("//"):
            self._icon = self._icon.replace("//", "./")
        if self._icon and not Path(self._icon).is_absolute():
            icon_path = self.package_folder / self._icon
        else:  # absolute path
            icon_path = Path(self._icon)
        try:
            icon_path = icon_path.resolve()
        except Exception as e:
            Logger().debug(f"Can't reslolve path of {str(icon_path)}: {str(e)}")
        return icon_path

    def get_icon(self) -> QIcon:
        """ Get an icon based on icon path """
        icon = None

        if not self._icon:
            icon = extract_icon(self.get_executable_path())
        else:
            icon = get_icon_from_image_file(self._eval_icon_path())

        # default icon, until package path is updated
        if icon.isNull():
            icon_path = get_themed_asset_image("icons/no-access.png")
            icon = get_icon_from_image_file(Path(icon_path))
            if self._icon:  # user input given -> warning
                Logger().debug(f"Can't find icon {str(self._icon)} for '{self.name}'")
        return icon

    def set_package_info(self, package_folder: Path):
        """
        Sets package path and all dependent paths.
        Use, when conan operation is done and paths can be validated.
        Usually to be called from conan worker.
        """

        if USE_LOCAL_CACHE_FOR_LOCAL_PKG_PATH:
            if self.package_folder != package_folder:
                app.conan_api.info_cache.update_local_package_path(self._conan_file_reference, package_folder)
        self.package_folder = package_folder

        # call registered update callback
        if self._update_cbk_func:
            self._update_cbk_func()

    def set_available_packages(self, available_refs: List[ConanFileReference]):
        """
        Set all other available packages.
        Usually to be called from conan worker.
        """
        self._available_refs = available_refs

        # call registered update callback
        if self._update_cbk_func:
            self._update_cbk_func()
