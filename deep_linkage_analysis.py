#!/usr/bin/env python3
"""
Diepere analyse van de motie-stemming koppeling problemen
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

def analyze_linkage_issues():
    data_dir = Path("bronmateriaal-onbewerkt")
    
    # Laad data
    print("🔍 Loading data for detailed analysis...")
    
    # Zaak data
    zaak_files = list((data_dir / "zaak").glob("*.json"))
    all_zaken = []
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_zaken.extend(data)
    
    # Besluit data  
    besluit_files = list((data_dir / "besluit").glob("*.json"))
    all_besluiten = []
    for file in besluit_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_besluiten.extend(data)
    
    # Stemming data
    stemming_files = list((data_dir / "stemming").glob("*.json"))
    all_stemmingen = []
    for file in stemming_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                all_stemmingen.extend(data)
            else:
                all_stemmingen.append(data)
    
    print(f"📊 Loaded {len(all_zaken)} zaken, {len(all_besluiten)} besluiten, {len(all_stemmingen)} stemmingen")
    
    # Analyseer moties
    moties = [z for z in all_zaken if z.get('Soort') == 'Motie']
    print(f"🎯 Found {len(moties)} moties")
    
    # Analyseer een specifieke motie in detail
    if moties:
        test_motie = moties[0]
        print(f"\n🔬 DETAILED ANALYSIS OF MOTIE:")
        print(f"   ID: {test_motie.get('Id')}")
        print(f"   Nummer: {test_motie.get('Nummer')}")
        print(f"   Titel: {test_motie.get('Titel')}")
        print(f"   Status: {test_motie.get('Status')}")
        print(f"   Datum: {test_motie.get('Datum')}")
        
        # Bekijk alle velden
        print(f"\n   📋 All fields in motie:")
        for key, value in test_motie.items():
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"     {key}: {value}")
    
    # Analyseer besluiten
    print(f"\n🔬 BESLUIT ANALYSIS:")
    
    # Maak zaak_id sets voor vergelijking
    zaak_ids = {z.get('Id') for z in all_zaken if z.get('Id')}
    motie_ids = {z.get('Id') for z in moties if z.get('Id')}
    besluit_zaak_ids = {b.get('Zaak_Id') for b in all_besluiten if b.get('Zaak_Id')}
    
    print(f"   📊 Total unique zaak IDs: {len(zaak_ids)}")
    print(f"   🎯 Total unique motie IDs: {len(motie_ids)}")
    print(f"   🔗 Besluiten referring to zaak IDs: {len(besluit_zaak_ids)}")
    print(f"   🤝 Overlap zaak-besluit: {len(zaak_ids & besluit_zaak_ids)}")
    print(f"   🎯 Motie IDs in besluiten: {len(motie_ids & besluit_zaak_ids)}")
    
    # Bekijk een besluit in detail
    if all_besluiten:
        test_besluit = all_besluiten[0]
        print(f"\n🔬 SAMPLE BESLUIT:")
        print(f"   ID: {test_besluit.get('Id')}")
        print(f"   Zaak_Id: {test_besluit.get('Zaak_Id')}")
        print(f"   Status: {test_besluit.get('Status')}")
        print(f"   Tekst: {test_besluit.get('Tekst', '')[:100]}...")
        
        # Alle velden
        print(f"\n   📋 All fields in besluit:")
        for key, value in test_besluit.items():
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"     {key}: {value}")
    
    # Analyseer stemmingen
    print(f"\n🔬 STEMMING ANALYSIS:")
    
    besluit_ids = {b.get('Id') for b in all_besluiten if b.get('Id')}
    stemming_besluit_ids = {s.get('Besluit_Id') for s in all_stemmingen if s.get('Besluit_Id')}
    
    print(f"   📊 Total unique besluit IDs: {len(besluit_ids)}")
    print(f"   🗳️ Stemmingen referring to besluit IDs: {len(stemming_besluit_ids)}")
    print(f"   🤝 Overlap besluit-stemming: {len(besluit_ids & stemming_besluit_ids)}")
    
    # Bekijk een stemming in detail
    if all_stemmingen:
        test_stemming = all_stemmingen[0]
        print(f"\n🔬 SAMPLE STEMMING:")
        print(f"   ID: {test_stemming.get('Id')}")
        print(f"   Besluit_Id: {test_stemming.get('Besluit_Id')}")
        print(f"   ActorFractie: {test_stemming.get('ActorFractie')}")
        print(f"   Soort: {test_stemming.get('Soort')}")
        
        # Alle velden  
        print(f"\n   📋 All fields in stemming:")
        for key, value in test_stemming.items():
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"     {key}: {value}")
    
    # Probeer complete keten te vinden
    print(f"\n🔗 TRYING TO FIND COMPLETE CHAIN:")
    
    # Zoek moties die wel besluiten hebben
    for motie in moties[:5]:
        motie_id = motie.get('Id')
        related_besluiten = [b for b in all_besluiten if b.get('Zaak_Id') == motie_id]
        
        if related_besluiten:
            print(f"\n✅ FOUND LINKAGE:")
            print(f"   Motie: {motie.get('Nummer')} - {motie.get('Titel')}")
            print(f"   Besluiten: {len(related_besluiten)}")
            
            for besluit in related_besluiten[:2]:
                besluit_id = besluit.get('Id')
                related_stemmingen = [s for s in all_stemmingen if s.get('Besluit_Id') == besluit_id]
                print(f"     Besluit {besluit_id}: {len(related_stemmingen)} stemmingen")
                
                if related_stemmingen:
                    # Show voting details
                    vote_counts = Counter(s.get('Soort') for s in related_stemmingen)
                    party_counts = Counter(s.get('ActorFractie') for s in related_stemmingen)
                    print(f"       Votes: {dict(vote_counts)}")
                    print(f"       Parties: {len(party_counts)} different parties")
                    print(f"       Example votes: {[(s.get('ActorFractie'), s.get('Soort')) for s in related_stemmingen[:3]]}")
                    return True
    
    print(f"\n❌ NO COMPLETE LINKAGE FOUND")
    
    # Check waarom er geen linkage is
    print(f"\n🔍 INVESTIGATING WHY NO LINKAGE:")
    
    # Zijn er uberhaupt besluiten met stemmingen?
    besluiten_with_votes = []
    for besluit in all_besluiten[:20]:
        besluit_id = besluit.get('Id')
        votes = [s for s in all_stemmingen if s.get('Besluit_Id') == besluit_id]
        if votes:
            besluiten_with_votes.append((besluit, len(votes)))
    
    print(f"   🗳️ Besluiten with votes: {len(besluiten_with_votes)}")
    
    if besluiten_with_votes:
        besluit, vote_count = besluiten_with_votes[0]
        zaak_id = besluit.get('Zaak_Id')
        related_zaak = next((z for z in all_zaken if z.get('Id') == zaak_id), None)
        
        print(f"\n✅ FOUND BESLUIT WITH VOTES:")
        print(f"   Besluit ID: {besluit.get('Id')}")
        print(f"   Zaak ID: {zaak_id}")
        print(f"   Vote count: {vote_count}")
        print(f"   Besluit tekst: {besluit.get('Tekst', '')[:100]}...")
        
        if related_zaak:
            print(f"   Related Zaak:")
            print(f"     Soort: {related_zaak.get('Soort')}")
            print(f"     Nummer: {related_zaak.get('Nummer')}")
            print(f"     Titel: {related_zaak.get('Titel')}")
    
    return False

if __name__ == "__main__":
    success = analyze_linkage_issues()
    if not success:
        print(f"\n💡 Next steps:")
        print(f"   1. Check if motions need more time to get voted on")
        print(f"   2. Check if we need different date ranges")
        print(f"   3. Verify the API data structure")