from typing import Optional

import conan_explorer.app as app
from conan_explorer.app import AsyncLoader
from conan_explorer.app.logger import Logger  # using global module pattern
from conan_explorer.conan_wrapper.conan_worker import ConanWorkerElement
from conan_explorer.settings import DEFAULT_INSTALL_PROFILE
from conan_explorer.ui.common import get_themed_asset_icon
from PySide6.QtCore import QSize, Qt, Signal, SignalInstance
from PySide6.QtWidgets import QDialog, QWidget, QTreeWidgetItem, QComboBox

from conan_explorer.conan_wrapper.types import ConanOptions, ConanRef
from conan_explorer.ui.dialogs.pkg_diff.diff import PkgDiffDialog


class ConanInstallDialog(QDialog):
    MARK_AS_DEFAULT_INSTALL_PROFILE = " *"
    conan_diff_requested: SignalInstance = Signal(str)  # type: ignore - conan_ref

    def __init__(self, parent: Optional[QWidget], conan_full_ref: str, 
                 pkg_installed_signal: Optional[SignalInstance] = None, 
                 lock_reference=False, capture_install_info=False):
        """
        conan_ref can be in full ref format with <ref>:<id> 
        lock_reference disables conan reference editing.
        capture_install_info does not actually install, just return the selected info.
        """
        super().__init__(parent)
        from .conan_install_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        self.pkg_installed_signal = pkg_installed_signal
        self._capture_install_info = capture_install_info
        self._conan_selected_install: Optional[ConanWorkerElement] = None
        # style
        icon = get_themed_asset_icon("icons/download_pkg.svg", True)
        self.setWindowIcon(icon)

        # init search bar
        self._ui.conan_ref_line_edit.validator_enabled = False
        self._ui.conan_ref_line_edit.setText(conan_full_ref)
        if lock_reference:
            self._ui.conan_ref_line_edit.setEnabled(False)

        # button box
        self._ui.button_box.accepted.connect(self.on_install)
        self.adjust_to_size()

        # hide items, when it has a ref:
        if ":" in conan_full_ref:
            self.hide_config_elements()
            self.setFixedHeight(175)
            return
        # profiles
        self.load_profiles()
        self.load_options(conan_full_ref)

        if capture_install_info: # auto install makes no sense in this mode
            self.hide_for_install_info()
            self.resize(self.width(), self.height() - 150)

        # disable profile and options on activating this
        self._ui.auto_install_check_box.clicked.connect(self.on_auto_install_check)
        self._ui.set_default_install_profile_button.clicked.connect(
            self.on_set_default_install_profile)
        self.conan_diff_requested.connect(self.show_package_diffs)

    def hide_config_elements(self):
        self._ui.profile_cbox.hide()
        self._ui.profile_label.hide()
        self._ui.set_default_install_profile_button.hide()
        self._ui.conan_opts_label.hide()
        self._ui.options_widget.hide()
        self._ui.line.hide()
        self._ui.auto_install_label.hide()
        self._ui.auto_install_check_box.hide()

    def hide_for_install_info(self):
        self._ui.auto_install_check_box.hide()
        self._ui.auto_install_label.hide()
        self._ui.update_label.hide()
        self._ui.update_check_box.hide()
        self._ui.line.hide()

    def load_profiles(self):
        self._ui.profile_cbox.clear()
        profiles = app.conan_api.get_profiles()
        default_profile = app.active_settings.get_string(DEFAULT_INSTALL_PROFILE)
        try:
            default_index = profiles.index(default_profile)
        except Exception:
            default_index = None
        if not default_index:
            app.active_settings.set(DEFAULT_INSTALL_PROFILE, "default")
        try:
            if default_index is not None:
                profiles.pop(default_index)
                profiles.insert(0, default_profile + self.MARK_AS_DEFAULT_INSTALL_PROFILE)
        except Exception:
            Logger().debug("Can't mark default install profile")
        self._ui.profile_cbox.addItems(profiles)

    def load_options(self, conan_full_ref: str):
        # options table
        default_options = {}
        conan_ref = ""
        try:
            conan_ref = conan_full_ref.split(":")[0]
            ConanRef.loads(conan_ref)
        except Exception:
            return
        loader = AsyncLoader(self)
        loader.async_loading(self, self.on_options_query, (conan_ref, ), 
                             loading_text="Loading options...")
        loader.wait_for_finished()
        default_options = self._default_options
        # doing this after connecting toggle_auto_install_on_pkg_ref initializes it correctly
        for name, value in default_options.items():
            item = QTreeWidgetItem(self._ui.options_widget)
            item.setData(0, 0, name)
            item.setData(1, 0, str(value))
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Qt.ItemFlag.ItemIsEditable |
            self._ui.options_widget.addTopLevelItem(item)
            try:
                values = self._available_options[name]
                if isinstance(values, list) and values != ["ANY"]:
                    cb = QComboBox()
                    values_str = [str(x) for x in values]
                    cb.addItems(values_str)
                    cb.setCurrentText(str(value))
                    self._ui.options_widget.setItemWidget(item, 1, cb)
            except Exception as e:
                Logger().debug(f"Error while gettings options: {str(e)}")
        self._ui.options_widget.resizeColumnToContents(1)
        self._ui.options_widget.resizeColumnToContents(0)
        self._ui.options_widget.itemDoubleClicked.connect(self.onTreeWidgetItemDoubleClicked)

    def onTreeWidgetItemDoubleClicked(self, item):
        self._ui.options_widget.openPersistentEditor(item, 1)

    def on_options_query(self, conan_ref: str):
        try:
            self._available_options, self._default_options = \
            app.conan_api.get_options_with_default_values(ConanRef.loads(conan_ref))
        except Exception:
            return

    def on_auto_install_check(self):
        enabled = True
        if self._ui.auto_install_check_box.isChecked():
            enabled = False
        self._ui.profile_cbox.setEnabled(enabled)
        self._ui.options_widget.setEnabled(enabled)
        self._ui.update_check_box.setEnabled(enabled)

    def adjust_to_size(self):
        """ Expands the dialog to the length of the install ref text.
        (Somehow the dialog sets a much smaller size then it should via expanding size policy and layout.)
        """
        self._ui.conan_ref_line_edit.adjustSize()
        self.adjustSize()
        h_offset = (self.size() - self._ui.conan_ref_line_edit.size()).width()  # type: ignore
        width = self._ui.conan_ref_line_edit.fontMetrics().boundingRect(self._ui.conan_ref_line_edit.text()).width()
        if width < 250:
            width = 250
        self.resize(QSize(width + h_offset + 15, self.height()))  # 15 margin

    def on_install(self):
        ref_text = self._ui.conan_ref_line_edit.text()
        update_check_state = False
        if self._ui.update_check_box.checkState() == Qt.CheckState.Checked:
            update_check_state = True
    
        auto_install_checked = False
        options = {}
        if self._ui.auto_install_check_box.checkState() == Qt.CheckState.Checked:
            auto_install_checked = True
        else:
            # options from selection
            options = self.get_user_options()
        self._conan_selected_install = {"ref_pkg_id": ref_text,
                                        "settings": {},
                                        "profile": self.get_selected_profile(),
                                        "options": options, "update": update_check_state,
                                        "auto_install": auto_install_checked}
        if not self._capture_install_info:
            app.conan_worker.put_ref_in_install_queue(self._conan_selected_install, 
                                                      self.emit_conan_pkg_signal_callback)

    def emit_conan_pkg_signal_callback(self, conan_ref: str, pkg_id: str):
        if not self.pkg_installed_signal:
            return
        if not pkg_id:
            self.conan_diff_requested.emit(conan_ref)
        self.pkg_installed_signal.emit(conan_ref, pkg_id)

    def show_package_diffs(self, conan_ref):
        # installation failed
        try:
            dialog = PkgDiffDialog(self)
            dialog.set_left_content(self._conan_selected_install)
            available_refs = app.conan_api.get_remote_pkgs_from_ref(ConanRef.loads(conan_ref), None)
            dialog.set_right_content(available_refs[0])
            dialog.update_diff()
            dialog.show()
        except Exception as e:
            Logger().error(str(e))

    def on_set_default_install_profile(self):
        selected_profile = self.get_selected_profile()
        app.active_settings.set(DEFAULT_INSTALL_PROFILE, selected_profile)
        # re-select after clear
        self.load_profiles()
        self._ui.profile_cbox.setCurrentText(selected_profile + self.MARK_AS_DEFAULT_INSTALL_PROFILE)

    def get_selected_profile(self) -> str:
        selected_profile = self._ui.profile_cbox.currentText()
        return selected_profile.rstrip(self.MARK_AS_DEFAULT_INSTALL_PROFILE)

    def get_user_options(self) -> ConanOptions:
        options = {}
        self._ui.options_widget.updateEditorData()
        for i in range(0, self._ui.options_widget.topLevelItemCount()):
            item = self._ui.options_widget.topLevelItem(i)
            widget = self._ui.options_widget.itemWidget(item, 1)
            value = item.data(1, 0)
            if isinstance(widget, QComboBox):
                value = widget.currentText()
            options[item.data(0, 0)] = value
        return options

    def get_selected_install_info(self):
        return self._conan_selected_install