import json
from collections import defaultdict
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "final_linked_data.json"

with DATA_FILE.open("r", encoding="utf-8") as handle:
    records = json.load(handle)

by_besluit = defaultdict(list)
for item in records:
    besluit_id = item.get("Besluit_Id")
    if besluit_id:
        by_besluit[besluit_id].append(item)

print(f"Total votes: {len(records)}")
print(f"Total unique besluiten: {len(by_besluit)}")

print("Top 5 by vote count:")
for besluit_id, votes in sorted(by_besluit.items(), key=lambda kv: len(kv[1]), reverse=True)[:5]:
    actors = {vote.get("ActorNaam") for vote in votes}
    print(f"- {besluit_id}: {len(votes)} votes, actors={len(actors)}")
