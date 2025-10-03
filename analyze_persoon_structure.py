#!/usr/bin/env python3
"""
Analyze parliament member data structure to understand collection issues
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import Counter

def find_persoon_files():
    """Find all persoon data files"""
    search_paths = [
        Path("bronmateriaal-onbewerkt/persoon"),
        Path("output/persoon"),
        Path("data/persoon"),
        Path("C:/motiematcher/bronmateriaal-onbewerkt/persoon"),
        Path(".")
    ]

    persoon_files = []
    for search_path in search_paths:
        if search_path.exists():
            for file in search_path.glob("*persoon*.json"):
                persoon_files.append(file)

    return persoon_files

def analyze_persoon_data(file_path):
    """Analyze a single persoon data file"""
    print(f"\n[*] Analyzing: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, dict) and 'value' in data:
            persons = data['value']
        elif isinstance(data, list):
            persons = data
        else:
            print("[-] Unexpected data structure")
            return

        print(f"[+] Found {len(persons)} persons")

        # Analyze status distribution
        statuses = []
        active_count = 0
        function_info = []

        for person in persons[:10]:  # Analyze first 10 for structure
            print(f"\n[*] Person: {person.get('Id', 'Unknown')}")
            print(f"   Naam: {person.get('Naam', 'Unknown')}")

            # Look for function information
            if 'Functies' in person:
                functies = person['Functies']
                print(f"   Functies: {len(functies)} functions")
                for functie in functies:
                    functie_type = functie.get('FunctieSoort', {}).get('Naam', 'Unknown')
                    functie_status = functie.get('Status', 'Unknown')
                    functie_start = functie.get('Begindatum', 'Unknown')
                    functie_end = functie.get('Einddatum')

                    print(f"     - {functie_type}: {functie_status} ({functie_start} - {functie_end})")

                    # Check if this is an active parliament member
                    if functie_type in ['Tweede Kamerlid', 'Lid Tweede Kamer'] and functie_end is None:
                        active_count += 1

                    function_info.append({
                        'type': functie_type,
                        'status': functie_status,
                        'start': functie_start,
                        'end': functie_end
                    })

            statuses.append(person.get('Status', 'Unknown'))

        # Overall statistics
        status_counts = Counter(statuses)
        print(f"\n[+] Status Distribution: {dict(status_counts)}")
        print(f"[+] Active Parliament Members Found: {active_count}")

        # Function type analysis
        functie_types = Counter([f['type'] for f in function_info])
        print(f"[+] Function Types: {dict(functie_types)}")

        functie_statuses = Counter([f['status'] for f in function_info])
        print(f"[+] Function Statuses: {dict(functie_statuses)}")

        return {
            'total_persons': len(persons),
            'status_distribution': dict(status_counts),
            'active_members': active_count,
            'function_types': dict(functie_types),
            'function_statuses': dict(functie_statuses)
        }

    except Exception as e:
        print(f"[-] Error analyzing {file_path}: {e}")
        return None

def main():
    print("[*] PERSON DATA STRUCTURE ANALYSIS")
    print("=" * 50)

    persoon_files = find_persoon_files()

    if not persoon_files:
        print("[-] No persoon data files found!")
        print("Searching in:")
        for path in [Path("bronmateriaal-onbewerkt/persoon"), Path("output/persoon"), Path("data/persoon")]:
            print(f"  - {path}")
        return

    print(f"[+] Found {len(persoon_files)} persoon files:")
    for file in persoon_files:
        print(f"  - {file}")

    # Analyze each file
    results = []
    for file_path in persoon_files:
        result = analyze_persoon_data(file_path)
        if result:
            results.append(result)

    # Summary
    if results:
        print(f"\n[+] ANALYSIS COMPLETE")
        print(f"Files analyzed: {len(results)}")

        total_persons = sum(r['total_persons'] for r in results)
        total_active = sum(r['active_members'] for r in results)

        print(f"Total persons: {total_persons}")
        print(f"Total active parliament members: {total_active}")

        if total_active < 150:
            print(f"[!] WARNING: Only {total_active} active members found, expected ~150")
            print("This suggests the collection logic needs to be fixed")

if __name__ == "__main__":
    main()