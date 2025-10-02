"""
Analyze the real voting data we just fetched
"""

import json

def analyze_voting_data():
    with open('output/real_motions_with_voting_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print('=== ECHTE NEDERLANDSE PARLEMENTAIRE STEMMING DATA ===\n')

    for i, motion in enumerate(data['motions']):
        print(f'MOTIE {i+1}: {motion["title"]}')
        print(f'Type: {motion["decision_type"]}')
        print(f'Datum: {motion["date"][:10]}')
        print(f'Stemming type: {motion["voting_type"]}\n')
        
        # Group by party
        parties = {}
        for vote in motion['voting_records']:
            party = vote['party_abbreviation']
            if party not in parties:
                parties[party] = {'voor': 0, 'tegen': 0, 'onthouding': 0}
            parties[party][vote['vote']] += 1
        
        print('PARTIJ STEMMING OVERZICHT:')
        for party, votes in sorted(parties.items()):
            voor = votes['voor']
            tegen = votes['tegen'] 
            onthouding = votes['onthouding']
            total = voor + tegen + onthouding
            print(f'  {party:15} | Voor: {voor:2d} | Tegen: {tegen:2d} | Onthouding: {onthouding:2d} | Totaal: {total:2d}')
        
        print(f'\nTOTAAL: {motion["vote_summary"]["voor"]} voor, {motion["vote_summary"]["tegen"]} tegen, {motion["vote_summary"]["onthouding"]} onthouding')
        print('=' * 80 + '\n')

if __name__ == "__main__":
    analyze_voting_data()