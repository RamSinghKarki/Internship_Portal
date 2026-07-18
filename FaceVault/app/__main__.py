"""FaceVault command line interface.

Every GUI feature is also reachable headlessly:

    python -m app scan ~/Pictures
    python -m app people
    python -m app rename 3 "Ram"
    python -m app merge 5 3
    python -m app duplicates --near
    python -m app similar query.jpg
    python -m app stats
    python -m app gui
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from .config import AppConfig
from .database.repository import Repository
from .database.session import create_session_factory


def _services(args):
    cfg = AppConfig.load(data_dir=args.data_dir)
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    return cfg, factory


def _fmt_dt(dt) -> str:
    return dt.strftime("%Y-%m-%d") if dt else "-"


def cmd_scan(args) -> int:
    from .services.scan_service import ScanService

    cfg, factory = _services(args)
    if args.mode:
        cfg.detection_mode = args.mode

    def progress(done: int, total: int, path: str) -> None:
        name = Path(path).name
        print(f"\r[{done}/{total}] {name[:60]:<60}", end="", flush=True)

    summary = ScanService(cfg, factory).scan(
        Path(args.folder), progress=progress, full_rescan=args.full
    )
    print()
    print(f"Scanned:        {summary['folder']}")
    print(f"Files found:    {summary['total_files']}")
    print(f"New/updated:    {summary['new_images']}  (skipped {summary['skipped']} unchanged, {summary['failed']} failed)")
    print(f"Faces detected: {summary['faces_found']}")
    print(f"Matched to existing people: {summary['faces_matched']}")
    print(f"New people discovered:      {summary['new_people']}")
    print(f"Still unknown faces:        {summary['unknown_faces']}")
    return 0


def cmd_people(args) -> int:
    from .services.people_service import PeopleService

    cfg, factory = _services(args)
    people = PeopleService(cfg, factory).list_people()
    if not people:
        print("No people yet — run a scan first.")
        return 0
    print(f"{'ID':>4}  {'Name':<24} {'Faces':>6}  Verified")
    for p in people:
        print(f"{p['id']:>4}  {p['name']:<24} {p['face_count']:>6}  {'yes' if p['verified'] else ''}")
    return 0


def cmd_person(args) -> int:
    from .services.people_service import PeopleService

    cfg, factory = _services(args)
    d = PeopleService(cfg, factory).person_detail(args.id)
    print(f"{d['name']}  (id {d['id']}{', verified' if d['verified'] else ''})")
    print(f"Photos: {d['photo_count']}   Faces: {d['face_count']}   Avg quality: {d['avg_quality']}")
    print(f"First seen: {_fmt_dt(d['first_seen'])}   Last seen: {_fmt_dt(d['last_seen'])}")
    for _id, path in d["images"]:
        print(f"  {path}")
    return 0


def cmd_rename(args) -> int:
    from .services.people_service import PeopleService

    cfg, factory = _services(args)
    PeopleService(cfg, factory).rename(args.id, args.name)
    print(f"Person {args.id} renamed to {args.name!r}")
    return 0


def cmd_merge(args) -> int:
    from .services.people_service import PeopleService

    cfg, factory = _services(args)
    PeopleService(cfg, factory).merge(args.source, args.target)
    print(f"Merged person {args.source} into {args.target}")
    return 0


def cmd_duplicates(args) -> int:
    cfg, factory = _services(args)
    with factory() as session:
        repo = Repository(session)
        groups = repo.exact_duplicate_groups()
        print(f"Exact duplicate groups: {len(groups)}")
        for g in groups:
            print(f"  [{g[0].file_hash[:12]}]")
            for img in g:
                print(f"    {img.path}")
        if args.near:
            from .ai.duplicate_detector import near_duplicate_groups
            from .database.models import Image

            items = repo.images_with_phash()
            near = near_duplicate_groups(items, max_distance=cfg.near_duplicate_distance)
            print(f"Near-duplicate groups: {len(near)}")
            for group in near:
                print("  group:")
                for image_id in group:
                    img = session.get(Image, image_id)
                    if img:
                        print(f"    {img.path}")
    return 0


def cmd_stats(args) -> int:
    cfg, factory = _services(args)
    with factory() as session:
        st = Repository(session).stats()
    print(f"Images:                 {st['images']:,}")
    print(f"Faces:                  {st['faces']:,}")
    print(f"People:                 {st['people']:,}")
    print(f"Unknown faces:          {st['unknown_faces']:,}")
    print(f"Exact duplicate groups: {st['exact_duplicate_groups']:,}")
    if cfg.db_path.is_file():
        print(f"Database size:          {cfg.db_path.stat().st_size / 1024:,.0f} KB")
    last = st["last_scan"]
    if last:
        print(f"Last scan:              {last.folder} ({last.status}, {last.new_images} new)")
    return 0


def cmd_semantic_index(args) -> int:
    from .services.search_service import SearchService

    cfg, factory = _services(args)
    def progress(done, total, path):
        print(f"\r[{done}/{total}] {Path(path).name[:60]:<60}", end="", flush=True)
    n = SearchService(cfg, factory).semantic_backfill(progress=progress)
    print(f"\nSemantically indexed {n} photo(s).")
    return 0


def cmd_search(args) -> int:
    from .services.search_service import SearchService

    cfg, factory = _services(args)
    if args.describe:
        hits = SearchService(cfg, factory).semantic_search(args.describe)
        print(f"{len(hits)} match(es) for {args.describe!r}")
        for img, score in hits:
            print(f"  {score:.3f}  {img.path}")
        return 0
    parse = lambda s: datetime.strptime(s, "%Y-%m-%d") if s else None
    images = SearchService(cfg, factory).search_images(
        person_name=args.person,
        camera=args.camera,
        taken_after=parse(args.after),
        taken_before=parse(args.before),
        min_quality=args.min_quality,
        has_gps=args.gps or None,
        unknown_faces_only=args.unknown,
    )
    print(f"{len(images)} result(s)")
    for img in images:
        print(f"  {_fmt_dt(img.taken_at)}  {img.camera or '-':<24} {img.path}")
    return 0


def cmd_similar(args) -> int:
    from .services.search_service import SearchService

    cfg, factory = _services(args)
    svc = SearchService(cfg, factory)
    n = svc.rebuild_index()
    print(f"Index built over {n} faces")
    hits = svc.find_similar_faces(Path(args.image), k=args.k)
    if not hits:
        print("No face found in the query image, or the library is empty.")
        return 1
    for h in hits:
        who = h["person"] or "unknown"
        print(f"  {h['similarity']:.3f}  {who:<20} {h['image_path']}")
    return 0


def cmd_export_people(args) -> int:
    from .services.export_service import ExportService

    cfg, factory = _services(args)
    result = ExportService(cfg, factory).export_people_to_folders(
        Path(args.dest), include_unknown=args.include_unknown
    )
    print(f"Copied {result['copied']} photo(s) into {len(result['folders'])} folder(s):")
    for folder, n in sorted(result["folders"].items()):
        print(f"  {folder}/  ({n} photos)")
    return 0


def cmd_rescan(args) -> int:
    from .services.scan_service import ScanService

    cfg, factory = _services(args)
    with factory() as session:
        folders = Repository(session).scanned_folders()
    if not folders:
        print("No previously scanned folders.")
        return 0
    scan = ScanService(cfg, factory)
    for folder in folders:
        if not Path(folder).is_dir():
            print(f"skipping missing folder: {folder}")
            continue
        summary = scan.scan(Path(folder))
        print(f"{folder}: {summary['new_images']} new, "
              f"{summary['skipped']} unchanged, {summary['faces_found']} faces")
    return 0


def cmd_export_person(args) -> int:
    from .services.export_service import ExportService

    cfg, factory = _services(args)
    n = ExportService(cfg, factory).export_person_photos(args.id, Path(args.dest))
    print(f"Copied {n} photo(s) to {args.dest}")
    return 0


def cmd_export_csv(args) -> int:
    from .services.export_service import ExportService

    cfg, factory = _services(args)
    n = ExportService(cfg, factory).export_images_csv(Path(args.dest))
    print(f"Wrote {n} row(s) to {args.dest}")
    return 0


def cmd_gui(args) -> int:
    try:
        from .views.main_window import run_gui
    except ImportError as exc:
        print("PySide6 is required for the GUI: pip install PySide6", file=sys.stderr)
        print(f"({exc})", file=sys.stderr)
        return 1
    cfg = AppConfig.load(data_dir=args.data_dir)
    return run_gui(cfg)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="facevault",
        description="FaceVault — offline photo library with local face recognition",
    )
    parser.add_argument("--data-dir", default=None,
                        help="library location (default: ~/.facevault)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("scan", help="scan a folder for photos and faces")
    p.add_argument("folder")
    p.add_argument("--full", action="store_true", help="reprocess unchanged files too")
    p.add_argument("--mode", choices=["fast", "accurate"],
                   help="detection mode for this scan (default: settings)")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("people", help="list discovered people")
    p.set_defaults(func=cmd_people)

    p = sub.add_parser("person", help="show one person's photos")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_person)

    p = sub.add_parser("rename", help="name a person")
    p.add_argument("id", type=int)
    p.add_argument("name")
    p.set_defaults(func=cmd_rename)

    p = sub.add_parser("merge", help="merge person SOURCE into TARGET")
    p.add_argument("source", type=int)
    p.add_argument("target", type=int)
    p.set_defaults(func=cmd_merge)

    p = sub.add_parser("duplicates", help="list duplicate photos")
    p.add_argument("--near", action="store_true", help="also find near-duplicates")
    p.set_defaults(func=cmd_duplicates)

    p = sub.add_parser("stats", help="library statistics")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("search", help="search the library")
    p.add_argument("--person")
    p.add_argument("--camera")
    p.add_argument("--after", help="YYYY-MM-DD")
    p.add_argument("--before", help="YYYY-MM-DD")
    p.add_argument("--min-quality", type=float)
    p.add_argument("--gps", action="store_true", help="only geotagged photos")
    p.add_argument("--unknown", action="store_true", help="photos with unknown faces")
    p.add_argument("--describe",
                   help='semantic AI search, e.g. --describe "sunset at the beach"')
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("semantic-index",
                       help="compute semantic embeddings for photos scanned "
                            "before CLIP models were installed")
    p.set_defaults(func=cmd_semantic_index)

    p = sub.add_parser("similar", help="find library faces similar to a query image")
    p.add_argument("image")
    p.add_argument("-k", type=int, default=10)
    p.set_defaults(func=cmd_similar)

    p = sub.add_parser(
        "export-people",
        help="copy the library into one folder per person (Google-Photos style)",
    )
    p.add_argument("dest")
    p.add_argument("--include-unknown", action="store_true",
                   help="also export photos whose faces are all unknown")
    p.set_defaults(func=cmd_export_people)

    p = sub.add_parser("rescan", help="re-scan every previously scanned folder")
    p.set_defaults(func=cmd_rescan)

    p = sub.add_parser("export-person", help="copy a person's photos to a folder")
    p.add_argument("id", type=int)
    p.add_argument("dest")
    p.set_defaults(func=cmd_export_person)

    p = sub.add_parser("export-csv", help="export image metadata to CSV")
    p.add_argument("dest")
    p.set_defaults(func=cmd_export_csv)

    p = sub.add_parser("gui", help="launch the desktop app")
    p.set_defaults(func=cmd_gui)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, FileNotFoundError, NotADirectoryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
