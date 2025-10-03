#!/usr/bin/env python3
"""
Deep analysis of parliament member collection issues
Investigate why we only get 221 persons with unknown status
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime
from collections import Counter

def test_persoon_api():
    """Test the persoon API directly to see what we get"""
    print("[*] TESTING PERSON API DIRECTLY")
    print("=" * 40)

    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"

    # Test basic persoon endpoint
    url = f"{base_url}/Persoon"
    print(f"Testing URL: {url}")

    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")

            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")

                if 'value' in data:
                    persons = data['value']
                    print(f"Number of persons: {len(persons)}")

                    if persons:
                        print("\n[*] FIRST PERSON STRUCTURE:")
                        first_person = persons[0]
                        print(f"Keys: {list(first_person.keys())}")

                        for key, value in first_person.items():
                            if key == 'Functies' and value:
                                print(f"{key}: {len(value)} functions")
                                if len(value) > 0:
                                    print(f"  First function keys: {list(value[0].keys())}")
                                    print(f"  First function: {value[0]}")
                            else:
                                print(f"{key}: {value}")

                        # Check for name fields
                        name_fields = ['Naam', 'Voornaam', 'Achternaam', 'VolledigeNaam']
                        print(f"\n[*] NAME FIELDS CHECK:")
                        for field in name_fields:
                            if field in first_person:
                                print(f"  {field}: {first_person[field]}")
                            else:
                                print(f"  {field}: NOT FOUND")

                        # Check for status fields
                        status_fields = ['Status', 'Actief', 'IsActief']
                        print(f"\n[*] STATUS FIELDS CHECK:")
                        for field in status_fields:
                            if field in first_person:
                                print(f"  {field}: {first_person[field]}")
                            else:
                                print(f"  {field}: NOT FOUND")

            elif isinstance(data, list):
                print(f"Direct list with {len(data)} items")
                if data:
                    print(f"First item keys: {list(data[0].keys())}")

        else:
            print(f"Error response: {response.text}")

    except Exception as e:
        print(f"Exception: {e}")

def analyze_existing_persoon_file():
    """Analyze the existing persoon file in detail"""
    print("\n[*] ANALYZING EXISTING PERSON FILE")
    print("=" * 40)

    file_path = Path("bronmateriaal-onbewerkt/persoon/persoon_page_1_fullterm_20251003_002435.json")

    if not file_path.exists():
        print(f"[-] File not found: {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, dict) and 'value' in data:
            persons = data['value']
        elif isinstance(data, list):
            persons = data
        else:
            print("[-] Unexpected data structure")
            return

        print(f"[+] Loaded {len(persons)} persons")

        # Analyze all persons for any non-unknown data
        names_found = []
        statuses_found = []
        functions_found = []

        for i, person in enumerate(persons):
            # Check for any name data
            name = person.get('Naam')
            if name and name != 'Unknown':
                names_found.append((i, name))

            # Check for any status data
            status = person.get('Status')
            if status and status != 'Unknown':
                statuses_found.append((i, status))

            # Check for functions
            functies = person.get('Functies', [])
            if functies:
                functions_found.append((i, len(functies)))

        print(f"\n[*] ANALYSIS RESULTS:")
        print(f"Persons with actual names: {len(names_found)}")
        if names_found:
            for idx, name in names_found[:5]:  # Show first 5
                print(f"  Person {idx}: {name}")

        print(f"Persons with actual status: {len(statuses_found)}")
        if statuses_found:
            for idx, status in statuses_found[:5]:
                print(f"  Person {idx}: {status}")

        print(f"Persons with functions: {len(functions_found)}")
        if functions_found:
            for idx, count in functions_found[:5]:
                print(f"  Person {idx}: {count} functions")

        # Check if all persons are identical
        if len(persons) > 1:
            first_person = persons[0]
            identical_count = sum(1 for p in persons if p == first_person)
            print(f"\n[*] DATA CONSISTENCY:")
            print(f"All persons identical to first: {identical_count}/{len(persons)}")

            if identical_count != len(persons):
                # Find differences
                different_persons = []
                for i, p in enumerate(persons):
                    if p != first_person:
                        different_persons.append(i)
                print(f"Different persons at indices: {different_persons[:10]}")

    except Exception as e:
        print(f"[-] Error analyzing file: {e}")

def check_api_metadata():
    """Check API metadata to understand available fields"""
    print("\n[*] CHECKING API METADATA")
    print("=" * 40)

    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"

    # Try to get metadata
    metadata_url = f"{base_url}/$metadata"
    print(f"Metadata URL: {metadata_url}")

    try:
        response = requests.get(metadata_url, timeout=30)
        print(f"Metadata status: {response.status_code}")

        if response.status_code == 200:
            # Save metadata for analysis
            metadata_file = Path("api_metadata.xml")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"[+] Saved metadata to {metadata_file}")

            # Look for Persoon entity
            text = response.text
            if 'Persoon' in text:
                print("[+] Persoon entity found in metadata")
                # Extract Persoon definition (rough)
                start = text.find('<EntityType Name="Persoon">')
                if start != -1:
                    end = text.find('</EntityType>', start)
                    if end != -1:
                        persoon_def = text[start:end+13]
                        print("[+] Persoon entity definition:")
                        print(persoon_def[:500] + "..." if len(persoon_def) > 500 else persoon_def)
            else:
                print("[-] Persoon entity not found in metadata")

        else:
            print(f"[-] Metadata request failed: {response.status_code}")

    except Exception as e:
        print(f"[-] Metadata check failed: {e}")

def main():
    print("[*] DEEP PERSON DATA ANALYSIS")
    print("=" * 50)

    # Test API directly
    test_persoon_api()

    # Analyze existing file
    analyze_existing_persoon_file()

    # Check API metadata
    check_api_metadata()

    print("\n[+] DEEP ANALYSIS COMPLETE")

if __name__ == "__main__":
    main()