"""Albums: user-curated collections; photos are added from the Photos view."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ..config import AppConfig
from ..services.album_service import AlbumService
from ..services.thumbnail_service import ThumbnailService
from ..widgets.photo_grid import PhotoGrid
from ..widgets.photo_viewer import PhotoViewerDialog


class AlbumsView(QWidget):
    data_changed = Signal()

    def __init__(self, config: AppConfig, session_factory, parent=None):
        super().__init__(parent)
        self.config = config
        self.session_factory = session_factory
        self.albums = AlbumService(config, session_factory)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Albums")
        title.setObjectName("heading")
        layout.addWidget(title)

        actions = QHBoxLayout()
        new_btn = QPushButton("New album…")
        new_btn.setObjectName("primary")
        rename_btn = QPushButton("Rename…")
        delete_btn = QPushButton("Delete")
        new_btn.clicked.connect(self._new_album)
        rename_btn.clicked.connect(self._rename_album)
        delete_btn.clicked.connect(self._delete_album)
        actions.addWidget(new_btn)
        actions.addWidget(rename_btn)
        actions.addWidget(delete_btn)
        actions.addStretch()
        layout.addLayout(actions)

        split = QSplitter(Qt.Horizontal)
        self.album_list = QListWidget()
        self.album_list.setMaximumWidth(260)
        self.album_list.currentItemChanged.connect(lambda *_: self._load_album())
        split.addWidget(self.album_list)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self._hint = QLabel(
            "Add photos from the Photos section: select, right-click → Add to album."
        )
        self._hint.setObjectName("subtle")
        right_layout.addWidget(self._hint)
        self.grid = PhotoGrid(ThumbnailService(config))
        self.grid.setContextMenuPolicy(Qt.CustomContextMenu)
        self.grid.customContextMenuRequested.connect(self._context_menu)
        self.grid.open_requested.connect(self._open_viewer)
        right_layout.addWidget(self.grid)
        split.addWidget(right)
        split.setStretchFactor(1, 1)
        layout.addWidget(split)

    # ---- data ---------------------------------------------------------
    def refresh(self) -> None:
        current = self._selected_album_id()
        self.album_list.clear()
        for album in self.albums.list_albums():
            item = QListWidgetItem(f"{album['name']}  ({album['photo_count']})")
            item.setData(Qt.UserRole, album["id"])
            self.album_list.addItem(item)
            if album["id"] == current:
                self.album_list.setCurrentItem(item)
        if self.album_list.currentItem() is None and self.album_list.count():
            self.album_list.setCurrentRow(0)
        self._load_album()

    def _selected_album_id(self) -> int | None:
        item = self.album_list.currentItem()
        return item.data(Qt.UserRole) if item else None

    def _load_album(self) -> None:
        album_id = self._selected_album_id()
        if album_id is None:
            self.grid.set_images([])
            return
        images = self.albums.images_in_album(album_id)
        self.grid.set_images([(i.id, i.path) for i in images])

    # ---- actions ------------------------------------------------------
    def _new_album(self) -> None:
        name, ok = QInputDialog.getText(self, "New album", "Album name:")
        if ok and name.strip():
            try:
                self.albums.create(name)
            except ValueError as exc:
                QMessageBox.warning(self, "Album", str(exc))
            self.refresh()

    def _rename_album(self) -> None:
        album_id = self._selected_album_id()
        if album_id is None:
            return
        name, ok = QInputDialog.getText(self, "Rename album", "New name:")
        if ok and name.strip():
            self.albums.rename(album_id, name)
            self.refresh()

    def _delete_album(self) -> None:
        album_id = self._selected_album_id()
        if album_id is None:
            return
        confirm = QMessageBox.question(
            self, "Delete album",
            "Delete this album? Photos stay in the library.",
        )
        if confirm == QMessageBox.Yes:
            self.albums.delete(album_id)
            self.refresh()

    def _context_menu(self, pos) -> None:
        selected = self.grid.selected_image_ids()
        album_id = self._selected_album_id()
        if not selected or album_id is None:
            return
        menu = QMenu(self)
        act_remove = menu.addAction(f"Remove {len(selected)} photo(s) from album")
        if menu.exec(self.grid.mapToGlobal(pos)) is act_remove:
            self.albums.remove_images(album_id, selected)
            self.refresh()

    def _open_viewer(self, index: int) -> None:
        PhotoViewerDialog(self.grid.images, index, self.session_factory,
                          config=self.config, parent=self).exec()
