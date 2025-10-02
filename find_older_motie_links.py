#!/usr/bin/env python3
"""
Zoek directe links voor oudere moties (minstens 14 dagen oud) met stemuitslagen
"""

import json
import requests
import re
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urljoin

def find_older_motie_links():
    print("🔍 SEARCHING FOR OLDER MOTIE LINKS (14+ DAYS OLD)")
    print("=" * 60)

    # Laad zaak data
    data_dir = Path("bronmateriaal-onbewerkt")
    zaak_files = list((data_dir / "zaak").glob("*.json"))

    all_zaken = []
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_zaken.extend(data)

    # Filter moties
    moties = [z for z in all_zaken if z.get('Soort') == 'Motie']

    # Bepaal cutoff datum (14 dagen geleden)
    cutoff_date = datetime.now() - timedelta(days=14)
    print(f"📅 Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}")

    # Filter oudere moties
    older_moties = []
    for motie in moties:
        gewijzigd_op = motie.get('GewijzigdOp', '')
        if gewijzigd_op:
            try:
                # Parse de datum (format: 2025-09-30T16:30:20.167+02:00)
                motie_date = datetime.fromisoformat(gewijzigd_op.replace('Z', '+00:00'))
                if motie_date < cutoff_date:
                    older_moties.append(motie)
            except:
                continue

    print(f"📊 Found {len(older_moties)} moties older than 14 days")

    # Test de voorbeeld link die de gebruiker gaf
    example_link = "https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z17656&did=2025D41255"
    print(f"\n🧪 TESTING USER'S EXAMPLE LINK:")
    print(f"   🔗 {example_link}")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(example_link, headers=headers, timeout=10)

        if response.status_code == 200:
            content = response.text.lower()
            print(f"   ✅ WORKS: Status {response.status_code}, {len(response.text):,} chars")

            # Check for voting content
            voting_indicators = ['stemming', 'voor', 'tegen', 'onthouding', 'vote', 'besluit']
            found_voting = [ind for ind in voting_indicators if ind in content]

            if found_voting:
                print(f"   🗳️ Contains voting info: {', '.join(found_voting)}")
            else:
                print(f"   ℹ️ No obvious voting content found")

        else:
            print(f"   ❌ Failed: Status {response.status_code}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Zoek naar oudere moties en probeer hun links te vinden
    working_links = []

    # Sorteer op leeftijd (oudste eerst)
    older_moties.sort(key=lambda x: x.get('GewijzigdOp', ''), reverse=False)

    # Test eerste 10 oudere moties
    test_moties = older_moties[:10]

    print(f"\n🔍 TESTING {len(test_moties)} OLDER MOTIES:")

    for i, motie in enumerate(test_moties, 1):
        nummer = motie.get('Nummer')
        titel = motie.get('Titel', '')
        gewijzigd_op = motie.get('GewijzigdOp', '')
        afgedaan = motie.get('Afgedaan')

        print(f"\n   🧪 MOTIE {i}: {nummer}")
        print(f"      📄 {titel[:60]}...")
        print(f"      📅 {gewijzigd_op}")
        print(f"      ✅ Afgedaan: {afgedaan}")

        # Strategie 1: Zoek naar directe links in zoekresultaten
        search_url = f"https://www.tweedekamer.nl/zoeken?qry={nummer}"

        try:
            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                content = response.text

                # Zoek naar motie detail links met regex
                # Pattern voor links naar motie detail pagina's
                pattern = r'href="([^"]*?/kamerstukken/moties/detail[^"]*?id=([^&]+)[^"]*?did=([^"&]+)[^"]*)"'
                matches = re.findall(pattern, content, re.IGNORECASE)

                found_direct_links = []
                for full_match, motie_id, doc_id in matches:
                    if motie_id == nummer:
                        # Maak volledige URL
                        if full_match.startswith('http'):
                            direct_link = full_match
                        else:
                            direct_link = urljoin('https://www.tweedekamer.nl', full_match)

                        found_direct_links.append((direct_link, doc_id))

                if found_direct_links:
                    print(f"      ✅ Found {len(found_direct_links)} direct link(s)")

                    # Test de eerste link
                    direct_link, did = found_direct_links[0]
                    print(f"         🔗 Testing: {direct_link}")

                    try:
                        verify_response = requests.get(direct_link, headers=headers, timeout=5)

                        if verify_response.status_code == 200:
                            verify_content = verify_response.text.lower()

                            # Check for voting content
                            has_voting = any(word in verify_content for word in ['stemming', 'voor', 'tegen', 'onthouding', 'besluit'])

                            print(f"            ✅ WORKS: Status {verify_response.status_code}")
                            if has_voting:
                                print(f"            🗳️ HAS VOTING RESULTS!")
                                working_links.append({
                                    'nummer': nummer,
                                    'titel': titel,
                                    'gewijzigd_op': gewijzigd_op,
                                    'afgedaan': afgedaan,
                                    'direct_link': direct_link,
                                    'did': did,
                                    'has_voting': True
                                })
                            else:
                                print(f"            ℹ️ No voting content found")
                                working_links.append({
                                    'nummer': nummer,
                                    'titel': titel,
                                    'gewijzigd_op': gewijzigd_op,
                                    'afgedaan': afgedaan,
                                    'direct_link': direct_link,
                                    'did': did,
                                    'has_voting': False
                                })
                        else:
                            print(f"            ❌ Link failed: {verify_response.status_code}")

                    except Exception as e:
                        print(f"            ❌ Verification error: {e}")

                else:
                    print(f"      ❌ No direct links found in search results")

            else:
                print(f"      ❌ Search failed: {response.status_code}")

        except Exception as e:
            print(f"      ❌ Search error: {e}")

        # Kleine pauze tussen requests
        import time
        time.sleep(0.5)

    # Resultaten tonen
    print(f"\n" + "="*80)
    print("🎯 RESULTS FOR OLDER MOTIES (14+ DAYS):")
    print("="*80)

    if working_links:
        voting_links = [link for link in working_links if link['has_voting']]
        no_voting_links = [link for link in working_links if not link['has_voting']]

        print(f"✅ FOUND {len(working_links)} WORKING DIRECT LINKS:")
        print(f"   🗳️ With voting results: {len(voting_links)}")
        print(f"   ℹ️ Without voting: {len(no_voting_links)}")

        # Toon alle links
        for i, link in enumerate(working_links, 1):
            print(f"\n📋 MOTIE {i}: {link['nummer']}")
            print(f"   📄 {link['titel'][:60]}...")
            print(f"   📅 {link['gewijzigd_op']}")
            print(f"   ✅ Afgedaan: {link['afgedaan']}")
            print(f"   🗳️ Voting: {'YES' if link['has_voting'] else 'NO'}")
            print(f"   🔗 {link['direct_link']}")

    else:
        print("❌ No working direct links found for older moties")

    # Conclusie
    print(f"\n💡 CONCLUSION:")
    print("="*80)
    if working_links:
        voting_count = len([l for l in working_links if l['has_voting']])
        print(f"✅ Older moties CAN have direct links with voting results")
        print(f"🗳️ Found {voting_count} links with voting information")
        print(f"📊 Success rate: {len(working_links)}/{len(test_moties)} tested moties")
    else:
        print("❌ Even older moties don't seem to have direct links")
        print("🔍 May need different search strategy or timing")

    return working_links

if __name__ == "__main__":
    find_older_motie_links()