import json
from collections import Counter
from pathlib import Path

FILE = Path("c:/motiematcher/step1_recent_filtered_enriched_data.json")


def main() -> None:
    with FILE.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    zaken = payload.get("zaken", [])
    print(f"Total zaken: {len(zaken)}")
    type_counts = Counter(item.get("type") for item in zaken)
    print("Type counts:")
    for soort, count in type_counts.items():
        print(f"  {soort}: {count}")
    has_votes = sum(1 for item in zaken if item.get("has_voting_data"))
    print(f"Records with voting data: {has_votes}")


if __name__ == "__main__":
    main()
