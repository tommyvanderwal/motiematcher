#!/usr/bin/env python3
"""
Breder onderzoek naar did= ID bronnen en relatie patronen
"""

import json
import requests
from pathlib import Path
from collections import defaultdict

def investigate_did_patterns():
    data_dir = Path("bronmateriaal-onbewerkt")

    print("🔍 BROADER INVESTIGATION OF did= ID PATTERNS")
    print("=" * 60)

    # Laad alle data
    zaak_data = []
    document_data = []

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

    print(f"📊 Loaded {len(zaak_data)} zaken, {len(document_data)} documents")

    # Zoek naar de specifieke did= ID die de gebruiker vond
    target_did = "2025D41494"
    target_motie = "2025Z17770"

    print(f"\n🎯 SEARCHING FOR did={target_did}:")

    found_doc = None
    for doc in document_data:
        if doc.get('Nummer') == target_did:
            found_doc = doc
            break

    if found_doc:
        print(f"   ✅ FOUND DOCUMENT {target_did}:")
        print(f"      Soort: {found_doc.get('Soort')}")
        print(f"      Onderwerp: {found_doc.get('Onderwerp', '')[:100]}...")
        print(f"      Zaak_Id: {found_doc.get('Zaak_Id')}")
        print(f"      ZaakId: {found_doc.get('ZaakId')}")

        # Check of dit document gerelateerd is aan onze motie
        zaak_id = found_doc.get('Zaak_Id') or found_doc.get('ZaakId')
        if zaak_id:
            related_zaak = None
            for zaak in zaak_data:
                if zaak.get('Id') == zaak_id:
                    related_zaak = zaak
                    break

            if related_zaak:
                print(f"   🔗 LINKED TO ZAAK: {related_zaak.get('Nummer')} ({related_zaak.get('Soort')})")
                print(f"      Titel: {related_zaak.get('Titel', '')[:80]}...")

                if related_zaak.get('Nummer') == target_motie:
                    print(f"   ✅ PERFECT MATCH! Document {target_did} belongs to motie {target_motie}")
                else:
                    print(f"   ⚠️ Document belongs to different zaak: {related_zaak.get('Nummer')}")
            else:
                print(f"   ❌ Could not find linked zaak with ID {zaak_id}")
    else:
        print(f"   ❌ Document {target_did} not found in our data")

    # Analyseer relatie patronen tussen zaken en documenten
    print(f"\n🔗 ANALYZING ZAAK-DOCUMENT RELATIONSHIPS:")

    zaak_doc_links = defaultdict(list)
    doc_zaak_links = defaultdict(list)

    sample_size = min(500, len(document_data))  # Sample voor analyse

    for doc in document_data[:sample_size]:
        zaak_id = doc.get('Zaak_Id') or doc.get('ZaakId')
        doc_nummer = doc.get('Nummer')

        if zaak_id and doc_nummer:
            if doc_nummer.startswith('2025D'):
                zaak_doc_links[zaak_id].append(doc_nummer)
                doc_zaak_links[doc_nummer].append(zaak_id)

    print(f"   Sampled {sample_size} documents")
    print(f"   Found {len(zaak_doc_links)} zaken with document links")
    print(f"   Found {len(doc_zaak_links)} documents with zaak links")

    # Toon voorbeelden van motie-document relaties
    motie_docs = []
    for zaak_id, doc_nums in zaak_doc_links.items():
        # Vind de zaak
        zaak = next((z for z in zaak_data if z.get('Id') == zaak_id), None)
        if zaak and zaak.get('Soort') == 'Motie':
            motie_docs.append((zaak.get('Nummer'), doc_nums))

    print(f"\n📋 MOTIE-DOCUMENT RELATION EXAMPLES:")
    for motie_num, docs in motie_docs[:5]:
        print(f"   Motie {motie_num} → Documents: {docs}")

    # Test de directe link die de gebruiker vond
    direct_link = f"https://www.tweedekamer.nl/kamerstukken/moties/detail?id={target_motie}&did={target_did}"

    print(f"\n🧪 TESTING USER'S DIRECT LINK:")
    print(f"   🔗 {direct_link}")

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

                # Check for voting information
                if 'stemming' in content or 'vote' in content or 'voor' in content:
                    print(f"   🗳️ Contains voting information")
                else:
                    print(f"   ℹ️ May not contain voting info yet")

                return direct_link
            else:
                print(f"   ⚠️ Link works but content check failed")
        else:
            print(f"   ❌ Link failed: Status {response.status_code}")

    except Exception as e:
        print(f"   ❌ Link test failed: {e}")

    # Zoek alternatieve manieren om did= ID te vinden
    print(f"\n🔍 ALTERNATIVE APPROACHES:")

    # Check of er andere relatie velden zijn
    relation_fields = set()
    for doc in document_data[:100]:
        for key in doc.keys():
            if 'zaak' in key.lower() or 'rel' in key.lower() or 'link' in key.lower():
                relation_fields.add(key)

    print(f"   Potential relation fields in documents: {sorted(relation_fields)}")

    # Check zaak velden die naar documenten kunnen verwijzen
    zaak_relation_fields = set()
    for zaak in zaak_data[:100]:
        for key in zaak.keys():
            if 'doc' in key.lower() or 'rel' in key.lower() or 'link' in key.lower():
                zaak_relation_fields.add(key)

    print(f"   Potential relation fields in zaken: {sorted(zaak_relation_fields)}")

    return direct_link if 'direct_link' in locals() and direct_link else None

if __name__ == "__main__":
    investigate_did_patterns()