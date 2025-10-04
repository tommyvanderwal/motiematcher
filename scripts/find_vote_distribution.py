import json
from collections import defaultdict, Counter
from pathlib import Path

STEMMING_FILES = list(Path("c:/motiematcher/bronmateriaal-onbewerkt/stemming_complete").glob("*.json"))

TARGET_TOTAL_FOR = 117
TARGET_DECISION_TYPE = "Met handopsteken"


def load_votes():
    grouped = defaultdict(list)
    for file in STEMMING_FILES:
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for record in data:
            besluit_id = record.get("Besluit_Id")
            if not besluit_id:
                continue
            grouped[besluit_id].append(record)
    return grouped


def summarize_votes(votes):
    totals = Counter()
    parties = {}
    for vote in votes:
        kind = vote.get("Soort")
        size = vote.get("FractieGrootte") or 0
        actor = vote.get("ActorNaam")
        totals[kind] += size
        parties.setdefault(actor, []).append(kind)
    return totals, parties


def main() -> None:
    grouped = load_votes()
    print(f"Loaded votes for {len(grouped)} Besluit_Id entries")
    matches = []
    for besluit_id, votes in grouped.items():
        totals, parties = summarize_votes(votes)
        if totals.get("Voor", 0) == TARGET_TOTAL_FOR:
            matches.append((besluit_id, totals))
    print(f"Found {len(matches)} potential matches with {TARGET_TOTAL_FOR} Voor")
    if matches:
        besluit_id, totals = matches[0]
        print(f"Example match: {besluit_id} -> totals {dict(totals)}")
        sample_votes = grouped[besluit_id]
        sample_votes.sort(key=lambda v: v.get("ActorNaam", ""))
        for vote in sample_votes:
            print(f"{vote.get('ActorNaam')}: {vote.get('Soort')} ({vote.get('FractieGrootte')})")


if __name__ == "__main__":
    main()
