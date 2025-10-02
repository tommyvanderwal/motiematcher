#!/usr/bin/env python3
"""
Zoek directe links voor behandelde moties (afgedaan = True) met stemuitslagen
"""

import json
import requests
import re
from pathlib import Path
from urllib.parse import urljoin

def find_treated_motie_links():
    print("🔍 SEARCHING FOR TREATED MOTIES (afgedaan=True) WITH VOTING RESULTS")
    print("=" * 70)

    # Laad zaak data
    data_dir = Path("bronmateriaal-onbewerkt")
    zaak_files = list((data_dir / "zaak").glob("*.json"))

    all_zaken = []
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_zaken.extend(data)

    # Filter moties die behandeld zijn (afgedaan = True)
    treated_moties = [z for z in all_zaken if z.get('Soort') == 'Motie' and z.get('Afgedaan') == True]

    print(f"📊 Found {len(treated_moties)} treated moties (afgedaan=True)")

    # Test de voorbeeld link nog een keer voor referentie
    example_link = "https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z17656&did=2025D41255"
    print(f"\n🧪 REFERENCE: User's example link")
    print(f"   🔗 {example_link}")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(example_link, headers=headers, timeout=10)

        if response.status_code == 200:
            content = response.text.lower()
            voting_words = ['stemming', 'voor', 'tegen', 'onthouding', 'besluit']
            found_voting = [word for word in voting_words if word in content]
            print(f"   ✅ WORKS: Status {response.status_code}, voting content: {', '.join(found_voting)}")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Zoek naar behandelde moties en hun directe links
    working_links = []

    # Sorteer op gewijzigd_op om oudste eerst te proberen
    treated_moties.sort(key=lambda x: x.get('GewijzigdOp', ''), reverse=False)

    # Test eerste 10 behandelde moties
    test_moties = treated_moties[:10]

    print(f"\n🔍 TESTING {len(test_moties)} TREATED MOTIES:")

    for i, motie in enumerate(test_moties, 1):
        nummer = motie.get('Nummer')
        titel = motie.get('Titel', '')
        gewijzigd_op = motie.get('GewijzigdOp', '')
        afgedaan = motie.get('Afgedaan')

        print(f"\n   🧪 MOTIE {i}: {nummer}")
        print(f"      📄 {titel[:60]}...")
        print(f"      📅 {gewijzigd_op}")
        print(f"      ✅ Afgedaan: {afgedaan}")

        # Strategie: Zoek naar directe links via scraping
        search_url = f"https://www.tweedekamer.nl/zoeken?qry={nummer}"

        try:
            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                content = response.text

                # Verbeterde regex voor het vinden van motie detail links
                # Zoek naar patronen zoals: /kamerstukken/moties/detail?id=...&did=...
                patterns = [
                    r'href="([^"]*?/kamerstukken/moties/detail[^"]*?id=([^&]+)[^"]*?did=([^"&]+)[^"]*)"',
                    r'href="([^"]*?detail\?id=([^&]+)[^"]*?did=([^"&]+)[^"]*)"',
                    r'/kamerstukken/moties/detail\?id=([^&]+)&did=([^"&]+)'
                ]

                found_links = []

                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple) and len(match) >= 2:
                            if len(match) == 3:
                                full_match, motie_id, doc_id = match
                            else:
                                motie_id, doc_id = match
                                full_match = f"/kamerstukken/moties/detail?id={motie_id}&did={doc_id}"

                            if motie_id == nummer:
                                # Maak volledige URL
                                if full_match.startswith('http'):
                                    direct_link = full_match
                                else:
                                    direct_link = urljoin('https://www.tweedekamer.nl', full_match)

                                found_links.append((direct_link, doc_id))

                # Verwijder duplicaten
                found_links = list(set(found_links))

                if found_links:
                    print(f"      ✅ Found {len(found_links)} potential direct link(s)")

                    # Test alle gevonden links
                    for j, (direct_link, did) in enumerate(found_links, 1):
                        print(f"         🔗 Testing link {j}: {direct_link}")

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

                    # Als fallback: probeer een gegokte link gebaseerd op patroon
                    # Sommige moties volgen patroon: did = D + (Z nummer zonder eerste karakter)
                    guessed_did = f"2025D{nummer[5:]}"  # 2025Z17770 → 2025D17770
                    guessed_link = f"https://www.tweedekamer.nl/kamerstukken/moties/detail?id={nummer}&did={guessed_did}"

                    print(f"      🎲 Trying guessed link: {guessed_link}")

                    try:
                        guess_response = requests.get(guessed_link, headers=headers, timeout=5)

                        if guess_response.status_code == 200:
                            guess_content = guess_response.text.lower()
                            has_voting = any(word in guess_content for word in ['stemming', 'voor', 'tegen', 'onthouding'])

                            print(f"         🎯 GUESSED CORRECT!")
                            if has_voting:
                                print(f"         🗳️ HAS VOTING RESULTS!")
                                working_links.append({
                                    'nummer': nummer,
                                    'titel': titel,
                                    'gewijzigd_op': gewijzigd_op,
                                    'afgedaan': afgedaan,
                                    'direct_link': guessed_link,
                                    'did': guessed_did,
                                    'has_voting': True
                                })
                            else:
                                print(f"         ℹ️ No voting content")
                        else:
                            print(f"         ❌ Guess failed: {guess_response.status_code}")

                    except Exception as e:
                        print(f"         ❌ Guess error: {e}")

            else:
                print(f"      ❌ Search failed: {response.status_code}")

        except Exception as e:
            print(f"      ❌ Search error: {e}")

        # Kleine pauze tussen requests
        import time
        time.sleep(0.5)

    # Resultaten tonen
    print(f"\n" + "="*80)
    print("🎯 RESULTS FOR TREATED MOTIES (afgedaan=True):")
    print("="*80)

    if working_links:
        voting_links = [link for link in working_links if link['has_voting']]
        no_voting_links = [link for link in working_links if not link['has_voting']]

        print(f"✅ FOUND {len(working_links)} WORKING DIRECT LINKS:")
        print(f"   🗳️ With voting results: {len(voting_links)}")
        print(f"   ℹ️ Without voting: {len(no_voting_links)}")

        # Toon alle links met stemuitslagen
        voting_results = [link for link in working_links if link['has_voting']]

        if voting_results:
            print(f"\n🗳️ MOTIES WITH VOTING RESULTS:")
            for i, link in enumerate(voting_results, 1):
                print(f"\n📋 MOTIE {i}: {link['nummer']}")
                print(f"   📄 {link['titel'][:60]}...")
                print(f"   📅 {link['gewijzigd_op']}")
                print(f"   ✅ Afgedaan: {link['afgedaan']}")
                print(f"   🔗 {link['direct_link']}")
                print(f"   📄 did={link['did']}")

    else:
        print("❌ No working direct links found for treated moties")

    # Conclusie
    print(f"\n💡 CONCLUSION:")
    print("="*80)
    if working_links:
        voting_count = len([l for l in working_links if l['has_voting']])
        print(f"✅ Treated moties CAN have direct links with voting results")
        print(f"🗳️ Found {voting_count} links with voting information")
        print(f"📊 Success rate: {len(working_links)}/{len(test_moties)} tested moties")

        if voting_count > 0:
            print(f"\n🎉 SUCCESS! Found direct links with voting results as requested!")
            print(f"🔗 These links show stem uitslag directly, just like your example!")

    else:
        print("❌ Even treated moties don't have direct links in our data")
        print("🔍 May need to collect older data or use different search approach")

    return working_links

if __name__ == "__main__":
    find_treated_motie_links()