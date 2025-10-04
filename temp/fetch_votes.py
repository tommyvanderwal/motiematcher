import json
import sys

import requests

BASE_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"

if len(sys.argv) < 2:
    raise SystemExit("Usage: fetch_votes.py BESLUIT_ID")

besluit_id = sys.argv[1]
filters = [
    f"Besluit_Id eq guid'{besluit_id}'",
    f"Besluit_Id eq {besluit_id}",
    f"Besluit_Id eq '{besluit_id}'",
    f"Besluit/Id eq guid'{besluit_id}'",
]

session = requests.Session()
session.headers.update({
    "User-Agent": "MotieMatcher-FetchVotes/1.0",
    "Accept": "application/json"
})

url = f"{BASE_URL}/Stemming"
last_error = None
data = None

for filter_value in filters:
    params = {
        "$filter": filter_value,
    "$expand": "Fractie,Persoon",
    "$top": 250
    }
    response = session.get(url, params=params, timeout=30)
    if response.status_code == 200:
        data = response.json()
        successful_filter = filter_value
        break
    last_error = (response.status_code, response.text[:200], filter_value)

if data is None:
    status_code, snippet, attempted_filter = last_error or ("?", "No response", filters[0])
    raise SystemExit(
        f"Request failed (status {status_code}) using filter '{attempted_filter}'. Response snippet: {snippet}"
    )

value = data.get("value", [])
print(json.dumps(value, ensure_ascii=False, indent=2))
print(f"Total votes fetched: {len(value)}")
print(f"Filter used: {successful_filter}")
