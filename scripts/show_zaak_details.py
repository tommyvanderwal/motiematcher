import json
from pathlib import Path

TARGET_PHRASE = "noodzakelijke infrastructurele systeemtaken"
FILES = [
    Path("c:/motiematcher/bronmateriaal-onbewerkt/zaak/zaak_page_6_fullterm_20251002_231439.json"),
    Path("c:/motiematcher/bronmateriaal-onbewerkt/zaak/moties_page_2_30days_20251002_193202.json")
]


def main() -> None:
    for file in FILES:
        print(f"\n=== {file.name} ===")
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict) and "value" in data:
            records = data["value"]
        else:
            records = []
        print(f"Records: {len(records)}")
        for record in records:
            onderwerp = record.get("Onderwerp", "").lower()
            titel = record.get("Titel", "").lower()
            if TARGET_PHRASE in onderwerp or TARGET_PHRASE in titel:
                print("Matched zaak:")
                print(json.dumps(record, indent=2, ensure_ascii=False))
                break
        else:
            print("No match in this file.")


if __name__ == "__main__":
    main()
