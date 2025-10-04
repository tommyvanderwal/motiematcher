import json
from pathlib import Path

FILE = Path("c:/motiematcher/bronmateriaal-onbewerkt/besluit/besluit_page_100_retry_20251003_080844.json")


def main() -> None:
    with FILE.open("r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Loaded {len(records)} records")
    if records:
        sample = records[0]
        print("Keys:")
        for key in sample.keys():
            print(f"- {key}")
        print("\nSelected fields:")
        for key in ["Id", "BesluitSoort", "BesluitTekst", "Status", "Zaak_Id", "Agendapunt_Id", "Vergadering_Id", "Document_Id"]:
            if key in sample:
                print(f"{key}: {sample[key]}")


if __name__ == "__main__":
    main()
