"""Reusable thumbnail grid for photos, shared by Photos/Albums/Person/Trash
views. Supports flat lists and date-sectioned "timeline" display."""

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from ..services.thumbnail_service import ThumbnailService

_INDEX_ROLE = Qt.UserRole + 1  # position in the flat image list


class PhotoGrid(QListWidget):
    open_requested = Signal(int)  # index into images

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
        self.itemDoubleClicked.connect(self._double_clicked)

    def _double_clicked(self, item: QListWidgetItem) -> None:
        index = item.data(_INDEX_ROLE)
        if index is not None:
            self.open_requested.emit(index)

    def _add_photo_item(self, flat_index: int, image_id: int, path: str) -> None:
        item = QListWidgetItem(Path(path).name)
        item.setData(Qt.UserRole, image_id)
        item.setData(_INDEX_ROLE, flat_index)
        item.setToolTip(path)
        thumb = self.thumbs.image_thumbnail(path)
        if thumb:
            item.setIcon(QIcon(str(thumb)))
        item.setSizeHint(QSize(170, 195))
        self.addItem(item)

    def set_images(self, images: list[tuple[int, str]]) -> None:
        self.clear()
        self._images = list(images)
        for i, (image_id, path) in enumerate(self._images):
            self._add_photo_item(i, image_id, path)

    def set_sections(self, sections: list[tuple[str, list[tuple[int, str]]]]) -> None:
        """Timeline display: a full-width header item before each group."""
        self.clear()
        self._images = []
        for header, images in sections:
            item = QListWidgetItem(header)
            item.setFlags(Qt.NoItemFlags)  # not selectable, not clickable
            item.setSizeHint(QSize(4000, 34))  # force onto its own row
            font = item.font()
            font.setBold(True)
            font.setPointSize(font.pointSize() + 2)
            item.setFont(font)
            self.addItem(item)
            for image_id, path in images:
                self._add_photo_item(len(self._images), image_id, path)
                self._images.append((image_id, path))

    @property
    def images(self) -> list[tuple[int, str]]:
        return self._images

    def selected_image_ids(self) -> list[int]:
        return [item.data(Qt.UserRole) for item in self.selectedItems()]
