#!/usr/bin/env python3
"""
Voting Behavior Linkage Analysis
Analyzes if voting data (stemming) can be linked to motions and amendments (zaak).
"""

from pathlib import Path
import json
from collections import Counter

def analyze_voting_linkage():
    """Analyze if voting data can be linked to parliamentary matters."""

    # Load zaak data to get motion/amendment IDs
    zaak_dir = Path("bronmateriaal-onbewerkt/zaak")
    stemming_dir = Path("bronmateriaal-onbewerkt/stemming")

    if not zaak_dir.exists() or not stemming_dir.exists():
        print("Required directories not found!")
        return

    # Get zaak IDs that are motions or amendments
    motion_amendment_ids = set()
    zaak_files = list(zaak_dir.glob("*fullterm*.json"))

    print(f"Loading zaak data from {len(zaak_files)} files...")

    for file_path in zaak_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Zaak files are direct lists, not wrapped in {'value': [...]}
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict) and 'value' in data:
                records = data['value']
            else:
                continue

            for record in records:
                if isinstance(record, dict):
                    zaak_type = record.get('Soort')
                    zaak_id = record.get('Id')

                    # Collect motions and amendments
                    if zaak_type in ['Motie', 'Amendement'] and zaak_id:
                        motion_amendment_ids.add(zaak_id)

        except Exception as e:
            print(f"Error processing zaak file {file_path}: {e}")
            continue

    print(f"Found {len(motion_amendment_ids)} motion/amendment IDs in zaak data")

    # Now analyze stemming data for linkages
    stemming_files = list(stemming_dir.glob("*fullterm*.json"))
    print(f"Analyzing {len(stemming_files)} stemming files...")

    linked_votes = 0
    total_votes = 0
    zaak_references = Counter()
    actor_votes = Counter()

    sample_linked = []

    for file_path in stemming_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Stemming files have {'value': [...]}
            if isinstance(data, dict) and 'value' in data:
                records = data['value']
            else:
                continue

            for record in records:
                if isinstance(record, dict):
                    total_votes += 1

                    # Check for zaak reference
                    zaak_id = record.get('ZaakId') or record.get('Zaak_Id') or record.get('zaak_id')

                    if zaak_id:
                        zaak_references[zaak_id] += 1

                        # Check if this zaak is a motion or amendment
                        if zaak_id in motion_amendment_ids:
                            linked_votes += 1

                            # Collect actor (party/person) voting data
                            actor = record.get('ActorNaam') or record.get('Actor_Naam')
                            if actor:
                                actor_votes[actor] += 1

                            # Sample some linked records
                            if len(sample_linked) < 5:
                                sample_linked.append({
                                    'zaak_id': zaak_id,
                                    'actor': actor,
                                    'soort': record.get('Soort'),
                                    'fractie': record.get('Fractie'),
                                    'besluit': record.get('Besluit')
                                })

        except Exception as e:
            print(f"Error processing stemming file {file_path}: {e}")
            continue

    # Print results
    print(f"\n=== VOTING BEHAVIOR LINKAGE ANALYSIS ===")
    print(f"Total votes analyzed: {total_votes:,}")
    print(f"Votes linked to motions/amendments: {linked_votes:,}")
    print(f"Percentage linked: {(linked_votes / total_votes * 100):.1f}%" if total_votes > 0 else "0%")

    print(f"\n=== UNIQUE ZAAK REFERENCES IN VOTES ===")
    print(f"Total unique zaak IDs referenced in votes: {len(zaak_references)}")

    print(f"\n=== TOP ACTORS BY VOTES ===")
    for actor, count in sorted(actor_votes.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{actor}: {count} votes")

    print(f"\n=== SAMPLE LINKED VOTES ===")
    for i, vote in enumerate(sample_linked, 1):
        print(f"Vote {i}:")
        print(f"  Zaak ID: {vote['zaak_id']}")
        print(f"  Actor: {vote['actor']}")
        print(f"  Fractie: {vote['fractie']}")
        print(f"  Besluit: {vote['besluit']}")
        print()

    # Assessment
    print(f"=== LINKAGE ASSESSMENT ===")
    if linked_votes > 10000:  # Substantial linkage
        print("✅ STRONG LINKAGE FOUND")
        print("   - Voting data properly linked to motions/amendments")
        print("   - Party voting patterns can be extracted")
    elif linked_votes > 1000:
        print("⚠️ MODERATE LINKAGE FOUND")
        print("   - Some voting data linked, but may be incomplete")
    else:
        print("❌ WEAK OR NO LINKAGE FOUND")
        print("   - Voting data may not be properly linked to parliamentary matters")

if __name__ == "__main__":
    analyze_voting_linkage()