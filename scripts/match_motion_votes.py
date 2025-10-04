import json
from collections import defaultdict
from pathlib import Path

STEMMING_DIR = Path("c:/motiematcher/bronmateriaal-onbewerkt/stemming_complete")

TARGET_PATTERN = {
    "PVV": "Voor",
    "GroenLinks-PvdA": "Tegen",
    "VVD": "Voor",
    "NSC": "Voor",
    "D66": "Voor",
    "BBB": "Voor",
    "CDA": "Voor",
    "SP": "Tegen",
    "ChristenUnie": "Voor",
    "DENK": "Voor",
    "FVD": "Voor",
    "PvdD": "Tegen",
    "SGP": "Voor",
    "Volt": "Voor",
    "JA21": "Voor",
}


def load_grouped_votes():
    grouped = defaultdict(list)
    for file in STEMMING_DIR.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for record in data:
            besluit_id = record.get("Besluit_Id")
            if not besluit_id:
                continue
            grouped[besluit_id].append(record)
    return grouped


def matches_target(votes):
    lookup = {v.get("ActorNaam"): v.get("Soort") for v in votes}
    return all(lookup.get(party) == expected for party, expected in TARGET_PATTERN.items())


def main() -> None:
    grouped = load_grouped_votes()
    print(f"Grouped votes for {len(grouped)} besluiten")
    for besluit_id, votes in grouped.items():
        if matches_target(votes):
            print(f"Found matching besluit: {besluit_id}")
            unique_soorten = sorted({(v.get('ActorNaam'), v.get('Soort')) for v in votes})
            for party, vote in unique_soorten:
                print(f"  {party}: {vote}")
            break
    else:
        print("No exact match found")


if __name__ == "__main__":
    main()
