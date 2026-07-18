"""Settings: tune AI thresholds; persisted via AppConfig.save()."""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..config import AppConfig


class SettingsView(QWidget):
    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setObjectName("heading")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.match_threshold = QDoubleSpinBox()
        self.match_threshold.setRange(0.20, 0.90)
        self.match_threshold.setSingleStep(0.01)
        self.match_threshold.setToolTip(
            "Cosine similarity needed to treat two faces as the same person.\n"
            "Higher = stricter grouping (fewer false merges, more split people)."
        )

        self.match_margin = QDoubleSpinBox()
        self.match_margin.setRange(0.0, 0.30)
        self.match_margin.setSingleStep(0.01)
        self.match_margin.setToolTip(
            "Look-alike protection: a face is auto-assigned only when its best\n"
            "match beats the runner-up person by this much. Raise it if similar-\n"
            "looking people get merged; ambiguous faces go to Unknown instead."
        )

        self.min_quality = QDoubleSpinBox()
        self.min_quality.setRange(0, 100)
        self.min_quality.setToolTip(
            "Faces below this quality are stored but not used for grouping."
        )

        self.det_threshold = QDoubleSpinBox()
        self.det_threshold.setRange(0.30, 0.99)
        self.det_threshold.setSingleStep(0.01)

        self.det_mode = QComboBox()
        self.det_mode.addItem("Accurate — multi-pass, finds small/dark/profile faces", "accurate")
        self.det_mode.addItem("Fast — single pass, ~3x quicker scans", "fast")

        self.min_face = QSpinBox()
        self.min_face.setRange(16, 300)
        self.min_face.setSuffix(" px")

        self.min_cluster = QSpinBox()
        self.min_cluster.setRange(1, 10)
        self.min_cluster.setToolTip("Faces required before a new person is auto-created.")

        self.near_dup = QSpinBox()
        self.near_dup.setRange(0, 16)
        self.near_dup.setToolTip("Max dHash bit distance for near-duplicates.")

        self.workers = QSpinBox()
        self.workers.setRange(1, 32)

        self.ocr_enabled = QCheckBox("Extract text from photos during scans")
        self.ocr_enabled.setToolTip(
            "Makes documents/receipts/screenshots searchable by their text.\n"
            "Slows scanning; needs `pip install rapidocr-onnxruntime`."
        )

        self.objects_enabled = QCheckBox("Auto-tag objects during scans")
        self.objects_enabled.setToolTip(
            "Detects objects (dog, car, laptop…) so photos are searchable\n"
            "by what's in them. Needs the YOLO model in models/."
        )

        form.addRow("Face match threshold", self.match_threshold)
        form.addRow("Look-alike margin", self.match_margin)
        form.addRow("Min quality for grouping", self.min_quality)
        form.addRow("Detection mode", self.det_mode)
        form.addRow("Detection confidence", self.det_threshold)
        form.addRow("Min face size", self.min_face)
        form.addRow("Min faces per new person", self.min_cluster)
        form.addRow("Near-duplicate distance", self.near_dup)
        form.addRow("Worker threads", self.workers)
        form.addRow("OCR", self.ocr_enabled)
        form.addRow("Objects", self.objects_enabled)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        save = QPushButton("Save")
        save.setObjectName("primary")
        save.clicked.connect(self._save)
        self._status = QLabel("")
        self._status.setObjectName("subtle")
        buttons.addWidget(save)
        buttons.addWidget(self._status)
        buttons.addStretch()
        layout.addLayout(buttons)

        from ..ai.runtime import gpu_summary

        gpu = gpu_summary()
        gpu_note = (
            f"AI compute: {gpu['active']}"
            + ("" if gpu["gpu"] else
               "  (CPU — for your GPU: pip install onnxruntime-directml on "
               "Windows, or onnxruntime-gpu for NVIDIA CUDA)")
        )
        model = config.active_recognition()
        model_note = (
            "ArcFace 512-d (best look-alike separation)" if model == "arcface"
            else "SFace 128-d — for better look-alike separation run\n"
                 "python models/download_models.py --arcface, then scan --full"
        )
        note = QLabel(
            f"Face recognition model: {model_note}\n"
            f"{gpu_note}\n"
            "Changes apply to future scans and re-clustering. "
            f"Library location: {config.data_dir}"
        )
        note.setObjectName("subtle")
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()

        self._load()

    def _load(self) -> None:
        c = self.config
        self.match_threshold.setValue(c.match_threshold)
        self.match_margin.setValue(c.match_margin)
        self.min_quality.setValue(c.min_cluster_quality)
        self.det_threshold.setValue(c.detection_score_threshold)
        self.det_mode.setCurrentIndex(max(0, self.det_mode.findData(c.detection_mode)))
        self.min_face.setValue(c.min_face_size)
        self.min_cluster.setValue(c.min_cluster_size)
        self.near_dup.setValue(c.near_duplicate_distance)
        self.workers.setValue(c.worker_threads)
        self.ocr_enabled.setChecked(c.ocr_enabled)
        self.objects_enabled.setChecked(c.objects_enabled)

    def _save(self) -> None:
        c = self.config
        c.match_threshold = self.match_threshold.value()
        c.match_margin = self.match_margin.value()
        c.min_cluster_quality = self.min_quality.value()
        c.detection_score_threshold = self.det_threshold.value()
        c.detection_mode = self.det_mode.currentData()
        c.min_face_size = self.min_face.value()
        c.min_cluster_size = self.min_cluster.value()
        c.near_duplicate_distance = self.near_dup.value()
        c.worker_threads = self.workers.value()
        c.ocr_enabled = self.ocr_enabled.isChecked()
        c.objects_enabled = self.objects_enabled.isChecked()
        c.save()
        self._status.setText("Saved ✓")
