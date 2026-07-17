"""Dashboard: library statistics, memories ("on this day"), scan history."""

from datetime import date

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..config import AppConfig
from ..database.repository import Repository


class StatTile(QFrame):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statTile")
        self.setMinimumSize(170, 90)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        self._value = QLabel("0")
        self._value.setObjectName("statValue")
        caption = QLabel(label)
        caption.setObjectName("statLabel")
        layout.addWidget(self._value)
        layout.addWidget(caption)

    def set_value(self, value) -> None:
        self._value.setText(f"{value:,}" if isinstance(value, int) else str(value))


class DashboardView(QWidget):
    def __init__(self, config: AppConfig, session_factory, parent=None):
        super().__init__(parent)
        self.config = config
        self.session_factory = session_factory

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Dashboard")
        title.setObjectName("heading")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)
        self.tiles = {
            "images": StatTile("Images"),
            "faces": StatTile("Faces"),
            "people": StatTile("People"),
            "unknown_faces": StatTile("Unknown faces"),
            "favorites": StatTile("Favorites"),
            "exact_duplicate_groups": StatTile("Duplicate groups"),
        }
        for i, tile in enumerate(self.tiles.values()):
            grid.addWidget(tile, i // 3, i % 3)
        layout.addLayout(grid)

        self._memories_label = QLabel("Memories — on this day")
        self._memories_label.setObjectName("heading")
        layout.addWidget(self._memories_label)
        self.memories = QListWidget()
        self.memories.setViewMode(QListWidget.IconMode)
        self.memories.setIconSize(QSize(110, 110))
        self.memories.setFixedHeight(150)
        self.memories.setFlow(QListWidget.LeftToRight)
        self.memories.setWrapping(False)
        layout.addWidget(self.memories)

        history_label = QLabel("Recent scans")
        history_label.setObjectName("heading")
        layout.addWidget(history_label)

        self.history = QTableWidget(0, 6)
        self.history.setHorizontalHeaderLabels(
            ["Folder", "Status", "Files", "New", "Faces", "Failed"]
        )
        self.history.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.history.verticalHeader().hide()
        self.history.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.history)

    def refresh(self) -> None:
        with self.session_factory() as session:
            repo = Repository(session)
            stats = repo.stats()
            scans = repo.recent_scans(limit=10)
        for key in ("images", "faces", "people", "unknown_faces", "favorites",
                    "exact_duplicate_groups"):
            self.tiles[key].set_value(stats[key])

        # Memories strip — hidden entirely when today has no anniversaries.
        today = date.today()
        with self.session_factory() as session:
            memories = Repository(session).on_this_day(today.month, today.day)
        self.memories.clear()
        visible = bool(memories)
        self._memories_label.setVisible(visible)
        self.memories.setVisible(visible)
        if visible:
            from ..services.thumbnail_service import ThumbnailService

            thumbs = ThumbnailService(self.config)
            for img in memories:
                year = img.taken_at.strftime("%Y") if img.taken_at else ""
                item = QListWidgetItem(year)
                item.setToolTip(img.path)
                thumb = thumbs.image_thumbnail(img.path)
                if thumb:
                    item.setIcon(QIcon(str(thumb)))
                item.setSizeHint(QSize(125, 140))
                self.memories.addItem(item)

        self.history.setRowCount(len(scans))
        for row, scan in enumerate(scans):
            cells = [scan.folder, scan.status, str(scan.total_files),
                     str(scan.new_images), str(scan.faces_found), str(scan.failed)]
            for col, text in enumerate(cells):
                self.history.setItem(row, col, QTableWidgetItem(text))
