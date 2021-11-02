import platform
import tempfile
from pathlib import Path
from typing import Callable, List, Optional

from conan_app_launcher import (INVALID_CONAN_REF,
                                USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH,
                                USE_LOCAL_INTERNAL_CACHE, asset_path)
from conan_app_launcher.app import conan_api, conan_worker
from conan_app_launcher.components.icon import extract_icon
from conan_app_launcher.logger import Logger
from conan_app_launcher.ui.data import UiAppLinkConfig, UiTabConfig
from conan_app_launcher.ui.model import UiApplicationModel
from conans.model.ref import ConanFileReference


class UiTabModel(UiTabConfig):
    """ Representation of a tab entry of the config schema """

    def __init__(self, *args, **kwargs):
        """ Create an empty AppModel on init, so we can load it later"""
        super().__init__(*args, **kwargs)
        self.parent = None
        self.root = None

    def load(self, tab_config: UiTabConfig, parent: UiApplicationModel):
        super().__init__(tab_config.name, tab_config.apps)
        self.parent = parent

    def save(self):
        if self.parent:  # delegate to top
            self.parent.save()


class UiAppLinkModel(UiAppLinkConfig):
    """ Representation of an app link entry of the config """
    INVALID_DESCR = "NA"
    OFFICIAL_RELEASE = "<official release>"  # to be used for "_" channel
    OFFICIAL_USER = "<official user>"  # to be used for "_" user

    def __init__(self, *args, **kwargs):
        """ Create an empty AppModel on init, so we can load it later"""
        # internal repr for vars which have other types or need to be manipulated
        self.conan_options = {}
        self._package_folder = Path("NULL")
        self._executable_path = Path("NULL")
        self._icon_path = Path("NULL")
        self._conan_ref = ConanFileReference.loads(INVALID_CONAN_REF)
        self._available_refs = [self.conan_ref]
        self._executable = ""
        self._icon: str = ""
        self.parent: Optional[UiTabModel] = None
        # can be regsistered from external function to notify when conan infos habe been fetched asynchronnaly
        self._update_cbk_func: Optional[Callable] = None
        # holds all conan refs for name/user
        self._available_refs: List[ConanFileReference] = []
        # calls public functions, every internal variable needs to initialitzed
        super().__init__(*args, **kwargs)  # empty init


    def load(self, config: UiAppLinkConfig, parent):
        super().__init__(config.name, config.conan_ref, config.executable, config.args,
                         config.is_console_application, config.args, config.conan_options)
        self._available_refs = [self.conan_ref]
        self.parent = parent

    def save(self):
        if self.parent:  # delegate to top
            self.parent.save()

    def update_from_cache(self):
        # get all info from cache
        self.set_available_packages(conan_api.info_cache.get_similar_pkg_refs(
            self.conan_ref.name, user="*"))
        if USE_LOCAL_INTERNAL_CACHE:
            self.set_package_info(conan_api.info_cache.get_local_package_path(self.conan_ref))
        elif not USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH:  # last chance to get path
            package_folder = conan_api.get_path_or_install(self.conan_ref, self.conan_options)
            self.set_package_info(package_folder)

    def register_update_callback(self, update_func: Callable):
        self._update_cbk_func = update_func

    @property
    def conan_ref(self) -> ConanFileReference:
        """ The conan reference to be used for the link. """
        return self._conan_ref

    @conan_ref.setter
    def conan_ref(self, new_value: ConanFileReference):
        try:
            self._conan_ref = new_value
            # add conan ref to worker
            if (self._conan_ref != new_value and new_value != INVALID_CONAN_REF
                    and self._conan_ref.version != self.INVALID_DESCR
                    and self._conan_ref.channel != self.INVALID_DESCR):  # don't put it for init
                conan_worker.put_ref_in_queue(str(self._conan_ref), self.conan_options)
            # invalidate old entries, which are dependent on the conan ref
            self.update_from_cache()

        except Exception as error:
            # errors happen fairly often, keep going
            self._conan_ref = ConanFileReference.loads(INVALID_CONAN_REF)
            Logger().warning(f"Conan reference invalid {str(error)}")

    @property
    def version(self) -> str:
        """ Version, as specified in the conan ref """
        return self.conan_ref.version

    @version.setter
    def version(self, new_value: str):
        user = self.conan_ref.user
        channel = self.conan_ref.channel
        if not self.conan_ref.user or not self.conan_ref.channel:
            user = "_"
            channel = "_"  # both must be unset if channel is official
        self.conan_ref = ConanFileReference(self.conan_ref.name, new_value, user, channel)

    @classmethod
    def convert_to_disp_channel(cls, channel: str) -> str:
        """ Substitute _ for official channel string """
        if not channel:
            return cls.OFFICIAL_RELEASE
        return channel

    @property
    def user(self) -> str:
        """ User, as specified in the conan ref """
        return self.convert_to_disp_user(self.conan_ref.user)

    @user.setter
    def user(self, new_value: str):
        channel = self.conan_ref.channel
        if new_value == self.OFFICIAL_USER or not new_value:
            new_value = "_"
            channel = "_"  # both must be unset if channel is official
        if not channel:
            channel = "NA"
        self.conan_ref = ConanFileReference(self.conan_ref.name, self.conan_ref.version, new_value, channel)

    @classmethod
    def convert_to_disp_user(cls, user: str) -> str:
        """ Substitute _ for official user string """
        if not user:
            return cls.OFFICIAL_USER
        return user

    @property
    def channel(self) -> str:
        """ Channel, as specified in the conan ref"""
        return self.convert_to_disp_channel(self.conan_ref.channel)

    @channel.setter
    def channel(self, new_value: str):
        user = self.conan_ref.user
        # even when changig to another channel, it will reset, user or whole ref has to be changed
        if new_value == self.OFFICIAL_RELEASE or not new_value or not user:
            new_value = "_"
            user = "_"  # both must be unset if channel is official
        self.conan_ref = ConanFileReference(self.conan_ref.name, self.conan_ref.version, user, new_value)

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
        for ref in self._available_refs:
            if ref.version == self.version:
                users.add(self.convert_to_disp_user(ref.user))
        users_list = list(users)
        users_list.sort()
        return users_list

    @property
    def channels(self) -> List[str]:
        """ All channels (sorted) for the current version and user only """
        channels = set()
        for ref in self._available_refs:
            if ref.version == self.version and self.convert_to_disp_user(ref.user) == self.user:
                channels.add(self.convert_to_disp_channel(ref.channel))
        channels_list = list(channels)
        channels_list.sort()
        return channels_list

    @property
    def executable(self) -> str:
        """ The executabel for this link to trigger """
        return self._executable

    @executable.setter
    def executable(self, new_value: str):
        if not new_value:
            Logger().error(f"No file/executable specified for {str(self.name)}")
            return
        self._executable = new_value

    def get_executable_path(self) -> Path:
        # adjust path on windows, if no file extension is given
        path = Path(self._executable)
        if platform.system() == "Windows" and not path.suffix:
            path = path.with_suffix(".exe")

        full_path = Path(self._package_folder / path)
        if self._package_folder.is_dir() and not full_path.is_file():
            Logger().error(
                f"Can't find file in package {str(self.conan_ref)}:\n    {str(full_path)}")
        self._executable_path = full_path

        return self._executable_path

    @property
    def icon(self) -> str:
        """ Internal represantation of Icon to display on the link"""
        return self._icon

    @icon.setter
    def icon(self, new_value: str):
        self._icon = new_value

    def get_icon_path(self) -> Path:
        # evaluate self.icon, so icon Path
        # validate icon path
        emit_warning = False

        # relative to package - migrate from old setting
        # config path will be deprecated
        if self._icon.startswith("//"):
            self._icon = self._icon.removeprefix("//")
        if self._icon and not Path(self._icon).is_absolute():
            self._icon_path = self._package_folder / self._icon
            emit_warning = True
        elif not self._icon:  # try to find icon in temp
            self._icon_path = extract_icon(self.get_executable_path(), Path(tempfile.gettempdir()))
        else:  # absolute path
            self._icon_path = Path(self._icon)
            emit_warning = True
        # default icon, until package path is updated
        if not self._icon_path.is_file():
            self._icon_path = asset_path / "icons" / "app.png"
            if self._icon and emit_warning:  # user input given -> warning
                Logger().error(f"Can't find icon {str(self._icon)} for '{self.name}'")

        # default icon, until package path is updated
        if not self._icon_path.is_file():
            self._icon_path = asset_path / "icons" / "app.png"
            if self._icon:  # user input given -> warning
                Logger().error(f"Can't find icon {str(self._icon)} for '{self.name}")
        else:
            self._icon_path = self._icon_path.resolve()
        return self._icon_path

    def set_package_info(self, package_folder: Path):
        """
        Sets package path and all dependent paths.
        Use, when conan operation is done and paths can be validated.
        Usually to be called from conan worker.
        """

        if USE_LOCAL_INTERNAL_CACHE:
            if self._package_folder != package_folder and conan_api.info_cache:
                conan_api.info_cache.update_local_package_path(self.conan_ref, package_folder)
        self._package_folder = package_folder

        # call registered update callback
        if self._update_cbk_func:
            self._update_cbk_func()

    def set_available_packages(self, available_refs: List[ConanFileReference]):
        """
        Set all other available packages.
        Usually to be called from conan worker.
        """
        if self._available_refs != available_refs and conan_api.info_cache:
            conan_api.info_cache.update_remote_package_list(available_refs)
        self._available_refs = available_refs

        # call registered update callback
        if self._update_cbk_func:
            self._update_cbk_func()
