#!/usr/bin/env python3
"""
Definitieve diagnose van het linkage probleem
"""

import json
from pathlib import Path
from collections import Counter

def diagnose_linkage_problem():
    data_dir = Path("bronmateriaal-onbewerkt")
    
    print("🔍 DEFINITIEVE LINKAGE DIAGNOSE")
    print("=" * 50)
    
    # Laad besluit data
    besluit_files = list((data_dir / "besluit").glob("*.json"))
    all_besluiten = []
    for file in besluit_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_besluiten.extend(data)
    
    # Laad stemming data  
    stemming_files = list((data_dir / "stemming").glob("*.json"))
    all_stemmingen = []
    for file in stemming_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                all_stemmingen.extend(data)
            else:
                all_stemmingen.append(data)
    
    print(f"📊 Loaded {len(all_besluiten)} besluiten, {len(all_stemmingen)} stemmingen")
    
    # Analyseer besluit_id coverage in stemmingen
    stemming_besluit_ids = [s.get('Besluit_Id') for s in all_stemmingen]
    none_count = stemming_besluit_ids.count(None)
    valid_count = len([x for x in stemming_besluit_ids if x is not None])
    unique_valid = len(set([x for x in stemming_besluit_ids if x is not None]))
    
    print(f"\n📊 STEMMING BESLUIT_ID ANALYSIS:")
    print(f"   Total stemmingen: {len(all_stemmingen)}")
    print(f"   With Besluit_Id=None: {none_count}")
    print(f"   With valid Besluit_Id: {valid_count}")
    print(f"   Unique valid Besluit_Ids: {unique_valid}")
    
    # Analyseer besluit IDs
    besluit_ids = [b.get('Id') for b in all_besluiten]
    valid_besluit_ids = len([x for x in besluit_ids if x is not None])
    
    print(f"\n📊 BESLUIT ID ANALYSIS:")
    print(f"   Total besluiten: {len(all_besluiten)}")
    print(f"   Valid besluit IDs: {valid_besluit_ids}")
    
    # Find overlap
    valid_stemming_besluit_ids = set([x for x in stemming_besluit_ids if x is not None])
    besluit_id_set = set([x for x in besluit_ids if x is not None])
    overlap = valid_stemming_besluit_ids & besluit_id_set
    
    print(f"   Overlap between stemming.Besluit_Id and besluit.Id: {len(overlap)}")
    
    if overlap:
        # Test een werkende koppeling
        sample_besluit_id = list(overlap)[0]
        related_stemmingen = [s for s in all_stemmingen if s.get('Besluit_Id') == sample_besluit_id]
        related_besluit = next(b for b in all_besluiten if b.get('Id') == sample_besluit_id)
        
        print(f"\n✅ FOUND WORKING LINKAGE!")
        print(f"   Sample besluit_id: {sample_besluit_id}")
        print(f"   Stemmingen count: {len(related_stemmingen)}")
        print(f"   Besluit agendapunt_id: {related_besluit.get('Agendapunt_Id')}")
        print(f"   Besluit tekst: {related_besluit.get('BesluitTekst', '')}")
        
        # Nu kijken naar Agendapunt connection
        agendapunt_files = list((data_dir / "agendapunt").glob("*.json"))
        all_agendapunten = []
        for file in agendapunt_files:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_agendapunten.extend(data)
        
        agendapunt_id = related_besluit.get('Agendapunt_Id')
        related_agendapunt = next((a for a in all_agendapunten if a.get('Id') == agendapunt_id), None)
        
        if related_agendapunt:
            print(f"\n📋 FOUND RELATED AGENDAPUNT:")
            print(f"   Agendapunt ID: {agendapunt_id}")
            print(f"   Onderwerp: {related_agendapunt.get('Onderwerp', '')[:100]}...")
            
            # Check for Zaak references
            if 'Zaak' in related_agendapunt and related_agendapunt['Zaak']:
                print(f"   📝 Zaak references found: {len(related_agendapunt['Zaak'])}")
                
                for zaak in related_agendapunt['Zaak'][:3]:
                    if isinstance(zaak, dict):
                        zaak_soort = zaak.get('Soort')
                        zaak_titel = zaak.get('Titel', '')
                        zaak_nummer = zaak.get('Nummer', '')
                        
                        print(f"     Zaak: {zaak_soort} - {zaak_nummer}")
                        print(f"       Titel: {zaak_titel[:80]}...")
                        
                        if zaak_soort == 'Motie':
                            print(f"\n🎯 COMPLETE LINKAGE FOUND!")
                            print(f"   Motie -> Agendapunt -> Besluit -> Stemming")
                            print(f"   Motie ID: {zaak.get('Id')}")
                            print(f"   Agendapunt ID: {agendapunt_id}")
                            print(f"   Besluit ID: {sample_besluit_id}")
                            print(f"   Stemmingen: {len(related_stemmingen)}")
                            
                            # Toon stemmingsresultaten
                            vote_counts = Counter(s.get('Soort') for s in related_stemmingen)
                            party_counts = Counter(s.get('ActorFractie') for s in related_stemmingen)
                            
                            print(f"\n   📊 VOTING RESULTS:")
                            print(f"     Votes: {dict(vote_counts)}")
                            print(f"     Parties: {len(party_counts)} different parties")
                            
                            # Toon enkele voorbeelden
                            for party, count in list(party_counts.items())[:5]:
                                party_votes = [s for s in related_stemmingen if s.get('ActorFractie') == party]
                                vote_type = party_votes[0].get('Soort') if party_votes else 'Unknown'
                                print(f"       {party}: {vote_type} ({count} leden)")
                            
                            return True
            else:
                print(f"   ❌ No Zaak references in agendapunt")
        else:
            print(f"   ❌ No agendapunt found with ID {agendapunt_id}")
    
    else:
        print(f"\n❌ NO OVERLAP between stemming and besluit IDs")
        print(f"   This suggests data collection timing issues")
    
    return False

if __name__ == "__main__":
    success = diagnose_linkage_problem()
    if success:
        print(f"\n🎉 DATA LINKAGE IS WORKING!")
        print(f"🚀 Ready to build proper motie-stemming matching!")
    else:
        print(f"\n⚠️ Data linkage issues need investigation")
        print(f"💡 May need different date ranges or collection strategy")