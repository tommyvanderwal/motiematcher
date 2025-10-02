#!/usr/bin/env python3
"""
Zoek moties met stemuitslagen door besluiten te analyseren
"""

import json
from pathlib import Path
from collections import defaultdict

def find_voted_motie_links():
    print("🔍 SEARCHING FOR MOTIES WITH VOTING RESULTS VIA BESLUITEN")
    print("=" * 60)

    # Laad alle data
    data_dir = Path("bronmateriaal-onbewerkt")

    # Laad zaak data (moties)
    zaak_data = []
    zaak_files = list((data_dir / "zaak").glob("*.json"))
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            zaak_data.extend(data)

    # Laad besluit data (stemmingen)
    besluit_data = []
    besluit_files = list((data_dir / "besluit").glob("*.json"))
    for file in besluit_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            besluit_data.extend(data)

    # Laad stemming data (individuele stemmen)
    stemming_data = []
    stemming_files = list((data_dir / "stemming").glob("*.json"))
    for file in stemming_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            stemming_data.extend(data)

    print(f"📊 Loaded {len(zaak_data)} zaken, {len(besluit_data)} besluiten, {len(stemming_data)} stemmingen")

    # Filter moties
    moties = [z for z in zaak_data if z.get('Soort') == 'Motie']
    print(f"📋 Found {len(moties)} moties")

    # Zoek besluiten die gekoppeld zijn aan moties
    motie_besluiten = defaultdict(list)
    besluit_details = {}

    for besluit in besluit_data:
        zaak_id = besluit.get('Zaak_Id')
        if zaak_id:
            motie_besluiten[zaak_id].append(besluit)
            besluit_details[besluit.get('Id')] = besluit

    print(f"🔗 Found {len(motie_besluiten)} zaken with besluiten")

    # Vind moties met besluiten
    moties_met_besluiten = []
    for motie in moties:
        zaak_id = motie.get('Id')
        if zaak_id in motie_besluiten:
            besluiten = motie_besluiten[zaak_id]
            moties_met_besluiten.append({
                'motie': motie,
                'besluiten': besluiten,
                'besluit_count': len(besluiten)
            })

    print(f"🗳️ Found {len(moties_met_besluiten)} moties with besluiten")

    # Sorteer op aantal besluiten (meeste eerst)
    moties_met_besluiten.sort(key=lambda x: x['besluit_count'], reverse=True)

    # Test de eerste 5 moties met besluiten
    test_cases = moties_met_besluiten[:5]

    print(f"\n🔍 TESTING {len(test_cases)} MOTIES WITH BESLUITEN:")

    working_links = []

    for i, case in enumerate(test_cases, 1):
        motie = case['motie']
        besluiten = case['besluiten']

        nummer = motie.get('Nummer')
        titel = motie.get('Titel', '')
        gewijzigd_op = motie.get('GewijzigdOp', '')
        afgedaan = motie.get('Afgedaan')

        print(f"\n   🧪 MOTIE {i}: {nummer}")
        print(f"      📄 {titel[:60]}...")
        print(f"      📅 {gewijzigd_op}")
        print(f"      ✅ Afgedaan: {afgedaan}")
        print(f"      🗳️ {len(besluiten)} besluit(en)")

        # Toon besluit details
        for j, besluit in enumerate(besluiten, 1):
            besluit_id = besluit.get('Id')
            besluit_status = besluit.get('Status')
            besluit_soort = besluit.get('Soort')
            besluit_datum = besluit.get('BesluitDatum')

            print(f"         Besluit {j}: {besluit_id} - {besluit_soort} - {besluit_status} - {besluit_datum}")

            # Zoek stemmingen voor dit besluit
            besluit_stemmingen = [s for s in stemming_data if s.get('Besluit_Id') == besluit_id]
            if besluit_stemmingen:
                print(f"            📊 {len(besluit_stemmingen)} stemmingen gevonden")

                # Toon voorbeeld stemmingen
                for k, stemming in enumerate(besluit_stemmingen[:3], 1):
                    stem = stemming.get('Stem')
                    persoon = stemming.get('Persoon_Id', 'Unknown')
                    partij = stemming.get('Partij', 'Unknown')
                    print(f"               Stem {k}: {persoon} ({partij}) - {stem}")

        # Probeer directe link te vinden
        # Strategie: Gebruik dezelfde did= discovery als eerder
        search_url = f"https://www.tweedekamer.nl/zoeken?qry={nummer}"

        try:
            import requests
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                content = response.text

                # Zoek naar directe links
                import re
                pattern = r'/kamerstukken/moties/detail\?id=([^&]+)&did=([^"&]+)'
                matches = re.findall(pattern, content)

                found_links = []
                for motie_id, doc_id in matches:
                    if motie_id == nummer:
                        direct_link = f"https://www.tweedekamer.nl/kamerstukken/moties/detail?id={motie_id}&did={doc_id}"
                        found_links.append(direct_link)

                if found_links:
                    print(f"      ✅ Found {len(found_links)} direct link(s)")

                    # Test de eerste link
                    test_link = found_links[0]
                    print(f"         🔗 Testing: {test_link}")

                    try:
                        verify_response = requests.get(test_link, headers=headers, timeout=5)

                        if verify_response.status_code == 200:
                            verify_content = verify_response.text.lower()

                            # Check for voting content
                            voting_indicators = ['stemming', 'voor', 'tegen', 'onthouding', 'besluit']
                            has_voting = any(indicator in verify_content for indicator in voting_indicators)

                            print(f"            ✅ WORKS: Status {verify_response.status_code}")
                            if has_voting:
                                print(f"            🗳️ HAS VOTING RESULTS!")
                                working_links.append({
                                    'nummer': nummer,
                                    'titel': titel,
                                    'gewijzigd_op': gewijzigd_op,
                                    'afgedaan': afgedaan,
                                    'direct_link': test_link,
                                    'besluit_count': len(besluiten),
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

        # Kleine pauze
        import time
        time.sleep(0.5)

    # Resultaten tonen
    print(f"\n" + "="*80)
    print("🎯 RESULTS FOR MOTIES WITH VOTING DATA:")
    print("="*80)

    if working_links:
        voting_links = [link for link in working_links if link['has_voting']]

        print(f"✅ FOUND {len(working_links)} MOTIES WITH BESLUITEN:")
        print(f"   🗳️ With voting results on website: {len(voting_links)}")

        if voting_links:
            print(f"\n🗳️ MOTIES WITH VOTING RESULTS ON WEBSITE:")
            for i, link in enumerate(voting_links, 1):
                print(f"\n📋 MOTIE {i}: {link['nummer']}")
                print(f"   📄 {link['titel'][:60]}...")
                print(f"   📅 {link['gewijzigd_op']}")
                print(f"   ✅ Afgedaan: {link['afgedaan']}")
                print(f"   🗳️ {link['besluit_count']} besluit(en)")
                print(f"   🔗 {link['direct_link']}")

    else:
        print("❌ No moties found with working direct links and voting results")

    # Conclusie
    print(f"\n💡 CONCLUSION:")
    print("="*80)
    print(f"📊 We have {len(moties_met_besluiten)} moties with besluit data in our collection")
    print(f"🗳️ These moties have been voted on (we have the voting records)")

    if working_links:
        print(f"✅ Found {len(working_links)} moties with working direct links")
        voting_count = len([l for l in working_links if l['has_voting']])
        if voting_count > 0:
            print(f"🗳️ {voting_count} of these show voting results directly on the website!")
    else:
        print(f"❌ Direct links not found, but voting data exists in our API collection")
        print(f"🔍 The working link format you provided suggests direct links exist for some moties")

    return working_links

if __name__ == "__main__":
    find_voted_motie_links()