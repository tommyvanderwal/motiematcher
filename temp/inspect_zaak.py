import json
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "bronnateriaal-onbewerkt" / "zaak_current" / "zaak_voted_motions_20251003_200218.json"

with FILE.open("r", encoding="utf-8") as handle:
    data = json.load(handle)

print("records", len(data))

first = data[0]
print("keys", sorted(first.keys()))

# find document info
with_docs = next((item for item in data if "Document" in item or "Documenten" in item), None)
if with_docs:
    print("record with documents keys", sorted(with_docs.keys()))
    print("documents field type", type(with_docs.get("Documenten")))
else:
    print("no document field found")
