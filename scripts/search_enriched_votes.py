"""Search enriched stemming files for a specific Zaak Id."""

import argparse
import json
from pathlib import Path

ENRICHED_DIR = Path("bronmateriaal-onbewerkt/stemming_enriched")


def find_votes(zaak_id: str):
    matches = []
    for path in sorted(ENRICHED_DIR.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        records = payload.get("value") or []
        for record in records:
            besluit = record.get("Besluit") or {}
            agendapunt = besluit.get("Agendapunt") or {}
            for zaak in agendapunt.get("Zaak") or []:
                if zaak.get("Id") == zaak_id:
                    matches.append(
                        {
                            "file": path.name,
                            "besluit_id": besluit.get("Id"),
                            "besluit_tekst": besluit.get("BesluitTekst"),
                            "stemmings_soort": besluit.get("StemmingsSoort"),
                            "stem_id": record.get("Id"),
                            "stem_soort": record.get("Soort"),
                            "stem_actor": record.get("ActorNaam"),
                        }
                    )
    return matches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zaak_id", help="Zaak GUID to search for")
    args = parser.parse_args()

    results = find_votes(args.zaak_id)
    if not results:
        print("No enriched vote records found for this Zaak Id.")
        return

    print(f"Found {len(results)} vote records:")
    for match in results:
        print(
            f"{match['file']} | Besluit {match['besluit_id']} | "
            f"{match['stem_actor']} -> {match['stem_soort']}"
        )


if __name__ == "__main__":
    main()
