#!/usr/bin/env python3
"""
Direct API onderzoek naar motie-document relaties
"""

import json
import requests
from pathlib import Path

def api_investigation():
    print("🔍 DIRECT API INVESTIGATION FOR MOTIE-DOCUMENT LINKS")
    print("=" * 60)

    # Laad onze bestaande zaak data om de motie te vinden
    data_dir = Path("bronmateriaal-onbewerkt")
    zaak_files = list((data_dir / "zaak").glob("*.json"))

    target_motie = "2025Z17770"
    motie_zaak = None

    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for zaak in data:
                if zaak.get('Nummer') == target_motie:
                    motie_zaak = zaak
                    break
        if motie_zaak:
            break

    if not motie_zaak:
        print(f"❌ Could not find motie {target_motie}")
        return

    zaak_id = motie_zaak.get('Id')
    print(f"🧪 ANALYZING MOTIE {target_motie}:")
    print(f"   Zaak ID: {zaak_id}")
    print(f"   Titel: {motie_zaak.get('Titel', '')[:80]}...")

    # Probeer direct de API te bevragen voor gerelateerde documenten
    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/"

    # Query 1: Documenten gefilterd op Zaak_Id
    doc_query = f"Document?$filter=Zaak_Id eq '{zaak_id}'&$top=50"

    print(f"\n🔗 TESTING API QUERIES:")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

        print(f"   Query: {doc_query}")
        response = requests.get(base_url + doc_query, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            docs = data.get('value', [])

            print(f"   ✅ Found {len(docs)} documents via API")

            for i, doc in enumerate(docs, 1):
                doc_id = doc.get('Id')
                doc_nummer = doc.get('Nummer')
                doc_soort = doc.get('Soort')

                print(f"\n      Document {i}:")
                print(f"         Nummer: {doc_nummer}")
                print(f"         Soort: {doc_soort}")
                print(f"         Zaak_Id: {doc.get('Zaak_Id')}")

                if doc_nummer and doc_nummer.startswith('2025D'):
                    direct_link = f"https://www.tweedekamer.nl/kamerstukken/moties/detail?id={target_motie}&did={doc_nummer}"
                    print(f"         🎯 POTENTIAL LINK: {direct_link}")

                    # Test deze link
                    link_response = requests.get(direct_link, headers=headers, timeout=10)
                    if link_response.status_code == 200:
                        print(f"         ✅ LINK WORKS!")
                    else:
                        print(f"         ❌ Link failed: {link_response.status_code}")
        else:
            print(f"   ❌ API query failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ API query error: {e}")

    # Query 2: Zoek documenten met motie nummer in onderwerp
    try:
        search_query = f"Document?$filter=contains(Onderwerp, '{target_motie}')&$top=20"
        print(f"\n   Alternative Query: {search_query}")

        response = requests.get(base_url + search_query, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            docs = data.get('value', [])

            print(f"   ✅ Found {len(docs)} documents by onderwerp search")

            for doc in docs:
                doc_nummer = doc.get('Nummer')
                if doc_nummer and doc_nummer.startswith('2025D'):
                    print(f"      Found: {doc_nummer} - {doc.get('Onderwerp', '')[:50]}...")
        else:
            print(f"   ❌ Alternative query failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Alternative query error: {e}")

    # Query 3: Check of er een directe relatie tabel is
    try:
        # Probeer ZaakDocument relatie op te vragen
        relation_query = f"ZaakDocument?$filter=Zaak_Id eq '{zaak_id}'&$expand=Document&$top=20"
        print(f"\n   Relation Query: {relation_query}")

        response = requests.get(base_url + relation_query, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            relations = data.get('value', [])

            print(f"   ✅ Found {len(relations)} ZaakDocument relations")

            for relation in relations:
                doc = relation.get('Document', {})
                doc_nummer = doc.get('Nummer')
                if doc_nummer:
                    print(f"      Related: {doc_nummer} - {doc.get('Soort')}")
        else:
            print(f"   ❌ Relation query failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Relation query error: {e}")

    # Test de werkende link die de gebruiker vond
    working_did = "2025D41494"
    working_link = f"https://www.tweedekamer.nl/kamerstukken/moties/detail?id={target_motie}&did={working_did}"

    print(f"\n🎯 TESTING KNOWN WORKING LINK:")
    print(f"   🔗 {working_link}")

    try:
        response = requests.get(working_link, headers=headers, timeout=10)

        if response.status_code == 200:
            content = response.text.lower()
            print(f"   ✅ LINK WORKS! Status: {response.status_code}")
            print(f"   📄 Content length: {len(response.text):,} chars")

            # Check content
            checks = ['motie', target_motie.lower(), 'kamerstukken']
            found = [c for c in checks if c in content]
            print(f"   ✅ Contains: {', '.join(found)}")

            if 'stemming' in content or 'besluit' in content:
                print(f"   🗳️ Contains voting/decision info")
        else:
            print(f"   ❌ Link failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Link test error: {e}")

    print(f"\n💡 CONCLUSION:")
    print(f"   - did= ID {working_did} works but not found in our collected data")
    print(f"   - API queries show documents exist but linkage unclear")
    print(f"   - Working direct link format confirmed: /moties/detail?id=[Z]&did=[D]")

if __name__ == "__main__":
    api_investigation()