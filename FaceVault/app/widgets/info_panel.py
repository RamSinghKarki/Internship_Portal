"""Right-hand information panel: details for the selected person."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class InfoPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("infoPanel")
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self._cover = QLabel()
        self._cover.setAlignment(Qt.AlignCenter)
        self._cover.setFixedSize(200, 200)
        self._cover.setStyleSheet("border-radius: 8px; background: #1a1b1e;")

        self._name = QLabel("")
        self._name.setObjectName("heading")
        self._name.setWordWrap(True)

        self._lines = QLabel("")
        self._lines.setObjectName("subtle")
        self._lines.setWordWrap(True)

        hint = QLabel("Select a person to see details.")
        hint.setObjectName("subtle")
        self._hint = hint

        layout.addWidget(self._cover)
        layout.addWidget(self._name)
        layout.addWidget(self._lines)
        layout.addWidget(hint)
        layout.addStretch()
        self.clear()

    def clear(self) -> None:
        self._cover.hide()
        self._name.setText("")
        self._lines.setText("")
        self._hint.show()

    def show_person(self, detail: dict, cover_path: Path | None) -> None:
        self._hint.hide()
        if cover_path and Path(cover_path).is_file():
            pix = QPixmap(str(cover_path)).scaled(
                200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            self._cover.setPixmap(pix)
            self._cover.show()
        else:
            self._cover.hide()

        self._name.setText(detail["name"])
        fmt = lambda d: d.strftime("%b %d, %Y") if d else "—"
        self._lines.setText(
            f"Photos: {detail['photo_count']}\n"
            f"Faces: {detail['face_count']}\n"
            f"Avg face quality: {detail['avg_quality']}\n"
            f"First seen: {fmt(detail['first_seen'])}\n"
            f"Last seen: {fmt(detail['last_seen'])}\n"
            f"{'✔ Verified' if detail['verified'] else 'Unverified (auto-grouped)'}"
        )
