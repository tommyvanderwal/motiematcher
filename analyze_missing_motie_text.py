#!/usr/bin/env python3
"""
Onderzoek waarom 1.5% van moties geen tekstinhoud heeft
"""

import json
from pathlib import Path
from collections import Counter

def analyze_missing_motie_text():
    data_dir = Path("bronmateriaal-onbewerkt")
    
    print("🔍 ANALYZING MISSING MOTIE TEXT")
    print("=" * 50)
    
    # Laad zaak data
    zaak_files = list((data_dir / "zaak").glob("*.json"))
    all_zaken = []
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_zaken.extend(data)
    
    # Filter moties
    moties = [z for z in all_zaken if z.get('Soort') == 'Motie']
    print(f"📊 Total moties: {len(moties)}")
    
    # Analyseer tekstinhoud
    moties_with_onderwerp = []
    moties_without_onderwerp = []
    
    for motie in moties:
        onderwerp = motie.get('Onderwerp', '')
        if onderwerp and len(onderwerp.strip()) > 50:  # Meer dan 50 chars = substantieel
            moties_with_onderwerp.append(motie)
        else:
            moties_without_onderwerp.append(motie)
    
    print(f"✅ Moties with substantial text: {len(moties_with_onderwerp)}")
    print(f"❌ Moties without substantial text: {len(moties_without_onderwerp)}")
    print(f"📈 Coverage: {len(moties_with_onderwerp)/len(moties)*100:.1f}%")
    
    print(f"\n🔬 ANALYZING MOTIES WITHOUT TEXT:")
    print("=" * 40)
    
    # Analyseer de moties zonder tekst in detail
    for i, motie in enumerate(moties_without_onderwerp[:10]):  # Eerste 10
        print(f"\n📋 Motie {i+1}:")
        print(f"   ID: {motie.get('Id')}")
        print(f"   Nummer: {motie.get('Nummer')}")
        print(f"   Titel: {motie.get('Titel')}")
        print(f"   Status: {motie.get('Status')}")
        print(f"   Afgedaan: {motie.get('Afgedaan')}")
        print(f"   GewijzigdOp: {motie.get('GewijzigdOp')}")
        print(f"   Onderwerp: '{motie.get('Onderwerp', '')}'")
        print(f"   Onderwerp length: {len(motie.get('Onderwerp', ''))}")
        
        # Check embedded documents
        docs = motie.get('Document', [])
        print(f"   Embedded documents: {len(docs)}")
        if docs:
            for j, doc in enumerate(docs[:2]):
                print(f"     Doc {j+1}: {doc.get('Soort')} - {doc.get('Titel', '')[:50]}...")
        
        # Check alle velden voor hints
        interesting_fields = []
        for key, value in motie.items():
            if key not in ['Id', 'Nummer', 'Titel', 'Status', 'Afgedaan', 'GewijzigdOp', 'Onderwerp', 'Document']:
                if value and str(value) != 'None' and str(value) != '[]':
                    interesting_fields.append((key, str(value)[:100]))
        
        if interesting_fields:
            print(f"   Other fields: {interesting_fields[:3]}")
    
    # Analyseer patronen in ontbrekende tekst
    print(f"\n📊 PATTERN ANALYSIS:")
    print("=" * 30)
    
    # Status analyse
    status_counts = Counter(m.get('Status') for m in moties_without_onderwerp)
    print(f"Status breakdown of moties without text:")
    for status, count in status_counts.items():
        print(f"   {status}: {count}")
    
    # Afgedaan analyse  
    afgedaan_counts = Counter(m.get('Afgedaan') for m in moties_without_onderwerp)
    print(f"\nAfgedaan breakdown:")
    for afgedaan, count in afgedaan_counts.items():
        print(f"   {afgedaan}: {count}")
    
    # Datum analyse
    recent_without_text = []
    older_without_text = []
    
    for motie in moties_without_onderwerp:
        gewijzigd_op = motie.get('GewijzigdOp', '')
        if '2025-10' in gewijzigd_op:
            recent_without_text.append(motie)
        else:
            older_without_text.append(motie)
    
    print(f"\nTiming analysis:")
    print(f"   Recent (Oct 2025): {len(recent_without_text)}")
    print(f"   Older: {len(older_without_text)}")
    
    # Check document coverage als compensatie
    print(f"\n📄 DOCUMENT COMPENSATION ANALYSIS:")
    print("=" * 40)
    
    moties_without_text_with_docs = [m for m in moties_without_onderwerp if m.get('Document')]
    moties_without_text_no_docs = [m for m in moties_without_onderwerp if not m.get('Document')]
    
    print(f"Moties without onderwerp text but WITH documents: {len(moties_without_text_with_docs)}")
    print(f"Moties without onderwerp text AND without documents: {len(moties_without_text_no_docs)}")
    
    if moties_without_text_with_docs:
        print(f"\n📝 Example motie with compensating document:")
        example = moties_without_text_with_docs[0]
        print(f"   Nummer: {example.get('Nummer')}")
        print(f"   Titel: {example.get('Titel')}")
        doc = example['Document'][0]
        print(f"   Document: {doc.get('Soort')} - {doc.get('Onderwerp', '')[:100]}...")
    
    # Final assessment
    effectively_covered = len(moties_with_onderwerp) + len(moties_without_text_with_docs)
    coverage_with_docs = effectively_covered / len(moties) * 100
    
    print(f"\n🎯 FINAL ASSESSMENT:")
    print(f"=" * 30)
    print(f"Moties with onderwerp text: {len(moties_with_onderwerp)}")
    print(f"Moties without onderwerp but with documents: {len(moties_without_text_with_docs)}")
    print(f"Truly missing text: {len(moties_without_text_no_docs)}")
    print(f"Effective coverage: {coverage_with_docs:.1f}%")
    print(f"Truly problematic: {len(moties_without_text_no_docs)/len(moties)*100:.1f}%")
    
    # Determine if this is concerning
    if len(moties_without_text_no_docs) < len(moties) * 0.01:  # Less than 1%
        print(f"\n✅ CONCLUSION: Not concerning!")
        print(f"   Most missing text has document compensation")
        print(f"   Truly missing: <1% - likely processing artifacts")
    else:
        print(f"\n⚠️ CONCLUSION: Needs investigation")
        print(f"   Significant missing text without compensation")

if __name__ == "__main__":
    analyze_missing_motie_text()