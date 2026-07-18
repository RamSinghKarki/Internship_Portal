"""Photo editor dialog: rotate, flip, crop, adjust, auto-enhance.

Edits always save as a copy next to the original, which is then indexed
into the library immediately (faces, duplicates, semantic embedding).
"""

from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRubberBand,
    QSlider,
    QVBoxLayout,
)

from ..services import edit_service
from ..utils.hashing import load_image_bgr


def _to_pixmap(img: np.ndarray) -> QPixmap:
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, _ = rgb.shape
    return QPixmap.fromImage(QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888))


class _CropLabel(QLabel):
    """Preview label with rubber-band crop selection."""

    crop_selected = Signal(QRect)  # in label coordinates

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self._band: QRubberBand | None = None
        self._origin = QPoint()
        self.crop_mode = False

    def mousePressEvent(self, e):
        if self.crop_mode and e.button() == Qt.LeftButton:
            self._origin = e.position().toPoint()
            if self._band is None:
                self._band = QRubberBand(QRubberBand.Rectangle, self)
            self._band.setGeometry(QRect(self._origin, self._origin))
            self._band.show()

    def mouseMoveEvent(self, e):
        if self.crop_mode and self._band is not None:
            self._band.setGeometry(
                QRect(self._origin, e.position().toPoint()).normalized()
            )

    def mouseReleaseEvent(self, e):
        if self.crop_mode and self._band is not None:
            rect = self._band.geometry()
            self._band.hide()
            self.crop_mode = False
            if rect.width() > 8 and rect.height() > 8:
                self.crop_selected.emit(rect)


class PhotoEditorDialog(QDialog):
    saved = Signal(str)  # path of the saved copy

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = Path(image_path)
        self.setWindowTitle(f"Edit — {self.image_path.name}")
        self.resize(1000, 760)

        self._original = load_image_bgr(self.image_path)
        if self._original is None:
            raise ValueError(f"Cannot load {image_path}")
        # `_base` carries geometry ops (rotate/flip/crop); sliders apply on top.
        self._base = self._original.copy()
        self._enhanced = False

        layout = QVBoxLayout(self)
        self._canvas = _CropLabel()
        self._canvas.setMinimumSize(400, 300)
        self._canvas.crop_selected.connect(self._apply_crop)
        layout.addWidget(self._canvas, stretch=1)

        tools = QHBoxLayout()
        for label, slot in (
            ("⟲ Rotate left", lambda: self._geometry(edit_service.rotate90, False)),
            ("⟳ Rotate right", lambda: self._geometry(edit_service.rotate90, True)),
            ("⇋ Flip", lambda: self._geometry(edit_service.flip_horizontal)),
        ):
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            tools.addWidget(btn)
        crop_btn = QPushButton("✂ Crop (drag on photo)")
        crop_btn.clicked.connect(self._enter_crop_mode)
        tools.addWidget(crop_btn)
        enhance_btn = QPushButton("✨ Auto-enhance")
        enhance_btn.clicked.connect(self._toggle_enhance)
        tools.addWidget(enhance_btn)
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self._reset)
        tools.addWidget(reset_btn)
        tools.addStretch()
        layout.addLayout(tools)

        sliders = QHBoxLayout()
        self._sliders: dict[str, QSlider] = {}
        for name in ("Brightness", "Contrast", "Saturation"):
            sliders.addWidget(QLabel(name))
            s = QSlider(Qt.Horizontal)
            s.setRange(-100, 100)
            s.setValue(0)
            s.valueChanged.connect(self._render)
            self._sliders[name.lower()] = s
            sliders.addWidget(s)
        layout.addLayout(sliders)

        actions = QHBoxLayout()
        save_btn = QPushButton("💾 Save as copy")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save)
        self._status = QLabel("Edits never modify the original file.")
        self._status.setObjectName("subtle")
        actions.addWidget(save_btn)
        actions.addWidget(self._status)
        actions.addStretch()
        layout.addLayout(actions)

        self._render()

    # ---- pipeline: base (geometry) -> enhance -> sliders --------------
    def _current(self) -> np.ndarray:
        img = edit_service.auto_enhance(self._base) if self._enhanced else self._base
        return edit_service.adjust(
            img,
            brightness=self._sliders["brightness"].value(),
            contrast=self._sliders["contrast"].value(),
            saturation=self._sliders["saturation"].value(),
        )

    def _render(self) -> None:
        pix = _to_pixmap(self._current())
        self._scaled = pix.scaled(
            self._canvas.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._canvas.setPixmap(self._scaled)

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self._render()

    def _geometry(self, op, *args) -> None:
        self._base = op(self._base, *args)
        self._render()

    def _toggle_enhance(self) -> None:
        self._enhanced = not self._enhanced
        self._status.setText(
            "Auto-enhance ON" if self._enhanced else "Auto-enhance off"
        )
        self._render()

    def _reset(self) -> None:
        self._base = self._original.copy()
        self._enhanced = False
        for s in self._sliders.values():
            s.blockSignals(True)
            s.setValue(0)
            s.blockSignals(False)
        self._status.setText("Reset to original.")
        self._render()

    def _enter_crop_mode(self) -> None:
        self._canvas.crop_mode = True
        self._status.setText("Drag a rectangle on the photo to crop.")

    def _apply_crop(self, rect: QRect) -> None:
        """Map the label-space rectangle back to image coordinates."""
        pix = self._scaled
        # Offset of the (centered) pixmap inside the label.
        off_x = (self._canvas.width() - pix.width()) // 2
        off_y = (self._canvas.height() - pix.height()) // 2
        scale = self._base.shape[1] / pix.width()
        x = int((rect.x() - off_x) * scale)
        y = int((rect.y() - off_y) * scale)
        w = int(rect.width() * scale)
        h = int(rect.height() * scale)
        self._base = edit_service.crop(self._current(), x, y, w, h)
        # Crop bakes in the current look; reset the adjustment layers.
        self._enhanced = False
        for s in self._sliders.values():
            s.blockSignals(True)
            s.setValue(0)
            s.blockSignals(False)
        self._status.setText("Cropped.")
        self._render()

    def _save(self) -> None:
        try:
            saved = edit_service.save_copy(self.image_path, self._current())
        except (IOError, OSError) as exc:
            QMessageBox.critical(self, "Save failed", str(exc))
            return
        self.saved.emit(str(saved))
        QMessageBox.information(
            self, "Saved", f"Saved as {saved.name} next to the original."
        )
        self.accept()
