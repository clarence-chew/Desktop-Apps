from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, QTimer

RESIZE_HANDLE_SIZE = 10
RESIZE_HANDLE_DURATION_MS = 3000

class ResizeHandle(QLabel):
    def __init__(self, parent, size=RESIZE_HANDLE_SIZE):
        super().__init__(parent)
        self.size_px = size

        self.resize(size, size)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 128); border: 1px solid gray;")
        self.hide()

        # Timer to hide automatically
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def show(self):
        if self.timer.isActive():
            self.timer.stop()
        super().show()

    def start_hide_timer(self, duration_ms=RESIZE_HANDLE_DURATION_MS):
        self.timer.start(duration_ms)

    def update_position(self):
        parent_size = self.parent().size()
        x = parent_size.width() - self.size_px
        y = parent_size.height() - self.size_px
        self.move(x, y)

    def contains_point(self, pos: QPoint) -> bool:
        """Check if given local point is inside the resize handle."""
        rect = QRect(self.pos(), self.size())
        return rect.contains(pos)

    def enterEvent(self, event):
        self.setCursor(Qt.SizeFDiagCursor)

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
