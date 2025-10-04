#!/usr/bin/env python3
"""Ensure large archived snapshots are available as plain JSON locally.

GitHub enforces a 100 MB limit per file, so the repository stores hefty
`zaak_current_parliament_*.json` snapshots as ZIP archives. This helper unpacks
those archives back to JSON files for local analysis (for example with pandas).

Usage:
    python scripts/restore_large_snapshots.py [--force]

The script scans the `bronmateriaal-onbewerkt/current/zaak_current` directory,
extracts any `.zip` archive, and recreates the matching `.json` file when it is
missing. With `--force` it will overwrite existing JSON files.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile

BASE_DIR = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = BASE_DIR / "bronmateriaal-onbewerkt" / "current" / "zaak_current"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restore large zaak snapshots from ZIP archives")
    parser.add_argument("--force", action="store_true", help="Overwrite JSON files even if they already exist")
    return parser.parse_args()


def restore_snapshot(zip_path: Path, force: bool) -> Path:
    target_json = zip_path.with_suffix(".json")
    if target_json.exists() and not force:
        print(f"✅ {target_json.name} already present; skipping")
        return target_json

    with ZipFile(zip_path) as archive:
        members = [member for member in archive.namelist() if not member.endswith("/")]
        if not members:
            raise RuntimeError(f"Archive {zip_path.name} bevat geen bestanden")
        # Always extract into the same directory as the archive lives in
        extracted_path = Path(archive.extract(members[0], path=zip_path.parent))

    # `Compress-Archive` on Windows stores the filename without directories, but
    # we guard against unexpected structures just in case.
    if extracted_path != target_json:
        if target_json.exists() and force:
            target_json.unlink()
        extracted_path.rename(target_json)

    print(f"📦 Hersteld: {target_json.relative_to(BASE_DIR)}")
    return target_json


def main() -> None:
    args = parse_args()
    if not SNAPSHOT_DIR.exists():
        raise SystemExit(f"Snapshot map ontbreekt: {SNAPSHOT_DIR}")

    archives = sorted(SNAPSHOT_DIR.glob("*.zip"))
    if not archives:
        print("Geen ZIP-archieven gevonden om te herstellen.")
        return

    for archive in archives:
        try:
            restore_snapshot(archive, force=args.force)
        except Exception as exc:  # pragma: no cover - diagnostic output
            print(f"⚠️  Kon {archive.name} niet herstellen: {exc}")


if __name__ == "__main__":
    main()
