import json
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "bronmateriaal-onbewerkt" / "comprehensive_motion_56e10506_20251002_192333.json"
with FILE.open("r", encoding="utf-8") as handle:
    data = json.load(handle)

print("keys", data.keys())
for key in data:
    print(key, type(data[key]))

print("decision keys", data['decision'].keys())
print("zaak keys", data['zaak'].keys())
print("document keys", data['document'].keys())
print("text snippet", data['document'].get('Inhoud', '')[:500])
