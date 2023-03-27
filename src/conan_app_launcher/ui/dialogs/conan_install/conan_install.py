from typing import Optional

import conan_app_launcher.app as app
from conan_app_launcher.app.logger import Logger  # using global module pattern
from conan_app_launcher.core.conan_worker import ConanWorkerElement
from conan_app_launcher.ui.common import get_themed_asset_icon
from PySide6.QtCore import QSize, Qt, SignalInstance
from PySide6.QtWidgets import QDialog, QWidget, QTreeWidgetItem, QComboBox

from conan_app_launcher.core.conan_common import ConanRef


class ConanInstallDialog(QDialog):
    def __init__(self, parent: Optional[QWidget], conan_full_ref: str, pkg_installed_signal: Optional[SignalInstance] = None, lock_ref=False):
        """ conan_ref can be in full ref format with <ref>:<id> """
        super().__init__(parent)
        from .conan_install_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        self.pkg_installed_signal = pkg_installed_signal

        # init search bar
        icon = get_themed_asset_icon("icons/download_pkg.svg", True)
        self.setWindowIcon(icon)
        self._ui.conan_ref_line_edit.validator_enabled = False
        self._ui.conan_ref_line_edit.textChanged.connect(self.toggle_auto_install_on_pkg_ref)
        if lock_ref:
            self._ui.conan_ref_line_edit.setEnabled(False)
        self._ui.button_box.accepted.connect(self.on_install)
        self._profiles = app.conan_api.get_profiles()
        options = []
        conan_ref = ""
        try:
            conan_ref = conan_full_ref.split(":")[0]
            self._ref_info = app.conan_api.conan.info(
                app.conan_api.generate_canonical_ref(ConanRef.loads(conan_ref)))
            # TODO: CONAN V2
            options = self._ref_info[0].root.dependencies[0].dst.conanfile.options.items() # type: ignore
        except Exception:
            Logger().warning("Can't determine options of " + conan_ref)
        # doing this after connecting toggle_auto_install_on_pkg_ref initializes it correctly
        self._ui.conan_ref_line_edit.setText(conan_full_ref)
        self._ui.profile_cbox.addItems(self._profiles)
        for name, value in options:
            item = QTreeWidgetItem(self._ui.options_widget)
            item.setData(0, 0, name)
            item.setData(1, 0, value)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Qt.ItemFlag.ItemIsEditable |
            self._ui.options_widget.addTopLevelItem(item)
            # TODO: selection
            try:
                values = self._ref_info[0].root.dependencies[0].dst.conanfile.options._data[name]._possible_values
                if isinstance(values, list):
                    cb = QComboBox()
                    cb.addItems(values)
                    cb.setCurrentText(value)
                    self._ui.options_widget.setItemWidget(item, 1, cb)
            except:
                pass
        self._ui.options_widget.resizeColumnToContents(1)
        self._ui.options_widget.resizeColumnToContents(0)
        self._ui.options_widget.itemDoubleClicked.connect(self.onTreeWidgetItemDoubleClicked)  
        # disable profile and options on activating this
        self._ui.auto_install_check_box.clicked.connect(self.on_auto_install_check)
        self.adjust_to_size()


    def onTreeWidgetItemDoubleClicked(self, item):
        self._ui.options_widget.openPersistentEditor(item, 1)

    def on_auto_install_check(self):
        enabled = True
        if self._ui.auto_install_check_box.isChecked():
            enabled = False
        self._ui.profile_cbox.setEnabled(enabled)
        self._ui.options_widget.setEnabled(enabled)
        self._ui.additional_args_line_edit.setEnabled(enabled)
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

    def toggle_auto_install_on_pkg_ref(self, text: str):
        if ":" in text:  # if a package id is given, auto install does not make sense
            self._ui.auto_install_check_box.setEnabled(False)
        else:
            self._ui.auto_install_check_box.setEnabled(True)

    def on_install(self):
        ref_text = self._ui.conan_ref_line_edit.text()
        update_check_state = False
        if self._ui.update_check_box.checkState() == Qt.CheckState.Checked:
            update_check_state = True
    
        auto_install_checked = False
        settings = {}
        options = {}
        if self._ui.auto_install_check_box.checkState() == Qt.CheckState.Checked:
            auto_install_checked = True
        else:
            # settings from profile
            settings = app.conan_api.get_profile_settings(self._ui.profile_cbox.currentText())
            # options from selection
            options = self.get_user_options()
        conan_worker_element: ConanWorkerElement = {"ref_pkg_id": ref_text, "settings": settings,
                                                    "options": options, "update": update_check_state,
                                                    "auto_install": auto_install_checked}

        app.conan_worker.put_ref_in_install_queue(conan_worker_element, self.emit_conan_pkg_signal_callback)

    def emit_conan_pkg_signal_callback(self, conan_ref: str, pkg_id: str):
        if not self.pkg_installed_signal:
            return
        self.pkg_installed_signal.emit(conan_ref, pkg_id)


    def get_user_options(self):
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