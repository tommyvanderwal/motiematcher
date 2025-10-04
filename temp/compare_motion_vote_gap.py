import json
from collections import Counter, defaultdict
from pathlib import Path

import requests

BASE_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
DATA_PATH = Path("bronmateriaal-onbewerkt/current/motion_index/motions_enriched.json")

MOTIONS = [
    "2023Z20635",
    "2023Z20636",
    "2023Z20639",
]

records = {record["motion_number"]: record for record in json.loads(DATA_PATH.read_text(encoding="utf-8")) if record.get("motion_number") in MOTIONS}

session = requests.Session()
session.headers.update({
    "User-Agent": "MotieMatcher-CompareVotes/1.0",
    "Accept": "application/json"
})

for motion_number in MOTIONS:
    record = records.get(motion_number)
    if not record:
        print(f"Motion {motion_number} not found in dataset")
        continue

    print(f"=== Motion {motion_number}: {record.get('motion_title')} ===")
    local_votes = record.get("vote_breakdown") or []
    local_totals = record.get("vote_totals") or {}
    print(f"Local vote_totals: {local_totals}")
    print(f"Local vote_breakdown entries: {len(local_votes)}")
    if local_votes:
        by_vote = Counter(entry.get("vote") for entry in local_votes)
        print(f"  Local counts by vote label: {dict(by_vote)}")
        summed = defaultdict(int)
        for entry in local_votes:
            summed[entry.get("vote")] += entry.get("fractie_grootte") or 0
        print(f"  Local summed fractie_grootte: {dict(summed)}")

    decision_summaries = record.get("decision_summaries") or []
    print(f"Decision summaries: {len(decision_summaries)}")

    for summary in decision_summaries:
        besluit_id = summary.get("besluit_id") or summary.get("Besluit", {}).get("Id")
        if not besluit_id:
            print("  Skipping decision without besluit_id")
            continue

        filters = [
            f"Besluit_Id eq {besluit_id}",
            f"Besluit_Id eq guid'{besluit_id}'",
            f"Besluit_Id eq '{besluit_id}'",
            f"Besluit/Id eq {besluit_id}",
        ]

        votes = None
        last_error = ("?", "No response", filters[0])
        for filter_value in filters:
            params = {
                "$filter": filter_value,
                "$expand": "Fractie,Persoon",
                "$top": 250
            }
            response = session.get(f"{BASE_URL}/Stemming", params=params, timeout=30)
            if response.status_code == 200:
                votes = response.json().get("value", [])
                break
            last_error = (response.status_code, response.text[:200], filter_value)

        if votes is None:
            status_code, snippet, attempted_filter = last_error
            print(f"  Failed to fetch votes for besluit {besluit_id}: status {status_code} using filter '{attempted_filter}'. Response snippet: {snippet}")
            continue

        counts = Counter(vote.get("Soort") for vote in votes)
        summed = defaultdict(int)
        for vote in votes:
            summed[vote.get("Soort")] += vote.get("FractieGrootte") or 0

        print(f"  Besluit {besluit_id} ({summary.get('besluit_soort')}):")
        print(f"    Summary vote_totals: {summary.get('vote_totals')} (vote_count={summary.get('vote_count')})")
        print(f"    API rows: {len(votes)} | counts {dict(counts)} | summed fractie_grootte {dict(summed)}")
    print()
