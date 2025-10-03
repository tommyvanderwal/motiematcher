#!/usr/bin/env python3
"""
Fix agendapunt-zaak koppeling onderzoek
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import os

def analyze_agendapunt_linkage():
    data_dir = Path("bronmateriaal-onbewerkt")
    
    print("🔍 Loading data for agendapunt linkage analysis...")
    
    # Laad alle data
    zaak_files = list((data_dir / "zaak").glob("*.json"))
    all_zaken = []
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_zaken.extend(data)
    
    besluit_files = list((data_dir / "besluit").glob("*.json"))
    all_besluiten = []
    for file in besluit_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_besluiten.extend(data)
    
    stemming_files = list((data_dir / "stemming").glob("*.json"))
    all_stemmingen = []
    for file in stemming_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                all_stemmingen.extend(data)
            else:
                all_stemmingen.append(data)
    
    agendapunt_files = list((data_dir / "agendapunt").glob("*.json"))
    all_agendapunten = []
    for file in agendapunt_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_agendapunten.extend(data)
    
    print(f"📊 Loaded {len(all_zaken)} zaken, {len(all_besluiten)} besluiten, {len(all_stemmingen)} stemmingen, {len(all_agendapunten)} agendapunten")
    
    # Analyseer de eerste stemming die we zagen
    first_stemming = all_stemmingen[0]
    besluit_id = first_stemming.get('Besluit_Id')
    
    print(f"\n🔬 ANALYZING LINKAGE via AGENDAPUNT:")
    print(f"   First stemming Besluit_Id: {besluit_id}")
    
    # Vind het bijbehorende besluit
    related_besluit = next((b for b in all_besluiten if b.get('Id') == besluit_id), None)
    
    if related_besluit:
        agendapunt_id = related_besluit.get('Agendapunt_Id')
        print(f"   Related besluit Agendapunt_Id: {agendapunt_id}")
        
        # Vind het agendapunt
        related_agendapunt = next((a for a in all_agendapunten if a.get('Id') == agendapunt_id), None)
        
        if related_agendapunt:
            print(f"   Found agendapunt: {related_agendapunt.get('Id')}")
            print(f"   Agendapunt fields:")
            for key, value in related_agendapunt.items():
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                print(f"     {key}: {value}")
            
            # Zoek naar zaak referenties in agendapunt
            zaak_refs = []
            for key, value in related_agendapunt.items():
                if 'zaak' in key.lower() and value:
                    zaak_refs.append((key, value))
            
            print(f"\n   🔗 Zaak references in agendapunt: {zaak_refs}")
            
            # Zoek ook in embedded objecten
            if isinstance(related_agendapunt.get('Zaak'), list):
                print(f"   📋 Embedded Zaak list found: {len(related_agendapunt['Zaak'])} items")
                for i, zaak in enumerate(related_agendapunt['Zaak'][:3]):
                    if isinstance(zaak, dict):
                        print(f"     Zaak {i+1}: {zaak.get('Id')} - {zaak.get('Titel')}")
                        print(f"       Soort: {zaak.get('Soort')}")
                        print(f"       Nummer: {zaak.get('Nummer')}")
                        
                        # Check of dit een motie is
                        if zaak.get('Soort') == 'Motie':
                            print(f"\n🎯 FOUND MOTIE LINKAGE!")
                            print(f"   Motie ID: {zaak.get('Id')}")
                            print(f"   Motie Nummer: {zaak.get('Nummer')}")
                            print(f"   Motie Titel: {zaak.get('Titel')}")
                            print(f"   Besluit ID: {besluit_id}")
                            print(f"   Stemming count: {len([s for s in all_stemmingen if s.get('Besluit_Id') == besluit_id])}")
                            
                            # Show voting details for this motie
                            related_votes = [s for s in all_stemmingen if s.get('Besluit_Id') == besluit_id]
                            vote_summary = Counter(s.get('Soort') for s in related_votes)
                            party_summary = Counter(s.get('ActorFractie') for s in related_votes)
                            
                            print(f"\n   📊 VOTING RESULTS:")
                            print(f"     Vote counts: {dict(vote_summary)}")
                            print(f"     Parties voted: {len(party_summary)}")
                            print(f"     Party breakdown: {dict(list(party_summary.items())[:5])}")
                            
                            return True
        
        else:
            print(f"   ❌ No agendapunt found with ID {agendapunt_id}")
    else:
        print(f"   ❌ No besluit found with ID {besluit_id}")
    
    # Check alternatieven
    print(f"\n🔍 CHECKING ALTERNATIVE LINKAGES:")
    
    # Check of er AgendapuntZaak entity bestaat in agendapunt
    sample_agendapunt = all_agendapunten[0] if all_agendapunten else None
    if sample_agendapunt:
        print(f"\n📋 Sample agendapunt structure:")
        for key, value in sample_agendapunt.items():
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            elif isinstance(value, list) and value:
                value = f"[{len(value)} items] - first: {str(value[0])[:50]}..."
            print(f"   {key}: {value}")
    
    # Test via activiteit koppeling
    activiteit_path = os.path.join(data_dir, "activiteit")
    if os.path.exists(activiteit_path) and os.listdir(activiteit_path):
        print("\n📋 Sample activiteit structure:")
        activiteit_files = [f for f in os.listdir(activiteit_path) if f.endswith('.json')]
        if activiteit_files:
            with open(os.path.join(activiteit_path, activiteit_files[0]), 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    sample_activiteit = data[0] if data else None
                except json.JSONDecodeError:
                    sample_activiteit = None
        else:
            sample_activiteit = None
        if sample_activiteit:
            for key, value in sample_activiteit.items():
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                print(f"   {key}: {value}")
    
    return False

if __name__ == "__main__":
    success = analyze_agendapunt_linkage()
    if success:
        print(f"\n✅ LINKAGE PATHWAY DISCOVERED!")
        print(f"   Motie -> Agendapunt.Zaak -> Besluit -> Stemming")
    else:
        print(f"\n❌ Need to investigate other linkage mechanisms")