import json
from pathlib import Path
import collections

FILE = Path("c:/motiematcher/final_linked_data.json")


def main() -> None:
    with FILE.open("r", encoding="utf-8") as f:
        records = json.load(f)

    totaal = len(records)
    print(f"Total records: {totaal}")

    zaak_counts = collections.Counter(rec.get("Matched_Zaak_Id") for rec in records)
    print("Unique zaak IDs:", len([k for k in zaak_counts if k]))
    print("Top zaak frequencies:")
    for zaak_id, count in zaak_counts.most_common(5):
        print(f"  {zaak_id}: {count}")

    soort_counts = collections.Counter(rec.get("Matched_Zaak_Soort") or rec.get("Soort_zaak") for rec in records)
    print("Type counts (Matched_Zaak_Soort / Soort_zaak):")
    for soort, count in soort_counts.items():
        print(f"  {soort}: {count}")

    besluit_soort_counts = collections.Counter(rec.get("BesluitSoort") for rec in records)
    print("BesluitSoort counts:")
    for bs, count in besluit_soort_counts.items():
        print(f"  {bs}: {count}")


if __name__ == "__main__":
    main()
