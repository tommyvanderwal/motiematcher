#!/usr/bin/env python3
"""
Specifiek zoeken naar directe motie links zoals het voorbeeld van de gebruiker
"""

import json
import requests
import re
from pathlib import Path

def find_direct_links_like_example():
    print("🎯 SEARCHING FOR DIRECT MOTIE LINKS LIKE USER'S EXAMPLE")
    print("=" * 60)

    # Het werkende voorbeeld van de gebruiker
    example_link = "https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z17656&did=2025D41255"
    example_motie = "2025Z17656"
    example_did = "2025D41255"

    print("📋 USER'S WORKING EXAMPLE:")
    print(f"   Motie: {example_motie}")
    print(f"   Document: {example_did}")
    print(f"   Link: {example_link}")

    # Verificeer nogmaals dat het voorbeeld werkt
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(example_link, headers=headers, timeout=10)

        if response.status_code == 200:
            content = response.text.lower()
            voting_words = ['stemming', 'voor', 'tegen', 'onthouding', 'besluit']
            found_voting = [word for word in voting_words if word in content]
            print(f"   ✅ VERIFIED: Status {response.status_code}, voting content: {', '.join(found_voting)}")
        else:
            print(f"   ❌ VERIFICATION FAILED: {response.status_code}")

    except Exception as e:
        print(f"   ❌ VERIFICATION ERROR: {e}")

    # Laad onze motie data
    data_dir = Path("bronmateriaal-onbewerkt")
    zaak_files = list((data_dir / "zaak").glob("*.json"))

    moties = []
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            moties.extend([z for z in data if z.get('Soort') == 'Motie'])

    print(f"\n📊 Found {len(moties)} moties in our data")

    # Zoek naar moties die mogelijk vergelijkbare links hebben
    # Focus op moties uit dezelfde periode als het voorbeeld (september 2025)
    september_moties = []
    for motie in moties:
        gewijzigd_op = motie.get('GewijzigdOp', '')
        if '2025-09-' in gewijzigd_op:
            september_moties.append(motie)

    print(f"📅 Found {len(september_moties)} moties from September 2025")

    # Test een paar september moties
    test_moties = september_moties[:5]  # Test eerste 5

    working_links = []

    print(f"\n🔍 TESTING {len(test_moties)} SEPTEMBER MOTIES:")

    for i, motie in enumerate(test_moties, 1):
        nummer = motie.get('Nummer')
        titel = motie.get('Titel', '')
        gewijzigd_op = motie.get('GewijzigdOp', '')
        afgedaan = motie.get('Afgedaan')

        print(f"\n   🧪 MOTIE {i}: {nummer}")
        print(f"      📄 {titel[:60]}...")
        print(f"      📅 {gewijzigd_op}")
        print(f"      ✅ Afgedaan: {afgedaan}")

        # Strategie 1: Probeer patroon gebaseerd op voorbeeld
        # 2025Z17656 → 2025D41255 (verschil van 23599)
        # Dit lijkt niet consistent te zijn

        # Strategie 2: Gebruik de zoekfunctie en parse HTML gedetailleerd
        search_url = f"https://www.tweedekamer.nl/zoeken?qry={nummer}"

        try:
            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                content = response.text

                # Gedetailleerde HTML parsing voor motie links
                # Zoek naar verschillende patronen

                found_links = []

                # Patroon 1: Directe detail links (met HTML entities)
                pattern1 = r'href="([^"]*?detail\?id=([^&]+)[^"]*?did=([^"&]+)[^"]*)"'
                matches1 = re.findall(pattern1, content, re.IGNORECASE)

                for match in matches1:
                    full_link, motie_id, doc_id = match
                    if motie_id == nummer:
                        # Fix HTML entities
                        full_link = full_link.replace('&amp;', '&')
                        if not full_link.startswith('http'):
                            full_link = f"https://www.tweedekamer.nl{full_link}"
                        found_links.append((full_link, doc_id, 'pattern1'))

                # Patroon 2: Kamerstukken moties links (met HTML entities)
                pattern2 = r'href="([^"]*kamerstukken/moties[^"]*id=([^&]+)[^"]*did=([^"&]+)[^"]*)"'
                matches2 = re.findall(pattern2, content, re.IGNORECASE)

                for match in matches2:
                    full_link, motie_id, doc_id = match
                    if motie_id == nummer:
                        # Fix HTML entities
                        full_link = full_link.replace('&amp;', '&')
                        if not full_link.startswith('http'):
                            full_link = f"https://www.tweedekamer.nl{full_link}"
                        found_links.append((full_link, doc_id, 'pattern2'))

                # Verwijder duplicaten
                unique_links = []
                seen = set()
                for link, did, pattern in found_links:
                    if (link, did) not in seen:
                        unique_links.append((link, did, pattern))
                        seen.add((link, did))

                if unique_links:
                    print(f"      ✅ Found {len(unique_links)} potential direct link(s)")

                    # Test alle gevonden links
                    for j, (direct_link, did, pattern) in enumerate(unique_links, 1):
                        print(f"         🔗 Testing link {j} ({pattern}): {direct_link}")

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
                                        'pattern': pattern,
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
                                        'pattern': pattern,
                                        'has_voting': False
                                    })
                            else:
                                print(f"            ❌ Link failed: {verify_response.status_code}")

                        except Exception as e:
                            print(f"            ❌ Verification error: {e}")

                else:
                    print(f"      ❌ No direct links found in search results")

                    # Strategie 3: Probeer gegokte links gebaseerd op voorbeeld patroon
                    # Als voorbeeld 2025Z17656 → 2025D41255, probeer dan voor andere moties
                    # Een patroon: neem de laatste 5 cijfers en tel er iets bij op?

                    base_num = nummer[5:]  # Neem alles na 2025Z
                    guessed_did = f"2025D{base_num}"  # Simpel: Z → D

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
                                    'pattern': 'guessed',
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
    print("🎯 RESULTS FOR DIRECT MOTIE LINKS:")
    print("="*80)

    if working_links:
        voting_links = [link for link in working_links if link['has_voting']]

        print(f"✅ FOUND {len(working_links)} WORKING DIRECT LINKS:")
        print(f"   🗳️ With voting results: {len(voting_links)}")

        if voting_links:
            print(f"\n🗳️ MOTIES WITH VOTING RESULTS (like your example):")
            for i, link in enumerate(voting_links, 1):
                print(f"\n📋 MOTIE {i}: {link['nummer']}")
                print(f"   📄 {link['titel'][:60]}...")
                print(f"   📅 {link['gewijzigd_op']}")
                print(f"   ✅ Afgedaan: {link['afgedaan']}")
                print(f"   🔗 {link['direct_link']}")
                print(f"   📄 did={link['did']} (found via {link['pattern']})")

        # Toon ook links zonder voting voor volledigheid
        no_voting_links = [link for link in working_links if not link['has_voting']]
        if no_voting_links:
            print(f"\nℹ️ ADDITIONAL WORKING LINKS (no voting shown):")
            for link in no_voting_links:
                print(f"   📋 {link['nummer']}: {link['direct_link']}")

    else:
        print("❌ No working direct links found")

    # Conclusie
    print(f"\n💡 CONCLUSION:")
    print("="*80)
    if working_links:
        voting_count = len([l for l in working_links if l['has_voting']])
        print(f"✅ Found {len(working_links)} working direct links")
        print(f"🗳️ {voting_count} show voting results directly (like your example)")

        if voting_count > 0:
            print(f"\n🎉 SUCCESS! Found direct links with voting results!")
            print(f"🔗 These work just like your example link")
            print(f"📊 Pattern: /kamerstukken/moties/detail?id=[MOTIE]&did=[DOCUMENT]")

    else:
        print("❌ No direct links found, but your example proves they exist")
        print("🔍 May need to collect data from different time periods")
        print("💡 The working format is confirmed: /moties/detail?id=[Z]&did=[D]")

    return working_links

if __name__ == "__main__":
    find_direct_links_like_example()