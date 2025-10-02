#!/usr/bin/env python3
"""
Strategie om directe motie links te genereren
"""

import json
import requests
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

def generate_direct_links():
    print("🎯 STRATEGY FOR GENERATING DIRECT MOTIE LINKS")
    print("=" * 60)

    # Laad onze zaak data
    data_dir = Path("bronmateriaal-onbewerkt")
    zaak_files = list((data_dir / "zaak").glob("*.json"))

    moties = []
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            moties.extend([z for z in data if z.get('Soort') == 'Motie'])

    print(f"📊 Found {len(moties)} moties in our data")

    # Test verschillende strategieën om directe links te vinden
    test_moties = moties[:5]  # Test met eerste 5

    working_links = []

    for i, motie in enumerate(test_moties, 1):
        nummer = motie.get('Nummer')
        titel = motie.get('Titel', '')

        print(f"\n🧪 TESTING MOTIE {i}: {nummer}")
        print(f"   Titel: {titel[:60]}...")

        # Strategie 1: Probeer de zoek link en extract de directe link
        search_url = f"https://www.tweedekamer.nl/zoeken?qry={nummer}"

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                content = response.text

                # Zoek naar links naar motie detail pagina's
                # Pattern: /kamerstukken/moties/detail?id=...&did=...
                pattern = r'/kamerstukken/moties/detail\?id=([^&]+)&did=([^"&]+)'
                matches = re.findall(pattern, content)

                if matches:
                    for match in matches:
                        motie_id, doc_id = match
                        if motie_id == nummer:
                            direct_link = f"https://www.tweedekamer.nl/kamerstukken/moties/detail?id={motie_id}&did={doc_id}"
                            print(f"   ✅ FOUND DIRECT LINK: {direct_link}")

                            # Verificeer de link
                            verify_response = requests.get(direct_link, headers=headers, timeout=5)
                            if verify_response.status_code == 200:
                                print(f"      ✅ VERIFIED WORKING!")
                                working_links.append({
                                    'nummer': nummer,
                                    'titel': titel,
                                    'direct_link': direct_link,
                                    'did': doc_id
                                })
                            break
                else:
                    print(f"   ❌ No direct links found in search results")

            else:
                print(f"   ❌ Search failed: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Search error: {e}")

        # Strategie 2: Als geen directe link gevonden, probeer te raden op basis van patterns
        if not any(link['nummer'] == nummer for link in working_links):
            # Vaak is did = D + (Z nummer minus eerste karakter)
            # 2025Z17770 → 2025D17770 zou kunnen zijn
            potential_did = nummer.replace('Z', 'D')

            potential_link = f"https://www.tweedekamer.nl/kamerstukken/moties/detail?id={nummer}&did={potential_did}"

            try:
                response = requests.get(potential_link, headers=headers, timeout=5)
                if response.status_code == 200:
                    content = response.text.lower()
                    if nummer.lower() in content and 'motie' in content:
                        print(f"   🎯 GUESSED CORRECT: {potential_link}")
                        working_links.append({
                            'nummer': nummer,
                            'titel': titel,
                            'direct_link': potential_link,
                            'did': potential_did
                        })
                    else:
                        print(f"   ❌ Guess failed - wrong content")
                else:
                    print(f"   ❌ Guess failed: {response.status_code}")
            except:
                print(f"   ❌ Guess error")

    # Toon resultaten
    print(f"\n" + "="*60)
    print("🎯 DIRECT LINK GENERATION RESULTS:")
    print("="*60)

    if working_links:
        print(f"✅ SUCCESSFULLY GENERATED {len(working_links)} DIRECT LINKS:")

        for link in working_links:
            print(f"\n📋 {link['nummer']}: {link['titel'][:60]}...")
            print(f"   🔗 {link['direct_link']}")
            print(f"   📄 did={link['did']}")

        # Test alle links nog een keer
        print(f"\n🔍 FINAL VERIFICATION:")
        all_working = True

        for link in working_links:
            try:
                response = requests.get(link['direct_link'], headers=headers, timeout=5)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"   {status} {link['nummer']}: {response.status_code}")
                if response.status_code != 200:
                    all_working = False
            except:
                print(f"   ❌ {link['nummer']}: Error")
                all_working = False

        if all_working:
            print(f"\n🎉 ALL LINKS VERIFIED WORKING!")
        else:
            print(f"\n⚠️ Some links may not work")

    else:
        print("❌ No direct links could be generated")

    # Geef strategie advies
    print(f"\n💡 RECOMMENDED STRATEGY:")
    print("1. 🔍 Use search URL as fallback: https://www.tweedekamer.nl/zoeken?qry=[NUMMER]")
    print("2. 🎯 Try direct format when possible: /kamerstukken/moties/detail?id=[Z]&did=[D]")
    print("3. 🔄 Extract did= from search results when available")
    print("4. 📊 Build mapping table for known motie→document relationships")

    return working_links

if __name__ == "__main__":
    generate_direct_links()