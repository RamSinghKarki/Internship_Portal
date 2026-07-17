# AI models

FaceVault runs entirely offline using two small ONNX models from the
[OpenCV Zoo](https://github.com/opencv/opencv_zoo) (Apache-2.0):

| File | Purpose | Size |
| --- | --- | --- |
| `face_detection_yunet_2023mar.onnx` | YuNet face detection (boxes + 5 landmarks) | ~230 KB |
| `face_recognition_sface_2021dec.onnx` | SFace 128-d face embeddings | ~37 MB |

Both files are committed to this repository, so a fresh clone works
offline immediately — no downloads at runtime, ever.

If you need to re-fetch them (new clone without LFS, corrupted file),
run once while online:

```bash
python models/download_models.py
```

To use a different location set `FACEVAULT_MODELS_DIR`.
