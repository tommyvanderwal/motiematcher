import requests
import json
import os
from datetime import datetime, timedelta

# Fast collection: Focus on voted motions from current parliament
# Limit to 10 minutes execution time

def collect_voted_motions_fast():
    base_url = 'https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0'
    start_date = '2023-12-01T00:00:00Z'  # Start of current parliament

    # Create directories
    os.makedirs('bronnateriaal-onbewerkt/zaak_current', exist_ok=True)
    os.makedirs('bronnateriaal-onbewerkt/besluit_current', exist_ok=True)
    os.makedirs('bronnateriaal-onbewerkt/stemming_current', exist_ok=True)

    print("Fast collection of voted motions from current parliament...")
    print(f"Time limit: 10 minutes from {datetime.now()}")

    start_time = datetime.now()
    max_duration = timedelta(minutes=10)

    # Step 1: Collect Zaak data with focus on motions likely to be voted
    print("\n1. Collecting Zaak data (motions only, recent first)...")
    zaak_url = f"{base_url}/Zaak?$filter=Soort eq 'Motie' and GewijzigdOp gt {start_date}&$orderby=GewijzigdOp desc"

    zaak_data = []
    skip = 0
    top = 100  # Smaller batches for faster processing
    pages_collected = 0

    while datetime.now() - start_time < max_duration and pages_collected < 20:  # Limit pages
        url = f"{zaak_url}&$top={top}&$skip={skip}"
        print(f"Fetching Zaak page {pages_collected + 1} (skip={skip})...")

        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                break

            data = response.json()
            batch = data.get('value', [])
            if not batch:
                break

            zaak_data.extend(batch)
            print(f"  Collected {len(batch)} motion records")

            pages_collected += 1
            if len(batch) < top:
                break
            skip += top

        except Exception as e:
            print(f"Error: {e}")
            break

    print(f"Total motion records collected: {len(zaak_data)}")

    # Step 2: Process Zaak data for votes (with time limit)
    print("\n2. Processing for votes (10 min limit)...")
    besluit_data = []
    stemming_data = []
    processed_count = 0

    for zaak in zaak_data:
        if datetime.now() - start_time >= max_duration:
            print("Time limit reached, stopping processing")
            break

        if processed_count % 20 == 0:
            print(f"Processing motion {processed_count + 1}/{len(zaak_data)}...")

        zaak_id = zaak['Id']
        url = f"{base_url}/Zaak({zaak_id})?$expand=Besluit($expand=Stemming)"

        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()

                # Extract Besluit data
                besluiten = data.get('Besluit', [])
                besluit_data.extend(besluiten)

                # Extract Stemming data
                for besluit in besluiten:
                    stemmingen = besluit.get('Stemming', [])
                    stemming_data.extend(stemmingen)

        except Exception as e:
            print(f"Error processing {zaak_id}: {e}")
            continue

        processed_count += 1

    # Save data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    with open(f'bronnateriaal-onbewerkt/zaak_current/zaak_voted_motions_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(zaak_data, f, ensure_ascii=False, indent=2)

    with open(f'bronnateriaal-onbewerkt/besluit_current/besluit_voted_motions_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(besluit_data, f, ensure_ascii=False, indent=2)

    with open(f'bronnateriaal-onbewerkt/stemming_current/stemming_voted_motions_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(stemming_data, f, ensure_ascii=False, indent=2)

    # Summary
    end_time = datetime.now()
    duration = end_time - start_time

    print("\n=== Collection Summary ===")
    print(f"Duration: {duration}")
    print(f"Motions collected: {len(zaak_data)}")
    print(f"Besluiten found: {len(besluit_data)}")
    print(f"Stemmingen found: {len(stemming_data)}")

    voted_motions = len([b for b in besluit_data if b.get('Stemming')])
    print(f"Motions with actual votes: {voted_motions}")

    if stemming_data:
        print("✅ Vote data successfully collected!")
    else:
        print("⚠️  No vote data found - may need different date range or filters")

if __name__ == "__main__":
    collect_voted_motions_fast()