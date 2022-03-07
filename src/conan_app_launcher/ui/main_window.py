from pathlib import Path
from shutil import rmtree
from typing import Optional
from ctypes.wintypes import MSG
import ctypes
import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher import (ADD_APP_LINK_BUTTON, ADD_TAB_BUTTON, PathLike,
                                user_save_path)
from conan_app_launcher.core.conan import ConanCleanup
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_USERS,
                                         DISPLAY_APP_VERSIONS, FONT_SIZE,
                                         GUI_STYLE, GUI_STYLE_DARK,
                                         GUI_STYLE_LIGHT, LAST_CONFIG_FILE)
from conan_app_launcher.ui.common import QtLoaderObject
from conan_app_launcher.ui.common.icon import get_themed_asset_image
from conan_app_launcher.ui.common.theming import activate_theme
from conan_app_launcher.ui.dialogs.conan_search import ConanSearchDialog
from conan_app_launcher.ui.model import UiApplicationModel
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtCore import QPropertyAnimation
from .dialogs.about_dialog import AboutDialog
from .views.app_grid import AppGridView
from .views.package_explorer import LocalConanPackageExplorer
QPoint = QtCore.QPoint
QRect = QtCore.QRect
Qt = QtCore.Qt
WM_SYSCOMMAND = 274
SC_MOVE = 61456
HTCAPTION = 2




class MainWindow(QtWidgets.QMainWindow):
    """ Instantiates MainWindow and holds all UI objects """
    conan_pkg_installed = QtCore.pyqtSignal(str, str)  # conan_ref, pkg_id
    conan_pkg_removed = QtCore.pyqtSignal(str, str)  # conan_ref, pkg_id

    display_versions_changed = QtCore.pyqtSignal()
    display_channels_changed = QtCore.pyqtSignal()
    display_users_changed = QtCore.pyqtSignal()

    new_message_logged = QtCore.pyqtSignal(str)  # str arg is the message




    def __init__(self, qt_app: QtWidgets.QApplication):
        super().__init__()
        self._qt_app = qt_app
        self.model = UiApplicationModel(self.conan_pkg_installed, self.conan_pkg_removed)
        self.menu_buttons = {}
        current_dir = Path(__file__).parent
        self.ui = uic.loadUi(current_dir / "main_window.ui", baseinstance=self)
        self.stacked_widget: QtWidgets.QStackedWidget

        self._about_dialog = AboutDialog(self)
        self.load_icons()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint |
                            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        #QtWin.enableBlurBehindWindow(self)
        GWL_STYLE = -16
        WS_MAXIMIZEBOX = 65536
        WS_CAPTION = 12582912
        CS_DBLCLKS = 8
        WS_THICKFRAME = 262144
        self.press_control = 0

        style = ctypes.windll.user32.GetWindowLongA(int(self.winId()), GWL_STYLE)

        WS_BORDER = 8388608
        WS_DLGFRAME = 4194304
        WS_SYSMENU = 524288
        WS_CHILD = 1073741824

        #newstyle = style & ~(WS_CAPTION) | WS_THICKFRAME | WS_MAXIMIZEBOX | CS_DBLCLKS

        ctypes.windll.user32.SetWindowLongA(
            int(self.winId()),
            GWL_STYLE,
            style
            | WS_BORDER
            | WS_MAXIMIZEBOX
            | WS_CAPTION
            | CS_DBLCLKS
            | WS_THICKFRAME
        )
        # TODO do transparency later
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.98)
        effect = QtWidgets.QGraphicsDropShadowEffect()
        effect.setOffset(0, 0)
        effect.setColor(QtGui.QColor(68, 68, 68))
        effect.setBlurRadius(10)
        #self.setGraphicsEffect(effect)
        
        self.minimized = False
#        self.setContentsMargins(5,5,5,5)


        # get theme color
        from winreg import OpenKey, ConnectRegistry, HKEY_CURRENT_USER, QueryValueEx
        reg = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(reg, r"Control Panel\Colors")
        value = QueryValueEx(key, "Hilight")[0] # Windows Theme Hilight color for border color in rgb

        def moveWindow(event):
            # IF MAXIMIZED CHANGE TO NORMAL
            # global state 
            # if self.minimized == True:
            #     self.maximize_restore()

            # # MOVE WINDOW
            # if event.buttons() == Qt.LeftButton:
            #     self.move(self.pos() + event.globalPos() - self.dragPos)
            #     self.dragPos = event.globalPos()
            #     event.accept()
            if self.cursor().shape() != Qt.ArrowCursor:
                self.eventFilter(None, event)
                return

            ctypes.windll.user32.ReleaseCapture()
            ctypes.windll.user32.SendMessageA(int(self.window().winId()), WM_SYSCOMMAND,
                                          SC_MOVE + HTCAPTION, 0)

        #self.ui.top_center_right_frame.mouseMoveEvent = moveWindow
        self.ui.top_frame.mouseMoveEvent = moveWindow

        # connect logger to console widget to log possible errors at init
        Logger.init_qt_logger(self.new_message_logged)
        self.new_message_logged.connect(self.write_log)

        #self.app_grid = AppGridView(self, self.model.app_grid)
        #self.local_package_explorer = LocalConanPackageExplorer(self)
        self.search_dialog: Optional[ConanSearchDialog] = ConanSearchDialog(None, self)


        # initialize view user settings
        # self.ui.menu_toggle_display_versions.setChecked(app.active_settings.get_bool(DISPLAY_APP_VERSIONS))
        # self.ui.menu_toggle_display_users.setChecked(app.active_settings.get_bool(DISPLAY_APP_USERS))
        # self.ui.menu_toggle_display_channels.setChecked(app.active_settings.get_bool(DISPLAY_APP_CHANNELS))
        # dark_mode_enabled = True if app.active_settings.get_string(GUI_STYLE) == GUI_STYLE_DARK else False
        # self.ui.menu_enable_dark_mode.setChecked(dark_mode_enabled)

        # self.ui.menu_about_action.triggered.connect(self._about_dialog.show)
        # self.ui.menu_open_config_file.triggered.connect(self.open_config_file_dialog)
        # self.ui.menu_search_in_remotes.triggered.connect(self.open_conan_search_dialog)
        # self.ui.menu_search_in_remotes.setShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_F))
        # self.ui.menu_toggle_display_versions.triggered.connect(self.display_versions_setting_toggled)
        # self.ui.menu_toggle_display_users.triggered.connect(self.apply_display_users_setting_toggled)
        # self.ui.menu_toggle_display_channels.triggered.connect(self.display_channels_setting_toggled)
        # self.ui.menu_enable_dark_mode.triggered.connect(self.on_theme_changed)
        # self.ui.menu_increase_font_size.triggered.connect(self.on_font_size_increased)
        # self.ui.menu_increase_font_size.setShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_Plus))
        # self.ui.menu_decrease_font_size.triggered.connect(self.on_font_size_decreased)
        # self.ui.menu_decrease_font_size.setShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_Minus))

        # self.ui.menu_cleanup_cache.triggered.connect(self.open_cleanup_cache_dialog)
        # self.ui.menu_remove_locks.triggered.connect(app.conan_api.remove_locks)
        
        # self.ui.main_toolbox.currentChanged.connect(self.on_main_view_changed)
        self.ui.toggle_left_menu_button.clicked.connect(lambda: self.toggleMenu(220, True))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_themed_asset_image("icons/grid.png")),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addNewMenu("App Grid", "app_grid_button", icon, True, self.search_dialog)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_themed_asset_image("icons/opened_folder.png")),
                               QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addNewMenu("Local Package Explorer", "lcl_pkg_expl_btn", icon, True, self.search_dialog)
        icon.addPixmap(QtGui.QPixmap(get_themed_asset_image("icons/search_packages.png")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addNewMenu("Conan Search", "conan_search_btn", icon, True, self.search_dialog)

        self.ui.settings_button.clicked.connect(lambda: self.toggleRightMenu(220, True))

        #self.addNewMenu(self, "HOME", "btn_home", "url(:/16x16/icons/16x16/cil-home.png)", True)
        #self.addNewMenu(self, "HOME", "btn_home", "url(:/16x16/icons/16x16/cil-home.png)", False)

    def addNewMenu(self, name, objName, icon, isTopMenu, page_Widget):
        button = QtWidgets.QPushButton(self)
        button.setObjectName(objName)
        sizePolicy3 = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy3)
        button.setMinimumSize(QtCore.QSize(0, 70))
        button.setLayoutDirection(Qt.LeftToRight)
        button.setToolTip(name)
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(32, 32))
        button.setStyleSheet("text-align:middle;")


        button.clicked.connect(self.switch_page)
        self.menu_buttons[name] = button

        if isTopMenu:
           self.ui.menu_top_subframe.layout().addWidget(button)
        else:
            self.ui.menu_bottom_subframe.layout().addWidget(button)

        self.stacked_widget.addWidget(page_Widget)

    def switch_page(self):
        # GET BT CLICKED
        btnWidget = self.sender()

        # PAGE HOME
        if btnWidget.objectName() == "app_grid_button":

            self.ui.stacked_widget.setCurrentWidget(self.search_dialog)
            # UIFunctions.resetStyle(self, "btn_home")
            # UIFunctions.labelPage(self, "Home")
            # parametrize
            btnWidget.styleSheet()
            btnWidget.setStyleSheet(btnWidget.styleSheet() + ";background-color: #B7B7B7")

        # PAGE NEW USER
        if btnWidget.objectName() == "lcl_pkg_expl_btn":
            self.ui.stacked_widget.setCurrentWidget(self.ui.page)
            # UIFunctions.resetStyle(self, "btn_new_user")
            # UIFunctions.labelPage(self, "New User")
            #btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

        # PAGE WIDGETS
        if btnWidget.objectName() == "btn_widgets":
            self.ui.stacked_widget.setCurrentWidget(self.ui.page_widgets)
            # UIFunctions.resetStyle(self, "btn_widgets")
            # UIFunctions.labelPage(self, "Custom Widgets")
            #btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

    def toggleMenu(self, maxWidth, enable):
        if enable:
            # GET WIDTH
            width = self.ui.left_menu_frame.width()
            maxExtend = maxWidth
            standard = 70

            # SET MAX WIDTH
            if width == 70:
                widthExtended = maxExtend
                maximize = True
            else:
                widthExtended = standard
                maximize = False

            # ANIMATION
            self.animation = QPropertyAnimation(self.ui.left_menu_frame, b"minimumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation2 = QPropertyAnimation(self.ui.toggle_left_menu_frame, b"minimumWidth")
            self.animation2.setDuration(200)
            self.animation2.setStartValue(width)
            self.animation2.setEndValue(widthExtended)
            self.animation2.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation.start()
            self.animation2.start()

            # TODO set Button texts
            for name, button in self.menu_buttons.items():
                if maximize:
                    button.setText(name)
                    button.setStyleSheet("text-align:left;")

                else:
                    button.setText("")
                    button.setStyleSheet("text-align:middle;")


    def toggleRightMenu(self, maxWidth, enable):
        if enable:
            # GET WIDTH
            width = self.ui.right_menu_frame.width()
            maxExtend = maxWidth
            standard = 0

            # SET MAX WIDTH
            if width == 0:
                    widthExtended = maxExtend
                    maximize = True
            else:
                widthExtended = standard
                maximize = False

            # ANIMATION
            self.animation = QPropertyAnimation(self.ui.right_menu_frame, b"minimumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation.start()



    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
        # if event.buttons() == Qt.LeftButton:
        #     print('Mouse click: LEFT CLICK')
        # if event.buttons() == Qt.RightButton:
        #     print('Mouse click: RIGHT CLICK')
        # if event.buttons() == Qt.MidButton:
        #     print('Mouse click: MIDDLE BUTTON')

    def nativeEvent(self, eventType, message):
        msg = MSG.from_address(message.__int__())
        if msg.message == 131:
            return True, 0
        return QtWidgets.QWidget.nativeEvent(self, eventType, message)

    def eventFilter(self, obj, e):
        #hovermoveevent
        if e.type() == 129:
            if self.press_control == 0:
                self.pos_control(e)  # cursor position control for cursor shape setup

        #mousepressevent
        if e.type() == 2:
            self.press_control = 1
            self.origin = self.mapToGlobal(e.pos())
            self.ori_geo = self.geometry()

        #mousereleaseevent
        if e.type() == 3:

            self.press_control = 0
            self.pos_control(e)

        #mosuemoveevent
        if e.type() == 5:
            if self.cursor().shape() != Qt.ArrowCursor:
                self.resizing(self.origin, e, self.ori_geo, self.value)

        return super().eventFilter(obj, e)

    def pos_control(self, e):
        rect = self.rect()
        top_left = rect.topLeft()
        top_right = rect.topRight()
        bottom_left = rect.bottomLeft()
        bottom_right = rect.bottomRight()
        pos = e.pos()

        #top catch
        if pos in QRect(QPoint(top_left.x()+5, top_left.y()), QPoint(top_right.x()-5, top_right.y()+5)):
            self.setCursor(Qt.SizeVerCursor)
            self.value = 1

        #bottom catch
        elif pos in QRect(QPoint(bottom_left.x()+5, bottom_left.y()), QPoint(bottom_right.x()-5, bottom_right.y()-5)):
            self.setCursor(Qt.SizeVerCursor)
            self.value = 2

        #right catch
        elif pos in QRect(QPoint(top_right.x()-5, top_right.y()+5), QPoint(bottom_right.x(), bottom_right.y()-5)):
            self.setCursor(Qt.SizeHorCursor)
            self.value = 3

        #left catch
        elif pos in QRect(QPoint(top_left.x()+5, top_left.y()+5), QPoint(bottom_left.x(), bottom_left.y()-5)):
            self.setCursor(Qt.SizeHorCursor)
            self.value = 4

        #top_right catch
        elif pos in QRect(QPoint(top_right.x(), top_right.y()), QPoint(top_right.x()-5, top_right.y()+5)):
            self.setCursor(Qt.SizeBDiagCursor)
            self.value = 5

        #botom_left catch
        elif pos in QRect(QPoint(bottom_left.x(), bottom_left.y()), QPoint(bottom_left.x()+5, bottom_left.y()-5)):
            self.setCursor(Qt.SizeBDiagCursor)
            self.value = 6

        #top_left catch
        elif pos in QRect(QPoint(top_left.x(), top_left.y()), QPoint(top_left.x()+5, top_left.y()+5)):
            self.setCursor(Qt.SizeFDiagCursor)
            self.value = 7

        #bottom_right catch
        elif pos in QRect(QPoint(bottom_right.x(), bottom_right.y()), QPoint(bottom_right.x()-5, bottom_right.y()-5)):
            self.setCursor(Qt.SizeFDiagCursor)
            self.value = 8

        #default
        else:
            self.setCursor(Qt.ArrowCursor)

    def resizing(self, ori, e, geo, value):
        #top_resize
        if self.value == 1:
            last = self.mapToGlobal(e.pos())-ori
            first = geo.height()
            first -= last.y()
            Y = geo.y()
            Y += last.y()

            if first > self.minimumHeight():
                self.setGeometry(geo.x(), Y, geo.width(), first)
            return

        #bottom_resize
        if self.value == 2:
            last = self.mapToGlobal(e.pos())-ori
            first = geo.height()
            first += last.y()
            self.resize(geo.width(), first)
            return

        #right_resize
        if self.value == 3:
            last = self.mapToGlobal(e.pos())-ori
            first = geo.width()
            first += last.x()
            self.resize(first, geo.height())
            return
        #left_resize
        if self.value == 4:
            last = self.mapToGlobal(e.pos())-ori
            first = geo.width()
            first -= last.x()
            X = geo.x()
            X += last.x()

            if first > self.minimumWidth():
                self.setGeometry(X, geo.y(), first, geo.height())
            return

        #top_right_resize
        if self.value == 5:
            last = self.mapToGlobal(e.pos())-ori
            first_width = geo.width()
            first_height = geo.height()
            first_Y = geo.y()
            first_width += last.x()
            first_height -= last.y()
            first_Y += last.y()

            if first_height > self.minimumHeight():
                self.setGeometry(geo.x(), first_Y, first_width, first_height)
            return
        #bottom_right_resize
        if self.value == 6:
            last = self.mapToGlobal(e.pos())-ori
            first_width = geo.width()
            first_height = geo.height()
            first_X = geo.x()
            first_width -= last.x()
            first_height += last.y()
            first_X += last.x()

            if first_width > self.minimumWidth():
                self.setGeometry(first_X, geo.y(), first_width, first_height)
            return
        #top_left_resize
        if self.value == 7:
            last = self.mapToGlobal(e.pos())-ori
            first_width = geo.width()
            first_height = geo.height()
            first_X = geo.x()
            first_Y = geo.y()
            first_width -= last.x()
            first_height -= last.y()
            first_X += last.x()
            first_Y += last.y()

            if first_height > self.minimumHeight() and first_width > self.minimumWidth():
                self.setGeometry(first_X, first_Y, first_width, first_height)
            return
        #bottom_right_resize
        if self.value == 8:
            last = self.mapToGlobal(e.pos())-ori
            first_width = geo.width()
            first_height = geo.height()
            first_width += last.x()
            first_height += last.y()

            self.setGeometry(geo.x(), geo.y(), first_width, first_height)
            return



    def maximize_restore(self):
        status = self.minimized
        if status == 0:
            self.showMaximized()
            GLOBAL_STATE = 1
            self.ui.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            self.ui.btn_maximize_restore.setToolTip("Restore")
            self.ui.btn_maximize_restore.setIcon(QtGui.QIcon(u":/16x16/icons/16x16/cil-window-restore.png"))
            self.ui.frame_top_btns.setStyleSheet("background-color: rgb(27, 29, 35)")
            self.ui.frame_size_grip.hide()
        else:
            GLOBAL_STATE = 0
            self.showNormal()
            self.resize(self.width()+1, self.height()+1)
            self.ui.horizontalLayout.setContentsMargins(10, 10, 10, 10)
            self.ui.btn_maximize_restore.setToolTip("Maximize")
            self.ui.btn_maximize_restore.setIcon(QtGui.QIcon(u":/16x16/icons/16x16/cil-window-maximize.png"))
            self.ui.frame_top_btns.setStyleSheet("background-color: rgba(27, 29, 35, 200)")
            self.ui.frame_size_grip.show()

    def closeEvent(self, event):  # override QMainWindow
        """ Remove qt logger, so it doesn't log into a non existant object """
        try:
            self.new_message_logged.disconnect(self.write_log)
        except Exception:
            # Sometimes the closeEvent is called twice and disconnect errors.
            pass
        Logger.remove_qt_logger()
        super().closeEvent(event)

    # def resizeEvent(self, a0: QtGui.QResizeEvent):
    #     if a0.oldSize().width() == -1:  # initial resize - can be skipped
    #         return
        # sizes = self.content_footer_splitter.sizes()
        # self.content_footer_splitter.setSizes(sizes)
        #self.app_grid.re_init_all_app_links()

    def load(self, config_source: Optional[PathLike] = None):
        """ Load all application gui elements specified in the GUI config (file) """
        config_source_str = str(config_source)
        if not config_source:
            config_source_str = app.active_settings.get_string(LAST_CONFIG_FILE)

        # model loads incrementally
        loader = QtLoaderObject(self)
        loader.async_loading(self, self.model.loadf, (config_source_str,))
        loader.wait_for_finished()

        # model loaded, now load the gui elements, which have a static model
        #self.app_grid.re_init(self.model.app_grid)

        # TODO: Other modules are currently loaded on demand. A window and view restoration would be nice and
        # should be called from here

    @pyqtSlot()
    def on_font_size_increased(self):
        """ Increase font size by 2. Ignore if font gets too large. """
        new_size = app.active_settings.get_int(FONT_SIZE) + 1
        if new_size > 24:
            return
        app.active_settings.set(FONT_SIZE, new_size)
        activate_theme(self._qt_app)

    @pyqtSlot()
    def on_font_size_decreased(self):
        """ Decrease font size by 2. Ignore if font gets too small. """
        new_size = app.active_settings.get_int(FONT_SIZE) - 1
        if new_size < 8:
            return
        app.active_settings.set(FONT_SIZE, new_size)
        activate_theme(self._qt_app)

    @pyqtSlot()
    def on_theme_changed(self):
        if self.ui.menu_enable_dark_mode.isChecked():
            app.active_settings.set(GUI_STYLE, GUI_STYLE_DARK)
        else:
            app.active_settings.set(GUI_STYLE, GUI_STYLE_LIGHT)

        activate_theme(self._qt_app)

        # all icons must be reloaded
        self.load_icons()
        self.local_package_explorer.apply_theme()
        self.app_grid.re_init(self.model.app_grid)  # needs a whole reload because models need to be reinitialized
        if self.search_dialog:
            self.search_dialog.apply_theme()

    @pyqtSlot()
    def on_main_view_changed(self):
        """ Change between main views (grid and package explorer) """
        if self.ui.main_toolbox.currentIndex() == 1:  # package view
            # hide floating grid buttons
            if ADD_APP_LINK_BUTTON:
                self.ui.add_app_link_button.hide()
            if ADD_TAB_BUTTON:
                self.ui.add_tab_button.hide()
        elif self.ui.main_toolbox.currentIndex() == 0:  # grid view
            # show floating buttons
            if ADD_APP_LINK_BUTTON:
                self.ui.add_app_link_button.show()
            if ADD_TAB_BUTTON:
                self.ui.add_tab_button.show()

    @ pyqtSlot()
    def open_conan_search_dialog(self):
        """ Opens a Conan Search dialog. Only one allowed. """
        if self.search_dialog:
            self.search_dialog.show()
            self.search_dialog.activateWindow()
            return

        # parent=None enables to hide the dialog behind the application window
        self.search_dialog = ConanSearchDialog(None, self)
        self.search_dialog.show()

    @ pyqtSlot()
    def open_cleanup_cache_dialog(self):
        """ Open the message box to confirm deletion of invalid cache folders """
        paths = ConanCleanup(app.conan_api).get_cleanup_cache_paths()
        if not paths:
            self.write_log("INFO: Nothing found in cache to clean up.")
            return
        if len(paths) > 1:
            path_list = "\n".join(paths)
        else:
            path_list = paths[0]

        msg = QtWidgets.QMessageBox(parent=self)
        msg.setWindowTitle("Delete folders")
        msg.setText("Are you sure, you want to delete the found folders?\t")
        msg.setDetailedText(path_list)
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        reply = msg.exec_()
        if reply == QtWidgets.QMessageBox.Yes:
            for path in paths:
                rmtree(str(path), ignore_errors=True)

    @ pyqtSlot()
    def open_config_file_dialog(self):
        """" Open File Dialog and load config file """
        dialog_path = user_save_path
        config_file_path = Path(app.active_settings.get_string(LAST_CONFIG_FILE))
        if config_file_path.exists():
            dialog_path = config_file_path.parent
        dialog = QtWidgets.QFileDialog(parent=self, caption="Select JSON Config File",
                                       directory=str(dialog_path), filter="JSON files (*.json)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            new_file = dialog.selectedFiles()[0]
            app.active_settings.set(LAST_CONFIG_FILE, new_file)
            # model loads incrementally
            self.model.loadf(new_file)

            # conan works, model can be loaded
            self.app_grid.re_init(self.model.app_grid)  # loads tabs
            # self.apply_view_settings()  # now view settings can be applied

    @pyqtSlot()
    def display_versions_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_versions.isChecked()
        app.active_settings.set(DISPLAY_APP_VERSIONS, status)
        self.app_grid.re_init_all_app_links()

    @pyqtSlot()
    def apply_display_users_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_users.isChecked()
        app.active_settings.set(DISPLAY_APP_USERS, status)
        self.app_grid.re_init_all_app_links()

    @pyqtSlot()
    def display_channels_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_channels.isChecked()
        app.active_settings.set(DISPLAY_APP_CHANNELS, status)
        self.app_grid.re_init_all_app_links()

    @pyqtSlot(str)
    def write_log(self, text):
        """ Write the text signaled by the logger """
        self.ui.console.append(text)

    def load_icons(self):
        """ Load icons for main toolbox and menu """
        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(get_themed_asset_image("icons/grid.png")),
        #                QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # self.ui.main_toolbox.setItemIcon(self.TOOLBOX_GRID_ITEM, icon)

        # icon.addPixmap(QtGui.QPixmap(get_themed_asset_image("icons/search_packages.png")),
        #                QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # self.ui.main_toolbox.setItemIcon(self.TOOLBOX_PACKAGES_ITEM, icon)

        # menu
        # self.ui.menu_cleanup_cache.setIcon(QtGui.QIcon(get_themed_asset_image("icons/cleanup.png")))
        # self.ui.menu_about_action.setIcon(QtGui.QIcon(get_themed_asset_image("icons/about.png")))
        # self.ui.menu_remove_locks.setIcon(QtGui.QIcon(get_themed_asset_image("icons/remove-lock.png")))
        # self.ui.menu_search_in_remotes.setIcon(QtGui.QIcon(get_themed_asset_image("icons/search_packages.png")))
        # self.ui.menu_increase_font_size.setIcon(QtGui.QIcon(get_themed_asset_image("icons/increase_font.png")))
        # self.ui.menu_decrease_font_size.setIcon(QtGui.QIcon(get_themed_asset_image("icons/decrease_font.png")))
