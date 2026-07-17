from pathlib import Path

THEMES_DIR = Path(__file__).resolve().parent


def load_theme(name: str = "dark") -> str:
    qss = THEMES_DIR / f"{name}.qss"
    return qss.read_text() if qss.is_file() else ""
