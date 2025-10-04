import csv
import json
from pathlib import Path

summary_path = Path("bronmateriaal-onbewerkt/current/motion_votes/motion_votes_summary.json")
jsonl_path = Path("bronmateriaal-onbewerkt/current/motion_votes/motion_votes_flat.jsonl")
csv_path = Path("bronmateriaal-onbewerkt/current/motion_votes/motion_votes_flat.csv")

summary = json.loads(summary_path.read_text(encoding="utf-8"))
print(f"Summary motions: {len(summary)}")
print(f"Sample summary item: {summary[0]['motion_id'] if summary else 'N/A'}")

jsonl_count = sum(1 for _ in jsonl_path.open("r", encoding="utf-8"))
print(f"JSONL rows: {jsonl_count}")

with csv_path.open("r", encoding="utf-8") as handle:
    reader = csv.reader(handle)
    row_count = sum(1 for _ in reader)
print(f"CSV rows (incl header): {row_count}")
