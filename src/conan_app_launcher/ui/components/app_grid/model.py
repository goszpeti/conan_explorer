from pathlib import Path
from typing import AnyStr, Callable, Dict, List, Optional
import tempfile
import platform
from typing import Type

from conan_app_launcher import INVALID_CONAN_REF, asset_path
from conan_app_launcher.app import active_settings
from conans.model.ref import ConanFileReference
from conan_app_launcher.logger import Logger
from conan_app_launcher.components.icon import extract_icon
from conan_app_launcher.settings import LAST_CONFIG_FILE
from conan_app_launcher.ui.data import UiAppLinkConfig, UiTabConfig


class UiTabModel(UiTabConfig):
    """ Representation of a tab entry of the config schema """

    def __init__(self, *args, **kwargs):
        """ Create an empty AppModel on init, so we can load it later"""
        super().__init__(*args, **kwargs)
        self.parent = None
        self.root = None

    def load(self, tab_config: UiTabConfig, parent):
        super().__init__(tab_config.name, tab_config.apps)
        self.parent = parent
        self.root = parent


class UiAppLinkModel(UiAppLinkConfig):
    """ Representation of an app link entry of the config """
    INVALID_DESCR = "NA"
    OFFICIAL_RELEASE = "<official release>"  # to be used for "_" channel
    OFFICIAL_USER = "<official user>"  # to be used for "_" user

    def __init__(self, *args, **kwargs):
        """ Create an empty AppModel on init, so we can load it later"""
        # super().__init__() # empty init
        self.parent = None
        self.root = None
        # can be regsistered from external function to notify when conan infos habe been fetched asynchronnaly
        self._update_cbk_func: Optional[Callable] = None

        # internal repr for vars which have other types or need to be manipulated
        self._package_folder = Path("NULL")
        self._executable = Path("NULL")
        self._icon = str
        self._icon_path = Path("NULL")
        self._conan_ref = INVALID_CONAN_REF

        # holds all conan refs for name/user
        self._available_refs: List[ConanFileReference] = []

    def load(self, config: UiAppLinkConfig, parent):
        super().__init__(config.name, config.conan_ref, config.executable, config.args,
                         config.is_console_application, config.args, config.conan_options)
        self._available_refs = [self.conan_ref]
        self.parent = parent
        self.root = parent

    def update_from_cache(self):
        pass
        # if cache:  # get all info from cache
        #     self.set_available_packages(cache.get_similar_pkg_refs(
        #         self._conan_ref.name, user="*"))
        #     if USE_LOCAL_INTERNAL_CACHE:
        #         self.set_package_info(cache.get_local_package_path(str(self._conan_ref)))
        #     elif not USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH:  # last chance to get path
        #         if not conan_api:
        #             conan_api = ConanApi()
        #         package_folder = conan_api.get_path_or_install(self.conan_ref, self.conan_options)
        #         self.set_package_info(package_folder)

    def register_update_callback(self, update_func: Callable):
        self._update_cbk_func = update_func

    # @property
    # def name(self):
    #     """ Name to be displayed on the link. """
    #     return self.app_data["name"]

    # @name.setter
    # def name(self, new_value: str):
    #     self.app_data["name"] = new_value

    @property
    def conan_ref(self) -> ConanFileReference:
        """ The conan reference to be used for the link. """
        return self._conan_ref

    @conan_ref.setter
    def conan_ref(self, new_value: str):
        try:
            self._conan_ref = ConanFileReference.loads(new_value)
            # add conan ref to worker
            if (self.app_data.get("conan_ref", "") != new_value and new_value != INVALID_CONAN_REF
                    and self._conan_ref.version != self.INVALID_DESCR
                    and self._conan_ref.channel != self.INVALID_DESCR):  # don't put it for init
                if conan_worker:
                    conan_worker.put_ref_in_queue(str(self._conan_ref), self.conan_options)
            # invalidate old entries, which are dependent on the conan ref
            self.app_data["conan_ref"] = new_value
            self._executable = Path("NULL")
            self.icon = self.app_data.get("icon", "")
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
        self.conan_ref = f"{self.conan_ref.name}/{new_value}@{user}/{channel}"

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
        self.conan_ref = f"{self.conan_ref.name}/{self.conan_ref.version}@{new_value}/{channel}"

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
        if new_value == self.OFFICIAL_RELEASE or not new_value:
            new_value = "_"
            user = "_"  # both must be unset if channel is official
        self.conan_ref = f"{self.conan_ref.name}/{self.conan_ref.version}@{user}/{new_value}"

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
    def executable(self) -> Path:
        """ The executabel for this link to trigger """
        return self._executable

    @executable.setter
    def executable(self, new_value: str):
        if not new_value:
            Logger().error(f"No file/executable specified for {str(self.name)}")
            return

        # adjust path on windows, if no file extension is given
        path = Path(new_value)
        if platform.system() == "Windows" and not path.suffix:
            path = path.with_suffix(".exe")

        full_path = Path(self._package_folder / path)
        if self._package_folder.is_dir() and not full_path.is_file():
            Logger().error(
                f"Can't find file in package {str(self.conan_ref)}:\n    {str(full_path)}")
        self._executable = full_path

    @property
    def icon(self) -> str:
        """ Icon to display on the link"""
        return self._icon

    @icon.setter
    def icon(self, new_value: str):
        self._icon = new_value
        # validate icon path
        emit_warning = False
        if new_value.startswith("//"):  # relative to package
            self._icon_path = self._package_folder / new_value.replace("//", "")
        elif new_value and not Path(new_value).is_absolute():
            # relative path is calculated from config file path
            self._icon_path = Path(active_settings.get_string(LAST_CONFIG_FILE)).parent / new_value
            emit_warning = True
        elif not new_value:  # try to find icon in temp
            self._ic_icon_pathon = extract_icon(self.executable, Path(tempfile.gettempdir()))
        else:  # absolute path
            self._icon_path = Path(new_value)
            emit_warning = True
        # default icon, until package path is updated
        if not self._icon_path.is_file():
            self._icon_path = asset_path / "icons" / "app.png"
            if new_value and emit_warning:  # user input given -> warning
                Logger().error(f"Can't find icon {str(new_value)} for '{self.name}'")

        # default icon, until package path is updated
        if not self._icon_path.is_file():
            self._icon_path = asset_path / "icons" / "app.png"
            if new_value:  # user input given -> warning
                Logger().error(f"Can't find icon {str(new_value)} for '{self.name}")
        else:
            self._icon_path = self._icon_path.resolve()

    def get_icon_path(self)-> Path:
        return self._icon_path

    # @property
    # def is_console_application(self) -> bool:
    #     return bool(self.app_data.get("console_application"))

    # @is_console_application.setter
    # def is_console_application(self, new_value: bool):
    #     self.app_data["console_application"] = new_value

    # @property
    # def args(self) -> str:
    #     """ Args to launch the executable with """
    #     return self.app_data.get("args", "")

    # @args.setter
    # def args(self, new_value: str):
    #     self.app_data["args"] = new_value

    # @property
    # def conan_options(self) -> Dict[str, str]:
    #     """ User specified conan options, can differ from the actual installation """
    #     conan_options: Dict[str, str] = {}
    #     for option_entry in self.app_data.get("conan_options", {}):
    #         conan_options[option_entry["name"]] = option_entry.get("value", "")
    #     return conan_options

    # @conan_options.setter
    # def conan_options(self, new_value: Dict[str, str]):
    #     conan_options: List[OptionType] = []
    #     for opt in new_value:
    #         conan_options.append({"name": opt, "value": new_value[opt]})
    #     self.app_data["conan_options"] = conan_options

    def set_package_info(self, package_folder: Path):
        """
        Sets package path and all dependent paths.
        Use, when conan operation is done and paths can be validated.
        Usually to be called from conan worker.
        """

        if USE_LOCAL_INTERNAL_CACHE:
            if self._package_folder != package_folder and cache:
                cache.update_local_package_path(str(self.conan_ref), package_folder)
        self._package_folder = package_folder

        # use setter to reevaluate
        self.executable = self.app_data.get("executable", "")
        # icon needs executable
        self.icon = self.app_data.get("icon", "")

        # call registered update callback
        if self._update_cbk_func:
            self._update_cbk_func()

    def set_available_packages(self, available_refs: List[ConanFileReference]):
        """
        Set all other available packages.
        Usually to be called from conan worker.
        """
        if self._available_refs != available_refs and cache:
            cache.update_remote_package_list(available_refs)
        self._available_refs = available_refs

        # call registered update callback
        if self._update_cbk_func:
            self._update_cbk_func()
