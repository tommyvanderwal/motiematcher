#!/usr/bin/env python3
"""
Fix Voting Linkage Analysis using Besluit as Bridge
Link Stemming → Besluit → Zaak to get party voting patterns per motion/amendment.
"""

from pathlib import Path
import json
from collections import Counter, defaultdict

def load_entity_data(entity_name):
    """Load all data for a specific entity."""
    entity_dir = Path(f"bronmateriaal-onbewerkt/{entity_name}")
    if not entity_dir.exists():
        print(f"Directory {entity_dir} does not exist!")
        return []

    data = []
    for file_path in entity_dir.glob("*fullterm*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    data.extend(file_data)
                elif isinstance(file_data, dict) and 'value' in file_data:
                    data.extend(file_data['value'])
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return data

def create_besluit_to_zaak_mapping(besluit_data):
    """Create mapping from Besluit ID to list of Zaak IDs."""
    besluit_to_zaak = defaultdict(list)

    for besluit in besluit_data:
        besluit_id = besluit.get('Id')
        # Besluit has navigation to Zaak, but in our data it might be embedded
        # For now, we'll need to use the reverse relationship from Zaak
        pass

    return besluit_to_zaak

def create_zaak_to_besluit_mapping(zaak_data):
    """Create mapping from Zaak ID to list of Besluit IDs."""
    zaak_to_besluit = defaultdict(list)

    for zaak in zaak_data:
        zaak_id = zaak.get('Id')
        # Zaak has Besluit navigation, but in our flat data we need to find another way
        # For now, let's collect all zaak IDs that are motions/amendments
        if zaak.get('Soort') in ['Motie', 'Amendement']:
            zaak_to_besluit[zaak_id] = []  # Will be populated from besluit data

    return zaak_to_besluit

def analyze_voting_linkage_fixed():
    """Analyze voting linkage using the correct relationship: Zaak ↔ Besluit ↔ Stemming."""

    print("🔍 ANALYZING VOTING LINKAGE: Zaak ↔ Besluit ↔ Stemming")
    print("=" * 60)

    # Load all required data
    print("Loading data...")
    zaak_data = load_entity_data('zaak')
    besluit_data = load_entity_data('besluit')
    stemming_data = load_entity_data('stemming')

    print(f"Loaded {len(zaak_data)} zaak records")
    print(f"Loaded {len(besluit_data)} besluit records")
    print(f"Loaded {len(stemming_data)} stemming records")

    # Create mappings
    print("\nCreating mappings...")

    # 1. Map Besluit ID to Zaak IDs (from besluit navigation)
    besluit_to_zaak = defaultdict(list)
    for besluit in besluit_data:
        besluit_id = besluit.get('Id')
        # In our flat data, we don't have the navigation expanded
        # We'll need to use the reverse relationship or find another way

    # 2. Map Zaak ID to Besluit IDs
    zaak_to_besluit = defaultdict(list)
    for zaak in zaak_data:
        zaak_id = zaak.get('Id')
        if zaak.get('Soort') in ['Motie', 'Amendement']:
            zaak_to_besluit[zaak_id] = []

    # 3. Map Besluit ID to Stemming records
    besluit_to_stemming = defaultdict(list)
    for stemming in stemming_data:
        besluit_id = stemming.get('Besluit_Id')
        if besluit_id:
            besluit_to_stemming[besluit_id].append(stemming)

    print(f"Found {len(zaak_to_besluit)} motion/amendment zaken")
    print(f"Found {len(besluit_to_stemming)} besluiten with stemmingen")

    # Now we need to link Besluit to Zaak
    # Since we don't have expanded navigation in our data, let's try a different approach
    # Check if Besluit records have any field that references Zaak

    print("\n🔍 INVESTIGATING BESLUIT TO ZAAK LINKAGE...")

    # Sample besluit records to see structure
    sample_besluiten = besluit_data[:5]
    for i, besluit in enumerate(sample_besluiten):
        print(f"\nBesluit {i+1}: {besluit.get('Id')}")
        print(f"  Keys: {list(besluit.keys())}")
        for key, value in besluit.items():
            if 'zaak' in key.lower() or 'agendapunt' in key.lower():
                print(f"  {key}: {value}")

    # Try to find linkage through Agendapunt (since Besluit → Agendapunt → Zaak)
    agendapunt_data = load_entity_data('agendapunt')
    print(f"\nLoaded {len(agendapunt_data)} agendapunt records")

    # Create Agendapunt to Zaak mapping
    agendapunt_to_zaak = {}
    for agendapunt in agendapunt_data:
        agendapunt_id = agendapunt.get('Id')
        # Agendapunt has Zaak navigation, but again not expanded in our data
        pass

    # For now, let's try a simpler approach: count how many linkages we can find
    linked_votes = 0
    total_votes = len(stemming_data)

    # Since we know Stemming → Besluit works, let's see what percentage of stemmen have besluit links
    stemming_with_besluit = sum(1 for s in stemming_data if s.get('Besluit_Id'))

    print("\n📊 LINKAGE ANALYSIS RESULTS:")
    print(f"Total stemming records: {total_votes}")
    print(f"Stemming with Besluit_Id: {stemming_with_besluit} ({stemming_with_besluit/total_votes*100:.1f}%)")

    # Now we need to figure out the Besluit → Zaak link
    # Let's check if there's a pattern in the data or if we need to use the API with $expand

    print("\n🔧 NEXT STEPS:")
    print("1. Use OData $expand to get Besluit with Zaak navigation")
    print("2. Or find the correct field name in besluit data that links to zaak")
    print("3. Then we can complete the Zaak ↔ Besluit ↔ Stemming linkage")

    return {
        'total_stemming': total_votes,
        'stemming_with_besluit': stemming_with_besluit,
        'zaak_count': len(zaak_to_besluit),
        'besluit_count': len(besluit_data)
    }

if __name__ == "__main__":
    results = analyze_voting_linkage_fixed()
    print(f"\n✅ Analysis complete: {results}")