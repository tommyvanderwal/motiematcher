import json
from pathlib import Path

FILE = Path("c:/motiematcher/final_linked_data.json")


def main() -> None:
    with FILE.open("r", encoding="utf-8") as f:
        records = json.load(f)

    unique_zaak_ids = {rec.get("Matched_Zaak_Id") for rec in records if rec.get("Matched_Zaak_Id")}
    print(f"Total records: {len(records)}")
    print(f"Unique Matched_Zaak_Id: {len(unique_zaak_ids)}")
    print("Sample IDs:")
    for zaak_id in list(unique_zaak_ids)[:10]:
        print(zaak_id)


if __name__ == "__main__":
    main()
