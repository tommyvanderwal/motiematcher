import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    raise SystemExit("Usage: find_stemming_entries.py BESLUIT_ID")

target = sys.argv[1]
root = Path("bronmateriaal-onbewerkt/stemming_enriched")
found = False
for json_path in sorted(root.glob("*.json")):
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        continue
    records = data.get("value") if isinstance(data, dict) else data
    if not isinstance(records, list):
        continue
    for record in records:
        besluit = record.get("Besluit") or {}
        if besluit.get("Id") == target or record.get("Besluit_Id") == target:
            print(f"Found in {json_path.name}")
            print(json.dumps(record, ensure_ascii=False, indent=2))
            found = True
            break
    if found:
        break

if not found:
    print("No record found for", target)
