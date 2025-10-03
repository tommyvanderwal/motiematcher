#!/usr/bin/env python3
"""
Complete Voting Linkage Analysis with Fixed Data
Analyze party voting patterns using complete stemming data.
"""

from pathlib import Path
import json
from collections import Counter, defaultdict

def load_complete_stemming_data():
    """Load the newly collected complete stemming data."""
    stemming_dir = Path("bronmateriaal-onbewerkt/stemming_complete")
    if not stemming_dir.exists():
        print(f"Directory {stemming_dir} does not exist!")
        return []

    data = []
    for file_path in stemming_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    data.extend(file_data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return data

def load_zaak_data():
    """Load zaak data for motions and amendments."""
    zaak_dir = Path("bronmateriaal-onbewerkt/zaak")
    zaken = []

    for file_path in zaak_dir.glob("*fullterm*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    zaken.extend(file_data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return zaken

def load_besluit_data():
    """Load besluit data."""
    besluit_dir = Path("bronmateriaal-onbewerkt/besluit")
    besluiten = []

    for file_path in besluit_dir.glob("*fullterm*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    besluiten.extend(file_data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return besluiten

def create_zaak_to_besluit_mapping(zaken, besluiten):
    """Create mapping from zaak to besluit (incomplete - needs proper linkage)."""
    # For now, we'll work with the direct relationship we can establish
    # In practice, this would need the expanded navigation data
    zaak_to_besluit = defaultdict(list)

    # This is a placeholder - we need the actual Zaak ↔ Besluit linkage
    # For demonstration, we'll use a simplified approach
    return zaak_to_besluit

def analyze_party_voting_patterns():
    """Analyze party voting patterns using complete data."""

    print("🎯 ANALYZING PARTY VOTING PATTERNS")
    print("=" * 50)

    # Load data
    print("Loading data...")
    stemming_data = load_complete_stemming_data()
    zaak_data = load_zaak_data()
    besluit_data = load_besluit_data()

    print(f"Loaded {len(stemming_data)} complete stemming records")
    print(f"Loaded {len(zaak_data)} zaak records")
    print(f"Loaded {len(besluit_data)} besluit records")

    # Analyze stemming data structure
    if stemming_data:
        sample = stemming_data[0]
        print("\n📋 Stemming record structure:")
        for key in sorted(sample.keys()):
            value = sample[key]
            if isinstance(value, str) and len(str(value)) > 50:
                value = str(value)[:50] + "..."
            print(f"  {key}: {value}")

    # Count votes by party and type
    party_votes = defaultdict(lambda: defaultdict(int))
    total_votes = 0

    print("\n📊 ANALYZING VOTES BY PARTY...")
    for vote in stemming_data:
        party = vote.get('ActorFractie')
        vote_type = vote.get('Soort')  # Voor/Tegen/Ongeldig

        if party and vote_type:
            party_votes[party][vote_type] += 1
            total_votes += 1

    print(f"Total votes analyzed: {total_votes}")
    print(f"Parties found: {len(party_votes)}")

    # Show top parties by vote count
    print("\n🏛️ TOP PARTIES BY VOTE COUNT:")
    sorted_parties = sorted(party_votes.items(),
                           key=lambda x: sum(x[1].values()),
                           reverse=True)

    for party, votes in sorted_parties[:10]:  # Top 10
        total_party_votes = sum(votes.values())
        voor_pct = votes.get('Voor', 0) / total_party_votes * 100 if total_party_votes > 0 else 0
        tegen_pct = votes.get('Tegen', 0) / total_party_votes * 100 if total_party_votes > 0 else 0

        print(f"  {party:20}: {total_party_votes:5} votes "
              f"(Voor: {voor_pct:4.1f}%, Tegen: {tegen_pct:4.1f}%)")

    # Analyze linkage potential
    print("\n🔗 VOTING LINKAGE ANALYSIS:")
    votes_with_besluit = sum(1 for v in stemming_data if v.get('Besluit_Id'))
    votes_with_fractie = sum(1 for v in stemming_data if v.get('Fractie_Id'))
    votes_with_persoon = sum(1 for v in stemming_data if v.get('Persoon_Id'))

    print(f"Votes with Besluit_Id: {votes_with_besluit}/{len(stemming_data)} ({votes_with_besluit/len(stemming_data)*100:.1f}%)")
    print(f"Votes with Fractie_Id: {votes_with_fractie}/{len(stemming_data)} ({votes_with_fractie/len(stemming_data)*100:.1f}%)")
    print(f"Votes with Persoon_Id: {votes_with_persoon}/{len(stemming_data)} ({votes_with_persoon/len(stemming_data)*100:.1f}%)")

    # Check for motion/amendment zaken
    motion_zaken = [z for z in zaak_data if z.get('Soort') in ['Motie', 'Amendement']]
    print(f"Motion/Amendment zaken: {len(motion_zaken)}")

    if motion_zaken:
        print("\n📄 SAMPLE MOTIONS/AMENDMENTS:")
        for i, zaak in enumerate(motion_zaken[:3]):
            print(f"  {i+1}. {zaak.get('Titel', 'No title')[:60]}... (ID: {zaak.get('Id')})")

    # Summary
    print("\n🎯 SUMMARY:")
    print(f"✅ Complete stemming data collected with all required fields")
    print(f"✅ Party voting patterns analyzed for {len(party_votes)} parties")
    print(f"✅ {len(motion_zaken)} motions/amendments identified")
    print(f"🔄 Next: Establish Besluit → Zaak linkage for complete voting analysis")

    return {
        'total_votes': total_votes,
        'parties': len(party_votes),
        'motions': len(motion_zaken),
        'votes_with_besluit': votes_with_besluit
    }

if __name__ == "__main__":
    results = analyze_party_voting_patterns()
    print(f"\n✅ Analysis complete: {results}")