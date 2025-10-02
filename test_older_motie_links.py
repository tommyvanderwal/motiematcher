#!/usr/bin/env python3
"""
Test werkende links met oudere moties die al gepubliceerd zijn
"""

import json
import requests
from pathlib import Path
from datetime import datetime
import time
import urllib.parse

def test_with_older_moties():
    data_dir = Path("bronmateriaal-onbewerkt")
    
    print("🔗 TESTING WITH OLDER, PUBLISHED MOTIES")
    print("=" * 50)
    
    # Laad zaak data
    zaak_files = list((data_dir / "zaak").glob("*.json"))
    all_zaken = []
    for file in zaak_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_zaken.extend(data)
    
    # Filter moties
    moties = [z for z in all_zaken if z.get('Soort') == 'Motie']
    
    # Zoek oudere moties (minder recent dan gisteren)
    older_moties = []
    for motie in moties:
        gewijzigd_op = motie.get('GewijzigdOp', '')
        if '2025-09-' in gewijzigd_op:  # September moties
            older_moties.append(motie)
    
    print(f"📊 Found {len(older_moties)} older moties from September")
    
    # Test eerste 3 oudere moties
    test_moties = older_moties[:3] if older_moties else moties[:3]
    
    for i, motie in enumerate(test_moties, 1):
        print(f"\n🧪 TESTING MOTIE {i}:")
        print("=" * 30)
        
        nummer = motie.get('Nummer')
        titel = motie.get('Titel', '')
        onderwerp = motie.get('Onderwerp', '')
        afgedaan = motie.get('Afgedaan')
        status = motie.get('Status')
        
        print(f"   Nummer: {nummer}")
        print(f"   Titel: {titel[:60]}...")
        print(f"   Afgedaan: {afgedaan}")
        print(f"   Status: {status}")
        print(f"   GewijzigdOp: {motie.get('GewijzigdOp')}")
        
        # Probeer werkende link formaten
        working_formats = []
        
        # Format 1: Zoekfunctie Tweede Kamer
        search_url = f"https://zoek.tweedekamer.nl/zoeken?qry={urllib.parse.quote(nummer)}"
        
        # Format 2: Officiële bekendmakingen
        ob_url = f"https://zoek.officielebekendmakingen.nl/zoeken/resultaat/?zkt=Uitgebreid&pst=ParlementaireDocumenten&tkst={nummer}"
        
        # Format 3: Simpele google-achtige zoek
        google_tk_url = f"https://www.tweedekamer.nl/zoeken?qry={urllib.parse.quote(nummer)}"
        
        test_urls = [
            ("TK Search", search_url),
            ("Official Publications", ob_url), 
            ("TK Site Search", google_tk_url)
        ]
        
        print(f"\n   🔗 Testing working formats:")
        
        for name, url in test_urls:
            print(f"\n     {name}: {url}")
            
            try:
                # Test de URL - gebruik user agent om bot detection te vermijden
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, timeout=15, headers=headers, allow_redirects=True)
                status = response.status_code
                
                if status == 200:
                    content = response.text.lower()
                    content_type = response.headers.get('content-type', '')
                    
                    print(f"       ✅ Status: {status}")
                    print(f"       📄 Content-Type: {content_type}")
                    print(f"       📏 Content Length: {len(response.text):,} chars")
                    
                    # Check for relevant content
                    if nummer.lower() in content:
                        print(f"       ✅ Contains motie nummer")
                        working_formats.append((name, url))
                    
                    # Check for motion-related keywords
                    motion_keywords = ['motie', 'kamerstuk', 'tweede kamer']
                    found_keywords = [kw for kw in motion_keywords if kw in content]
                    if found_keywords:
                        print(f"       ✅ Contains keywords: {', '.join(found_keywords)}")
                    
                    # Check for search results
                    if 'resultaten' in content or 'results' in content:
                        print(f"       ℹ️ Shows search results")
                        
                elif status == 404:
                    print(f"       ❌ Status: {status} - Page not found")
                else:
                    print(f"       ⚠️ Status: {status}")
                    
            except requests.exceptions.Timeout:
                print(f"       ⏰ Timeout (15s)")
            except requests.exceptions.ConnectionError:
                print(f"       🔌 Connection error")  
            except Exception as e:
                print(f"       ❌ Error: {str(e)[:50]}...")
                
            # Pause tussen requests
            time.sleep(1)
        
        # Toon werkende links voor deze motie
        if working_formats:
            print(f"\n       ✅ WORKING LINKS FOUND:")
            for name, url in working_formats:
                print(f"          {name}: {url}")
        else:
            print(f"\n       ❌ No working links found for {nummer}")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print("=" * 40)
    print("✅ Use Tweede Kamer search function: https://zoek.tweedekamer.nl/zoeken?qry=[NUMMER]")
    print("✅ Use Official Publications search: https://zoek.officielebekendmakingen.nl/...")
    print("⚠️ Direct kamerstuk links don't work for recent/unpublished moties")
    print("💡 Recent moties may need time to be published on the website")

if __name__ == "__main__":
    test_with_older_moties()