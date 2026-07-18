"""Object detection — auto-tag photos with what's in them (dog, car, …).

YOLOv8n exported to ONNX (~13 MB, committed in models/), running on
ONNX Runtime with the shared GPU/CPU provider selection. Detected COCO
labels are stored per photo and become searchable tags: "dog", "bicycle",
"laptop", "cup" — no manual tagging.

Optional: scans work without the model file; tags just stay empty.
"""

from pathlib import Path

import cv2
import numpy as np

try:
    import onnxruntime as ort

    _HAS_ORT = True
except ImportError:
    _HAS_ORT = False

COCO_LABELS = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
    "truck", "boat", "traffic light", "fire hydrant", "stop sign",
    "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
    "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag",
    "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
    "baseball bat", "baseball glove", "skateboard", "surfboard",
    "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon",
    "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot",
    "hot dog", "pizza", "donut", "cake", "chair", "couch", "potted plant",
    "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote",
    "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear",
    "hair drier", "toothbrush",
]

_INPUT_SIZE = 640
_SCORE_THRESHOLD = 0.35
_NMS_THRESHOLD = 0.45


def objects_runtime_available() -> bool:
    return _HAS_ORT


class ObjectDetector:
    """Thread-safe: ONNX Runtime sessions may be shared across threads."""

    def __init__(self, model_path: Path):
        if not _HAS_ORT:
            raise RuntimeError("Object detection needs: pip install onnxruntime")
        from .runtime import ort_providers

        self._session = ort.InferenceSession(str(model_path), providers=ort_providers())
        self._input = self._session.get_inputs()[0].name

    def detect(self, image_bgr: np.ndarray) -> list[tuple[str, float]]:
        """Return unique (label, best_confidence) pairs found in the image."""
        h, w = image_bgr.shape[:2]
        scale = _INPUT_SIZE / max(h, w)
        nh, nw = round(h * scale), round(w * scale)
        resized = cv2.resize(image_bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)
        canvas = np.full((_INPUT_SIZE, _INPUT_SIZE, 3), 114, np.uint8)
        canvas[:nh, :nw] = resized

        blob = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        blob = blob.transpose(2, 0, 1)[None]
        (out,) = self._session.run(None, {self._input: blob})
        preds = out[0].T  # (8400, 84): cx, cy, w, h + 80 class scores

        class_scores = preds[:, 4:]
        class_ids = class_scores.argmax(axis=1)
        confidences = class_scores[np.arange(len(preds)), class_ids]
        keep = confidences >= _SCORE_THRESHOLD
        if not keep.any():
            return []

        boxes_xywh = preds[keep, :4]
        confidences = confidences[keep]
        class_ids = class_ids[keep]
        # cxcywh -> xywh for OpenCV NMS
        boxes = np.column_stack([
            boxes_xywh[:, 0] - boxes_xywh[:, 2] / 2,
            boxes_xywh[:, 1] - boxes_xywh[:, 3] / 2,
            boxes_xywh[:, 2], boxes_xywh[:, 3],
        ])
        idxs = cv2.dnn.NMSBoxes(
            boxes.tolist(), confidences.tolist(), _SCORE_THRESHOLD, _NMS_THRESHOLD
        )
        best: dict[str, float] = {}
        for i in np.array(idxs).flatten():
            label = COCO_LABELS[class_ids[i]]
            best[label] = max(best.get(label, 0.0), float(confidences[i]))
        return sorted(best.items(), key=lambda kv: -kv[1])
