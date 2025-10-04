import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DATA_PATH = Path("bronmateriaal-onbewerkt/current/motion_index/motions_enriched.json")

records = json.loads(DATA_PATH.read_text(encoding="utf-8"))

TARGET_DATES = {"2025-10-02", "2025-10-03"}

matches = []
missing_votes = []
for record in records:
    motion_date = record.get("motion", {}).get("GestartOp") or record.get("motion_date")
    if not motion_date:
        continue
    try:
        date_only = motion_date[:10]
    except Exception:
        continue
    if date_only not in TARGET_DATES:
        continue
    matches.append(record)
    if not record.get("vote_breakdown"):
        missing_votes.append(record.get("motion_number"))

print(f"Total motions on target dates: {len(matches)}")
print(f"Motions missing vote_breakdown: {len(missing_votes)}")
if missing_votes:
    print("Missing vote breakdown for motions:")
    for num in missing_votes:
        print(f"  - {num}")

# Summaries per date
counts_by_date = defaultdict(int)
with_votes_by_date = defaultdict(int)
for record in matches:
    motion_date = record.get("motion", {}).get("GestartOp") or record.get("motion_date")
    date_only = motion_date[:10]
    counts_by_date[date_only] += 1
    if record.get("vote_breakdown"):
        with_votes_by_date[date_only] += 1

print("Counts by date:")
for date in sorted(counts_by_date):
    print(
        f"  {date}: total {counts_by_date[date]}, with votes {with_votes_by_date[date]}"
    )
