#!/usr/bin/env python3
"""
Onderzoek waar het did= ID vandaan komt voor directe motie links
"""

import json
import requests
from pathlib import Path
from collections import defaultdict

def investigate_did_source():
    data_dir = Path("bronmateriaal-onbewerkt")

    print("🔍 INVESTIGATING did= ID SOURCE FOR DIRECT MOTIE LINKS")
    print("=" * 60)

    # Laad alle data
    zaak_data = []
    document_data = []
    besluit_data = []

    # Laad zaak data
    zaak_files = list((data_dir / "zaak").glob("*.json"))
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            zaak_data.extend(data)

    # Laad document data
    doc_files = list((data_dir / "document").glob("*.json"))
    for file in doc_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            document_data.extend(data)

    # Laad besluit data
    besluit_files = list((data_dir / "besluit").glob("*.json"))
    for file in besluit_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            besluit_data.extend(data)

    print(f"📊 Loaded {len(zaak_data)} zaken, {len(document_data)} documents, {len(besluit_data)} besluiten")

    # Zoek naar de specifieke motie
    target_motie = "2025Z17770"
    motie_zaak = None

    for zaak in zaak_data:
        if zaak.get('Nummer') == target_motie:
            motie_zaak = zaak
            break

    if not motie_zaak:
        print(f"❌ Could not find motie {target_motie}")
        return

    print(f"\n🧪 ANALYZING MOTIE {target_motie}:")
    print(f"   Zaak ID: {motie_zaak.get('Id')}")
    print(f"   Titel: {motie_zaak.get('Titel', '')[:80]}...")

    # Zoek gerelateerde documenten
    zaak_id = motie_zaak.get('Id')
    related_docs = []

    for doc in document_data:
        # Check verschillende relatie velden
        if doc.get('Zaak_Id') == zaak_id:
            related_docs.append(doc)
        elif doc.get('ZaakId') == zaak_id:
            related_docs.append(doc)
        elif str(doc.get('Zaak_Id', '')).lower() == str(zaak_id).lower():
            related_docs.append(doc)

    print(f"\n📄 FOUND {len(related_docs)} RELATED DOCUMENTS:")

    for i, doc in enumerate(related_docs, 1):
        doc_id = doc.get('Id')
        doc_nummer = doc.get('Nummer')
        doc_soort = doc.get('Soort')
        doc_onderwerp = doc.get('Onderwerp', '')[:100]

        print(f"\n   Document {i}:")
        print(f"      ID: {doc_id}")
        print(f"      Nummer: {doc_nummer}")
        print(f"      Soort: {doc_soort}")
        print(f"      Onderwerp: {doc_onderwerp}...")

        # Check of dit het did= ID zou kunnen zijn
        if doc_nummer and doc_nummer.startswith('2025D'):
            print(f"      🎯 POTENTIAL did= ID: {doc_nummer}")
            print(f"      🔗 DIRECT LINK: https://www.tweedekamer.nl/kamerstukken/moties/detail?id={target_motie}&did={doc_nummer}")

    # Check ook besluiten voor extra context
    related_besluiten = [b for b in besluit_data if b.get('Zaak_Id') == zaak_id]

    if related_besluiten:
        print(f"\n🏛️ RELATED BESLUITEN ({len(related_besluiten)}):")
        for besluit in related_besluiten:
            print(f"   Besluit ID: {besluit.get('Id')}")
            print(f"   Status: {besluit.get('Status')}")

    # Analyseer document structuur voor pattern discovery
    print(f"\n🔍 DOCUMENT PATTERN ANALYSIS:")
    doc_soorten = defaultdict(int)
    doc_nummer_patterns = defaultdict(int)

    for doc in document_data[:100]:  # Sample voor analyse
        soort = doc.get('Soort')
        nummer = doc.get('Nummer', '')

        if soort:
            doc_soorten[soort] += 1

        if nummer:
            if nummer.startswith('2025D'):
                doc_nummer_patterns['2025D'] += 1
            elif nummer.startswith('2025Z'):
                doc_nummer_patterns['2025Z'] += 1
            else:
                doc_nummer_patterns['other'] += 1

    print(f"   Document soorten: {dict(doc_soorten)}")
    print(f"   Nummer patterns: {dict(doc_nummer_patterns)}")

    # Test de gevonden directe link
    if related_docs:
        potential_did = None
        for doc in related_docs:
            if doc.get('Nummer', '').startswith('2025D'):
                potential_did = doc.get('Nummer')
                break

        if potential_did:
            direct_link = f"https://www.tweedekamer.nl/kamerstukken/moties/detail?id={target_motie}&did={potential_did}"
            print(f"\n🎯 TESTING DIRECT LINK:")
            print(f"   🔗 {direct_link}")

            # Test de link
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(direct_link, timeout=10, headers=headers)

                if response.status_code == 200:
                    content = response.text.lower()
                    if target_motie.lower() in content and 'motie' in content:
                        print(f"   ✅ DIRECT LINK WORKS! Status: {response.status_code}")
                        print(f"   📄 Contains motie content: {len(response.text):,} chars")
                        return direct_link
                    else:
                        print(f"   ⚠️ Link works but may not contain expected content")
                else:
                    print(f"   ❌ Link failed: Status {response.status_code}")

            except Exception as e:
                print(f"   ❌ Link test failed: {e}")

    print(f"\n💡 CONCLUSION:")
    print(f"   - did= ID comes from Document entities with Nummer starting with '2025D'")
    print(f"   - Documents are linked to Zaak via Zaak_Id field")
    print(f"   - Direct link format: /kamerstukken/moties/detail?id=[ZAK_NUMMER]&did=[DOC_NUMMER]")

if __name__ == "__main__":
    investigate_did_source()