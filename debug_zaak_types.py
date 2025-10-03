#!/usr/bin/env python3
"""
Debug zaak types - see what actual types exist
"""

import json
from pathlib import Path
from collections import Counter

def debug_zaak_types():
    """Debug what zaak types actually exist"""

    zaak_dir = Path('bronmateriaal-onbewerkt/zaak')

    if not zaak_dir.exists():
        print("❌ Zaak directory not found")
        return

    # Load first file and examine soorten
    zaak_files = list(zaak_dir.glob('*fullterm*.json'))[:1]
    print(f"📁 Examining first zaak file: {zaak_files[0].name}")

    with open(zaak_files[0], 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Records in file: {len(data)}")

    # Get all unique soorten
    soorten = set()
    for zaak in data[:50]:  # First 50 records
        soort = zaak.get('Soort')
        if soort:
            soorten.add(soort)

    print(f"\nActual zaak soorten found: {sorted(soorten)}")

    # Count them
    counter = Counter()
    for zaak in data:
        soort = zaak.get('Soort', 'Unknown')
        counter[soort] += 1

    print("\nCounts in this file:")
    for soort, count in sorted(counter.items(), key=lambda x: x[1], reverse=True):
        print("15")

if __name__ == "__main__":
    debug_zaak_types()