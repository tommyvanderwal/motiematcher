#!/usr/bin/env python3
"""
Specifieke motie data verkenner
"""

import json
from pathlib import Path

def inspect_motie_structure():
    """Onderzoek de structuur van een motie bestand"""
    zaak_dir = Path("bronmateriaal-onbewerkt/zaak")
    motie_files = list(zaak_dir.glob('moties_page_*.json'))
    
    if not motie_files:
        print("❌ Geen motie bestanden gevonden")
        return
        
    file = motie_files[0]
    print(f"🔍 Onderzoeken: {file.name}")
    
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Top-level keys: {list(data.keys())}")
    
    if 'value' in data:
        print(f"📝 Aantal moties: {len(data['value'])}")
        if len(data['value']) > 0:
            sample = data['value'][0]
            print(f"🏷️ Sample motie keys: {list(sample.keys())}")
            
            # Toon alle properties met voorbeelden
            print(f"\n📋 Alle properties van eerste motie:")
            for key, value in sample.items():
                if isinstance(value, str):
                    display_value = value[:100] + "..." if len(value) > 100 else value
                elif value is None:
                    display_value = "None"
                else:
                    display_value = str(value)
                print(f"  {key:25}: {display_value}")
            
            # Zoek moties met daadwerkelijke content
            print(f"\n🔍 Zoeken naar moties met content:")
            for i, motie in enumerate(data['value'][:10]):
                onderwerp = motie.get('Onderwerp')
                titel_kort = motie.get('TitelKort') 
                titel_lang = motie.get('TitelLang')
                nummer = motie.get('Nummer')
                
                if onderwerp or titel_kort or titel_lang:
                    print(f"  Motie {i+1} (#{nummer}):")
                    if onderwerp:
                        print(f"    Onderwerp: {onderwerp}")
                    if titel_kort:
                        print(f"    TitelKort: {titel_kort}")
                    if titel_lang:
                        print(f"    TitelLang: {titel_lang[:100]}...")

def inspect_voting_structure():
    """Onderzoek stemming data structuur"""
    stemming_dir = Path("bronmateriaal-onbewerkt/stemming")
    voting_files = list(stemming_dir.glob('votes_page_*.json'))
    
    if not voting_files:
        print("❌ Geen stemming bestanden gevonden")
        return
        
    file = voting_files[0]
    print(f"\n🗳️ Onderzoeken stemming: {file.name}")
    
    with open(file, 'r', encoding='utf-8') as f:
        votes = json.load(f)
    
    print(f"📊 Aantal stemmingen: {len(votes)}")
    
    if len(votes) > 0:
        sample = votes[0]
        print(f"🏷️ Sample stemming keys: {list(sample.keys())}")
        
        print(f"\n📋 Sample stemming properties:")
        for key, value in sample.items():
            if isinstance(value, str):
                display_value = value[:100] + "..." if len(value) > 100 else value
            elif value is None:
                display_value = "None"  
            else:
                display_value = str(value)
            print(f"  {key:25}: {display_value}")
        
        # Analyse partijen en stemmingen
        print(f"\n🏛️ Partijen analyse:")
        parties = {}
        for vote in votes[:50]:  # Eerste 50 voor snelheid
            party = vote.get('FractieNaam')
            vote_type = vote.get('Soort')
            
            if party:
                if party not in parties:
                    parties[party] = []
                parties[party].append(vote_type)
        
        for party, vote_types in parties.items():
            voor = vote_types.count('Voor')
            tegen = vote_types.count('Tegen') 
            onthouding = len(vote_types) - voor - tegen
            print(f"  {party:25}: Voor={voor:2d}, Tegen={tegen:2d}, Anders={onthouding:2d}")

if __name__ == "__main__":
    print("🔍 Gedetailleerde data structuur analyse")
    inspect_motie_structure()
    inspect_voting_structure()
    print("\n✅ Analyse voltooid!")