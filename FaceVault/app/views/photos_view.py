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
        self.text_filter = QLineEdit()
        self.text_filter.setPlaceholderText("Text in photo… (OCR)")
        self.text_filter.setFixedWidth(180)
        self.text_filter.returnPressed.connect(self.refresh)
        self.tag_filter = QLineEdit()
        self.tag_filter.setPlaceholderText("Object… (dog, car)")
        self.tag_filter.setFixedWidth(140)
        self.tag_filter.returnPressed.connect(self.refresh)
        self.unknown_only = QCheckBox("Unknown faces only")
        self.favorites_only = QCheckBox("★ Favorites")
        self.favorites_only.stateChanged.connect(lambda *_: self.refresh())
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.refresh)
        self.person_filter.returnPressed.connect(self.refresh)
        self.camera_filter.returnPressed.connect(self.refresh)
        self._count = QLabel("")
        self._count.setObjectName("subtle")
        filters.addWidget(self.person_filter)
        filters.addWidget(self.camera_filter)
        filters.addWidget(self.text_filter)
        filters.addWidget(self.tag_filter)
        filters.addWidget(self.unknown_only)
        filters.addWidget(self.favorites_only)
        filters.addWidget(apply_btn)
        filters.addStretch()
        filters.addWidget(self._count)
        layout.addLayout(filters)

        # Semantic (natural-language) search — enabled when CLIP models exist.
        ai_row = QHBoxLayout()
        self.describe = QLineEdit()
        self.ai_btn = QPushButton("🔍 AI Search")
        self.ai_btn.setObjectName("primary")
        if config.semantic_available():
            self.describe.setPlaceholderText(
                'Describe what you\'re looking for… e.g. "sunset at the beach", '
                '"person smiling", "red car"'
            )
            self.describe.returnPressed.connect(self._semantic_search)
            self.ai_btn.clicked.connect(self._semantic_search)
        else:
            self.describe.setPlaceholderText(
                "Semantic search not installed — run models/download_models.py "
                "and pip install onnxruntime tokenizers"
            )
            self.describe.setEnabled(False)
            self.ai_btn.setEnabled(False)
        ai_row.addWidget(self.describe, stretch=1)
        ai_row.addWidget(self.ai_btn)
        layout.addLayout(ai_row)

        self.grid = PhotoGrid(ThumbnailService(config))
        self.grid.setContextMenuPolicy(Qt.CustomContextMenu)
        self.grid.customContextMenuRequested.connect(self._context_menu)
        self.grid.open_requested.connect(self._open_viewer)
        layout.addWidget(self.grid)

    def _semantic_search(self) -> None:
        query = self.describe.text().strip()
        if not query:
            self.refresh()
            return
        hits = self.search.semantic_search(query)
        self.grid.set_images([(img.id, img.path) for img, _score in hits])
        self._count.setText(f"{len(hits)} AI match(es) for “{query}”")

    def refresh(self) -> None:
        images = self.search.search_images(
            person_name=self.person_filter.text().strip() or None,
            camera=self.camera_filter.text().strip() or None,
            unknown_faces_only=self.unknown_only.isChecked(),
            favorites_only=self.favorites_only.isChecked(),
            text_contains=self.text_filter.text().strip() or None,
            tag=self.tag_filter.text().strip() or None,
        )
        # Timeline: group by month like Google Photos' main feed.
        sections: list[tuple[str, list[tuple[int, str]]]] = []
        for img in images:
            header = img.taken_at.strftime("%B %Y") if img.taken_at else "No date"
            if not sections or sections[-1][0] != header:
                sections.append((header, []))
            sections[-1][1].append((img.id, img.path))
        self.grid.set_sections(sections)
        self._count.setText(f"{len(images)} photo(s)")

    def _open_viewer(self, index: int) -> None:
        dlg = PhotoViewerDialog(self.grid.images, index, self.session_factory,
                                config=self.config, parent=self)
        dlg.exec()
        self.refresh()  # an edit may have added a new library photo

    def _context_menu(self, pos) -> None:
        selected = self.grid.selected_image_ids()
        if not selected:
            return
        menu = QMenu(self)
        act_fav = menu.addAction(f"★ Favorite {len(selected)} photo(s)")
        act_unfav = menu.addAction("Remove from favorites")
        act_album = menu.addAction(f"Add {len(selected)} photo(s) to album…")
        act_trash = menu.addAction("Move to trash")
        chosen = menu.exec(self.grid.mapToGlobal(pos))

        if chosen is act_fav or chosen is act_unfav:
            with self.session_factory() as session:
                Repository(session).set_favorite(selected, chosen is act_fav)
            self.refresh()
        elif chosen is act_album:
            self._add_to_album(selected)
        elif chosen is act_trash:
            with self.session_factory() as session:
                Repository(session).set_trashed(selected, True)
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
