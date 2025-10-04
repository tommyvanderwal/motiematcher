import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("motion_number")
parser.add_argument("--limit", type=int, default=1)
parser.add_argument("--include-votes", action="store_true")
args = parser.parse_args()

data_path = Path("bronmateriaal-onbewerkt/current/motion_index/motions_enriched.json")
records = json.loads(data_path.read_text(encoding="utf-8"))

matches = [r for r in records if r.get("motion_number") == args.motion_number]

if not matches:
    raise SystemExit(f"Motion {args.motion_number} not found")

for record in matches[: args.limit]:
    payload = {
        "motion_number": record.get("motion_number"),
        "motion_title": record.get("motion_title"),
        "vote_totals": record.get("vote_totals"),
        "vote_breakdown_count": len(record.get("vote_breakdown") or []),
        "decision_summaries": record.get("decision_summaries"),
    }
    if args.include_votes:
        payload["vote_breakdown"] = record.get("vote_breakdown")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
