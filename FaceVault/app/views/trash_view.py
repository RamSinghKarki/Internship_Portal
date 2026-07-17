"""Trash: soft-deleted photos with restore, like Google Photos' bin.

Files on disk are never touched — "delete permanently" only removes the
photo and its face data from the FaceVault library.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..config import AppConfig
from ..database.repository import Repository
from ..services.thumbnail_service import ThumbnailService
from ..widgets.photo_grid import PhotoGrid


class TrashView(QWidget):
    data_changed = Signal()

    def __init__(self, config: AppConfig, session_factory, parent=None):
        super().__init__(parent)
        self.config = config
        self.session_factory = session_factory

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Trash")
        title.setObjectName("heading")
        layout.addWidget(title)

        hint = QLabel(
            "Photos moved to trash are hidden everywhere else. "
            "Restoring brings them back; permanent deletion removes them from "
            "the library only — image files on disk are never deleted."
        )
        hint.setObjectName("subtle")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        actions = QHBoxLayout()
        restore_btn = QPushButton("Restore selected")
        restore_btn.setObjectName("primary")
        delete_btn = QPushButton("Delete selected from library permanently")
        restore_btn.clicked.connect(self._restore)
        delete_btn.clicked.connect(self._delete_forever)
        self._count = QLabel("")
        self._count.setObjectName("subtle")
        actions.addWidget(restore_btn)
        actions.addWidget(delete_btn)
        actions.addStretch()
        actions.addWidget(self._count)
        layout.addLayout(actions)

        self.grid = PhotoGrid(ThumbnailService(config))
        layout.addWidget(self.grid)

    def refresh(self) -> None:
        with self.session_factory() as session:
            images = Repository(session).trashed_images()
        self.grid.set_images([(i.id, i.path) for i in images])
        self._count.setText(f"{len(images)} photo(s) in trash")

    def _restore(self) -> None:
        selected = self.grid.selected_image_ids()
        if not selected:
            return
        with self.session_factory() as session:
            Repository(session).set_trashed(selected, False)
        self.refresh()
        self.data_changed.emit()

    def _delete_forever(self) -> None:
        selected = self.grid.selected_image_ids()
        if not selected:
            return
        confirm = QMessageBox.question(
            self, "Delete permanently",
            f"Remove {len(selected)} photo(s) and their face data from the "
            "library permanently?\nThe image files on disk are NOT deleted.",
        )
        if confirm == QMessageBox.Yes:
            with self.session_factory() as session:
                Repository(session).remove_images(selected)
            self.refresh()
            self.data_changed.emit()
