"""Inspect a specific motie entry from the step1 output."""

import argparse
import json
from pathlib import Path

DATA_FILE = Path("step1_fullterm_filtered_enriched_data.json")


def load_zaken():
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["zaken"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nummer", help="Zaak nummer to inspect (e.g., 2024Z13308)")
    args = parser.parse_args()

    for zaak in load_zaken():
        if zaak.get("nummer") == args.nummer:
            print(json.dumps(zaak, indent=2, ensure_ascii=False))
            break
    else:
        print(f"Motie with nummer {args.nummer} not found.")


if __name__ == "__main__":
    main()
