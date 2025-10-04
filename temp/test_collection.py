import requests
import json
import os
from datetime import datetime

# Quick test: Collect small sample of current parliament voting data
# Using Zaak-centric approach with expansions

def test_current_parliament_collection():
    base_url = 'https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0'
    start_date = '2023-12-01T00:00:00Z'

    print("Testing collection of current parliament voting data...")
    print(f"Collecting from {start_date} to present")

    # Step 1: Collect small sample of Zaak (motions) - only 10 records
    print("\n1. Collecting sample Zaak data...")
    zaak_url = f"{base_url}/Zaak?$filter=GewijzigdOp gt {start_date}&$orderby=GewijzigdOp desc&$top=10"
    response = requests.get(zaak_url)

    if response.status_code != 200:
        print(f"Error fetching Zaak data: {response.status_code}")
        return

    zaak_data = response.json().get('value', [])
    print(f"Sample Zaak records collected: {len(zaak_data)}")

    # Show sample Zaak data
    for zaak in zaak_data[:3]:
        titel = zaak.get('Titel') or zaak.get('Onderwerp') or 'No title'
        print(f"  - {zaak.get('Nummer', 'N/A')}: {titel[:50]}...")

    # Step 2: Test expansions on first Zaak
    if zaak_data:
        print("\n2. Testing expansions on first Zaak...")
        zaak_id = zaak_data[0]['Id']
        url = f"{base_url}/Zaak({zaak_id})?$expand=Besluit($expand=Stemming)"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            besluiten = data.get('Besluit', [])
            print(f"  Besluiten found: {len(besluiten)}")

            total_stemmingen = 0
            for besluit in besluiten:
                stemmingen = besluit.get('Stemming', [])
                total_stemmingen += len(stemmingen)

            print(f"  Total Stemmingen: {total_stemmingen}")

            if total_stemmingen > 0:
                print("  ✅ Expansions working - vote data available")
            else:
                print("  ⚠️  No votes found (motion may not have been voted on yet)")
        else:
            print(f"  ❌ Error: {response.status_code}")

    print("\n=== Test Complete ===")
    print("Collection approach validated. Ready for full collection.")

if __name__ == "__main__":
    test_current_parliament_collection()