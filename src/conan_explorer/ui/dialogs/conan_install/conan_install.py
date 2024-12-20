from typing import Optional

from PySide6.QtCore import QSize, Qt, Signal, SignalInstance
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHeaderView,
    QMessageBox,
    QTreeWidgetItem,
    QWidget,
)

import conan_explorer.app as app
from conan_explorer.app import LoaderGui
from conan_explorer.app.logger import Logger  # using global module pattern
from conan_explorer.conan_wrapper.conan_worker import ConanWorkerElement
from conan_explorer.conan_wrapper.types import ConanOptions, ConanPkg, ConanRef
from conan_explorer.settings import DEFAULT_INSTALL_PROFILE
from conan_explorer.ui.common import get_themed_asset_icon
from conan_explorer.ui.dialogs.pkg_diff.diff import PkgDiffDialog


class ConanInstallDialog(QDialog):
    MARK_AS_DEFAULT_INSTALL_PROFILE = " *"
    MIN_WITDH = 300
    installation_failed: SignalInstance = Signal(str)  # type: ignore - conan_ref

    def __init__(
        self,
        parent: Optional[QWidget],
        conan_full_ref: str,
        pkg_installed_signal: Optional[SignalInstance] = None,
        lock_reference=False,
        capture_install_info=False,
    ):
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
        self._pkg_diff_items = []
        # style
        icon = get_themed_asset_icon("icons/download_pkg.svg", True)
        self.setWindowIcon(icon)

        # init search bar
        self._ui.conan_ref_line_edit.validator_enabled = True
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

        if capture_install_info:  # auto install makes no sense in this mode
            self.hide_for_install_info()
            self.resize(self.width(), self.height() - 150)

        # disable profile and options on activating this
        self._ui.auto_install_check_box.clicked.connect(self.on_auto_install_check)
        self._ui.set_default_install_profile_button.clicked.connect(
            self.on_set_default_install_profile
        )
        self.installation_failed.connect(self.on_installation_failed)

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
        loader = LoaderGui(self)
        loader.load(
            self, self.on_options_query, (conan_ref,), loading_text="Loading options..."
        )
        loader.wait_for_finished()
        options = loader.return_value
        if options is None:
            return
        available_options, default_options = options

        # doing this after connecting toggle_auto_install_on_pkg_ref initializes it correctly
        for name, value in default_options.items():
            item = QTreeWidgetItem(self._ui.options_widget)
            item.setData(0, 0, name)
            item.setData(1, 0, str(value))
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Qt.ItemFlag.ItemIsEditable |
            self._ui.options_widget.addTopLevelItem(item)
            try:
                values = available_options[name]
                if isinstance(values, list) and values != ["ANY"]:
                    cb = QComboBox()
                    values_str = [str(x) for x in values]
                    cb.addItems(values_str)
                    cb.setCurrentText(str(value))
                    self._ui.options_widget.setItemWidget(item, 1, cb)
            except Exception as e:
                Logger().debug("Error while gettings options: %s", str(e))
        self._ui.options_widget.resizeColumnToContents(1)
        self._ui.options_widget.resizeColumnToContents(0)
        self._ui.options_widget.itemDoubleClicked.connect(self.onTreeWidgetItemDoubleClicked)

    def onTreeWidgetItemDoubleClicked(self, item):
        self._ui.options_widget.openPersistentEditor(item, 1)

    def on_options_query(self, conan_ref: str):
        try:
            return app.conan_api.get_options_with_default_values(ConanRef.loads(conan_ref))
        except Exception:
            return {}, {}

    def on_auto_install_check(self):
        enabled = True
        if self._ui.auto_install_check_box.isChecked():
            enabled = False
        self._ui.profile_cbox.setEnabled(enabled)
        self._ui.options_widget.setEnabled(enabled)
        self._ui.update_check_box.setEnabled(enabled)

    def adjust_to_size(self):
        """Expands the dialog to the length of the install ref text.
        (Somehow the dialog sets a much smaller size then it should via expanding size policy and layout.)
        """
        self._ui.conan_ref_line_edit.adjustSize()
        self.adjustSize()
        h_offset = (self.size() - self._ui.conan_ref_line_edit.size()).width()  # type: ignore
        width = (
            self._ui.conan_ref_line_edit.fontMetrics()
            .boundingRect(self._ui.conan_ref_line_edit.text())
            .width()
        )
        if width < self.MIN_WITDH:
            width = self.MIN_WITDH
        self.resize(QSize(width + h_offset + 15, self.height()))  # 15 margin
        self._ui.options_widget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

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
        self._conan_selected_install = {
            "ref_pkg_id": ref_text,
            "settings": {},
            "profile": self.get_selected_profile(),
            "options": options,
            "update": update_check_state,
            "auto_install": auto_install_checked,
        }
        if not self._capture_install_info:
            app.conan_worker.put_ref_in_install_queue(
                self._conan_selected_install, self.emit_conan_pkg_signal_callback
            )

    def emit_conan_pkg_signal_callback(self, conan_ref: str, pkg_id: str):
        if not pkg_id:
            self.installation_failed.emit(conan_ref)
            return
        if not self.pkg_installed_signal:
            return
        self.pkg_installed_signal.emit(conan_ref, pkg_id)

    def on_installation_failed(self, conan_ref: str):
        # installation failed
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Compare packages")
        message_box.setText(
            (
                f"Installation of '{conan_ref}' failed.\n"
                "Do you want compare this package to the available packages on the remotes?"
            )
        )
        sb = QMessageBox.StandardButton
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setStandardButtons(sb.Yes | sb.Cancel)
        reply = message_box.exec()
        if reply == sb.Yes:
            self.show_package_diffs(conan_ref)
        message_box.close()

    def get_all_pkgs(self, conan_ref: str):
        return app.conan_api.get_remote_pkgs_from_ref(ConanRef.loads(conan_ref), "all")

    def show_package_diffs(self, conan_ref: str):
        try:
            loader = LoaderGui(self)
            loader.load(
                self, self.get_all_pkgs, (conan_ref,), loading_text="Getting all packages..."
            )
            loader.wait_for_finished()
            items = loader.return_value
            if not items:
                return
            if len(items) < 2:
                return
            if not self._conan_selected_install:
                return
            dialog = PkgDiffDialog(self.parent())
            installed_pkg_info: ConanPkg = {
                "id": "User input",
                "settings": app.conan_api.get_profile_settings(
                    self._conan_selected_install["profile"]
                ),
                "options": self._conan_selected_install["options"],
                "requires": [],
                "outdated": False,
            }
            dialog.add_diff_item(installed_pkg_info)
            for item in items:
                dialog.add_diff_item(item)
            dialog.show()
        except Exception as e:
            Logger().error(str(e))

    def on_set_default_install_profile(self):
        selected_profile = self.get_selected_profile()
        app.active_settings.set(DEFAULT_INSTALL_PROFILE, selected_profile)
        # re-select after clear
        self.load_profiles()
        self._ui.profile_cbox.setCurrentText(
            selected_profile + self.MARK_AS_DEFAULT_INSTALL_PROFILE
        )

    def get_selected_profile(self) -> str:
        selected_profile = self._ui.profile_cbox.currentText()
        return selected_profile.rstrip(self.MARK_AS_DEFAULT_INSTALL_PROFILE)

    def get_user_options(self) -> ConanOptions:
        options = {}
        self._ui.options_widget.updateEditorData()
        for i in range(0, self._ui.options_widget.topLevelItemCount()):
            item = self._ui.options_widget.topLevelItem(i)
            if not item:
                continue
            widget = self._ui.options_widget.itemWidget(item, 1)
            value = item.data(1, 0)
            if isinstance(widget, QComboBox):
                value = widget.currentText()
            options[item.data(0, 0)] = value
        return options

    def get_selected_install_info(self):
        return self._conan_selected_install
