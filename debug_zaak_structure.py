#!/usr/bin/env python3
"""
Debug Zaak Data Structure
Check what types of zaken are actually in the data.
"""

from pathlib import Path
import json
from collections import Counter

def debug_zaak_structure():
    """Debug the zaak data structure to understand what's actually there."""

    zaak_dir = Path("bronmateriaal-onbewerkt/zaak")
    if not zaak_dir.exists():
        print(f"Directory {zaak_dir} does not exist!")
        return

    zaak_files = list(zaak_dir.glob("*fullterm*.json"))
    print(f"Found {len(zaak_files)} zaak files")

    # Sample first few files to understand structure
    sample_files = zaak_files[:3]

    for file_path in sample_files:
        print(f"\n=== ANALYZING {file_path.name} ===")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"Data type: {type(data)}")

            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")

                if 'value' in data:
                    records = data['value']
                    print(f"Records in 'value': {len(records)}")

                    # Sample first few records
                    for i, record in enumerate(records[:3]):
                        if isinstance(record, dict):
                            print(f"Record {i+1} keys: {list(record.keys())}")
                            print(f"Record {i+1} Soort: {record.get('Soort')}")
                            print(f"Record {i+1} Id: {record.get('Id')}")
                            print()

            elif isinstance(data, list):
                print(f"Direct list with {len(data)} records")

                # Sample first few records
                for i, record in enumerate(data[:3]):
                    if isinstance(record, dict):
                        print(f"Record {i+1} keys: {list(record.keys())}")
                        print(f"Record {i+1} Soort: {record.get('Soort')}")
                        print(f"Record {i+1} Id: {record.get('Id')}")
                        print()

        except Exception as e:
            print(f"Error: {e}")

    # Now do a broader analysis of zaak types
    print(f"\n=== BROAD ZAAK TYPE ANALYSIS ===")
    zaak_types = Counter()
    total_records = 0

    for file_path in zaak_files[:10]:  # Sample of files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict) and 'value' in data:
                records = data['value']
            elif isinstance(data, list):
                records = data
            else:
                continue

            for record in records:
                if isinstance(record, dict):
                    total_records += 1
                    soort = record.get('Soort')
                    if soort:
                        zaak_types[soort] += 1

        except Exception as e:
            continue

    print(f"Total records sampled: {total_records}")
    print(f"Zaak types found:")
    for soort, count in sorted(zaak_types.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {soort}: {count}")

if __name__ == "__main__":
    debug_zaak_structure()