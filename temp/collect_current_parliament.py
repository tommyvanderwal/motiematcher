import requests
import json
import os
from datetime import datetime

# Collect all voting data from current parliament (since Dec 2023)
# Using Zaak-centric approach with expansions as validated

def collect_current_parliament_voting():
    base_url = 'https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0'
    start_date = '2023-12-01T00:00:00Z'  # Start of current parliament

    # Create directories
    os.makedirs('bronnateriaal-onbewerkt/zaak_current', exist_ok=True)
    os.makedirs('bronnateriaal-onbewerkt/besluit_current', exist_ok=True)
    os.makedirs('bronnateriaal-onbewerkt/stemming_current', exist_ok=True)

    print("Starting collection of current parliament voting data...")
    print(f"Collecting from {start_date} to present")

    # Step 1: Collect all Zaak (motions) voted on since start_date
    print("\n1. Collecting Zaak data...")
    zaak_url = f"{base_url}/Zaak?$filter=GewijzigdOp gt {start_date}&$orderby=GewijzigdOp desc"
    zaak_data = []
    skip = 0
    top = 250

    while True:
        url = f"{zaak_url}&$top={top}&$skip={skip}"
        print(f"Fetching Zaak page {skip//top + 1}...")
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        data = response.json()
        batch = data.get('value', [])
        if not batch:
            break

        zaak_data.extend(batch)
        print(f"  Collected {len(batch)} Zaak records")

        if len(batch) < top:
            break
        skip += top

    print(f"Total Zaak records collected: {len(zaak_data)}")

    # Save Zaak data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f'bronnateriaal-onbewerkt/zaak_current/zaak_current_parliament_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(zaak_data, f, ensure_ascii=False, indent=2)

    # Step 2: For each Zaak, get expanded Besluit and Stemming data
    print("\n2. Collecting Besluit and Stemming data via expansions...")
    besluit_data = []
    stemming_data = []

    for i, zaak in enumerate(zaak_data):
        if i % 50 == 0:
            print(f"Processing Zaak {i+1}/{len(zaak_data)}...")

        zaak_id = zaak['Id']
        url = f"{base_url}/Zaak({zaak_id})?$expand=Besluit($expand=Stemming)"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()

                # Extract Besluit data
                besluiten = data.get('Besluit', [])
                besluit_data.extend(besluiten)

                # Extract Stemming data from all Besluit
                for besluit in besluiten:
                    stemmingen = besluit.get('Stemming', [])
                    stemming_data.extend(stemmingen)

        except Exception as e:
            print(f"Error processing Zaak {zaak_id}: {e}")
            continue

    print(f"Total Besluit records collected: {len(besluit_data)}")
    print(f"Total Stemming records collected: {len(stemming_data)}")

    # Save Besluit data
    with open(f'bronnateriaal-onbewerkt/besluit_current/besluit_current_parliament_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(besluit_data, f, ensure_ascii=False, indent=2)

    # Save Stemming data
    with open(f'bronnateriaal-onbewerkt/stemming_current/stemming_current_parliament_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(stemming_data, f, ensure_ascii=False, indent=2)

    # Summary
    print("\n=== Collection Summary ===")
    print(f"Zaak records: {len(zaak_data)}")
    print(f"Besluit records: {len(besluit_data)}")
    print(f"Stemming records: {len(stemming_data)}")
    print(f"Data saved with timestamp: {timestamp}")

    # Check for voted motions
    voted_motions = len([b for b in besluit_data if b.get('Stemming')])
    print(f"Motions with votes: {voted_motions}")

if __name__ == "__main__":
    collect_current_parliament_voting()