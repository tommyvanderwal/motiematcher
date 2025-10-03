#!/usr/bin/env python3
"""
Analyze Party Positions for Website Matching
Check if we can extract clear party positions (80%+ majority) for matching users     # Show sample party positions
    print("\n📊 VOORBEELD PARTIJ STANDPUNTEN:")
    sample_positions = []
    for besluit_id, positions in list(party_positions.items())[:5]:  # Show first 5 besluit
        sample_positions.extend([f"Besluit {besluit_id[:8]}...: {pos}" for pos in positions])

    for pos in sample_positions[:10]:  # Show first 10 positions
        print(f"  {pos}")es.
"""

from pathlib import Path
import json
from collections import Counter, defaultdict

def analyze_individual_votes():
    """Analyze party positions that can be used for website matching."""

    print("🔍 ANALYSE PARTIJ STANDPUNTEN VOOR WEBSITE MATCHING")
    print("=" * 55)

    # Load ALL voting data instead of sample
    print("Loading complete voting dataset...")
    all_votes = []
    stemming_dir = Path("bronnateriaal-onbewerkt/stemming_complete")

    if not stemming_dir.exists():
        print("❌ Stemming directory not found")
        return {}

    for file_path in stemming_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_votes.extend(data)
                else:
                    all_votes.append(data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue

    print(f"Loaded {len(all_votes)} total votes for analysis")

    # Analyze vote structure
    sample_vote = all_votes[0]
    print("\n📋 Vote record structure:")
    for key in sorted(sample_vote.keys()):
        value = sample_vote[key]
        if isinstance(value, str) and len(str(value)) > 50:
            value = str(value)[:50] + "..."
        print(f"  {key}: {value}")

    # Analyze individual vs party votes
    print("\n🧑‍🤝‍🧑 ANALYZING INDIVIDUAL VS PARTY VOTES...")
    votes_with_persoon = 0
    votes_with_fractie = 0
    individual_votes = 0
    party_block_votes = 0

    party_vote_counts = defaultdict(lambda: defaultdict(int))
    person_vote_counts = defaultdict(int)

    for vote in all_votes:
        persoon_id = vote.get('Persoon_Id')
        fractie_id = vote.get('Fractie_Id')
        actor_naam = vote.get('ActorNaam')
        actor_fractie = vote.get('ActorFractie')
        fractie_grootte = vote.get('FractieGrootte', 0)

        if persoon_id:
            votes_with_persoon += 1
            person_vote_counts[persoon_id] += 1

        if fractie_id:
            votes_with_fractie += 1

        # Check if this looks like an individual vote
        # Individual votes typically have Persoon_Id and specific actor names
        if persoon_id and actor_naam and not actor_naam.endswith(')') and len(actor_naam.split()) >= 2:
            individual_votes += 1
        else:
            party_block_votes += 1

        # Count votes per party
        if actor_fractie:
            party_vote_counts[actor_fractie][vote.get('Soort', 'Unknown')] += 1

    print(f"Total votes: {len(all_votes)}")
    print(f"Votes with Persoon_Id: {votes_with_persoon} ({votes_with_persoon/len(all_votes)*100:.1f}%)")
    print(f"Votes with Fractie_Id: {votes_with_fractie} ({votes_with_fractie/len(all_votes)*100:.1f}%)")
    print(f"Potential individual votes: {individual_votes}")
    print(f"Potential party block votes: {party_block_votes}")

    # Analyze voting patterns
    print("\n🏛️ PARTY VOTING PATTERNS:")
    for party, vote_types in sorted(party_vote_counts.items()):
        total_party_votes = sum(vote_types.values())
        voor_pct = vote_types.get('Voor', 0) / total_party_votes * 100 if total_party_votes > 0 else 0
        tegen_pct = vote_types.get('Tegen', 0) / total_party_votes * 100 if total_party_votes > 0 else 0

        print(f"  {party:20}: {total_party_votes:4} votes "
              f"(Voor: {voor_pct:5.1f}%, Tegen: {tegen_pct:5.1f}%)")

    # Check for party positions (80%+ majority = clear party position)
    print("\n🎯 PARTIJ STANDPUNTEN VOOR WEBSITE MATCHING:")
    party_positions_90pct = 0
    party_positions_80pct = 0
    party_positions = defaultdict(list)  # Track party positions per besluit

    besluit_vote_patterns = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for vote in all_votes:
        besluit_id = vote.get('Besluit_Id')
        party = vote.get('ActorFractie')
        vote_type = vote.get('Soort')

        if besluit_id and party and vote_type:
            besluit_vote_patterns[besluit_id][party][vote_type] += 1

    print(f"Analyzing {len(besluit_vote_patterns)} unique besluit with voting data...")

    for besluit_id, party_votes in besluit_vote_patterns.items():
        total_besluit_votes = sum(sum(party.values()) for party in party_votes.values())

        if total_besluit_votes < 10:  # Skip very small votes
            continue

        # Check if any party has clear position (80%+ in one direction)
        for party, votes in party_votes.items():
            total_party = sum(votes.values())
            voor = votes.get('Voor', 0)
            tegen = votes.get('Tegen', 0)
            onthouding = votes.get('Onthouding', 0)

            if total_party >= 3:  # At least 3 votes from party for meaningful position
                voor_pct = voor / total_party * 100
                tegen_pct = tegen / total_party * 100
                onthouding_pct = onthouding / total_party * 100

                # Check for 90%+ majority in one direction
                if voor_pct >= 90:
                    party_positions[besluit_id].append(f"{party}: VOOR ({voor_pct:.1f}%)")
                    party_positions_90pct += 1
                elif tegen_pct >= 90:
                    party_positions[besluit_id].append(f"{party}: TEGEN ({tegen_pct:.1f}%)")
                    party_positions_90pct += 1
                elif onthouding_pct >= 90:
                    party_positions[besluit_id].append(f"{party}: ONTHOUDING ({onthouding_pct:.1f}%)")
                    party_positions_90pct += 1

                # Also count 80%+ as clear party position
                elif voor_pct >= 80:
                    party_positions[besluit_id].append(f"{party}: VOOR ({voor_pct:.1f}%)")
                    party_positions_80pct += 1
                elif tegen_pct >= 80:
                    party_positions[besluit_id].append(f"{party}: TEGEN ({tegen_pct:.1f}%)")
                    party_positions_80pct += 1
                elif onthouding_pct >= 80:
                    party_positions[besluit_id].append(f"{party}: ONTHOUDING ({onthouding_pct:.1f}%)")
                    party_positions_80pct += 1

    print(f"Partij standpunten (≥90% unaniem): {party_positions_90pct}")
    print(f"Partij standpunten (≥80% meerderheid): {party_positions_80pct}")
    print(f"Totaal besluit met partij stemmen: {len(besluit_vote_patterns)}")

    # Show sample party positions
    print("\n� VOORBEELD PARTIJ STANDPUNTEN (≥90%):")
    sample_positions = []
    for besluit_id, positions in list(party_positions.items())[:10]:  # Show first 10
        sample_positions.extend([f"Besluit {besluit_id[:8]}...: {pos}" for pos in positions])

    for pos in sample_positions[:15]:  # Show first 15 positions
        print(f"  {pos}")

    # Analyze how many party positions we can extract
    total_party_positions = party_positions_90pct + party_positions_80pct
    print(f"\n📈 TOTAAL UITWINBARE PARTIJ STANDPUNTEN: {total_party_positions}")

    # Calculate potential for website matching
    unique_parties = len(set(party for party_votes in besluit_vote_patterns.values() for party in party_votes.keys()))
    print(f"Unieke partijen in dataset: {unique_parties}")

    avg_positions_per_party = total_party_positions / unique_parties if unique_parties > 0 else 0
    print(f"Gemiddeld aantal standpunten per partij: {avg_positions_per_party:.1f}")

    # Conclusion
    print("\n🎯 CONCLUSION VOOR WEBSITE MATCHING:")
    if total_party_positions > 500:
        print("✅ UITSTEKEND: Voldoende partij standpunten voor goede matching")
        print(f"   - {total_party_positions} partij standpunten gevonden")
        print("   - Uitstekend voor partij matching functionaliteit")
    elif total_party_positions > 200:
        print("✅ GOED: Ruime hoeveelheid partij standpunten")
        print(f"   - {total_party_positions} partij standpunten gevonden")
        print("   - Goede basis voor partij matching")
    elif total_party_positions > 100:
        print("⚠️ VOLDOENDE: Redelijke hoeveelheid partij standpunten")
        print(f"   - {total_party_positions} partij standpunten gevonden")
        print("   - Basis voor partij matching, kan worden uitgebreid")
    elif total_party_positions > 50:
        print("⚠️ MINIMAAL: Beperkte partij standpunten")
        print(f"   - {total_party_positions} partij standpunten gevonden")
        print("   - Mogelijk voor basis matching, maar beperkt")
    else:
        print("❌ ONVOLDOENDE: Weinig partij standpunten gevonden")
        print(f"   - {total_party_positions} partij standpunten gevonden")
        print("   - Overweeg meer data te verzamelen voor betere matching")

    return {
        'total_votes': len(all_votes),
        'individual_votes': votes_with_persoon,
        'party_votes': votes_with_fractie,
        'party_positions_90pct': party_positions_90pct,
        'party_positions_80pct': party_positions_80pct,
        'total_party_positions': total_party_positions,
        'unique_parties': unique_parties,
        'ready_for_party_matching': total_party_positions > 50
    }

if __name__ == "__main__":
    results = analyze_individual_votes()
    print(f"\n✅ Analysis complete: {results}")