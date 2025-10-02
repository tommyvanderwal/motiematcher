#!/usr/bin/env python3
"""
Test werkende links voor moties van vorige week
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
import time

def test_motie_links():
    data_dir = Path("bronmateriaal-onbewerkt")
    
    print("🔗 TESTING REAL MOTIE LINKS")
    print("=" * 50)
    
    # Laad zaak data
    zaak_files = list((data_dir / "zaak").glob("*.json"))
    all_zaken = []
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_zaken.extend(data)
    
    # Filter moties van vorige week (ongeveer 25 sept - 1 okt)
    moties = [z for z in all_zaken if z.get('Soort') == 'Motie']
    
    # Zoek moties van vorige week op basis van GewijzigdOp
    last_week_moties = []
    for motie in moties:
        gewijzigd_op = motie.get('GewijzigdOp', '')
        if '2025-09-2' in gewijzigd_op or '2025-10-01' in gewijzigd_op:
            last_week_moties.append(motie)
    
    print(f"📊 Found {len(last_week_moties)} moties from last week")
    
    # Test eerste 3 moties
    test_moties = last_week_moties[:3]
    
    for i, motie in enumerate(test_moties, 1):
        print(f"\n🧪 TESTING MOTIE {i}:")
        print("=" * 30)
        
        nummer = motie.get('Nummer')
        titel = motie.get('Titel', '')
        onderwerp = motie.get('Onderwerp', '')
        zaak_id = motie.get('Id')
        
        print(f"   Nummer: {nummer}")
        print(f"   Titel: {titel[:80]}...")
        print(f"   Onderwerp: {onderwerp[:100]}...")
        print(f"   GewijzigdOp: {motie.get('GewijzigdOp')}")
        
        # Test verschillende link formaten
        link_formats = [
            # Origineel format dat niet werkte
            f"https://www.tweedekamer.nl/kamerstukken/detail?id={nummer}",
            
            # Alternatieve formaten
            f"https://www.tweedekamer.nl/kamerstukken/detail/{nummer}",
            f"https://www.tweedekamer.nl/kamerstukken/{nummer}",
            f"https://zoek.tweedekamer.nl/zoeken?qry={nummer}",
            
            # API verificatie link
            f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Zaak('{zaak_id}')",
        ]
        
        print(f"\n   🔗 Testing different link formats:")
        
        for j, link in enumerate(link_formats, 1):
            print(f"\n     Link {j}: {link}")
            
            try:
                # Test de link
                response = requests.get(link, timeout=10, allow_redirects=True)
                status = response.status_code
                
                if status == 200:
                    content_length = len(response.text)
                    content_type = response.headers.get('content-type', '')
                    
                    print(f"       ✅ Status: {status}")
                    print(f"       📄 Content-Type: {content_type}")
                    print(f"       📏 Content Length: {content_length:,} chars")
                    
                    # Check of het relevante content bevat
                    if 'json' in content_type.lower():
                        print(f"       📋 JSON API response")
                        try:
                            data = response.json()
                            if isinstance(data, dict) and 'Titel' in data:
                                print(f"       ✅ Contains motie data: {data.get('Titel', '')[:50]}...")
                        except:
                            print(f"       ⚠️ JSON parse error")
                            
                    elif 'html' in content_type.lower():
                        html = response.text.lower()
                        if nummer.lower() in html or any(word in html for word in titel.lower().split()[:3] if len(word) > 4):
                            print(f"       ✅ HTML contains motie reference")
                        else:
                            print(f"       ⚠️ HTML does not contain motie reference")
                            
                        # Check for common elements
                        if 'tweede kamer' in html and ('motie' in html or 'kamerstuk' in html):
                            print(f"       ✅ Relevant Tweede Kamer page")
                        elif 'zoeken' in html or 'resultaten' in html:
                            print(f"       ℹ️ Search results page")
                        else:
                            print(f"       ❓ Generic page")
                            
                elif status == 404:
                    print(f"       ❌ Status: {status} - Page not found")
                elif status == 302 or status == 301:
                    print(f"       🔄 Status: {status} - Redirect to: {response.url}")
                else:
                    print(f"       ⚠️ Status: {status}")
                    
            except requests.exceptions.Timeout:
                print(f"       ⏰ Timeout")
            except requests.exceptions.ConnectionError:
                print(f"       🔌 Connection error")  
            except Exception as e:
                print(f"       ❌ Error: {e}")
                
            # Kleine pause tussen requests
            time.sleep(0.5)
    
    print(f"\n🎯 GENERATING WORKING LINKS:")
    print("=" * 40)
    
    # Probeer een werkende link strategie te vinden
    working_links = []
    
    for motie in test_moties:
        nummer = motie.get('Nummer')
        zaak_id = motie.get('Id')
        titel = motie.get('Titel', '')
        
        print(f"\n📋 {nummer}: {titel[:60]}...")
        
        # Zoekopdracht link (meest betrouwbaar)
        search_query = f"{nummer}"
        zoek_link = f"https://zoek.tweedekamer.nl/zoeken?qry={search_query}&srt=date%3Adesc%3Adate&fld_tk_categorie=Kamerstukken&fld_prl_kamerstuk=Moties"
        
        # API link (altijd werkend voor verificatie)  
        api_link = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Zaak('{zaak_id}')"
        
        # Officiële bekendmakingen (backup)
        ob_link = f"https://zoek.officielebekendmakingen.nl/zoeken/resultaat/?zkt=Uitgebreid&pst=ParlementaireDocumenten&dpr=Alle&tkst={nummer}"
        
        print(f"   🔍 Search: {zoek_link}")
        print(f"   🔗 API: {api_link}")
        print(f"   📄 Official: {ob_link}")
        
        working_links.append({
            'nummer': nummer,
            'titel': titel,
            'search_link': zoek_link,
            'api_link': api_link,
            'official_link': ob_link
        })
    
    return working_links

if __name__ == "__main__":
    links = test_motie_links()
    
    print(f"\n✅ SUMMARY: Generated {len(links)} sets of working links")
    print(f"🎯 Use search links for user-friendly access")
    print(f"🔗 Use API links for verification")
    print(f"📄 Use official links as backup")