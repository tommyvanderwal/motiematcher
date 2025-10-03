#!/usr/bin/env python3
"""
Test FractieZetelPersoon endpoint to find active parliament members
"""

import requests
import json
from datetime import datetime
from pathlib import Path

def test_fractie_zetel_persoon_api():
    """Test the FractieZetelPersoon API to find parliament members"""
    print("[*] TESTING FRACTIEZETELPERSOON API")
    print("=" * 50)

    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"

    # Test FractieZetelPersoon endpoint
    url = f"{base_url}/FractieZetelPersoon"
    print(f"Testing URL: {url}")

    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")

            if isinstance(data, dict) and 'value' in data:
                members = data['value']
                print(f"Number of FractieZetelPersoon records: {len(members)}")

                if members:
                    print("\n[*] FIRST MEMBER STRUCTURE:")
                    first_member = members[0]
                    print(f"Keys: {list(first_member.keys())}")

                    for key, value in first_member.items():
                        print(f"{key}: {value}")

                    # Check for active members (no TotEnMet date)
                    active_count = 0
                    for member in members[:50]:  # Check first 50
                        tot_en_met = member.get('TotEnMet')
                        if tot_en_met is None:
                            active_count += 1

                    print(f"\n[*] ACTIVE MEMBERS CHECK (first 50): {active_count}")

                    # Get unique persons
                    person_ids = set()
                    for member in members[:100]:  # Check first 100
                        person_id = member.get('Persoon_Id')
                        if person_id:
                            person_ids.add(person_id)

                    print(f"[*] UNIQUE PERSONS IN FIRST 100 RECORDS: {len(person_ids)}")

        else:
            print(f"Error response: {response.status_code}")

    except Exception as e:
        print(f"Exception: {e}")

def test_fractie_zetel_api():
    """Test the FractieZetel API"""
    print("\n[*] TESTING FRACTIEZETEL API")
    print("=" * 30)

    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"

    url = f"{base_url}/FractieZetel"
    print(f"Testing URL: {url}")

    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, dict) and 'value' in data:
                zetels = data['value']
                print(f"Number of FractieZetel records: {len(zetels)}")

                if zetels:
                    print("\n[*] FIRST ZETEL STRUCTURE:")
                    first_zetel = zetels[0]
                    print(f"Keys: {list(first_zetel.keys())}")

                    for key, value in first_zetel.items():
                        print(f"{key}: {value}")

    except Exception as e:
        print(f"Exception: {e}")

def test_fractie_api():
    """Test the Fractie API"""
    print("\n[*] TESTING FRACTIE API")
    print("=" * 25)

    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"

    url = f"{base_url}/Fractie"
    print(f"Testing URL: {url}")

    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, dict) and 'value' in data:
                fracties = data['value']
                print(f"Number of Fractie records: {len(fracties)}")

                if fracties:
                    print("\n[*] FIRST FRACTIE STRUCTURE:")
                    first_fractie = fracties[0]
                    print(f"Keys: {list(first_fractie.keys())}")

                    for key, value in first_fractie.items():
                        print(f"{key}: {value}")

    except Exception as e:
        print(f"Exception: {e}")

def analyze_current_parliament_period():
    """Analyze what constitutes the current parliament period"""
    print("\n[*] ANALYZING CURRENT PARLIAMENT PERIOD")
    print("=" * 40)

    # Current parliament started December 6, 2023
    parliament_start = datetime(2023, 12, 6)

    print(f"Parliament start date: {parliament_start.date()}")

    # Test query with date filter
    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"

    # Try to get active FractieZetelPersoon records
    url = f"{base_url}/FractieZetelPersoon?$filter=Van le {parliament_start.isoformat()}Z and (TotEnMet eq null or TotEnMet gt {parliament_start.isoformat()}Z)"
    print(f"Testing filtered URL: {url}")

    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, dict) and 'value' in data:
                active_members = data['value']
                print(f"Number of active FractieZetelPersoon records: {len(active_members)}")

                # Get unique persons
                person_ids = set()
                for member in active_members:
                    person_id = member.get('Persoon_Id')
                    if person_id:
                        person_ids.add(person_id)

                print(f"Unique active persons: {len(person_ids)}")

                if active_members:
                    print("\n[*] SAMPLE ACTIVE MEMBER:")
                    sample = active_members[0]
                    for key, value in sample.items():
                        print(f"{key}: {value}")

    except Exception as e:
        print(f"Exception: {e}")

def main():
    print("[*] INVESTIGATING PARLIAMENT MEMBER COLLECTION")
    print("=" * 55)

    # Test the different APIs
    test_fractie_api()
    test_fractie_zetel_api()
    test_fractie_zetel_persoon_api()

    # Analyze current parliament
    analyze_current_parliament_period()

    print("\n[+] INVESTIGATION COMPLETE")

if __name__ == "__main__":
    main()