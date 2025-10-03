#!/usr/bin/env python3
"""
Step 1 CORRECT: Use the regular fullterm stemming data which has MORE records
Then enrich with Besluit info and match to Zaken

The key insight: We have 130k+ stemmingen in fullterm files!
We just need to analyze vote patterns directly.
"""

import json
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Any

def load_fullterm_stemming_data() -> List[Dict[str, Any]]:
    """Load ALL fullterm stemming data - much more than stemming_complete!"""
    stemming_dir = Path("bronmateriaal-onbewerkt/stemming")
    all_stemmingen = []
    
    print("Loading fullterm stemming data...")
    file_count = 0
    for file_path in stemming_dir.glob("stemming_page_*_fullterm_*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_stemmingen.extend(data)
                    file_count += 1
                    if file_count % 100 == 0:
                        print(f"  Loaded {file_count} files, {len(all_stemmingen)} stemmingen so far...")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    print(f"✅ Total stemmingen loaded: {len(all_stemmingen)} from {file_count} files")
    return all_stemmingen

def load_fullterm_zaak_data() -> List[Dict[str, Any]]:
    """Load all zaak data"""
    zaak_dir = Path("bronmateriaal-onbewerkt/zaak")
    all_zaken = []
    
    print("Loading fullterm zaak data...")
    for file_path in zaak_dir.glob("zaak_page_*_fullterm_*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_zaken.extend(data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    print(f"✅ Total zaken loaded: {len(all_zaken)}")
    return all_zaken

def analyze_vote_patterns_direct(stemmingen: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Group votes by common identifiers to find voting sessions.
    Since we don't have Besluit_Id in regular stemming, we group by timestamp + similarity
    """
    
    # Group by GewijzigdOp timestamp (votes happen in batches)
    votes_by_timestamp = defaultdict(list)
    
    for stemming in stemmingen:
        timestamp = stemming.get('GewijzigdOp', '')
        if timestamp:
            # Truncate to minute level - all votes in same minute are likely same besluit
            timestamp_key = timestamp[:16]  # YYYY-MM-DDTHH:MM
            votes_by_timestamp[timestamp_key].append(stemming)
    
    print(f"\n✅ Grouped into {len(votes_by_timestamp)} voting sessions by timestamp")
    
    # Filter for sessions with reasonable vote counts (multiple parties voted)
    voting_sessions = {}
    for timestamp_key, votes in votes_by_timestamp.items():
        if len(votes) >= 5:  # At least 5 votes (multiple parties)
            voting_sessions[timestamp_key] = {
                'timestamp': timestamp_key,
                'votes': votes,
                'vote_count': len(votes)
            }
    
    print(f"✅ Found {len(voting_sessions)} substantial voting sessions (≥5 votes)")
    return voting_sessions

def calculate_session_results(session: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate vote results for a session"""
    votes = session['votes']
    
    voor_count = sum(1 for v in votes if v.get('Soort') == 'Voor')
    tegen_count = sum(1 for v in votes if v.get('Soort') == 'Tegen')
    total = voor_count + tegen_count
    margin = abs(voor_count - tegen_count)
    
    return {
        'voor': voor_count,
        'tegen': tegen_count,
        'total': total,
        'margin': margin,
        'passed': voor_count > tegen_count,
        'vote_percentage': (voor_count / total * 100) if total > 0 else 0,
        'timestamp': session['timestamp'],
        'votes': votes
    }

def match_voting_sessions_to_zaken(
    voting_sessions: Dict[str, Dict[str, Any]],
    zaken: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Match voting sessions to zaken by date proximity.
    Votes typically happen shortly after zaak is introduced.
    """
    
    # Create zaak lookup by date
    zaken_by_date = defaultdict(list)
    for zaak in zaken:
        datum_str = zaak.get('GestartOp', '')
        if datum_str:
            try:
                # Extract date part (YYYY-MM-DD)
                date_key = datum_str[:10]
                zaken_by_date[date_key].append(zaak)
            except:
                continue
    
    print(f"\n✅ Indexed {len(zaken)} zaken by {len(zaken_by_date)} unique dates")
    
    matched_items = []
    
    for session_key, session in voting_sessions.items():
        # Extract date from timestamp
        vote_date = session['timestamp'][:10]
        
        # Look for zaken on same day or nearby days
        candidate_zaken = []
        for day_offset in [0, -1, 1, -2, 2]:  # Check same day and ±2 days
            check_date_obj = datetime.fromisoformat(vote_date)
            from datetime import timedelta
            check_date = (check_date_obj + timedelta(days=day_offset)).strftime('%Y-%m-%d')
            candidate_zaken.extend(zaken_by_date.get(check_date, []))
        
        # For each candidate zaak, create a matched item
        for zaak in candidate_zaken:
            soort = zaak.get('Soort', '')
            if soort not in ['Motie', 'Wet', 'Amendement']:
                continue
            
            # Calculate vote results
            vote_results = calculate_session_results(session)
            
            # Skip if too few votes
            if vote_results['total'] < 10:
                continue
            
            matched_item = zaak.copy()
            matched_item['vote_results'] = vote_results
            matched_item['voting_session_key'] = session_key
            matched_items.append(matched_item)
    
    print(f"✅ Matched {len(matched_items)} zaken with voting sessions")
    return matched_items

def filter_recent_close_votes(matched_items: List[Dict[str, Any]], top_n: int = 100) -> List[Dict[str, Any]]:
    """Filter for recent period and close votes"""
    
    # Filter for 2022-2025
    recent_items = []
    for item in matched_items:
        datum_str = item.get('GestartOp', '')
        if not datum_str:
            continue
        
        try:
            datum = datetime.fromisoformat(datum_str.replace('Z', '+00:00'))
            year = datum.year
            if year >= 2022 and year <= 2025:
                item['year'] = year
                recent_items.append(item)
        except:
            continue
    
    print(f"\n✅ Filtered to {len(recent_items)} recent items (2022-2025)")
    
    # Type distribution
    type_counts = Counter(i.get('Soort') for i in recent_items)
    print(f"   Type distribution: {dict(type_counts)}")
    
    # Sort by vote margin (closest first)
    sorted_items = sorted(recent_items, key=lambda x: x['vote_results']['margin'])
    
    # Select top N with balanced types
    selected = []
    type_targets = {
        'Motie': int(top_n * 0.7),
        'Wet': int(top_n * 0.15),
        'Amendement': int(top_n * 0.15)
    }
    
    type_selected = Counter()
    
    for item in sorted_items:
        soort = item.get('Soort')
        if type_selected[soort] < type_targets.get(soort, 0):
            selected.append(item)
            type_selected[soort] += 1
            if len(selected) >= top_n:
                break
    
    # Fill remaining
    if len(selected) < top_n:
        for item in sorted_items:
            if item not in selected:
                selected.append(item)
                if len(selected) >= top_n:
                    break
    
    print(f"\n✅ Selected top {len(selected)} closest votes")
    print(f"   Type distribution: {dict(Counter(i.get('Soort') for i in selected))}")
    
    if selected:
        margins = [i['vote_results']['margin'] for i in selected]
        print(f"   Vote margins: min={min(margins)}, max={max(margins)}, avg={sum(margins)/len(margins):.1f}")
    
    return selected

def create_output(selected_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create structured output for Step 2"""
    
    output_items = []
    
    for item in selected_items:
        vote_results = item['vote_results']
        
        # Extract full text
        titel = item.get('Titel', '')
        onderwerp = item.get('Onderwerp', '')
        full_text = f"{titel}\n{onderwerp}"
        
        # Check if zaak has embedded documents with more text
        documenten = item.get('Zaa kdocument', [])
        if documenten and len(documenten) > 0:
            doc_text = documenten[0].get('Inhoud', '')
            if doc_text and len(doc_text) > len(full_text):
                full_text = doc_text
        
        output_item = {
            'id': item.get('Id'),
            'nummer': item.get('Nummer'),
            'type': item.get('Soort'),
            'titel': titel,
            'onderwerp': onderwerp,
            'full_text': full_text,
            'date': item.get('GestartOp'),
            'year': item.get('year'),
            'vergaderjaar': item.get('Vergaderjaar'),
            'status': item.get('Status'),
            # Voting data
            'vote_voor': vote_results['voor'],
            'vote_tegen': vote_results['tegen'],
            'vote_total': vote_results['total'],
            'vote_margin': vote_results['margin'],
            'vote_passed': vote_results['passed'],
            'vote_percentage': round(vote_results['vote_percentage'], 1),
            'vote_timestamp': vote_results['timestamp'],
            # Close vote flags
            'extremely_close': vote_results['margin'] <= 5,
            'very_close': vote_results['margin'] <= 10,
            'close': vote_results['margin'] <= 20
        }
        
        output_items.append(output_item)
    
    output = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'step': 'step1_final_voting_filtering',
            'total_items': len(output_items),
            'date_range': '2022-2025',
            'method': 'timestamp_based_vote_grouping',
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
    print("🚀 Step 1 FINAL: Voting Data Filtering (Timestamp-based)")
    print("=" * 60)
    
    # Load data
    print("\n📂 Loading data...")
    stemmingen = load_fullterm_stemming_data()
    zaken = load_fullterm_zaak_data()
    
    if not stemmingen:
        print("❌ No stemming data found. Cannot proceed.")
        return
    
    # Analyze vote patterns
    print("\n🔍 Analyzing vote patterns...")
    voting_sessions = analyze_vote_patterns_direct(stemmingen)
    
    # Match to zaken
    print("\n🔗 Matching voting sessions to zaken...")
    matched_items = match_voting_sessions_to_zaken(voting_sessions, zaken)
    
    # Filter and select
    print("\n🎯 Filtering for recent close votes...")
    selected_items = filter_recent_close_votes(matched_items, top_n=100)
    
    if not selected_items:
        print("❌ No items found matching criteria.")
        return
    
    # Create output
    print("\n📊 Creating output...")
    output = create_output(selected_items)
    
    # Save
    output_file = 'step1_close_votes_filtered.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Step 1 Complete!")
    print(f"   Results saved to: {output_file}")
    
    # Summary
    print("\n📈 SUMMARY:")
    print(f"   Total stemmingen analyzed: {len(stemmingen)}")
    print(f"   Voting sessions found: {len(voting_sessions)}")
    print(f"   Items with votes: {len(matched_items)}")
    print(f"   Top close votes selected: {len(selected_items)}")
    print(f"   Type distribution: {output['metadata']['type_distribution']}")
    
    # Show top 5
    print("\n🏆 TOP 5 CLOSEST VOTES:")
    for i, item in enumerate(selected_items[:5], 1):
        title = item.get('titel', '')[:60]
        margin = item['vote_results']['margin']
        voor = item['vote_results']['voor']
        tegen = item['vote_results']['tegen']
        soort = item.get('Soort')
        print(f"{i}. [{soort}] {title}...")
        print(f"   Votes: {voor} voor vs {tegen} tegen (margin: {margin})")

if __name__ == '__main__':
    main()
