import json
from pathlib import Path

TARGET_ZAAK = "ffcfee5e-b5f9-4dc4-b630-2f6948bcd5ac"
AGENDAPUNT_DIR = Path("c:/motiematcher/bronmateriaal-onbewerkt/agendapunt")


def main() -> None:
    matches = []
    for file in AGENDAPUNT_DIR.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        records = data if isinstance(data, list) else data.get("value", [])
        for record in records:
            zaken = record.get("Zaak")
            if isinstance(zaken, dict):
                zaken = [zaken]
            if isinstance(zaken, list):
                for zaak in zaken:
                    if isinstance(zaak, dict) and zaak.get("Id") == TARGET_ZAAK:
                        matches.append((file.name, record.get("Id")))
                        print(f"Found agendapunt {record.get('Id')} in {file.name}")
                        print(json.dumps(record, indent=2, ensure_ascii=False))
                        break
        if matches:
            break
    print(f"Total matches: {len(matches)}")


if __name__ == "__main__":
    main()
