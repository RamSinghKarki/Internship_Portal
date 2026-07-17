"""PyInstaller entry point: launches the GUI directly.

When frozen, bundled data (models/, themes/) lives in sys._MEIPASS —
point the app there before anything reads config paths.
"""

import os
import sys


def main() -> int:
    if getattr(sys, "frozen", False):
        bundle = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        os.environ.setdefault("FACEVAULT_MODELS_DIR", os.path.join(bundle, "models"))

    from app.config import AppConfig
    from app.views.main_window import run_gui

    return run_gui(AppConfig.load())


if __name__ == "__main__":
    raise SystemExit(main())
