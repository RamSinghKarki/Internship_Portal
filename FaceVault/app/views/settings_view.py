"""Settings: tune AI thresholds; persisted via AppConfig.save()."""

from PySide6.QtWidgets import (
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

        self.min_quality = QDoubleSpinBox()
        self.min_quality.setRange(0, 100)
        self.min_quality.setToolTip(
            "Faces below this quality are stored but not used for grouping."
        )

        self.det_threshold = QDoubleSpinBox()
        self.det_threshold.setRange(0.30, 0.99)
        self.det_threshold.setSingleStep(0.01)

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

        form.addRow("Face match threshold", self.match_threshold)
        form.addRow("Min quality for grouping", self.min_quality)
        form.addRow("Detection confidence", self.det_threshold)
        form.addRow("Min face size", self.min_face)
        form.addRow("Min faces per new person", self.min_cluster)
        form.addRow("Near-duplicate distance", self.near_dup)
        form.addRow("Worker threads", self.workers)
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

        note = QLabel(
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
        self.min_quality.setValue(c.min_cluster_quality)
        self.det_threshold.setValue(c.detection_score_threshold)
        self.min_face.setValue(c.min_face_size)
        self.min_cluster.setValue(c.min_cluster_size)
        self.near_dup.setValue(c.near_duplicate_distance)
        self.workers.setValue(c.worker_threads)

    def _save(self) -> None:
        c = self.config
        c.match_threshold = self.match_threshold.value()
        c.min_cluster_quality = self.min_quality.value()
        c.detection_score_threshold = self.det_threshold.value()
        c.min_face_size = self.min_face.value()
        c.min_cluster_size = self.min_cluster.value()
        c.near_duplicate_distance = self.near_dup.value()
        c.worker_threads = self.workers.value()
        c.save()
        self._status.setText("Saved ✓")
