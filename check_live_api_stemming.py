#!/usr/bin/env python3
"""
Check Live API for Actual Stemming Structure
Compare with our collected data to see what's missing.
"""

import requests
import json

def check_live_stemming_structure():
    """Check the actual Stemming entity structure from the live API."""

    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"

    print("🔍 CHECKING LIVE API STEMMING STRUCTURE")
    print("=" * 50)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'MotieMatcher-DataCheck/1.0',
        'Accept': 'application/json'
    })

    # 1. Get metadata for Stemming
    print("1. Getting Stemming metadata...")
    try:
        metadata_url = f"{base_url}/$metadata"
        response = session.get(metadata_url, timeout=30)

        if response.status_code == 200:
            metadata = response.text
            # Find Stemming entity definition
            if "Stemming" in metadata:
                print("   ✅ Stemming found in metadata")

                # Extract Stemming property definitions
                lines = metadata.split('\n')
                in_stemming = False
                stemming_props = []

                for line in lines:
                    if '<EntityType Name="Stemming"' in line:
                        in_stemming = True
                        continue
                    elif in_stemming and '<EntityType Name=' in line and 'Stemming' not in line:
                        break
                    elif in_stemming and '<Property Name=' in line:
                        stemming_props.append(line.strip())

                print("   Stemming properties from metadata:")
                for prop in stemming_props[:15]:  # Show first 15
                    print(f"     {prop}")

                # Check for Besluit_Id
                besluit_id_found = any('Besluit_Id' in prop for prop in stemming_props)
                print(f"   Besluit_Id property: {'✅ FOUND' if besluit_id_found else '❌ MISSING'}")

        else:
            print(f"   ❌ Metadata request failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Metadata error: {e}")

    # 2. Get actual Stemming records
    print("\n2. Getting actual Stemming records...")
    try:
        url = f"{base_url}/Stemming?$top=3"
        response = session.get(url, timeout=30)

        if response.status_code == 200:
            data = response.json()
            records = data.get('value', [])

            print(f"   ✅ Got {len(records)} records")

            if records:
                record = records[0]
                print("   Live API Stemming record keys:")
                for key in sorted(record.keys()):
                    value = record[key]
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    print(f"     {key}: {value}")

                # Check for Besluit_Id
                has_besluit_id = 'Besluit_Id' in record or 'BesluitId' in record
                print(f"   Besluit_Id in live data: {'✅ FOUND' if has_besluit_id else '❌ MISSING'}")

                if has_besluit_id:
                    besluit_key = 'Besluit_Id' if 'Besluit_Id' in record else 'BesluitId'
                    print(f"   Besluit_Id value: {record[besluit_key]}")

        else:
            print(f"   ❌ Stemming request failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Stemming request error: {e}")

    # 3. Try with $expand to see relationships
    print("\n3. Testing $expand for Stemming relationships...")
    try:
        url = f"{base_url}/Stemming?$top=1&$expand=Besluit"
        response = session.get(url, timeout=30)

        print(f"   Expand query status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            records = data.get('value', [])

            if records:
                record = records[0]
                expanded_keys = [k for k in record.keys() if k not in ['Id', 'Soort', 'FractieGrootte', 'ActorNaam', 'ActorFractie', 'Vergissing', 'SidActorLid', 'SidActorFractie', 'GewijzigdOp', 'ApiGewijzigdOp', 'Verwijderd']]

                if expanded_keys:
                    print("   ✅ Expanded data found:")
                    for key in expanded_keys:
                        value = record[key]
                        if isinstance(value, dict):
                            print(f"     {key}: [Object with keys: {list(value.keys())[:3]}...]")
                        elif isinstance(value, list):
                            print(f"     {key}: [Array with {len(value)} items]")
                        else:
                            print(f"     {key}: {value}")
                else:
                    print("   ⚠️ No expanded data found")

        else:
            print(f"   ❌ Expand query failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Expand query error: {e}")

    # 4. Compare with our collected data
    print("\n4. COMPARISON WITH COLLECTED DATA:")
    print("   Our data keys: Id, Soort, FractieGrootte, ActorNaam, ActorFractie, Vergissing, SidActorLid, SidActorFractie, GewijzigdOp, ApiGewijzigdOp, Verwijderd")
    print("   Missing from our data: Besluit_Id, Persoon_Id, Fractie_Id")

    print("\n🔧 CONCLUSION:")
    if "besluit_id_found" in locals() and besluit_id_found:
        print("   ✅ Live API has Besluit_Id - our data collection is incomplete")
        print("   🔄 Need to re-collect Stemming data with proper field selection")
    else:
        print("   ❌ Live API also missing Besluit_Id - metadata might be wrong")
        print("   🔍 Need to investigate alternative linkage methods")

if __name__ == "__main__":
    check_live_stemming_structure()