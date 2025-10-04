import json
from pathlib import Path

TARGET_ZAAK_ID = "ffcfee5e-b5f9-4dc4-b630-2f6948bcd5ac"
BESLUIT_DIR = Path("c:/motiematcher/bronmateriaal-onbewerkt/besluit")


def main() -> None:
    matches = []
    for file in BESLUIT_DIR.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict) and "value" in data:
            records = data["value"]
        else:
            records = []
        for record in records:
            zaak_ids = []
            if "Zaak" in record:
                if isinstance(record["Zaak"], list):
                    zaak_ids.extend([z.get("Id") for z in record["Zaak"] if isinstance(z, dict)])
                elif isinstance(record["Zaak"], dict):
                    zaak_ids.append(record["Zaak"].get("Id"))
            if record.get("Zaak_Id"):
                zaak_ids.append(record["Zaak_Id"])
            if TARGET_ZAAK_ID in zaak_ids:
                matches.append((file.name, record.get("Id")))
                print(f"Match in {file.name}: Besluit_Id={record.get('Id')}, BesluitTekst={record.get('BesluitTekst')}")
    print(f"Total besluit matches: {len(matches)}")


if __name__ == "__main__":
    main()
