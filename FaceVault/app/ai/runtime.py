"""Shared ONNX Runtime provider selection for every AI model.

Preference order:
  1. CUDAExecutionProvider  — NVIDIA cards via `pip install onnxruntime-gpu`
  2. DmlExecutionProvider   — any Windows GPU via `pip install onnxruntime-directml`
                              (easiest path for NVIDIA laptops: no CUDA install)
  3. CPUExecutionProvider   — always works, silently used as fallback

Note: only the ONNX-based models (ArcFace, CLIP, OCR) run on GPU. YuNet
detection and SFace run through OpenCV DNN, which is CPU-only in pip
builds — they are lightweight, so this costs little.
"""

_PREFERRED = ["CUDAExecutionProvider", "DmlExecutionProvider", "CPUExecutionProvider"]


def ort_providers() -> list[str]:
    import onnxruntime as ort

    available = ort.get_available_providers()
    chosen = [p for p in _PREFERRED if p in available]
    return chosen or ["CPUExecutionProvider"]


def gpu_summary() -> dict:
    """Diagnostics for the `gpu` CLI command and the Settings page."""
    try:
        import onnxruntime as ort
    except ImportError:
        return {
            "onnxruntime": None,
            "available": [],
            "active": "none (onnxruntime not installed)",
            "gpu": False,
        }
    available = ort.get_available_providers()
    active = ort_providers()[0]
    return {
        "onnxruntime": ort.__version__,
        "available": available,
        "active": active,
        "gpu": active != "CPUExecutionProvider",
    }
