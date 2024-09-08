from typing import Optional
from PySide6.QtWidgets import QDialog, QWidget, QStyle

class QuestionWithItemListDialog(QDialog):

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        from .qwil_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        pixmapi = getattr(QStyle, "SP_MessageBoxQuestion")
        if pixmapi:
            icon = self.style().standardIcon(pixmapi)
            self._ui.icon.setPixmap(icon.pixmap(40,40))
