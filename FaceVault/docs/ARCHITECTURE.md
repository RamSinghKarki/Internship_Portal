# FaceVault Architecture (improved)

This document takes the original "FaceVault Enterprise" design and improves
it section by section. Each improvement states **what changed and why**.
The codebase in this repository implements the v1 core of this design;
everything marked *roadmap* has a designed seam but no code yet.

---

## 1. Technology stack — the biggest change

| Component | Original spec | Improved (implemented) | Why |
| --- | --- | --- | --- |
| Detection | InsightFace | **YuNet** (OpenCV `FaceDetectorYN`) | InsightFace is accurate but heavy (onnxruntime + compiled Cython) and notoriously painful to package with PyInstaller. YuNet is a 230 KB ONNX model built into stock OpenCV — zero extra dependencies, few ms/image on CPU. |
| Embeddings | ArcFace (InsightFace) | **SFace** (OpenCV `FaceRecognizerSF`) | Same reasoning: 37 MB model, built-in alignment (`alignCrop`), published verification threshold, ships inside opencv-python. ArcFace remains a drop-in upgrade behind the same `FaceRecognizer.embed()` interface. |
| Vector search | FAISS (required) | **Brute-force NumPy, FAISS optional** | A normalized 128-d matrix dot product handles ~1M faces in tens of ms. FAISS is auto-enabled if installed and the library exceeds 50k vectors (`app/ai/indexing.py`). Making it optional keeps installation to 4 pure-pip packages. |
| Clustering | HDBSCAN | **Incremental centroid matching + union-find** | HDBSCAN re-clusters the whole library each scan — O(everything) every time, and person IDs are unstable between runs (cluster 7 today may be cluster 3 tomorrow, breaking user renames). The incremental design (§4) preserves identities and only pays for new faces. HDBSCAN is still right for the periodic *maintenance* re-cluster (roadmap). |
| Background tasks | multiprocessing | **ThreadPoolExecutor** | OpenCV releases the GIL during inference, so threads get real parallelism without pickling images across process boundaries. One model pair per thread (`threading.local`) because OpenCV DNN objects are not thread-safe. |
| Metadata | ExifTool / Pillow | **Pillow only** | ExifTool is an external Perl binary — a packaging liability. Pillow covers camera/lens/timestamp/GPS. |
| Offline | implied | **guaranteed** | Models are committed to the repo; the app performs zero network calls at runtime. This was the driving requirement. |

Everything else from the original stack is kept: PySide6, SQLite + SQLAlchemy,
Qt Style Sheets, pytest, PyInstaller as the packaging target.

## 2. Layered architecture — kept, with two rules added

```
Presentation (views/, widgets/, __main__.py CLI)
      │  calls services, never AI or DB directly
Service (services/)
      │  owns transactions and orchestration
AI (ai/)                 ← pure functions/classes, no DB imports
      │
Database (database/)     ← schema + queries, no AI imports
      │
Storage (SQLite + originals on disk + cache/)
```

Improvements over the original:

1. **The AI layer is DB-free and the DB layer is AI-free.** `ai/clustering.py`
   takes plain NumPy arrays and returns plain results. This is what makes the
   algorithms swappable (HDBSCAN, ArcFace) and unit-testable without fixtures.
2. **The CLI is a first-class presentation layer.** Every GUI feature exists
   headlessly (`python -m app scan|people|merge|similar|…`). This is how the
   pipeline is integration-tested, and it is the seam where the roadmap's
   client-server mode plugs in.

## 3. Database schema — kept, with fixes

The original schema was good. Changes:

| Change | Why |
| --- | --- |
| `faces.embedding` is a float32 BLOB **in the DB**, vector index is a rebuildable cache | The original put embeddings "in the vector database". If the index is the only home of embeddings, index corruption = re-scan a million photos. DB is the single source of truth; the index rebuilds from it in seconds. |
| `images` has **both** `file_hash` (sha256) and `phash` (dHash) | The spec had one `hash` column. Exact duplicates (same bytes) and near duplicates (resized/re-encoded) are different features needing different hashes; exact-dup detection becomes a pure SQL `GROUP BY`. |
| `images.mtime` + `size_bytes` | Enables incremental re-scans: unchanged files are skipped without reading them. The original had no incremental story ("Incremental AI indexing" was future roadmap — it needs to be v1, it's the difference between a 4-hour and a 4-second re-scan). |
| `faces.person_id` is `ON DELETE SET NULL` | Deleting a person must return its faces to the unknown pool, not delete biometric rows silently. Deleting an image cascades to its faces (the derived data has no meaning without the source). |
| Face pose columns (`yaw/pitch/roll`) dropped from v1 | YuNet doesn't output pose; storing always-null columns is noise. The quality score (§5) covers the "is this face usable" question pose was for. Add the columns in the migration that adds a pose model. |
| `scan_history` gains `skipped` / `failed` counts | Operational visibility: "5,000 files, 4,980 skipped, 3 failed" tells you what a scan actually did. |

Kept as designed: `persons`, `albums` + `image_albums`, `tags` + `image_tags`,
`settings` key/value.

**Migrations:** v1 creates the schema directly (`create_all`). The moment the
schema changes post-release, introduce Alembic — retrofitting migrations after
users have data is far harder than starting with them. *(roadmap)*

## 4. AI pipeline — same stages, two structural fixes

Original stage order kept:
validate → EXIF → hash → detect → align → embed → cluster → assign → persist.

**Fix 1 — identity assignment is two-phase and incremental** (`ai/clustering.py`):

```
new faces ──► phase 1: cosine vs existing person centroids ──► join person
                   │ (no match)
                   ▼
              phase 2: union-find clustering among leftovers
                   ├─ cluster ≥ min_cluster_size ──► new person
                   └─ smaller ──► stays "unknown", retried next scan
```

Why: person IDs must be *stable* — a user who renamed "Person 3" to "Ram"
must never see those faces re-shuffled by a later scan. Full re-clustering
(the original design) cannot guarantee that. The O(n²) phase-2 cost applies
only to new unassigned faces, not the library.

**Fix 2 — quality gating before clustering** (`ai/quality.py`):
every face gets a composite score (detector confidence 40%, Laplacian
sharpness 35%, resolution 25%). Low-quality faces are stored and searchable
but excluded from clustering — blurry 30-px faces produce embeddings near
the centroid of *everything* and will eventually chain-merge two real people.
This one rule is the difference between Google-Photos-like grouping and a
mess at scale.

**Threading model** (`workers/pipeline.py`), simplified from the original's
scanner-thread/queue/six-workers/db-writer diagram, keeping its intent:

```
discover (main) ──► ThreadPoolExecutor workers ──► generator ──► single DB writer
                    (decode, hash, EXIF,            (batched commits, WAL mode)
                     detect, embed — GIL released)
```

SQLite gets exactly one writer; readers are never blocked (WAL). No separate
writer thread is needed because the consuming loop *is* the writer.

## 5. Scope — the biggest correction to the original

The original lists 17 AI features and a 14-item roadmap. Building all of it
at once produces none of it working well. The improved scope ladder:

**v1 (implemented):** scan, EXIF, exact + near duplicates, face detection,
alignment, embeddings, quality scoring, incremental clustering,
rename/merge/delete people, similarity search ("find this face"),
structured search (person/camera/date/GPS/quality), person export, CSV
export, dashboard, people grid, duplicates view, settings, dark theme,
CLI parity.

**v2 (designed seams exist):** albums UI (tables already in the schema),
GPS map view (lat/lon already extracted), periodic HDBSCAN maintenance
re-cluster, FAISS at scale, Alembic, blur-aware best-photo picker.

**v3+ (roadmap, unchanged from original):** scene/object tagging, OCR,
semantic search (all three are one "CLIP-ish embedding per image" feature —
note: offline-compatible), age/gender/emotion (see §6), client-server mode,
S3/NAS sources, plugin system, PyInstaller packaging.

## 6. Privacy — missing from the original, now a design requirement

Face embeddings are **biometric data**. Consequences baked into the design:

- Everything stays on-device (also the offline requirement). No telemetry.
- Deleting an image cascades to its faces/embeddings; deleting a person
  never silently deletes biometric rows (SET NULL back to unknown).
- The whole library is one directory (`~/.facevault`) — trivial to back up,
  trivial to *fully delete*. Full-library encryption (SQLCipher) is roadmap.
- Age/gender/emotion estimation from the original feature list is
  deliberately **not** in scope for v1/v2: high misuse-to-utility ratio for
  a photo organizer, and in several jurisdictions it moves the product into
  a stricter regulatory class. Liveness detection was dropped entirely — it
  serves authentication systems, not photo libraries.

## 7. Testing — missing from the original

- **Unit**: clustering, duplicate grouping, quality scoring run on synthetic
  NumPy data — fast, deterministic, no models needed (`tests/test_*.py`).
- **Integration**: a real end-to-end scan (detect → embed → cluster → DB)
  against a real portrait, exercising incremental re-scan, exact-dup
  detection and person formation (`tests/test_e2e_scan.py`). Portrait
  fixtures are git-ignored — never commit real people's photos to a repo.
- **GUI**: offscreen smoke test (`QT_QPA_PLATFORM=offscreen`) instantiating
  every view against a scanned library.

## 8. Original ideas kept verbatim

Layered architecture; folder layout (`ai/ services/ database/ workers/
views/ widgets/ themes/ utils/`); sidebar + grid + info-panel desktop
layout; dashboard tiles; people grid with counts; merge/rename/verified
flags; scan history; settings as data; dark Lightroom-like theme; SQLite
now with a clean path to PostgreSQL later (SQLAlchemy abstracts the
dialect); "personal app growing into multi-user without redesign".
