# FaceVault

Offline photo library manager with **local face recognition** — sort and
group your photos by the people in them, entirely on your own machine.

- **100% offline.** The AI models (YuNet detection + SFace embeddings,
  ~37 MB total, committed in `models/`) run on CPU via OpenCV. No cloud
  APIs, no accounts, no telemetry, zero network calls at runtime.
- **Desktop app** (PySide6, dark Lightroom-style UI) **and CLI** with full
  feature parity.
- Faces are detected, aligned, embedded and clustered into people you can
  rename, merge and export. Exact and near-duplicates are found
  automatically. Everything is searchable by person, camera, date, GPS and
  quality.

The desktop app has seven sections: **Dashboard** (library stats + scan
history), **Photos** (browse everything, filter by person/camera/unknown,
open in a viewer that outlines each face with its name), **People**
(auto-grouped person grid — rename, merge, export, browse), **Unknown
faces** (assign leftover faces to people manually or create new people),
**Albums** (curate collections from the Photos view), **Duplicates**
(exact + near), and **Settings** (all AI thresholds).

![Photos view](docs/screenshot-photos.png)
![Photo viewer with face overlays](docs/screenshot-viewer.png)

## Quick start

```bash
cd FaceVault
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# CLI
python -m app scan ~/Pictures        # detect faces, group people, find duplicates
python -m app people                 # list discovered people
python -m app rename 1 "Ram"         # name person 1
python -m app person 1               # all photos of Ram
python -m app merge 4 1              # person 4 was also Ram — merge
python -m app duplicates --near      # exact + near duplicate report
python -m app similar selfie.jpg     # who is this? search the library
python -m app search --person Ram --camera Sony --after 2025-01-01
python -m app export-person 1 ~/Desktop/Ram
python -m app stats

# Desktop app
python -m app gui
```

Re-scans are incremental — unchanged files are skipped, new photos are
matched against the people you already named.

Detection runs in **accurate** mode by default (multi-pass: high
resolution + contrast-enhanced + mirrored, merged — better on small,
dark and profile faces). For very large libraries use
`python -m app scan ~/Pictures --mode fast` (~3× quicker), or change the
default under Settings in the GUI.

Your library (database + thumbnails) lives in `~/.facevault` (override
with `--data-dir` or `FACEVAULT_DATA_DIR`). Original photos are never
moved or modified.

## How it works

```
scan folder ─► worker pool: decode → sha256 + dHash → EXIF
                            → YuNet face detection → SFace 128-d embedding
            ─► SQLite (WAL) ─► incremental clustering ─► People
```

New faces are first matched against existing person centroids (so named
people stay stable), and only the leftovers are clustered into new people.
Blurry or tiny faces are quality-gated out of grouping so they can't
corrupt clusters. Full design rationale: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Project layout

```
FaceVault/
├── app/
│   ├── ai/          # detector, recognizer, clustering, duplicates, quality, index
│   ├── database/    # SQLAlchemy models, session, queries
│   ├── services/    # scan, people, search, thumbnails, export
│   ├── workers/     # multi-threaded scan pipeline
│   ├── views/       # PySide6 screens (dashboard, people, duplicates, settings)
│   ├── widgets/     # sidebar, info panel
│   ├── themes/      # dark.qss
│   ├── utils/       # hashing, EXIF
│   └── __main__.py  # CLI
├── models/          # ONNX models (committed — offline out of the box)
├── docs/            # architecture
└── tests/           # unit + end-to-end (pytest)
```

## Build a standalone executable

To get a double-click app that doesn't need Python installed:

```bash
pip install pyinstaller
python build_app.py
```

The result is `dist/FaceVault/` — a self-contained folder (models and
theme bundled, still fully offline). Run the `FaceVault` executable
inside it, or zip the folder to move it to another machine with the same
OS. Build on the OS you're targeting (build on Windows to get a Windows
.exe, etc.).

## Tests

```bash
pip install pytest
python -m pytest tests/
```

The end-to-end test needs a real portrait photo: drop any portrait into
`tests/fixtures/` (git-ignored) or set `FACEVAULT_TEST_IMAGE=/path/to/portrait.jpg`.

## Privacy

Face embeddings are biometric data. FaceVault keeps everything on your
device, deletes derived face data when you delete an image, and your whole
library is a single folder you can back up — or completely erase — at any
time. Please respect the consent of people in the photos you index.
