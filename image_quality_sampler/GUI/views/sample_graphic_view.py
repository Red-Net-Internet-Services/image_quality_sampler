from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsView


class SamplingGraphicView(QGraphicsView):
    def __init__(self, parent=None):
        super(SamplingGraphicView, self).__init__(parent)  # Corrected super call
        self.setMouseTracking(True)
        self._panning = False
        self._last_pan_point = QPointF()

    def wheelEvent(self, event):
        factor = 1.2
        if event.angleDelta().y() > 0:
            self.scale(factor, factor)
        else:
            self.scale(1 / factor, 1 / factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._panning = True
            self._last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        super(SamplingGraphicView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            new_pan_point = event.pos()
            delta = new_pan_point - self._last_pan_point
            self._last_pan_point = new_pan_point
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super(SamplingGraphicView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
        super(SamplingGraphicView, self).mouseReleaseEvent(event)
