import os
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtCore import QSize, Qt

def scale_to_screen_bounds(size: QSize) -> QSize:
    screen_rect = QApplication.primaryScreen().availableGeometry()
    bound = min(screen_rect.width(), screen_rect.height()) // 2

    if size.width() <= bound and size.height() <= bound:
        return size # No need to scale

    scale_factor = min(bound / size.width(), bound / size.height())
    new_width = int(size.width() * scale_factor)
    new_height = int(size.height() * scale_factor)

    return QSize(new_width, new_height)

class MediaDisplay:
    def __init__(self, parent=None):
        self.label = QLabel(parent)
        self.path = None
        self.is_gif = False
        self.movie = None
        self.pixmap = None
        self.original_size = QSize(100, 100) # fallback size
        self.display_size = QSize(100, 100) # fallback size

    def set_media(self, path: str):
        self.path = path
        ext = os.path.splitext(path)[-1].lower()
        self.is_gif = (ext == ".gif")

        if self.is_gif:
            self.movie = QMovie(path)
            self.movie.start()
            self.label.setMovie(self.movie)
            self.original_size = self.movie.frameRect().size()
        else:
            self.pixmap = QPixmap(path)
            self.label.setPixmap(self.pixmap)
            self.original_size = self.pixmap.size()

        self.resize_to(scale_to_screen_bounds(self.original_size))

    def resize_to(self, size: QSize):
        self.display_size = size
        if self.is_gif:
            self.movie.setScaledSize(size)
        else:
            scaled = self.pixmap.scaled(size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(scaled)
        self.label.resize(size)

    def get_original_size(self) -> QSize:
        return self.original_size

    def get_display_size(self) -> QSize:
        return self.display_size

    def widget(self) -> QLabel:
        return self.label

