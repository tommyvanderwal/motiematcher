#!/usr/bin/env python3
"""
Cross-reference Stemming IDs with Zaak IDs
Check if stemming Id fields match zaak Id fields for linkage.
"""

from pathlib import Path
import json
from collections import Counter

def cross_reference_ids():
    """Cross-reference stemming IDs with zaak IDs to find potential linkages."""

    # Load zaak IDs
    zaak_dir = Path("bronmateriaal-onbewerkt/zaak")
    stemming_dir = Path("bronmateriaal-onbewerkt/stemming")

    if not zaak_dir.exists() or not stemming_dir.exists():
        print("Required directories not found!")
        return

    # Get sample zaak IDs
    zaak_files = list(zaak_dir.glob("*fullterm*.json"))[:2]  # Sample first 2 files
    zaak_ids = set()

    print("=== COLLECTING ZAAK IDs ===")
    for file_path in zaak_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                for record in data:
                    if isinstance(record, dict) and 'Id' in record:
                        zaak_ids.add(record['Id'])
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    print(f"Collected {len(zaak_ids)} zaak IDs from sample")

    # Get sample stemming IDs
    stemming_files = list(stemming_dir.glob("*fullterm*.json"))[:2]  # Sample first 2 files
    stemming_ids = set()

    print("\n=== COLLECTING STEMMING IDs ===")
    for file_path in stemming_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                for record in data:
                    if isinstance(record, dict) and 'Id' in record:
                        stemming_ids.add(record['Id'])
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    print(f"Collected {len(stemming_ids)} stemming IDs from sample")

    # Check for overlaps
    overlap = zaak_ids.intersection(stemming_ids)
    print(f"\n=== ID OVERLAP ANALYSIS ===")
    print(f"Zaak IDs in stemming: {len(overlap)}")

    if overlap:
        print("✅ FOUND ID OVERLAPS - POSSIBLE LINKAGE")
        print(f"Sample overlaps: {list(overlap)[:5]}")
    else:
        print("❌ NO ID OVERLAPS FOUND")

    # Check if stemming records have any field that might reference zaak
    print(f"\n=== CHECKING STEMMING RECORD STRUCTURE ===")
    sample_stemming_file = list(stemming_dir.glob("*fullterm*.json"))[0]
    try:
        with open(sample_stemming_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list) and data:
            record = data[0]
            print(f"Stemming record keys: {list(record.keys())}")

            # Look for any field that might contain zaak reference
            potential_links = []
            for key, value in record.items():
                if 'zaak' in key.lower() or 'motie' in key.lower() or 'amendement' in key.lower():
                    potential_links.append((key, value))

            if potential_links:
                print("POTENTIAL ZAAK LINK FIELDS:")
                for key, value in potential_links:
                    print(f"  {key}: {value}")
            else:
                print("No obvious zaak reference fields found")

    except Exception as e:
        print(f"Error analyzing stemming structure: {e}")

if __name__ == "__main__":
    cross_reference_ids()