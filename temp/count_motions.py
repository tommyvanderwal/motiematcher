import json
from pathlib import Path

path = Path("bronmateriaal-onbewerkt/current/motion_index/motions_enriched.json")
if not path.exists():
    raise SystemExit("motions_enriched.json not found")

with path.open("r", encoding="utf-8") as handle:
    data = json.load(handle)

if not isinstance(data, list):
    raise SystemExit("Unexpected structure")

print(len(data))
