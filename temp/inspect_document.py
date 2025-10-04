import json
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "bronmateriaal-onbewerkt" / "document" / "document_page_1_fullterm_20251002_235824.json"

with FILE.open("r", encoding="utf-8") as handle:
    docs = json.load(handle)

print("docs", len(docs))
print("keys", sorted(docs[0].keys()))
print("has inhoud", 'Inhoud' in docs[0])
print("sample inhoud", docs[0].get('Inhoud', '')[:200])
