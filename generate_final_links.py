#!/usr/bin/env python3
"""
Ontwikkel een robuuste strategie voor motie links
"""

import json
import requests
from pathlib import Path
from urllib.parse import urljoin

def develop_link_strategy():
    print("🚀 DEVELOPING ROBUST MOTIE LINK STRATEGY")
    print("=" * 60)

    # Test de werkende link die de gebruiker vond
    working_example = {
        'motie': '2025Z17770',
        'did': '2025D41494',
        'link': 'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z17770&did=2025D41494'
    }

    print("📋 KNOWN WORKING EXAMPLE:")
    print(f"   Motie: {working_example['motie']}")
    print(f"   Document: {working_example['did']}")
    print(f"   Link: {working_example['link']}")

    # Verificeer dat deze link werkt
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(working_example['link'], headers=headers, timeout=10)

        if response.status_code == 200:
            print(f"   ✅ VERIFIED WORKING: Status {response.status_code}")
            print(f"   📄 Content: {len(response.text):,} chars")
        else:
            print(f"   ❌ VERIFICATION FAILED: {response.status_code}")
    except Exception as e:
        print(f"   ❌ VERIFICATION ERROR: {e}")

    # Analyseer het patroon
    print(f"\n🔍 PATTERN ANALYSIS:")
    motie_num = working_example['motie']  # 2025Z17770
    doc_num = working_example['did']     # 2025D41494

    print(f"   Motie number: {motie_num}")
    print(f"   Document number: {doc_num}")

    # Check of er een wiskundig patroon is
    # Z17770 vs D41494 - geen duidelijk patroon
    print(f"   No obvious mathematical pattern")

    # Strategie: Bouw een mapping table door API calls
    print(f"\n🗺️ BUILDING MAPPING STRATEGY:")

    # Laad onze motie data
    data_dir = Path("bronmateriaal-onbewerkt")
    zaak_files = list((data_dir / "zaak").glob("*.json"))

    moties = []
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            moties.extend([z for z in data if z.get('Soort') == 'Motie'])

    print(f"   Found {len(moties)} moties to map")

    # Probeer voor een paar moties de mapping te vinden via scraping
    mapping_results = []

    test_moties = moties[10:15]  # Neem andere moties

    for motie in test_moties:
        nummer = motie.get('Nummer')
        titel = motie.get('Titel', '')

        print(f"\n   🔍 Mapping {nummer}: {titel[:40]}...")

        # Stap 1: Zoek op de website
        search_url = f"https://www.tweedekamer.nl/zoeken?qry={nummer}"

        try:
            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                content = response.text

                # Zoek naar motie detail links
                import re
                pattern = r'href="([^"]*kamerstukken/moties/detail[^"]*id=([^&]+)[^"]*did=([^"&]+)[^"]*)"'
                matches = re.findall(pattern, content)

                found_links = []
                for full_link, motie_id, doc_id in matches:
                    if motie_id == nummer:
                        full_url = urljoin('https://www.tweedekamer.nl', full_link)
                        found_links.append((full_url, doc_id))

                if found_links:
                    # Neem de eerste werkende link
                    direct_link, did = found_links[0]
                    print(f"      ✅ Found mapping: {nummer} → {did}")

                    # Verificeer
                    verify_response = requests.get(direct_link, headers=headers, timeout=5)
                    if verify_response.status_code == 200:
                        print(f"         ✅ Verified working")
                        mapping_results.append({
                            'motie': nummer,
                            'did': did,
                            'link': direct_link,
                            'verified': True
                        })
                    else:
                        print(f"         ❌ Verification failed: {verify_response.status_code}")
                else:
                    print(f"      ❌ No direct links found in search results")

            else:
                print(f"      ❌ Search failed: {response.status_code}")

        except Exception as e:
            print(f"      ❌ Error: {e}")

    # Resultaten tonen
    print(f"\n" + "="*60)
    print("🎯 MAPPING RESULTS:")
    print("="*60)

    if mapping_results:
        print(f"✅ SUCCESSFULLY MAPPED {len(mapping_results)} MOTIES:")

        for result in mapping_results:
            print(f"\n📋 {result['motie']}")
            print(f"   📄 did={result['did']}")
            print(f"   🔗 {result['link']}")
            print(f"   ✅ Verified: {result['verified']}")

    # Finale strategie
    print(f"\n💡 FINAL STRATEGY FOR MOTIE LINKS:")
    print("="*60)
    print("1. 🥇 PRIORITY: Direct links with did= parameter (when available)")
    print("   Format: https://www.tweedekamer.nl/kamerstukken/moties/detail?id=[MOTIE]&did=[DOCUMENT]")
    print("   ")
    print("2. 🥈 FALLBACK: Search-based links")
    print("   Format: https://www.tweedekamer.nl/zoeken?qry=[MOTIE]")
    print("   Reliable but requires user to click through")
    print("   ")
    print("3. 🔄 DISCOVERY: Extract did= from search results")
    print("   Scrape search pages to find direct links")
    print("   Build mapping table for known relationships")
    print("   ")
    print("4. 📊 DATA SOURCE: did= IDs come from Document entities")
    print("   But linkage may not be in our collected API data")
    print("   May require real-time API queries or web scraping")

    # Specifieke aanbeveling voor gebruiker
    print(f"\n🎯 FOR YOUR USE CASE:")
    print("Since you found one working direct link manually, the best approach is:")
    print("1. Use the direct format when you can determine the did= ID")
    print("2. Fall back to search links for reliability")
    print("3. Consider building a lookup table of known motie→document mappings")

    return mapping_results

if __name__ == "__main__":
    develop_link_strategy()