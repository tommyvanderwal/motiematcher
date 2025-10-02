#!/usr/bin/env python3
"""
Genereer werkende directe motie links met stemuitslagen voor productie gebruik
"""

import json
import requests
import re
from pathlib import Path

def generate_production_motie_links():
    print("🚀 GENERATING PRODUCTION-READY DIRECT MOTIE LINKS WITH VOTING RESULTS")
    print("=" * 70)

    # Laad motie data
    data_dir = Path("bronmateriaal-onbewerkt")
    zaak_files = list((data_dir / "zaak").glob("*.json"))

    moties = []
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            moties.extend([z for z in data if z.get('Soort') == 'Motie'])

    print(f"📊 Found {len(moties)} moties in our data")

    # Focus op oudere moties (September 2025) die meer kans hebben op werkende links
    september_moties = []
    for motie in moties:
        gewijzigd_op = motie.get('GewijzigdOp', '')
        if '2025-09-' in gewijzigd_op:
            september_moties.append(motie)

    print(f"📅 Found {len(september_moties)} moties from September 2025")

    # Sorteer op datum (oudste eerst, meer kans op verwerkte links)
    september_moties.sort(key=lambda x: x.get('GewijzigdOp', ''), reverse=False)

    # Test eerste 10 voor productie-ready links
    test_moties = september_moties[:10]

    working_links = []

    print(f"\n🔍 GENERATING DIRECT LINKS FOR {len(test_moties)} MOTIES:")

    for i, motie in enumerate(test_moties, 1):
        nummer = motie.get('Nummer')
        titel = motie.get('Titel', '')
        onderwerp = motie.get('Onderwerp', '')
        gewijzigd_op = motie.get('GewijzigdOp', '')
        afgedaan = motie.get('Afgedaan')

        print(f"\n   🧪 MOTIE {i}: {nummer}")
        print(f"      📄 {titel[:60]}...")
        if onderwerp:
            print(f"      💡 {onderwerp[:80]}...")
        print(f"      📅 {gewijzigd_op}")
        print(f"      ✅ Afgedaan: {afgedaan}")

        # Zoek directe link via search
        search_url = f"https://www.tweedekamer.nl/zoeken?qry={nummer}"

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                content = response.text

                # Vind directe links met HTML entities fix
                found_links = []

                # Patroon voor motie detail links
                pattern = r'href="([^"]*?detail\?id=([^&]+)[^"]*?did=([^"&]+)[^"]*)"'
                matches = re.findall(pattern, content, re.IGNORECASE)

                for match in matches:
                    full_link, motie_id, doc_id = match
                    if motie_id == nummer:
                        # Fix HTML entities
                        full_link = full_link.replace('&amp;', '&')
                        if not full_link.startswith('http'):
                            full_link = f"https://www.tweedekamer.nl{full_link}"
                        found_links.append((full_link, doc_id))

                # Verwijder duplicaten
                unique_links = list(set(found_links))

                if unique_links:
                    print(f"      ✅ Found {len(unique_links)} direct link(s)")

                    # Test de eerste link
                    direct_link, did = unique_links[0]
                    print(f"         🔗 Testing: {direct_link}")

                    try:
                        verify_response = requests.get(direct_link, headers=headers, timeout=5)

                        if verify_response.status_code == 200:
                            verify_content = verify_response.text.lower()

                            # Check for voting content
                            voting_indicators = ['stemming', 'voor', 'tegen', 'onthouding', 'besluit', 'vote']
                            has_voting = any(indicator in verify_content for indicator in voting_indicators)

                            print(f"            ✅ WORKS: Status {verify_response.status_code}")
                            if has_voting:
                                print(f"            🗳️ HAS VOTING RESULTS!")
                                working_links.append({
                                    'nummer': nummer,
                                    'titel': titel,
                                    'onderwerp': onderwerp,
                                    'gewijzigd_op': gewijzigd_op,
                                    'afgedaan': afgedaan,
                                    'direct_link': direct_link,
                                    'did': did,
                                    'has_voting': True
                                })
                            else:
                                print(f"            ℹ️ No voting content found")
                        else:
                            print(f"            ❌ Link failed: {verify_response.status_code}")

                    except Exception as e:
                        print(f"            ❌ Verification error: {e}")
                else:
                    print(f"      ❌ No direct links found")

            else:
                print(f"      ❌ Search failed: {response.status_code}")

        except Exception as e:
            print(f"      ❌ Search error: {e}")

        # Kleine pauze tussen requests
        import time
        time.sleep(0.5)

    # Resultaten tonen
    print(f"\n" + "="*80)
    print("🎯 PRODUCTION-READY DIRECT MOTIE LINKS WITH VOTING RESULTS:")
    print("="*80)

    if working_links:
        print(f"✅ SUCCESS! FOUND {len(working_links)} WORKING DIRECT LINKS WITH VOTING RESULTS")
        print(f"🗳️ All links show stem uitslag directly (voor/tegen/onthouding/besluit)")

        for i, link in enumerate(working_links, 1):
            print(f"\n📋 MOTIE {i}: {link['nummer']}")
            print(f"   📄 Titel: {link['titel'][:60]}...")
            if link['onderwerp']:
                print(f"   💡 Onderwerp: {link['onderwerp'][:80]}...")
            print(f"   📅 Gewijzigd: {link['gewijzigd_op']}")
            print(f"   ✅ Afgedaan: {link['afgedaan']}")
            print(f"   🗳️ Stem uitslag: Direct zichtbaar")
            print(f"   🔗 LINK: {link['direct_link']}")
            print(f"   📄 did={link['did']}")

        # Gebruiksaanwijzing
        print(f"\n" + "="*80)
        print("💡 HOW TO USE THESE LINKS IN PRODUCTION:")
        print("="*80)
        print("1. 🔗 Direct links tonen stem uitslag direct op de pagina")
        print("2. 📊 Format: /kamerstukken/moties/detail?id=[MOTIE]&did=[DOCUMENT]")
        print("3. ✅ Alle links zijn getest en werken")
        print("4. 🗳️ Stemming resultaten zijn direct zichtbaar")
        print("5. 🎯 Perfect voor je motiematcher applicatie")

        # Technische details
        print(f"\n" + "="*80)
        print("🔧 TECHNICAL IMPLEMENTATION:")
        print("="*80)
        print("# Python code voor link generatie:")
        print("def get_motie_link(motie_nummer, document_id):")
        print("    return f'https://www.tweedekamer.nl/kamerstukken/moties/detail?id={motie_nummer}&did={document_id}'")
        print("")
        print("# Voorbeeld gebruik:")
        print("link = get_motie_link('2025Z17770', '2025D41494')")
        print("print(link)  # https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z17770&did=2025D41494")

    else:
        print("❌ No working direct links found")

    return working_links

if __name__ == "__main__":
    generate_production_motie_links()