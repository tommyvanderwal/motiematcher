import json
from pathlib import Path

TARGET_ZAAK = "ffcfee5e-b5f9-4dc4-b630-2f6948bcd5ac"

FILES = [
    Path("c:/motiematcher/bronmateriaal-onbewerkt/stemming/recent_votes_last_10_days_20251002_192333.json"),
    Path("c:/motiematcher/bronmateriaal-onbewerkt/stemming/recent_votes_last_10_days_20251002_192415.json")
]


def main() -> None:
    for file in FILES:
        print(f"\n=== {file.name} ===")
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        records = data.get("value", []) if isinstance(data, dict) else data
        print(f"Records: {len(records)}")
        if records:
            print("Sample keys:", list(records[0].keys()))
            besluit_sample = records[0].get("Besluit", {})
            if besluit_sample:
                print("Besluit sample keys:", list(besluit_sample.keys()))
        for record in records:
            besluit = record.get("Besluit") or {}
            zaak_list = besluit.get("Zaak") or []
            if isinstance(zaak_list, dict):
                zaak_list = [zaak_list]
            zaak_ids = {z.get("Id") for z in zaak_list if isinstance(z, dict)}
            if TARGET_ZAAK in zaak_ids:
                print("Found matching vote record")
                print(json.dumps(record, indent=2, ensure_ascii=False))
                break
        else:
            print("No matching votes for target zaak")


if __name__ == "__main__":
    main()
