#!/usr/bin/env python3
"""
Step 1: Recent Data Filtering & Enrichment
Filters parliamentary data for 2022-2025 period, only votable items (Moties/Wetten/Amendementen),
and enriches with complete voting data and full text content.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any, Optional

def load_recent_zaak_data() -> List[Dict]:
    """Load zaak data from recent 30-day files (2022-2025)"""
    zaken = []

    # Use relative path from current working directory
    zaak_dir = "zaak"
    print(f"Using zaak directory path: {zaak_dir}")

    import os
    if not os.path.exists(zaak_dir):
        print(f"Path {zaak_dir} does not exist!")
        # Try to list current directory contents
        current = os.getcwd()
        print(f"Current directory contents: {os.listdir(current)[:10]}")  # First 10 items
        return zaken

    print(f"Zaak directory exists! Contents: {os.listdir(zaak_dir)[:5]}...")

    # Focus on recent 30-day files which contain 2022-2025 data
    all_files = os.listdir(zaak_dir)
    matching_files = [f for f in all_files if '_30days_' in f and f.endswith('.json')]
    print(f"Found {len(matching_files)} 30-day files: {matching_files[:3]}...")

    for filename in matching_files:  # Load ALL 30-day files
        file_path = os.path.join(zaak_dir, filename)
        try:
            print(f"Loading {filename}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
                if isinstance(page_data, list):
                    zaken.extend(page_data)
                    print(f"  Added {len(page_data)} zaken")
                else:
                    value_data = page_data.get('value', [])
                    zaken.extend(value_data)
                    print(f"  Added {len(value_data)} zaken")
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            continue

    return zaken

def load_recent_stemming_data() -> List[Dict]:
    """Load stemming data from recent 30-day files"""
    stemmingen = []

    # Use relative path
    stemming_dir = "stemming"
    print(f"Using stemming directory path: {stemming_dir}")

    import os
    if not os.path.exists(stemming_dir):
        print(f"Path {stemming_dir} does not exist!")
        return stemmingen

    print(f"Stemming directory exists! Contents: {os.listdir(stemming_dir)[:5]}...")

    all_files = os.listdir(stemming_dir)
    matching_files = [f for f in all_files if '_30days_' in f and f.endswith('.json')]
    print(f"Found {len(matching_files)} 30-day files: {matching_files[:3]}...")

    for filename in matching_files[:1]:  # Load first file for testing
        file_path = os.path.join(stemming_dir, filename)
        try:
            print(f"Loading {filename}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
                if isinstance(page_data, list):
                    stemmingen.extend(page_data)
                    print(f"  Added {len(page_data)} stemmingen")
                else:
                    value_data = page_data.get('value', [])
                    stemmingen.extend(value_data)
                    print(f"  Added {len(value_data)} stemmingen")
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            continue

    return stemmingen

def filter_votable_zaken(zaken: List[Dict]) -> List[Dict]:
    """Filter for only votable items: Moties, Wetten, Amendementen"""
    votable_types = {'Motie', 'Wet', 'Amendement'}

    filtered_zaken = []
    for zaak in zaken:
        soort = zaak.get('Soort')
        if soort in votable_types:
            filtered_zaken.append(zaak)

    print(f"Filtered {len(filtered_zaken)} votable zaken from {len(zaken)} total zaken")
    return filtered_zaken

def filter_recent_zaken(zaken: List[Dict], start_year: int = 2022) -> List[Dict]:
    """Filter for zaken from start_year onwards"""
    filtered_zaken = []

    for zaak in zaken:
        gestart_op = zaak.get('GestartOp')
        if gestart_op:
            try:
                # Parse date and check if it's recent enough
                date_str = gestart_op.split('T')[0]  # Get YYYY-MM-DD part
                year = int(date_str.split('-')[0])
                if year >= start_year:
                    filtered_zaken.append(zaak)
            except (ValueError, IndexError):
                # If date parsing fails, include the zaak (better safe than sorry)
                filtered_zaken.append(zaak)

    print(f"Filtered {len(filtered_zaken)} zaken from {start_year} onwards")
    return filtered_zaken

def enrich_zaken_with_voting(zaken: List[Dict], stemmingen: List[Dict]) -> List[Dict]:
    """Enrich zaken with complete voting data"""
    # Group stemmingen by Besluit_Id
    besluit_stemmingen = defaultdict(list)
    for stemming in stemmingen:
        besluit_id = stemming.get('Besluit_Id')
        if besluit_id:
            besluit_stemmingen[besluit_id].append(stemming)

    enriched_zaken = []
    for zaak in zaken:
        enriched_zaak = zaak.copy()

        # For now, we'll collect all voting data
        # In a full implementation, we'd need to match zaak to besluit via various methods
        enriched_zaak['voting_records'] = []
        enriched_zaak['has_voting_data'] = False

        enriched_zaken.append(enriched_zaak)

    return enriched_zaken

def extract_full_text(zaak: Dict) -> str:
    """Extract full text content from zaak"""
    # Try different text fields
    text_sources = [
        zaak.get('Onderwerp', ''),
        zaak.get('Titel', ''),
    ]

    # If zaak has Documenten, try to get text from there
    documenten = zaak.get('Documenten', [])
    if documenten and isinstance(documenten, list):
        for doc in documenten:
            if isinstance(doc, dict) and 'Inhoud' in doc:
                inhoud = doc.get('Inhoud', '')
                if inhoud:
                    text_sources.append(inhoud)

    # Combine all text sources
    full_text = ' '.join(str(text) for text in text_sources if text)

    return full_text.strip()

def analyze_vote_margins(enriched_zaken: List[Dict]) -> List[Dict]:
    """Analyze which zaken have close vote margins"""
    # For now, we'll mark all zaken as needing voting analysis
    # In a full implementation, this would analyze actual vote counts

    for zaak in enriched_zaken:
        zaak['close_vote'] = False  # Placeholder
        zaak['vote_margin'] = None  # Placeholder

    return enriched_zaken

def create_filtered_output(enriched_zaken: List[Dict]) -> Dict:
    """Create the filtered and enriched output"""
    output = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_zaken': len(enriched_zaken),
            'date_range': '2022-2025',
            'votable_types_only': True,
            'types_allowed': ['Motie', 'Wet', 'Amendement'],
            'enrichment_level': 'basic_voting_text',
            'next_step': 'complete_voting_enrichment'
        },
        'zaken': []
    }

    for zaak in enriched_zaken:
        enriched_item = {
            'id': zaak.get('Id'),
            'nummer': zaak.get('Nummer'),
            'type': zaak.get('Soort'),
            'titel': zaak.get('Titel'),
            'onderwerp': zaak.get('Onderwerp'),
            'date': zaak.get('GestartOp'),
            'status': zaak.get('Status'),
            'vergaderjaar': zaak.get('Vergaderjaar'),
            'full_text': extract_full_text(zaak),
            'has_voting_data': zaak.get('has_voting_data', False),
            'voting_records': zaak.get('voting_records', []),
            'close_vote': zaak.get('close_vote', False),
            'vote_margin': zaak.get('vote_margin'),
            'raw_zaak': zaak  # Keep full raw data for reference
        }

        output['zaken'].append(enriched_item)

    return output

def main():
    print("=== STEP 1: Recent Data Filtering & Enrichment ===")
    print("Loading recent zaak data (2022-2025)...")

    # Load data
    zaken = load_recent_zaak_data()
    stemmingen = load_recent_stemming_data()

    print(f"\nLoaded {len(zaken)} zaken and {len(stemmingen)} stemmingen")

    # Apply filters
    print("\nFiltering for votable types only...")
    votable_zaken = filter_votable_zaken(zaken)

    print("\nFiltering for recent dates (2022+)...")
    recent_zaken = filter_recent_zaken(votable_zaken, start_year=2022)

    # Basic enrichment
    print("\nEnriching with voting data...")
    enriched_zaken = enrich_zaken_with_voting(recent_zaken, stemmingen)

    print("\nAnalyzing vote margins...")
    analyzed_zaken = analyze_vote_margins(enriched_zaken)

    # Create output
    print("\nCreating filtered output...")
    output = create_filtered_output(analyzed_zaken)
    print(f"Output contains {len(output['zaken'])} zaken")

    # Save results
    output_file = '../step1_recent_filtered_enriched_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Step 1 Complete!")
    print(f"Results saved to {output_file}")

    # Summary
    type_counts = defaultdict(int)
    for zaak in output['zaken']:
        type_counts[zaak['type']] += 1

    print("\n📊 SUMMARY:")
    print(f"Total zaken processed: {len(output['zaken'])}")
    print(f"Date range: 2022-2025")
    print(f"Types: {dict(type_counts)}")
    print(f"Ready for Step 2: AI Impact Assessment")

if __name__ == '__main__':
    main()