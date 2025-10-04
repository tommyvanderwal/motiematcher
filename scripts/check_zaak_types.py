import json
from collections import Counter
from pathlib import Path

ZAAK_DIR = Path("c:/motiematcher/bronmateriaal-onbewerkt/zaak")


def main() -> None:
    counter = Counter()
    total = 0
    for file in ZAAK_DIR.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        records = data if isinstance(data, list) else data.get("value", [])
        total += len(records)
        for record in records:
            counter[record.get("Soort")] += 1
    print(f"Total zaak records scanned: {total}")
    for soort, count in counter.most_common(10):
        print(f"{soort}: {count}")


if __name__ == "__main__":
    main()
