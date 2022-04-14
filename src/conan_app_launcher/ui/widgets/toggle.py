from PyQt5.QtCore import (QEasingCurve, QPoint, QPointF, QPropertyAnimation,
                          QRectF, QSequentialAnimationGroup, QSize, Qt,
                          pyqtProperty, pyqtSlot)
from PyQt5.QtGui import QBrush, QColor, QPainter, QPaintEvent, QPen
from PyQt5.QtWidgets import QCheckBox


class AnimatedToggle(QCheckBox):

    _transparent_pen = QPen(Qt.transparent)
    _light_grey_pen = QPen(Qt.lightGray)

    def __init__(self, parent=None, bar_color=Qt.gray, checked_color="#00B0FF", handle_color=Qt.white, 
                 pulse_unchecked_color="#44999999", pulse_checked_color="#4400B0EE"):

        super().__init__(parent)

        # needed for paintEvent.
        self._bar_brush = QBrush(bar_color)
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())
        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(QColor(checked_color))

        # Setup the rest of the widget.

        self.setContentsMargins(8, 0, 0, 0)
        self._handle_position = 0

        self.stateChanged.connect(self.handle_state_change)

        self._pulse_radius = 0

        self.handle_anim = QPropertyAnimation(self, b"handle_position", self)
        self.handle_anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.handle_anim.setDuration(200)  # ms

        self.pulse_anim = QPropertyAnimation(self, b"pulse_radius", self)
        self.pulse_anim.setDuration(300)  # ms
        self.pulse_anim.setStartValue(10)
        self.pulse_anim.setEndValue(20)

        self.animations_group = QSequentialAnimationGroup()
        self.animations_group.addAnimation(self.handle_anim)
        self.animations_group.addAnimation(self.pulse_anim)

        self._pulse_unchecked_animation = QBrush(QColor(pulse_unchecked_color))
        self._pulse_checked_animation = QBrush(QColor(pulse_checked_color))

    def sizeHint(self):
        return QSize(70, 50)

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    @pyqtProperty(float)
    def handle_position(self):
        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos):
        """change the property
        we need to trigger QWidget.update() method, either by:
            1- calling it here [ what we're doing ].
            2- connecting the QPropertyAnimation.valueChanged() signal to it.
        """
        self._handle_position = pos
        self.update()

    @pyqtProperty(float)
    def pulse_radius(self):
        return self._pulse_radius

    @pulse_radius.setter
    def pulse_radius(self, pos):
        self._pulse_radius = pos
        self.update()

    @pyqtSlot(int)
    def handle_state_change(self, value):
        self.animations_group.stop()
        if value:
            self.handle_anim.setEndValue(1)
        else:
            self.handle_anim.setEndValue(0)
        self.animations_group.start()

    def paintEvent(self, e: QPaintEvent):

        cont_rect = self.contentsRect()
        handle_radius = round(0.2* cont_rect.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(self._transparent_pen)
        bar_rect = QRectF(0, 0,
            cont_rect.width() - handle_radius, 0.40 * cont_rect.height()
        )
        bar_rect.moveCenter(cont_rect.center())
        rounding = bar_rect.height() / 2

        # the handle will move along this line
        trail_length = cont_rect.width() - 2 * handle_radius

        x_pos = cont_rect.x() + handle_radius + trail_length * self._handle_position

        if self.pulse_anim.state() == QPropertyAnimation.Running:
            painter.setBrush(
                self._pulse_checked_animation if
                self.isChecked() else self._pulse_unchecked_animation)
            painter.drawEllipse(QPointF(x_pos, bar_rect.center().y()),
                          self._pulse_radius, self._pulse_radius)

        if self.isChecked():
            painter.setBrush(self._bar_checked_brush)
            painter.drawRoundedRect(bar_rect, rounding, rounding)
            painter.setBrush(self._handle_checked_brush)
        else:
            painter.setBrush(self._bar_brush)
            painter.drawRoundedRect(bar_rect, rounding, rounding)
            painter.setPen(self._light_grey_pen)
            painter.setBrush(self._handle_brush)

        painter.drawEllipse(
            QPointF(x_pos, bar_rect.center().y()),
            handle_radius, handle_radius)

        painter.end()
