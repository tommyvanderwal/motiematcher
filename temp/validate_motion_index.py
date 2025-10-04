"""Validation script for the generated motion index."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "bronmateriaal-onbewerkt" / "current" / "motion_index" / "motions_list.json"
SUMMARY_FILE = BASE_DIR / "bronmateriaal-onbewerkt" / "current" / "motion_index" / "motions_summary.json"
START_DATE = "2023-12-06"

NUMBER_PATTERN = re.compile(r"^\d{4}Z\d{5}$")

with INDEX_FILE.open("r", encoding="utf-8") as handle:
    motions = json.load(handle)

with SUMMARY_FILE.open("r", encoding="utf-8") as handle:
    summary = json.load(handle)

numbers = [m.get("nummer") for m in motions if m.get("nummer")]
unique_numbers = len(set(numbers))
invalid_numbers = [n for n in numbers if not NUMBER_PATTERN.match(n)]
bron_missing = [m["zaak_id"] for m in motions if not m.get("bronbestanden")]
start_dates = [m.get("gestart_op") for m in motions if m.get("gestart_op")]
start_dates.sort()

vergaderjaar_counts = Counter(m.get("vergaderjaar") for m in motions if m.get("vergaderjaar"))

print("Total motions:", len(motions))
print("Unique numbers:", unique_numbers)
print("Numbers without pattern:", len(invalid_numbers))
print("Motions missing source reference:", len(bron_missing))
print("Earliest gestart_op:", start_dates[0] if start_dates else None)
print("Latest gestart_op:", start_dates[-1] if start_dates else None)
print("Counts per vergaderjaar:")
for year, count in sorted(vergaderjaar_counts.items()):
    print(f"  {year}: {count}")

print("Summary total motions:", summary.get("total_motions"))
print("Summary duplicate numbers:", len(summary.get("duplicate_motion_numbers", [])))
print("Summary start filter:", summary.get("start_date_filter"))
