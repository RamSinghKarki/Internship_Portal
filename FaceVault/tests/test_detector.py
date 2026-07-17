"""Detection-mode tests against the real YuNet model.

Uses the same portrait fixture convention as test_e2e_scan.py
(tests/fixtures/ or FACEVAULT_TEST_IMAGE); skipped without it.
"""

import cv2
import numpy as np
import pytest

from app.ai.detector import FaceDetector, _mirror_row
from app.ai.recognizer import FaceRecognizer, cosine_similarity
from app.config import AppConfig
from tests.test_e2e_scan import _find_portrait

portrait = _find_portrait()
_cfg = AppConfig()

pytestmark = [
    pytest.mark.skipif(portrait is None, reason="no portrait fixture available"),
    pytest.mark.skipif(not _cfg.models_available(), reason="ONNX models not downloaded"),
]


@pytest.fixture(scope="module")
def img():
    image = cv2.imread(str(portrait))
    assert image is not None
    return image


def _detector(mode: str) -> FaceDetector:
    return FaceDetector(_cfg.detector_model, score_threshold=0.65, mode=mode)


def test_accurate_mode_merges_passes_without_duplicates(img):
    """Three passes over one face must still yield exactly the fast-mode
    face count — the IoU merge deduplicates across passes."""
    fast = _detector("fast").detect(img, min_face_size=36)
    accurate = _detector("accurate").detect(img, min_face_size=36)
    assert len(fast) >= 1
    assert len(accurate) == len(fast)


def test_accurate_mode_recovers_dark_faces(img):
    """A severely underexposed photo: the CLAHE pass should recover at
    least as many faces as fast mode finds."""
    dark = cv2.convertScaleAbs(img, alpha=0.22, beta=0)
    n_fast = len(_detector("fast").detect(dark, min_face_size=36))
    n_accurate = len(_detector("accurate").detect(dark, min_face_size=36))
    assert n_accurate >= max(n_fast, 1)


def test_accurate_mode_upscales_tiny_images(img):
    """A 240px copy: accurate mode upscales before detecting."""
    h, w = img.shape[:2]
    scale = 240 / max(h, w)
    tiny = cv2.resize(img, (int(w * scale), int(h * scale)),
                      interpolation=cv2.INTER_AREA)
    dets = _detector("accurate").detect(tiny, min_face_size=16)
    assert len(dets) >= 1


def test_mirrored_landmarks_still_align_for_embedding(img):
    """The mirror-pass row must produce a valid aligned embedding that
    matches the direct detection of the same face."""
    det = _detector("fast")
    rec = FaceRecognizer(_cfg.recognizer_model)

    direct = det.detect(img, min_face_size=36)
    assert direct

    flipped = cv2.flip(img, 1)
    self_run = det.detect(flipped, min_face_size=36)
    assert self_run
    mirrored_row = _mirror_row(self_run[0].raw, flipped.shape[1])
    mirrored = type(direct[0])(box=direct[0].box, score=self_run[0].score,
                               raw=mirrored_row)

    e_direct = rec.embed(img, direct[0])
    e_mirrored = rec.embed(img, mirrored)
    assert e_direct is not None and e_mirrored is not None
    # Same person, same photo: must be an extremely confident match.
    assert cosine_similarity(e_direct, e_mirrored) > 0.6
