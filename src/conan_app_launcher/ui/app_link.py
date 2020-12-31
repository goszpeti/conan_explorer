
from conan_app_launcher.components import AppConfigEntry, run_file
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_VERSIONS, Settings)
from conan_app_launcher.ui.qt.app_button import AppButton
from PyQt5 import QtCore, QtWidgets
from .qt import app_edit

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class AppLink(QtWidgets.QVBoxLayout):
    def __init__(self, parent: QtWidgets.QTabWidget, app: AppConfigEntry, gui_update_signal: QtCore.pyqtSignal):
        super().__init__(parent)
        self._app_info = app
        self._app_button = AppButton(parent, app.icon)
        self._app_button.setFixedHeight(200)
        self._app_name_label = QtWidgets.QLabel(parent)
        self._app_version_cbox = QtWidgets.QComboBox(parent)
        self._app_channel_cbox = QtWidgets.QComboBox(parent)
        self._gui_update_signal = gui_update_signal

        self.setObjectName(parent.objectName() + app.name)  # to find it for tests
        self.setSpacing(5)

        # size policies
        self.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                            QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self._app_button.setSizePolicy(size_policy)

        self._app_button.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._app_button.setToolTip(str(app.conan_ref))

        self.addWidget(self._app_button)
        # self._app_name_label.setSizePolicy(size_policy)
        self._app_name_label.setAlignment(Qt.AlignCenter)
        self._app_name_label.setText(app.name)
        self.addWidget(self._app_name_label)

        self._app_version_cbox.addItem(app.conan_ref.version)
        self._app_version_cbox.setDisabled(True)
        self._app_version_cbox.setDuplicatesEnabled(False)
        self.addWidget(self._app_version_cbox)

        self._app_channel_cbox.addItem(app.conan_ref.channel)
        self._app_channel_cbox.setDisabled(True)
        self._app_channel_cbox.setDuplicatesEnabled(False)
        self.addWidget(self._app_channel_cbox)

        self._app_button.clicked.connect(self.app_clicked)
        self._app_version_cbox.currentIndexChanged.connect(self.version_selected)
        self._app_channel_cbox.currentIndexChanged.connect(self.channel_selected)

        # add right click context menu actions
        self._app_button.setContextMenuPolicy(Qt.ActionsContextMenu)
        edit_action = QtWidgets.QAction("Edit", self)
        edit_action.triggered.connect(self.disp_edit_dialog)
        self._app_button.addAction(edit_action)

    def disp_edit_dialog(self):
        # save dialog, otherwise it will close
        self.dialog = QtWidgets.QDialog()
        self.dialog.setModal(True)
        self._edit_dialog = app_edit.Ui_Dialog()
        self._edit_dialog.setupUi(self.dialog)

        # fill up current info
        self._edit_dialog.name_line_edit.setText(self._app_info.name)
        self._edit_dialog.conan_ref_line_edit.setText(str(self._app_info.conan_ref))
        self._edit_dialog.exec_path_line_edit.setText(self._app_info.app_data["executable"])
        self._edit_dialog.is_console_app_checkbox.setChecked(self._app_info.is_console_application)
        self._edit_dialog.icon_line_edit.setText(self._app_info.app_data["icon"])
        self._edit_dialog.args_line_edit.setText(self._app_info.args)

        conan_options_text = ""
        for option in self._app_info.conan_options:
            conan_options_text += f"{option}={self._app_info.conan_options.get(option)}\n"
        self._edit_dialog.conan_opts_text_edit.setText(conan_options_text)

        self._edit_dialog.button_box.accepted.connect(self.save_edited_dialog)
        self.dialog.show()

    def save_edited_dialog(self):
        self._edit_dialog

    def update_entry(self, settings: Settings):
        # set icon and ungrey if package is available
        if self._app_info.executable.is_file():
            self._app_button.set_icon(self._app_info.icon)
            self._app_button.ungrey_icon()

        if len(self._app_info.versions) > 0 and self._app_version_cbox.count() != len(self._app_info.versions):  # on nums changed
            self._app_version_cbox.clear()
            self._app_channel_cbox.clear()
            self._app_version_cbox.addItems(self._app_info.versions)
            self._app_channel_cbox.addItems(self._app_info.channels)
            try:  # TODO
                self._app_version_cbox.setCurrentIndex(self._app_info.versions.index(self._app_info.version))
                self._app_channel_cbox.setCurrentIndex(self._app_info.channels.index(self._app_info.channel))
            except Exception:
                pass
            self._app_version_cbox.setDisabled(False)
            self._app_channel_cbox.setDisabled(False)

        if settings.get(DISPLAY_APP_VERSIONS):
            self._app_version_cbox.show()
        else:
            self._app_version_cbox.hide()
        if settings.get(DISPLAY_APP_CHANNELS):
            self._app_channel_cbox.show()
        else:
            self._app_channel_cbox.hide()

    def app_clicked(self):
        """ Callback for opening the executable on click """
        run_file(self._app_info.executable, self._app_info.is_console_application, self._app_info.args)

    def version_selected(self, index):
        if not self._app_version_cbox.isEnabled():
            return
        if index == -1:  # on clear
            return
        if self._app_info.version == self._app_version_cbox.currentText():  # no change
            return
        self._app_button.grey_icon()
        self._app_info.version = self._app_version_cbox.currentText()

    def channel_selected(self, index):
        if not self._app_channel_cbox.isEnabled():
            return
        if index == -1:
            return
        if self._app_info.channel == self._app_channel_cbox.currentText():
            return
        self._app_button.grey_icon()
        self._app_info.channel = self._app_channel_cbox.currentText()
