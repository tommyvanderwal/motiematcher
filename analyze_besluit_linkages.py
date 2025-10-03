#!/usr/bin/env python3
"""
Analyze Besluit Data for Voting Linkages
Check if besluit (decision) data links votes to zaken.
"""

from pathlib import Path
import json
from collections import Counter

def analyze_besluit_linkages():
    """Analyze besluit data to see if it links votes to zaken."""

    besluit_dir = Path("bronmateriaal-onbewerkt/besluit")
    if not besluit_dir.exists():
        print(f"Directory {besluit_dir} does not exist!")
        return

    besluit_files = list(besluit_dir.glob("*fullterm*.json"))
    print(f"Found {len(besluit_files)} besluit files")

    # Sample first few files to understand structure
    sample_files = besluit_files[:3]

    total_besluiten = 0
    zaak_links = 0
    stemming_links = 0

    for file_path in sample_files:
        print(f"\n=== ANALYZING {file_path.name} ===")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"Data type: {type(data)}")

            if isinstance(data, list):
                records = data
            elif isinstance(data, dict) and 'value' in data:
                records = data['value']
            else:
                continue

            print(f"Records: {len(records)}")

            # Sample first few records
            for i, record in enumerate(records[:5]):
                if isinstance(record, dict):
                    total_besluiten += 1
                    print(f"\nRecord {i+1} keys: {list(record.keys())}")

                    zaak_id = record.get('ZaakId') or record.get('Zaak_Id')
                    stemming_id = record.get('StemmingId') or record.get('Stemming_Id')

                    if zaak_id:
                        zaak_links += 1
                        print(f"  ZaakId: {zaak_id}")

                    if stemming_id:
                        stemming_links += 1
                        print(f"  StemmingId: {stemming_id}")

                    print(f"  Soort: {record.get('Soort')}")
                    print(f"  Besluit: {record.get('Besluit')}")

        except Exception as e:
            print(f"Error: {e}")

    print(f"\n=== BESLUIT LINKAGE SUMMARY ===")
    print(f"Total besluiten analyzed: {total_besluiten}")
    print(f"Besluiten with ZaakId: {zaak_links}")
    print(f"Besluiten with StemmingId: {stemming_links}")

    if zaak_links > 0 and stemming_links > 0:
        print("✅ BESLUIT DATA LINKS VOTES TO ZAKEN")
        print("   - Besluit entity may provide the missing linkage")
    else:
        print("❌ NO CLEAR LINKAGE IN BESLUIT DATA")

if __name__ == "__main__":
    analyze_besluit_linkages()