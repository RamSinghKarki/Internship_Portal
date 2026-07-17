"""Build a double-click FaceVault executable with PyInstaller.

Usage (from the FaceVault directory, inside your venv):

    pip install pyinstaller
    python build_app.py

Output lands in dist/FaceVault/ — a self-contained folder you can move
anywhere (or zip and share). The ONNX models and theme are bundled, so
the built app is fully offline, same as running from source.
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEP = ";" if sys.platform == "win32" else ":"


def main() -> int:
    models = ROOT / "models"
    if not (models / "face_detection_yunet_2023mar.onnx").is_file():
        print("Models missing — run models/download_models.py first.", file=sys.stderr)
        return 1

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--windowed",              # no console window on Windows/macOS
        "--name", "FaceVault",
        # Bundle models and theme next to the executable.
        "--add-data", f"{models}{SEP}models",
        "--add-data", f"{ROOT / 'app' / 'themes' / 'dark.qss'}{SEP}app/themes",
        # PySide6 pulls these automatically; OpenCV needs the hint.
        "--collect-binaries", "cv2",
        str(ROOT / "launcher.py"),
    ]
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode == 0:
        print(f"\nDone → {ROOT / 'dist' / 'FaceVault'}")
        print("Run the FaceVault executable inside that folder.")
        shutil.rmtree(ROOT / "build", ignore_errors=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
