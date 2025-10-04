"""Inspect sample vote files to confirm multiple votes per besluit are retained."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def main() -> None:
    sample_dir = Path("temp/stemming_enriched_test")
    if not sample_dir.exists():
        raise SystemExit("Sample directory temp/stemming_enriched_test not found")

    besluit_counts: Counter[str] = Counter()

    for file_path in sorted(sample_dir.glob("*.json")):
        with file_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        records = payload.get("value", [])
        for record in records:
            besluit_id = record.get("Besluit_Id")
            if not besluit_id:
                besluit = record.get("Besluit") or {}
                besluit_id = besluit.get("Id")
            if besluit_id:
                besluit_counts[besluit_id] += 1

    print("Top besluit vote counts:")
    for besluit_id, count in besluit_counts.most_common(5):
        print(f"  {besluit_id}: {count}")

    large_counts = [(bid, cnt) for bid, cnt in besluit_counts.items() if cnt >= 13]
    print(f"Decisions with >=13 votes: {len(large_counts)}")
    for besluit_id, count in large_counts[:10]:
        print(f"  {besluit_id}: {count}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - manual inspection helper
        print(f"Error while inspecting sample votes: {exc}")
        raise
