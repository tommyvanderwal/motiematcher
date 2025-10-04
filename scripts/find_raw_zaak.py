"""Find a raw zaak entry by Id and dump its contents."""

import argparse
import json
from pathlib import Path

ZAAK_DIR = Path("bronmateriaal-onbewerkt/zaak")


def find_zaak(zaak_id: str):
    for path in ZAAK_DIR.glob("*.json"):
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        records = payload if isinstance(payload, list) else payload.get("value") or []
        for record in records:
            if record.get("Id") == zaak_id:
                return record, path
    return None, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zaak_id")
    args = parser.parse_args()

    record, path = find_zaak(args.zaak_id)
    if not record:
        print("Zaak not found")
        return

    print(f"Found in {path}")
    print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
