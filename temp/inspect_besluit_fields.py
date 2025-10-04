import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
BESLUIT_DIR = BASE / "bronmateriaal-onbewerkt" / "current" / "besluit_current"


def iter_records():
    for path in sorted(BESLUIT_DIR.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to load {path.name}: {exc}")
            continue
        records = payload if isinstance(payload, list) else payload.get("value", [])
        if not isinstance(records, list):
            continue
        for record in records:
            if isinstance(record, dict):
                yield record


def main() -> None:
    seen = 0
    for idx, record in enumerate(iter_records()):
        besluit_id = record.get("Id")
        zaak_id = record.get("Zaak_Id")
        besluitsoort = record.get("BesluitSoort")
        beslutdatum = record.get("BesluitDatum")
        stemming = record.get("Stemming")
        print(f"Record {idx}: Id={besluit_id}")
        print(f"  Zaak_Id={zaak_id}")
        print(f"  BesluitSoort={besluitsoort}")
        print(f"  BesluitDatum={beslutdatum}")
        if isinstance(stemming, list) and stemming:
            print(f"  First stemming keys: {list(stemming[0].keys())[:5]}")
            print(f"  First stemming record snippet: {stemming[0]}")
        else:
            print("  No stemming data inlined")
        print("-" * 40)
        seen += 1
        if seen >= 3:
            break

    # find record with Zaak_Id filled
    for record in iter_records():
        zaak_id = record.get("Zaak_Id")
        if zaak_id:
            print("Found besluit with Zaak_Id linkage:")
            print(f"  Id={record.get('Id')}")
            print(f"  Zaak_Id={zaak_id}")
            print(f"  BesluitSoort={record.get('BesluitSoort')}")
            print(f"  BesluitDatum={record.get('BesluitDatum')}")
            docs = record.get('DocumentReference', []) or []
            if docs:
                first_doc = docs[0]
                print(f"  First document reference: {first_doc}")
            else:
                print("  No document reference array")
            break
    else:
        print("No besluit with Zaak_Id found in the sample")


if __name__ == "__main__":
    main()
