# media_widget.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint

from resize_handle import ResizeHandle
from media_display import MediaDisplay

class MediaWidget(QWidget):
    def __init__(self, image_path, callbacks=None):
        super().__init__()
        self.callbacks = callbacks or {}
        self.drag_position = QPoint(0, 0)
        self.resizing = False
        self.dragging = False
        self.image_path = image_path  # Used by profile saving

        self.media_display = MediaDisplay(self)
        self.resize_handle = ResizeHandle(self)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.load_new_image(image_path)
        self.show()

    def resizeEvent(self, event):
        self.media_display.resize_to(self.size())
        self.resize_handle.update_position()

    def mousePressEvent(self, event):
        pos = event.pos()
        if event.button() == Qt.LeftButton:
            self.resize_handle.update_position()
            self.resize_handle.show()
            if self.resize_handle.contains_point(pos):
                self.resizing = True
                self.drag_start_geom = self.geometry()
                self.drag_start_pos = event.globalPos()
            else:
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.callbacks.get("context_menu", lambda _, __: None)(self, event.globalPos())

    def mouseMoveEvent(self, event):
        if self.resizing:
            self._perform_aspect_ratio_resize(event.globalPos())
        elif self.dragging:
            self.move(event.globalPos() - self.drag_position)
        else:
            self._update_cursor(event.pos())

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.dragging = False
        self.resize_handle.start_hide_timer()
        self.try_save_profile()

    def _update_cursor(self, pos):
        if self.resize_handle.contains_point(pos):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def _perform_aspect_ratio_resize(self, global_pos):
        delta = global_pos - self.drag_start_pos
        base_width = self.drag_start_geom.width()
        rect = self.media_display.get_original_size()
        aspect_ratio = rect.width() / rect.height()
        new_width = max(50, base_width + delta.x())
        new_height = int(new_width / aspect_ratio)
        self.setGeometry(self.drag_start_geom.x(), self.drag_start_geom.y(), new_width, new_height)

    def try_save_profile(self):
        self.callbacks.get("save", lambda: None)()

    def load_new_image(self, path, size=None):
        self.image_path = path
        self.media_display.set_media(path)
        if size:
            self.media_display.resize_to(size)
        rect = self.media_display.get_display_size()
        self.setGeometry(self.x(), self.y(), rect.width(), rect.height())
        self.try_save_profile()

    def serialize(self):
        geom = self.geometry()
        return {
            "type": "media",
            "path": self.image_path,
            "x": geom.x(),
            "y": geom.y(),
            "width": geom.width(),
            "height": geom.height(),
        }
