"""Reusable thumbnail grid for photos, shared by Photos/Albums/Person views."""

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from ..services.thumbnail_service import ThumbnailService


class PhotoGrid(QListWidget):
    open_requested = Signal(int)  # index into the current image list

    def __init__(self, thumbs: ThumbnailService, parent=None):
        super().__init__(parent)
        self.thumbs = thumbs
        self._images: list[tuple[int, str]] = []  # (image_id, path)
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(150, 150))
        self.setResizeMode(QListWidget.Adjust)
        self.setSpacing(10)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setWordWrap(True)
        self.itemDoubleClicked.connect(
            lambda item: self.open_requested.emit(self.row(item))
        )

    def set_images(self, images: list[tuple[int, str]]) -> None:
        self.clear()
        self._images = list(images)
        for image_id, path in self._images:
            item = QListWidgetItem(Path(path).name)
            item.setData(Qt.UserRole, image_id)
            item.setToolTip(path)
            thumb = self.thumbs.image_thumbnail(path)
            if thumb:
                item.setIcon(QIcon(str(thumb)))
            item.setSizeHint(QSize(170, 195))
            self.addItem(item)

    @property
    def images(self) -> list[tuple[int, str]]:
        return self._images

    def selected_image_ids(self) -> list[int]:
        return [item.data(Qt.UserRole) for item in self.selectedItems()]
