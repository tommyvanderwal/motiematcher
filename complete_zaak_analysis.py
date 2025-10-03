#!/usr/bin/env python3
"""
Complete zaak types analysis across all files
"""

import json
from pathlib import Path
from collections import Counter

def analyze_all_zaak_types():
    """Analyze zaak types across all files efficiently"""

    zaak_dir = Path('bronmateriaal-onbewerkt/zaak')

    if not zaak_dir.exists():
        print("❌ Zaak directory not found")
        return

    zaak_files = list(zaak_dir.glob('*fullterm*.json'))
    print(f"📁 Analyzing all {len(zaak_files)} zaak files")

    # Count types efficiently without loading all data
    soorten = Counter()

    for i, file_path in enumerate(zaak_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                for zaak in data:
                    soort = zaak.get('Soort', 'Unknown')
                    soorten[soort] += 1

            if (i + 1) % 100 == 0:
                print(f"📊 Processed {i+1}/{len(zaak_files)} files...")

        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")

    print("\n🏛️ COMPLETE ZAAK TYPES DISTRIBUTION:")
    print("=" * 50)

    total_count = sum(soorten.values())
    print(f"Total zaken: {total_count:,}")

    # Show all types sorted by count
    for soort, count in sorted(soorten.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_count) * 100
        print("15")

    # Focus on key parliamentary types
    print("\n🎯 KEY PARLIAMENTARY MATTER TYPES:")
    print("=" * 40)

    key_types = {
        'Motie': soorten.get('Motie', 0),
        'Amendement': soorten.get('Amendement', 0),
        'Wet': soorten.get('Wet', 0),
        'Wetsvoorstel': soorten.get('Wetsvoorstel', 0),
        'Wetsartikel': soorten.get('Wetsartikel', 0),
        'Wetswijziging': soorten.get('Wetswijziging', 0),
        'Begrotingswet': soorten.get('Begrotingswet', 0),
        'Grondwet': soorten.get('Grondwet', 0)
    }

    for type_name, count in key_types.items():
        if count > 0:
            percentage = (count / total_count) * 100
            print("15")

    # Summary
    motie_count = key_types['Motie']
    amendement_count = key_types['Amendement']
    wet_count = sum([key_types.get(t, 0) for t in ['Wet', 'Wetsvoorstel', 'Wetsartikel', 'Wetswijziging', 'Begrotingswet', 'Grondwet']])

    print("\n📊 FINAL ASSESSMENT:")
    print("=" * 25)
    print(f"Total zaken: {total_count:,}")
    print(f"Moties: {motie_count:,} ({motie_count/total_count*100:.1f}%)")
    print(f"Amendementen: {amendement_count:,} ({amendement_count/total_count*100:.1f}%)")
    print(f"Wet-related: {wet_count:,} ({wet_count/total_count*100:.1f}%)")

    if motie_count > 1000 and amendement_count > 100 and wet_count > 100:
        print("✅ COMPREHENSIVE COVERAGE: All key parliamentary matter types well represented")
        return True
    else:
        print("❌ INCOMPLETE COVERAGE: Missing or insufficient key types")
        return False

if __name__ == "__main__":
    analyze_all_zaak_types()