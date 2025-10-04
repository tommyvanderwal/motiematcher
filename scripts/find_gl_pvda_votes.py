import json
from pathlib import Path

STEMMING_DIR = Path("c:/motiematcher/bronmateriaal-onbewerkt/stemming_complete")


def main() -> None:
    matches = {}
    for file in STEMMING_DIR.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for record in data:
            if record.get("ActorNaam") == "GroenLinks-PvdA" and record.get("Soort") == "Tegen":
                matches.setdefault(record.get("Besluit_Id"), []).append(record)
    print(f"Found {len(matches)} besluiten where GroenLinks-PvdA voted Tegen")
    for besluit_id, records in list(matches.items())[:5]:
        print(f"- {besluit_id} ({len(records)} records)")


if __name__ == "__main__":
    main()
