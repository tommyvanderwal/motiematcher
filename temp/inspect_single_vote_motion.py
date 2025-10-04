import json
from pathlib import Path

path = Path("bronmateriaal-onbewerkt/current/motion_index/motions_enriched.json")
records = json.loads(path.read_text(encoding="utf-8"))

single = None
for record in records:
    votes = record.get("vote_breakdown") or []
    if len(votes) == 1:
        single = record
        break

if not single:
    raise SystemExit("No single-vote motions found")

print(f"Motion: {single.get('motion_number')} ({single.get('motion_title')})")
print(f"Vote breakdown length: {len(single.get('vote_breakdown') or [])}")
print("Vote breakdown entry:")
print(json.dumps(single.get('vote_breakdown')[0], ensure_ascii=False, indent=2))
print("Decision summaries:")
print(json.dumps(single.get('decision_summaries'), ensure_ascii=False, indent=2))
