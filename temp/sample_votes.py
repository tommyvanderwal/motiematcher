import json
import requests

BASE_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"

response = requests.get(
    f"{BASE_URL}/Stemming",
    params={"$top": 5, "$orderby": "GewijzigdOp desc"},
    timeout=30,
)
response.raise_for_status()
value = response.json().get("value", [])
print(json.dumps(value, ensure_ascii=False, indent=2))
