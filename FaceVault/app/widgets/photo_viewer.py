"""Full photo viewer with face overlays and prev/next navigation.

Detected faces are outlined on the photo with the person's name (or
"unknown"), which makes the AI's work inspectable — the difference
between trusting and debugging your library.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QKeySequence, QPainter, QPen, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from sqlalchemy import select

from ..database.models import Face

ACCENT = QColor("#3574f0")
UNKNOWN = QColor("#e0a030")


class PhotoViewerDialog(QDialog):
    def __init__(self, images: list[tuple[int, str]], start_index: int,
                 session_factory, parent=None):
        super().__init__(parent)
        self.images = images
        self.index = max(0, min(start_index, len(images) - 1))
        self.session_factory = session_factory

        self.resize(1000, 720)
        layout = QVBoxLayout(self)

        self._canvas = QLabel()
        self._canvas.setAlignment(Qt.AlignCenter)
        self._canvas.setMinimumSize(400, 300)
        layout.addWidget(self._canvas, stretch=1)

        nav = QHBoxLayout()
        prev_btn = QPushButton("◀  Previous")
        next_btn = QPushButton("Next  ▶")
        self._caption = QLabel("")
        self._caption.setObjectName("subtle")
        prev_btn.clicked.connect(lambda: self._step(-1))
        next_btn.clicked.connect(lambda: self._step(1))
        QShortcut(QKeySequence(Qt.Key_Left), self, lambda: self._step(-1))
        QShortcut(QKeySequence(Qt.Key_Right), self, lambda: self._step(1))
        nav.addWidget(prev_btn)
        nav.addWidget(next_btn)
        nav.addStretch()
        nav.addWidget(self._caption)
        layout.addLayout(nav)

        self._show()

    def _step(self, delta: int) -> None:
        new = self.index + delta
        if 0 <= new < len(self.images):
            self.index = new
            self._show()

    def _annotated_pixmap(self, image_id: int, path: str) -> QPixmap | None:
        pix = QPixmap(path)
        if pix.isNull():
            return None
        # Resolve names inside the session — lazy loads fail once it closes.
        with self.session_factory() as session:
            faces = [
                (f.x, f.y, f.w, f.h,
                 f.person_id is not None,
                 f.person.display_name if f.person else "unknown")
                for f in session.scalars(select(Face).where(Face.image_id == image_id))
            ]
        if faces:
            painter = QPainter(pix)
            # Keep overlay stroke/text legible at any photo resolution.
            stroke = max(2, pix.width() // 400)
            font = QFont()
            font.setPixelSize(max(14, pix.width() // 50))
            font.setBold(True)
            painter.setFont(font)
            for x, y, w, h, has_person, label in faces:
                color = ACCENT if has_person else UNKNOWN
                painter.setPen(QPen(color, stroke))
                painter.drawRect(x, y, w, h)
                metrics = painter.fontMetrics()
                tw = metrics.horizontalAdvance(label) + 12
                th = metrics.height() + 6
                ty = y - th if y - th > 0 else y + h
                painter.fillRect(x, ty, tw, th, color)
                painter.setPen(QPen(QColor("white"), 1))
                painter.drawText(x + 6, ty + th - metrics.descent() - 3, label)
            painter.end()
        return pix

    def _show(self) -> None:
        image_id, path = self.images[self.index]
        pix = self._annotated_pixmap(image_id, path)
        if pix is None:
            self._canvas.setText(f"Cannot load\n{path}")
        else:
            scaled = pix.scaled(
                self._canvas.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._canvas.setPixmap(scaled)
        name = Path(path).name
        self.setWindowTitle(f"{name}  —  {self.index + 1}/{len(self.images)}")
        self._caption.setText(path)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._show()
