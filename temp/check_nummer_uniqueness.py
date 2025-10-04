import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE / "bronmateriaal-onbewerkt" / "current" / "zaak_current"


def main() -> None:
    numbers = Counter()
    ids = {}  # nummer -> first id
    total = 0
    for path in sorted(INPUT_DIR.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to load {path.name}: {exc}")
            continue

        records = payload if isinstance(payload, list) else payload.get("value", [])
        if not isinstance(records, list):
            continue
        for item in records:
            if not isinstance(item, dict):
                continue
            nummer = (item.get("Nummer") or "").strip()
            if not nummer:
                continue
            numbers[nummer] += 1
            if nummer not in ids:
                ids[nummer] = item.get("Id")
            total += 1

    duplicates = {num: count for num, count in numbers.items() if count > 1}
    print(f"Total records with Nummer: {total}")
    print(f"Unique Nummer values: {len(numbers)}")
    print(f"Duplicate Nummer values: {len(duplicates)}")
    if duplicates:
        print("Sample duplicates (first 10):")
        for nummer, count in list(duplicates.items())[:10]:
            print(f"  {nummer}: {count} occurrences (first Id={ids.get(nummer)})")


if __name__ == "__main__":
    main()
