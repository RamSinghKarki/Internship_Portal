"""Dashboard: library statistics at a glance."""

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
            "exact_duplicate_groups": StatTile("Duplicate groups"),
            "db_size": StatTile("Database size"),
        }
        for i, tile in enumerate(self.tiles.values()):
            grid.addWidget(tile, i // 3, i % 3)
        layout.addLayout(grid)

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
        for key in ("images", "faces", "people", "unknown_faces", "exact_duplicate_groups"):
            self.tiles[key].set_value(stats[key])
        if self.config.db_path.is_file():
            kb = self.config.db_path.stat().st_size / 1024
            self.tiles["db_size"].set_value(f"{kb / 1024:.1f} MB" if kb > 1024 else f"{kb:.0f} KB")

        self.history.setRowCount(len(scans))
        for row, scan in enumerate(scans):
            cells = [scan.folder, scan.status, str(scan.total_files),
                     str(scan.new_images), str(scan.faces_found), str(scan.failed)]
            for col, text in enumerate(cells):
                self.history.setItem(row, col, QTableWidgetItem(text))
