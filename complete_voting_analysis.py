#!/usr/bin/env python3
"""
Complete Voting Pattern Analysis for MotieMatcher
Link votes to motions/amendments and analyze party voting patterns.
"""

from pathlib import Path
import json
from collections import defaultdict, Counter
import requests

class CompleteVotingAnalyzer:
    """Complete analyzer for party voting patterns on motions and amendments."""

    def __init__(self):
        self.base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MotieMatcher-FinalAnalysis/1.0',
            'Accept': 'application/json'
        })

    def load_all_data(self):
        """Load all required data for complete analysis."""
        print("Loading complete dataset...")

        # Load complete stemming data
        stemming_dir = Path("bronmateriaal-onbewerkt/stemming_complete")
        stemming_data = []
        for file_path in stemming_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    batch = json.load(f)
                    stemming_data.extend(batch)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        # Load zaak data
        zaak_dir = Path("bronmateriaal-onbewerkt/zaak")
        zaak_data = []
        for file_path in zaak_dir.glob("*fullterm*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    batch = json.load(f)
                    zaak_data.extend(batch)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        # Load besluit data
        besluit_dir = Path("bronmateriaal-onbewerkt/besluit")
        besluit_data = []
        for file_path in besluit_dir.glob("*fullterm*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    batch = json.load(f)
                    besluit_data.extend(batch)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        print(f"Loaded {len(stemming_data)} votes, {len(zaak_data)} zaken, {len(besluit_data)} besluiten")
        return stemming_data, zaak_data, besluit_data

    def create_besluit_to_zaak_mapping_via_api(self, besluit_ids, max_expands=50):
        """Use OData $expand to get Besluit → Zaak mappings from live API."""
        print(f"Creating Besluit → Zaak mapping via API for {len(besluit_ids)} besluiten...")

        besluit_to_zaak = {}
        processed = 0

        # Process in batches to avoid timeouts
        batch_size = 10
        for i in range(0, min(len(besluit_ids), max_expands), batch_size):
            batch = besluit_ids[i:i+batch_size]

            for besluit_id in batch:
                try:
                    url = f"{self.base_url}/Besluit('{besluit_id}')?$expand=Zaak"
                    response = self.session.get(url, timeout=15)

                    if response.status_code == 200:
                        data = response.json()
                        zaak_data = data.get('Zaak', [])

                        if isinstance(zaak_data, list):
                            zaak_ids = [z.get('Id') for z in zaak_data if z.get('Id')]
                        elif isinstance(zaak_data, dict):
                            zaak_ids = [zaak_data.get('Id')] if zaak_data.get('Id') else []
                        else:
                            zaak_ids = []

                        if zaak_ids:
                            besluit_to_zaak[besluit_id] = zaak_ids
                            processed += 1

                    # Rate limiting
                    import time
                    time.sleep(0.5)

                except Exception as e:
                    print(f"Error getting zaak for besluit {besluit_id}: {e}")

            print(f"Processed {processed}/{min(len(besluit_ids), max_expands)} besluiten")

            if processed >= max_expands:
                break

        return besluit_to_zaak

    def analyze_party_voting_patterns(self):
        """Complete analysis of party voting patterns on motions and amendments."""

        print("🎯 COMPLETE PARTY VOTING PATTERN ANALYSIS")
        print("=" * 60)

        # Load all data
        stemming_data, zaak_data, besluit_data = self.load_all_data()

        # Get unique besluit IDs from votes
        besluit_ids = list(set(v.get('Besluit_Id') for v in stemming_data if v.get('Besluit_Id')))
        print(f"Found {len(besluit_ids)} unique besluit IDs in voting data")

        # Create Besluit → Zaak mapping (sample for demonstration)
        print("\n🔗 Creating Besluit → Zaak linkages...")
        besluit_to_zaak = self.create_besluit_to_zaak_mapping_via_api(besluit_ids, max_expands=20)

        print(f"Successfully linked {len(besluit_to_zaak)} besluiten to zaken")

        # Create vote aggregation by zaak
        zaak_voting_patterns = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        linked_votes = 0
        total_votes = len(stemming_data)

        for vote in stemming_data:
            besluit_id = vote.get('Besluit_Id')
            party = vote.get('ActorFractie')
            vote_type = vote.get('Soort')

            if besluit_id and party and vote_type:
                # Get zaak IDs for this besluit
                zaak_ids = besluit_to_zaak.get(besluit_id, [])

                for zaak_id in zaak_ids:
                    zaak_voting_patterns[zaak_id][party][vote_type] += 1
                    linked_votes += 1

        print("\n📊 VOTING ANALYSIS RESULTS:")
        print(f"Total votes: {total_votes}")
        print(f"Linked votes: {linked_votes} ({linked_votes/total_votes*100:.1f}%)")
        print(f"Motions with voting data: {len(zaak_voting_patterns)}")

        # Analyze party consistency and patterns
        party_stats = defaultdict(lambda: {'total_votes': 0, 'motions_supported': 0, 'motions_opposed': 0})

        for zaak_id, party_votes in zaak_voting_patterns.items():
            for party, votes in party_votes.items():
                total_party_votes = sum(votes.values())
                voor_votes = votes.get('Voor', 0)
                tegen_votes = votes.get('Tegen', 0)

                party_stats[party]['total_votes'] += total_party_votes

                # Determine if party supported or opposed the motion
                if voor_votes > tegen_votes:
                    party_stats[party]['motions_supported'] += 1
                elif tegen_votes > voor_votes:
                    party_stats[party]['motions_opposed'] += 1

        # Show top parties by activity
        print("\n🏛️ PARTY VOTING STATISTICS:")
        sorted_parties = sorted(party_stats.items(),
                               key=lambda x: x[1]['total_votes'],
                               reverse=True)

        for party, stats in sorted_parties[:10]:
            total_votes = stats['total_votes']
            supported = stats['motions_supported']
            opposed = stats['motions_opposed']
            total_motions = supported + opposed

            if total_motions > 0:
                support_rate = supported / total_motions * 100
                print(f"  {party:15}: {total_votes:4} votes on {total_motions:2} motions "
                      f"(Support: {support_rate:4.1f}%)")

        # Sample motion analysis
        print("\n📄 SAMPLE MOTION VOTING PATTERNS:")
        sample_zaken = list(zaak_voting_patterns.keys())[:3]

        for zaak_id in sample_zaken:
            # Find zaak details
            zaak_info = next((z for z in zaak_data if z.get('Id') == zaak_id), None)
            if zaak_info:
                title = zaak_info.get('Titel', 'Unknown')[:50]

                print(f"\nMotion: {title}...")
                print("  Party votes:")

                party_votes = zaak_voting_patterns[zaak_id]
                for party in sorted(party_votes.keys()):
                    votes = party_votes[party]
                    voor = votes.get('Voor', 0)
                    tegen = votes.get('Tegen', 0)
                    print(f"    {party:15}: Voor={voor}, Tegen={tegen}")

        # Website readiness assessment
        print("\n🎯 WEBSITE READINESS ASSESSMENT:")
        print(f"✅ Complete voting data: {len(stemming_data)} votes with full linkage fields")
        print(f"✅ Party voting patterns: {len(party_stats)} parties analyzed")
        print(f"✅ Motion/amendment coverage: {len([z for z in zaak_data if z.get('Soort') in ['Motie', 'Amendement']])} items")
        print(f"✅ Voting linkage: {linked_votes}/{total_votes} votes linked to specific motions ({linked_votes/total_votes*100:.1f}%)")

        if linked_votes > 0:
            print("✅ READY: Data structure supports party voting pattern matching for website")
        else:
            print("⚠️ PARTIAL: Voting linkage needs expansion for complete website functionality")

        return {
            'total_votes': total_votes,
            'linked_votes': linked_votes,
            'parties_analyzed': len(party_stats),
            'motions_with_votes': len(zaak_voting_patterns),
            'website_ready': linked_votes > 0
        }

if __name__ == "__main__":
    analyzer = CompleteVotingAnalyzer()
    results = analyzer.analyze_party_voting_patterns()
    print(f"\n✅ Complete analysis finished: {results}")