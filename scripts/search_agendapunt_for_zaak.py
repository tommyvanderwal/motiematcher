import argparse
import json
from pathlib import Path

AGENDAPUNT_DIR = Path("c:/motiematcher/bronmateriaal-onbewerkt/agendapunt")


def find_matches(zaak_id: str):
    matches = []
    for file in sorted(AGENDAPUNT_DIR.glob("*.json")):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        records = data if isinstance(data, list) else data.get("value", [])
        for record in records:
            zaken = record.get("Zaak")
            if isinstance(zaken, dict):
                zaken = [zaken]
            if isinstance(zaken, list):
                for zaak in zaken:
                    if isinstance(zaak, dict) and zaak.get("Id") == zaak_id:
                        matches.append((record, file.name))
    return matches


def main() -> None:
    parser = argparse.ArgumentParser(description="Search agendapunt files for a given Zaak Id")
    parser.add_argument("zaak_id")
    args = parser.parse_args()

    matches = find_matches(args.zaak_id)
    if not matches:
        print("No agendapunt records linked to this Zaak.")
        return

    print(f"Found {len(matches)} agendapunten:")
    for record, filename in matches:
        print(f"File: {filename} | Agendapunt {record.get('Id')} | Onderwerp={record.get('Onderwerp')}")


if __name__ == "__main__":
    main()
