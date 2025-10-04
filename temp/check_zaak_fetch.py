import json
import sys
from pathlib import Path

import requests

BASE_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
ZAAK_ID = sys.argv[1]

params = {
    "$expand": "Document($expand=HuidigeDocumentVersie($expand=DocumentPublicatie,DocumentPublicatieMetadata))",
}

url_guid = f"{BASE_URL}/Zaak(guid'{ZAAK_ID}')"
url_plain = f"{BASE_URL}/Zaak('{ZAAK_ID}')"

for label, url in (("guid", url_guid), ("plain", url_plain)):
    try:
        response = requests.get(url, params=params, timeout=30)
    except requests.RequestException as exc:  # pragma: no cover - manual test helper
        print(f"{label} request error: {exc}")
        continue
    print(f"{label} status: {response.status_code}")
    if response.ok:
        data = response.json()
        documents = data.get("Document") or []
        print(f"{label} document count: {len(documents)}")
        print(f"{label} keys: {list(data.keys())[:10]}")
    else:
        print(f"{label} body: {response.text[:400]}")

for literal_label, literal in (
    ("guid_literal", f"guid'{ZAAK_ID}'"),
    ("string_literal", f"'{ZAAK_ID}'"),
    ("bare_literal", ZAAK_ID),
):
    params_full = dict(params)
    params_full["$filter"] = f"Id eq {literal}"
    try:
        response = requests.get(f"{BASE_URL}/Zaak", params=params_full, timeout=30)
    except requests.RequestException as exc:
        print(f"filter {literal_label} request error: {exc}")
        continue
    print(f"filter {literal_label} status: {response.status_code}")
    if response.ok:
        data = response.json()
        value = data.get("value") or []
        print(f"filter {literal_label} count: {len(value)}")
    else:
        print(f"filter {literal_label} body: {response.text[:400]}")

cache_file = Path("temp/zaak_check_result.json")
cache_file.parent.mkdir(parents=True, exist_ok=True)
cache_data = {
    "zaak_id": ZAAK_ID,
    "urls": {
        "guid": url_guid,
        "plain": url_plain,
    }
}
cache_file.write_text(json.dumps(cache_data, indent=2))
