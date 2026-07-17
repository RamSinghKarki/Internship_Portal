"""Dashboard: library statistics at a glance."""

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
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

        self._last_scan = QLabel("")
        self._last_scan.setObjectName("subtle")
        layout.addWidget(self._last_scan)
        layout.addStretch()

    def refresh(self) -> None:
        with self.session_factory() as session:
            stats = Repository(session).stats()
        for key in ("images", "faces", "people", "unknown_faces", "exact_duplicate_groups"):
            self.tiles[key].set_value(stats[key])
        if self.config.db_path.is_file():
            kb = self.config.db_path.stat().st_size / 1024
            self.tiles["db_size"].set_value(f"{kb / 1024:.1f} MB" if kb > 1024 else f"{kb:.0f} KB")
        last = stats["last_scan"]
        self._last_scan.setText(
            f"Last scan: {last.folder}  ({last.status}, {last.new_images} new, "
            f"{last.faces_found} faces)" if last else "No scans yet — use Scan Folder to begin."
        )
