import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "final_linked_data.json"
ALT_FILE = Path(__file__).resolve().parent.parent / "final_filtered_data.json"

with DATA_FILE.open("r", encoding="utf-8") as handle:
    records = json.load(handle)

print(f"total records: {len(records)}")

for idx, record in enumerate(records[:5]):
    print(f"\n--- record {idx} ---")
    for key, value in record.items():
        if isinstance(value, (str, int, float)) or value is None:
            display = value
        else:
            display = str(value)[:200]
        print(f"{key}: {display}")

if ALT_FILE.exists():
    with ALT_FILE.open("r", encoding="utf-8") as handle:
        alt_records = json.load(handle)
    print(f"\nalt records: {len(alt_records)} in final_filtered_data.json")
    alt = alt_records[0]
    print("\nfields in alt sample:")
    for key in sorted(alt.keys()):
        value = alt[key]
        if isinstance(value, (str, int, float)) or value is None:
            display = value
        else:
            display = str(value)[:200]
        print(f"{key}: {display}")
