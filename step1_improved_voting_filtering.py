#!/usr/bin/env python3
"""
Step 1 IMPROVED: Filter recent parliamentary data (2022-2025) for items with ACTUAL VOTES
Focus on close votes where every vote matters - the most democratic significant items.

Strategy:
1. Load stemming_complete data (has Besluit_Id linking)
2. Match Besluit_Id to Zaak IDs via besluit files
3. Filter for recent period (2022-2025)
4. Calculate vote margins - focus on close votes
5. Select top 100 with good mix of Motie/Wet/Amendement
"""

import json
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Any

def load_stemming_complete_data() -> List[Dict[str, Any]]:
    """Load all stemming data from stemming_complete directory (has Besluit_Id)"""
    stemming_dir = Path("bronmateriaal-onbewerkt/stemming_complete")
    all_stemmingen = []
    
    if not stemming_dir.exists():
        print(f"⚠️  Warning: {stemming_dir} not found, falling back to regular stemming")
        return []
    
    for file_path in stemming_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_stemmingen.extend(data)
                print(f"Loaded {len(data)} stemmingen from {file_path.name}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    print(f"\n✅ Total stemmingen loaded: {len(all_stemmingen)}")
    return all_stemmingen

def load_besluit_data() -> Dict[str, Dict[str, Any]]:
    """
    Load besluit data - Note: besluit does NOT have Zaak_Id directly.
    We need to use agendapunt or document linking instead.
    """
    besluit_dir = Path("bronmateriaal-onbewerkt/besluit")
    besluiten = {}
    
    if not besluit_dir.exists():
        print(f"⚠️  Warning: {besluit_dir} not found")
        return {}
    
    for file_path in besluit_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for besluit in data:
                        besluit_id = besluit.get('Id')
                        if besluit_id:
                            besluiten[besluit_id] = besluit
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    print(f"✅ Loaded {len(besluiten)} besluiten")
    return besluiten

def load_agendapunt_data() -> List[Dict[str, Any]]:
    """Load agendapunt data which links besluiten to zaken"""
    agendapunt_dir = Path("bronmateriaal-onbewerkt/agendapunt")
    all_agendapunten = []
    
    if not agendapunt_dir.exists():
        print(f"⚠️  Warning: {agendapunt_dir} not found")
        return []
    
    for file_path in agendapunt_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_agendapunten.extend(data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    print(f"✅ Loaded {len(all_agendapunten)} agendapunten")
    return all_agendapunten

def load_fullterm_zaak_data() -> List[Dict[str, Any]]:
    """Load all zaak data from fullterm files"""
    zaak_dir = Path("bronmateriaal-onbewerkt/zaak")
    all_zaken = []
    
    for file_path in zaak_dir.glob("zaak_page_*_fullterm_*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_zaken.extend(data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    print(f"✅ Loaded {len(all_zaken)} zaken")
    return all_zaken

def group_votes_by_besluit(stemmingen: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group individual votes by Besluit_Id"""
    votes_by_besluit = defaultdict(list)
    
    for stemming in stemmingen:
        besluit_id = stemming.get('Besluit_Id')
        if besluit_id:
            votes_by_besluit[besluit_id].append(stemming)
    
    print(f"✅ Grouped votes into {len(votes_by_besluit)} besluiten")
    return votes_by_besluit

def calculate_vote_results(votes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate vote totals and margin for a besluit"""
    voor_count = 0
    tegen_count = 0
    
    for vote in votes:
        soort = vote.get('Soort', '')
        if soort == 'Voor':
            voor_count += 1
        elif soort == 'Tegen':
            tegen_count += 1
    
    total = voor_count + tegen_count
    margin = abs(voor_count - tegen_count)
    
    # Determine if passed
    passed = voor_count > tegen_count
    
    return {
        'voor': voor_count,
        'tegen': tegen_count,
        'total': total,
        'margin': margin,
        'passed': passed,
        'vote_percentage': (voor_count / total * 100) if total > 0 else 0
    }

def link_besluiten_to_zaken(
    votes_by_besluit: Dict[str, List[Dict[str, Any]]],
    besluiten: Dict[str, Dict[str, Any]],
    zaken: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Link voting data to zaken via besluiten"""
    
    # Create zaak lookup by ID
    zaken_by_id = {z.get('Id'): z for z in zaken if z.get('Id')}
    
    enriched_zaken = []
    
    for besluit_id, votes in votes_by_besluit.items():
        # Get the besluit
        besluit = besluiten.get(besluit_id)
        if not besluit:
            continue
        
        # Get zaak_id from besluit
        zaak_id = besluit.get('Zaak_Id')
        if not zaak_id:
            continue
        
        # Get the zaak
        zaak = zaken_by_id.get(zaak_id)
        if not zaak:
            continue
        
        # Calculate vote results
        vote_results = calculate_vote_results(votes)
        
        # Enrich zaak with voting data
        enriched_zaak = zaak.copy()
        enriched_zaak['besluit_id'] = besluit_id
        enriched_zaak['besluit'] = besluit
        enriched_zaak['voting_records'] = votes
        enriched_zaak['vote_results'] = vote_results
        enriched_zaak['has_voting_data'] = True
        
        enriched_zaken.append(enriched_zaak)
    
    print(f"✅ Linked {len(enriched_zaken)} zaken with voting data")
    return enriched_zaken

def filter_recent_votable_zaken(enriched_zaken: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter for recent period (2022-2025) and votable types"""
    filtered = []
    
    votable_types = {'Motie', 'Wet', 'Amendement'}
    
    for zaak in enriched_zaken:
        # Check type
        soort = zaak.get('Soort', '')
        if soort not in votable_types:
            continue
        
        # Check date
        datum_str = zaak.get('GestartOp', '')
        if not datum_str:
            continue
        
        try:
            # Parse date
            datum = datetime.fromisoformat(datum_str.replace('Z', '+00:00'))
            year = datum.year
            
            if year >= 2022 and year <= 2025:
                zaak['year'] = year
                filtered.append(zaak)
        except:
            continue
    
    print(f"✅ Filtered to {len(filtered)} recent votable zaken (2022-2025)")
    
    # Type distribution
    type_counts = Counter(z.get('Soort') for z in filtered)
    print(f"   Type distribution: {dict(type_counts)}")
    
    return filtered

def select_close_votes(zaken_with_votes: List[Dict[str, Any]], top_n: int = 100) -> List[Dict[str, Any]]:
    """
    Select items with closest votes - where every vote matters.
    Focus on dramatic democratic moments where one party could have changed the outcome.
    """
    
    # Filter for items with reasonable vote counts (at least 10 votes)
    valid_votes = [z for z in zaken_with_votes if z['vote_results']['total'] >= 10]
    
    print(f"✅ Found {len(valid_votes)} zaken with substantial voting (≥10 votes)")
    
    # Sort by margin (closest votes first)
    sorted_by_margin = sorted(valid_votes, key=lambda x: x['vote_results']['margin'])
    
    # Get balanced mix of types
    selected = []
    type_targets = {
        'Motie': int(top_n * 0.7),  # 70% moties (most common)
        'Wet': int(top_n * 0.15),   # 15% wetten (important)
        'Amendement': int(top_n * 0.15)  # 15% amendementen
    }
    
    type_counts = Counter()
    
    # First pass: select closest votes respecting type balance
    for zaak in sorted_by_margin:
        soort = zaak.get('Soort')
        if type_counts[soort] < type_targets.get(soort, 0):
            selected.append(zaak)
            type_counts[soort] += 1
            
            if len(selected) >= top_n:
                break
    
    # Second pass: fill remaining slots with closest votes regardless of type
    if len(selected) < top_n:
        for zaak in sorted_by_margin:
            if zaak not in selected:
                selected.append(zaak)
                if len(selected) >= top_n:
                    break
    
    print(f"\n✅ Selected top {len(selected)} closest votes")
    print(f"   Type distribution: {dict(Counter(z.get('Soort') for z in selected))}")
    
    # Show margin statistics
    margins = [z['vote_results']['margin'] for z in selected]
    print(f"   Vote margins: min={min(margins)}, max={max(margins)}, avg={sum(margins)/len(margins):.1f}")
    
    return selected

def create_output(selected_zaken: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create structured output for Step 2"""
    
    output_items = []
    
    for zaak in selected_zaken:
        vote_results = zaak['vote_results']
        
        # Extract full text
        titel = zaak.get('Titel', '')
        onderwerp = zaak.get('Onderwerp', '')
        full_text = f"{titel}\n{onderwerp}"
        
        item = {
            'id': zaak.get('Id'),
            'nummer': zaak.get('Nummer'),
            'type': zaak.get('Soort'),
            'titel': titel,
            'onderwerp': onderwerp,
            'full_text': full_text,
            'date': zaak.get('GestartOp'),
            'year': zaak.get('year'),
            'vergaderjaar': zaak.get('Vergaderjaar'),
            'status': zaak.get('Status'),
            # Voting data
            'besluit_id': zaak.get('besluit_id'),
            'vote_voor': vote_results['voor'],
            'vote_tegen': vote_results['tegen'],
            'vote_total': vote_results['total'],
            'vote_margin': vote_results['margin'],
            'vote_passed': vote_results['passed'],
            'vote_percentage': round(vote_results['vote_percentage'], 1),
            # Flag for close votes
            'extremely_close': vote_results['margin'] <= 5,
            'very_close': vote_results['margin'] <= 10,
            'close': vote_results['margin'] <= 20
        }
        
        output_items.append(item)
    
    output = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'step': 'step1_improved_voting_filtering',
            'total_items': len(output_items),
            'date_range': '2022-2025',
            'filter_criteria': {
                'has_actual_votes': True,
                'minimum_votes': 10,
                'votable_types': ['Motie', 'Wet', 'Amendement'],
                'sorted_by': 'vote_margin_ascending',
                'focus': 'close_votes_where_every_vote_matters'
            },
            'type_distribution': dict(Counter(item['type'] for item in output_items)),
            'next_step': 'step2_llm_impact_assessment'
        },
        'close_vote_items': output_items
    }
    
    return output

def main():
    print("🚀 Step 1 IMPROVED: Voting Data Filtering")
    print("=" * 60)
    
    # Load data
    print("\n📂 Loading data...")
    stemmingen = load_stemming_complete_data()
    besluiten = load_besluit_data()
    zaken = load_fullterm_zaak_data()
    
    if not stemmingen:
        print("❌ No stemming_complete data found. Cannot proceed.")
        return
    
    # Group votes by besluit
    print("\n🔗 Linking votes to besluiten...")
    votes_by_besluit = group_votes_by_besluit(stemmingen)
    
    # Link to zaken
    print("\n🔗 Linking besluiten to zaken...")
    enriched_zaken = link_besluiten_to_zaken(votes_by_besluit, besluiten, zaken)
    
    # Filter for recent and votable
    print("\n🔍 Filtering for recent votable items...")
    filtered_zaken = filter_recent_votable_zaken(enriched_zaken)
    
    # Select close votes
    print("\n🎯 Selecting closest votes (most democratic significant)...")
    selected_zaken = select_close_votes(filtered_zaken, top_n=100)
    
    # Create output
    print("\n📊 Creating output...")
    output = create_output(selected_zaken)
    
    # Save
    output_file = 'step1_close_votes_filtered.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Step 1 IMPROVED Complete!")
    print(f"   Results saved to: {output_file}")
    
    # Summary
    print("\n📈 SUMMARY:")
    print(f"   Total items with votes: {len(enriched_zaken)}")
    print(f"   Recent votable items: {len(filtered_zaken)}")
    print(f"   Top close votes selected: {len(selected_zaken)}")
    print(f"   Type distribution: {output['metadata']['type_distribution']}")
    
    # Show top 5 closest
    print("\n🏆 TOP 5 CLOSEST VOTES:")
    for i, item in enumerate(selected_zaken[:5], 1):
        title = item.get('titel', '')[:60]
        margin = item['vote_results']['margin']
        voor = item['vote_results']['voor']
        tegen = item['vote_results']['tegen']
        soort = item.get('Soort')
        print(f"{i}. [{soort}] {title}...")
        print(f"   Votes: {voor} voor vs {tegen} tegen (margin: {margin})")

if __name__ == '__main__':
    main()
