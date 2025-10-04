import json
from pathlib import Path

DATA_PATH = Path("bronmateriaal-onbewerkt/current/motion_index/motions_enriched.json")
TARGET_COUNT = 3

records = json.loads(DATA_PATH.read_text(encoding="utf-8"))

candidates = []
for record in records:
    votes = record.get("vote_breakdown") or []
    totals = record.get("vote_totals") or {}
    if not totals:
        continue
    if len(votes) <= 1:
        besluit_ids = []
        for summary in record.get("decision_summaries") or []:
            besluit_id = summary.get("Besluit", {}).get("Id")
            if besluit_id:
                besluit_ids.append(besluit_id)
        candidates.append(
            {
                "motion_number": record.get("motion_number"),
                "motion_title": record.get("motion_title"),
                "vote_total_for": totals.get("Voor"),
                "vote_total_against": totals.get("Tegen"),
                "vote_breakdown_count": len(votes),
                "decision_summaries_count": len(record.get("decision_summaries") or []),
                "decision_besluit_ids": besluit_ids,
            }
        )
        if len(candidates) >= TARGET_COUNT:
            break

if not candidates:
    raise SystemExit("No low-vote motions found")

for idx, info in enumerate(candidates, start=1):
    print(f"Sample {idx}:")
    print(json.dumps(info, ensure_ascii=False, indent=2))
