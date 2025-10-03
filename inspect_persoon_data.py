#!/usr/bin/env python3
"""
Quick script to inspect persoon data
"""

import json
from collections import Counter

# Load persoon data
with open('bronmateriaal-onbewerkt/persoon/persoon_page_1_fullterm_20251003_002435.json', 'r', encoding='utf-8') as f:
    personen = json.load(f)

print(f"Aantal personen: {len(personen)}")
print("\nStatus distributie:")
statuses = [p.get('Status', 'Unknown') for p in personen]
status_counts = Counter(statuses)
for status, count in status_counts.most_common():
    print(f"  {status}: {count}")

print("\nEerste 10 personen:")
for i, p in enumerate(personen[:10]):
    roepnaam = p.get('Roepnaam', '')
    achternaam = p.get('Achternaam', '')
    status = p.get('Status', 'Unknown')
    print(f"  {i+1}. {roepnaam} {achternaam} - Status: {status}")

# Check for active parliament members
active_count = 0
for p in personen:
    functies = p.get('Functie', [])
    if isinstance(functies, list):
        for functie in functies:
            if isinstance(functie, dict):
                eind_date = functie.get('FunctieEind')
                if not eind_date:  # No end date = active
                    active_count += 1
                    break

print(f"\nActieve parlementariërs (ongeveer): {active_count}")