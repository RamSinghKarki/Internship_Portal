"""Photos: browse the whole library with filters; the main browsing surface."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..config import AppConfig
from ..database.repository import Repository
from ..services.album_service import AlbumService
from ..services.search_service import SearchService
from ..services.thumbnail_service import ThumbnailService
from ..widgets.photo_grid import PhotoGrid
from ..widgets.photo_viewer import PhotoViewerDialog


class PhotosView(QWidget):
    data_changed = Signal()

    def __init__(self, config: AppConfig, session_factory, parent=None):
        super().__init__(parent)
        self.config = config
        self.session_factory = session_factory
        self.search = SearchService(config, session_factory)
        self.albums = AlbumService(config, session_factory)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Photos")
        title.setObjectName("heading")
        layout.addWidget(title)

        filters = QHBoxLayout()
        self.person_filter = QLineEdit()
        self.person_filter.setPlaceholderText("Person…")
        self.person_filter.setFixedWidth(160)
        self.camera_filter = QLineEdit()
        self.camera_filter.setPlaceholderText("Camera…")
        self.camera_filter.setFixedWidth(160)
        self.unknown_only = QCheckBox("Unknown faces only")
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.refresh)
        self.person_filter.returnPressed.connect(self.refresh)
        self.camera_filter.returnPressed.connect(self.refresh)
        self._count = QLabel("")
        self._count.setObjectName("subtle")
        filters.addWidget(self.person_filter)
        filters.addWidget(self.camera_filter)
        filters.addWidget(self.unknown_only)
        filters.addWidget(apply_btn)
        filters.addStretch()
        filters.addWidget(self._count)
        layout.addLayout(filters)

        self.grid = PhotoGrid(ThumbnailService(config))
        self.grid.setContextMenuPolicy(Qt.CustomContextMenu)
        self.grid.customContextMenuRequested.connect(self._context_menu)
        self.grid.open_requested.connect(self._open_viewer)
        layout.addWidget(self.grid)

    def refresh(self) -> None:
        images = self.search.search_images(
            person_name=self.person_filter.text().strip() or None,
            camera=self.camera_filter.text().strip() or None,
            unknown_faces_only=self.unknown_only.isChecked(),
        )
        self.grid.set_images([(i.id, i.path) for i in images])
        self._count.setText(f"{len(images)} photo(s)")

    def _open_viewer(self, index: int) -> None:
        PhotoViewerDialog(self.grid.images, index, self.session_factory, self).exec()

    def _context_menu(self, pos) -> None:
        selected = self.grid.selected_image_ids()
        if not selected:
            return
        menu = QMenu(self)
        act_album = menu.addAction(f"Add {len(selected)} photo(s) to album…")
        act_remove = menu.addAction("Remove from library (files stay on disk)")
        chosen = menu.exec(self.grid.mapToGlobal(pos))

        if chosen is act_album:
            self._add_to_album(selected)
        elif chosen is act_remove:
            confirm = QMessageBox.question(
                self, "Remove from library",
                f"Remove {len(selected)} photo(s) from the FaceVault library?\n"
                "The image files on disk are NOT deleted.",
            )
            if confirm == QMessageBox.Yes:
                with self.session_factory() as session:
                    Repository(session).remove_images(selected)
                self.refresh()
                self.data_changed.emit()

    def _add_to_album(self, image_ids: list[int]) -> None:
        existing = self.albums.list_albums()
        options = [a["name"] for a in existing] + ["➕  New album…"]
        choice, ok = QInputDialog.getItem(
            self, "Add to album", "Album:", options, 0, False
        )
        if not ok:
            return
        if choice == "➕  New album…":
            name, ok = QInputDialog.getText(self, "New album", "Album name:")
            if not ok or not name.strip():
                return
            try:
                album_id = self.albums.create(name)
            except ValueError as exc:
                QMessageBox.warning(self, "Album", str(exc))
                return
        else:
            album_id = existing[options.index(choice)]["id"]
        added = self.albums.add_images(album_id, image_ids)
        self.data_changed.emit()
        QMessageBox.information(self, "Album", f"Added {added} photo(s).")
