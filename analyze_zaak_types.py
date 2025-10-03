#!/usr/bin/env python3
"""
Improved zaak data analysis with better type display
"""

import json
from pathlib import Path
from collections import Counter

def analyze_zaak_types():
    """Analyze zaak types with proper display"""

    zaak_dir = Path('bronmateriaal-onbewerkt/zaak')

    if not zaak_dir.exists():
        print("❌ Zaak directory not found")
        return

    # Load just first few files for quick analysis
    zaak_files = list(zaak_dir.glob('*fullterm*.json'))[:5]  # First 5 files
    print(f"📁 Analyzing first {len(zaak_files)} zaak files (sample)")

    all_zaken = []
    for file_path in zaak_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                all_zaken.extend(data)
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")

    print(f"✅ Sample zaken loaded: {len(all_zaken)}")

    # Analyze zaak types
    soorten = Counter()
    for zaak in all_zaken:
        soort = zaak.get('Soort', 'Unknown')
        soorten[soort] += 1

    print("\n🏛️ ZAAK TYPES (sample):")
    print("=" * 40)

    total_count = sum(soorten.values())
    for soort, count in sorted(soorten.items(), key=lambda x: x[1], reverse=True)[:20]:  # Top 20
        percentage = (count / total_count) * 100
        print("15")

    # Check specific types
    print("\n🎯 KEY TYPES:")
    print(f"Motie: {soorten.get('Motie', 0)}")
    print(f"Amendement: {soorten.get('Amendement', 0)}")
    print(f"Wet: {soorten.get('Wet', 0)}")
    print(f"Wetsvoorstel: {soorten.get('Wetsvoorstel', 0)}")
    print(f"Wetsartikel: {soorten.get('Wetsartikel', 0)}")

    # Show if we have comprehensive coverage
    motie_count = soorten.get('Motie', 0)
    amendement_count = soorten.get('Amendement', 0)
    wet_count = soorten.get('Wet', 0) + soorten.get('Wetsvoorstel', 0) + soorten.get('Wetsartikel', 0)

    print("\n📊 COVERAGE ASSESSMENT:")
    print(f"Total zaken in sample: {total_count}")
    print(f"Moties: {motie_count} ({motie_count/total_count*100:.1f}%)")
    print(f"Amendementen: {amendement_count} ({amendement_count/total_count*100:.1f}%)")
    print(f"Wet-related: {wet_count} ({wet_count/total_count*100:.1f}%)")

    if motie_count > 0 and amendement_count > 0 and wet_count > 0:
        print("✅ All key parliamentary matter types present")
    else:
        print("❌ Missing some key types")

if __name__ == "__main__":
    analyze_zaak_types()