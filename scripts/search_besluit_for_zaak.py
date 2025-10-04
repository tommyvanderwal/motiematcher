"""Search besluit data for a specific Zaak Id."""

import argparse
import json
from pathlib import Path

BESLUIT_DIR = Path("bronmateriaal-onbewerkt/besluit")


def find_besluiten(zaak_id: str):
    matches = []
    for path in BESLUIT_DIR.glob("*.json"):
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        records = payload if isinstance(payload, list) else payload.get("value") or []
        for record in records:
            zaken = record.get("Zaak") or []
            for zaak in zaken:
                if zaak.get("Id") == zaak_id:
                    matches.append((record, path.name))
    return matches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zaak_id")
    args = parser.parse_args()

    matches = find_besluiten(args.zaak_id)
    if not matches:
        print("No besluit entries linked to this Zaak.")
        return

    print(f"Found {len(matches)} besluiten:")
    for record, filename in matches:
        print(f"File: {filename}")
        print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
