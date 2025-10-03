#!/usr/bin/env python3
"""
Analyze zaak data structure and completeness
Check if wetsartikelen and amendementen are fully collected
"""

import json
import os
from pathlib import Path
from collections import Counter

def analyze_zaak_data():
    """Analyze zaak data to check completeness of law articles and amendments"""

    zaak_dir = Path('bronmateriaal-onbewerkt/zaak')

    if not zaak_dir.exists():
        print("❌ Zaak directory not found")
        return

    # Find all fullterm zaak files
    zaak_files = list(zaak_dir.glob('*fullterm*.json'))
    print(f"📁 Found {len(zaak_files)} zaak files")

    if not zaak_files:
        print("❌ No zaak files found")
        return

    # Load and analyze zaak data
    all_zaken = []
    total_files = len(zaak_files)

    for i, file_path in enumerate(zaak_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                all_zaken.extend(data)
            else:
                all_zaken.append(data)

            if (i + 1) % 10 == 0:
                print(f"📊 Loaded {i+1}/{total_files} files, {len(all_zaken)} zaken so far...")

        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")

    print(f"\n✅ Total zaken loaded: {len(all_zaken)}")

    # Analyze zaak types
    soorten = Counter()
    for zaak in all_zaken:
        soort = zaak.get('Soort', 'Unknown')
        soorten[soort] += 1

    print(f"\n🏛️ ZAAK TYPES DISTRIBUTION:")
    print("=" * 40)

    total_count = sum(soorten.values())
    for soort, count in sorted(soorten.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_count) * 100
        print("15")

    # Check for wetsartikelen and amendementen specifically
    wet_related = ['Wet', 'Wetsartikel', 'Wetsvoorstel', 'Amendement']
    amendment_related = ['Amendement', 'Wijzigingsvoorstel']

    wet_count = sum(soorten.get(soort, 0) for soort in wet_related)
    amendment_count = sum(soorten.get(soort, 0) for soort in amendment_related)

    print("\n🎯 SPECIFIC ANALYSIS:")
    print(f"Wet-related zaken: {wet_count}")
    print(f"Amendment-related zaken: {amendment_count}")

    # Show sample records for key types
    print("\n📋 SAMPLE RECORDS:")
    print("=" * 30)

    samples_found = {}
    for zaak in all_zaken[:500]:  # Check first 500 for samples
        soort = zaak.get('Soort', 'Unknown')
        if soort not in samples_found and soort in ['Motie', 'Wet', 'Amendement', 'Wetsvoorstel']:
            samples_found[soort] = zaak
            if len(samples_found) >= 4:
                break

    for soort, zaak in samples_found.items():
        titel = zaak.get('Titel', '')[:80]
        print(f"{soort}: {titel}...")

if __name__ == "__main__":
    analyze_zaak_data()