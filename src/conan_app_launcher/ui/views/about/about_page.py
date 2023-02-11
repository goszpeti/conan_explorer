from pathlib import Path
from conan_app_launcher import APP_NAME, AUTHOR, REPO_URL, __version__, asset_path
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QFrame, QLabel, QSizePolicy, QSpacerItem,
                             QVBoxLayout)
from conan_app_launcher.ui.fluent_window.plugins import PluginInterface

from jinja2 import Template

class AboutPage(PluginInterface):
    """ Defines About page """
    html_content = f"""

    """

    def __init__(self, parent, base_signals):
        super().__init__(parent, base_signals=base_signals)
        from .about_ui import Ui_Form
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.setObjectName("about_page")
        icon = QIcon(str(asset_path / "icons" / "icon.ico"))
        self._ui.logo_label.setPixmap(icon.pixmap(100, 100))

        with open(Path(__file__).parent / "about_text.html", "r") as fd:
            template = Template(fd.read())
        html_content = template.render(app_name=APP_NAME, version=__version__, 
                                        author=AUTHOR, repo_url=REPO_URL)

        self._ui.about_label.setText(html_content)
