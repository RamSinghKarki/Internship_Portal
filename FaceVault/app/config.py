"""Application configuration.

Configuration precedence: explicit kwargs > environment variables > defaults.
Everything lives under a single data directory so the whole library
(DB + caches) can be backed up or moved as one unit.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


@dataclass
class AppConfig:
    # Storage
    data_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("FACEVAULT_DATA_DIR", Path.home() / ".facevault")
        )
    )
    models_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("FACEVAULT_MODELS_DIR", PROJECT_ROOT / "models")
        )
    )

    # AI thresholds
    # Cosine similarity above which two SFace embeddings are considered the
    # same person. 0.363 is the OpenCV-published verification threshold; we
    # default slightly higher to favour precision when auto-grouping.
    match_threshold: float = 0.40
    # Faces below this composite quality score (0-100) are stored but not
    # used for clustering, so blurry/tiny faces don't pollute person groups.
    min_cluster_quality: float = 40.0
    detection_score_threshold: float = 0.65
    min_face_size: int = 36  # px, smaller detections are ignored
    min_cluster_size: int = 2  # faces needed to auto-create a person
    # Hamming distance (on 64-bit dHash) at or below which two images are
    # flagged as near-duplicates.
    near_duplicate_distance: int = 5

    # Processing
    worker_threads: int = max(2, (os.cpu_count() or 4) - 1)
    write_batch_size: int = 32

    # Thumbnails
    thumbnail_size: int = 512
    face_thumbnail_size: int = 160

    @property
    def db_path(self) -> Path:
        return self.data_dir / "facevault.db"

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"

    @property
    def thumbs_dir(self) -> Path:
        return self.cache_dir / "thumbs"

    @property
    def faces_dir(self) -> Path:
        return self.cache_dir / "faces"

    @property
    def detector_model(self) -> Path:
        return self.models_dir / "face_detection_yunet_2023mar.onnx"

    @property
    def recognizer_model(self) -> Path:
        return self.models_dir / "face_recognition_sface_2021dec.onnx"

    @property
    def settings_file(self) -> Path:
        return self.data_dir / "settings.json"

    def ensure_dirs(self) -> None:
        for d in (self.data_dir, self.cache_dir, self.thumbs_dir, self.faces_dir):
            d.mkdir(parents=True, exist_ok=True)

    def models_available(self) -> bool:
        return self.detector_model.is_file() and self.recognizer_model.is_file()

    # Tunable settings persist as JSON so the GUI settings page and CLI
    # share them across runs. Paths are intentionally not persisted.
    _PERSISTED = (
        "match_threshold",
        "min_cluster_quality",
        "detection_score_threshold",
        "min_face_size",
        "min_cluster_size",
        "near_duplicate_distance",
        "worker_threads",
    )

    def save(self) -> None:
        self.ensure_dirs()
        data = {k: getattr(self, k) for k in self._PERSISTED}
        self.settings_file.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, data_dir: Path | None = None) -> "AppConfig":
        cfg = cls() if data_dir is None else cls(data_dir=Path(data_dir))
        if cfg.settings_file.is_file():
            try:
                stored = json.loads(cfg.settings_file.read_text())
                for k in cls._PERSISTED:
                    if k in stored:
                        setattr(cfg, k, stored[k])
            except (json.JSONDecodeError, OSError):
                pass  # corrupt settings fall back to defaults
        return cfg

    def as_dict(self) -> dict:
        d = asdict(self)
        d["data_dir"] = str(self.data_dir)
        d["models_dir"] = str(self.models_dir)
        return d
