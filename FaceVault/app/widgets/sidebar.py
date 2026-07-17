from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem

SECTIONS = [
    ("dashboard", "⌂  Dashboard"),
    ("photos", "🖼  Photos"),
    ("people", "👤  People"),
    ("unknown", "❓  Unknown faces"),
    ("albums", "📁  Albums"),
    ("duplicates", "⧉  Duplicates"),
    ("settings", "⚙  Settings"),
]


class Sidebar(QListWidget):
    section_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(190)
        self.setIconSize(QSize(20, 20))
        for key, label in SECTIONS:
            item = QListWidgetItem(label)
            item.setData(256, key)  # Qt.UserRole
            self.addItem(item)
        self.currentItemChanged.connect(
            lambda cur, _prev: cur and self.section_selected.emit(cur.data(256))
        )
        self.setCurrentRow(0)
