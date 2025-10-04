import json
from pathlib import Path

BESLUIT_DIR = Path("c:/motiematcher/bronmateriaal-onbewerkt/besluit")


def main() -> None:
    total = 0
    with_zaak_field = 0
    with_agendapunt = 0
    sample_with_zaak = None
    for file in BESLUIT_DIR.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        records = data if isinstance(data, list) else data.get("value", [])
        for record in records:
            total += 1
            if record.get("Agendapunt_Id"):
                with_agendapunt += 1
            if record.get("Zaak_Id") or record.get("Zaak"):
                with_zaak_field += 1
                if sample_with_zaak is None:
                    sample_with_zaak = record
    print(f"Total besluiten: {total}")
    print(f"Met Agendapunt_Id: {with_agendapunt}")
    print(f"Met Zaak verwijzing: {with_zaak_field}")
    if sample_with_zaak:
        print("Voorbeeld besluit met zaak:")
        print(sample_with_zaak)


if __name__ == "__main__":
    main()
