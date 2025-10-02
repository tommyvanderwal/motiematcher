"""
Debug the Besluit API to understand what's going wrong
"""

import requests
import json

def test_besluit_api():
    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'MotieMatcher-Debug/1.0',
        'Accept': 'application/json'
    })
    
    print("=== Testing Besluit API ===\n")
    
    # Test 1: Simple query
    print("1. Simple Besluit query (top 10):")
    try:
        url = f"{base_url}/Besluit"
        params = {'$top': 10}
        
        response = session.get(url, params=params, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            decisions = data.get('value', [])
            print(f"   Found: {len(decisions)} decisions")
            
            if decisions:
                print("   Sample decision:")
                sample = decisions[0]
                for key, value in sample.items():
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"     {key}: {value}")
        else:
            print(f"   Error: {response.text[:500]}")
            
    except Exception as e:
        print(f"   Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: With expand
    print("2. Besluit with expand (top 5):")
    try:
        url = f"{base_url}/Besluit"
        params = {
            '$top': 5,
            '$expand': 'Stemming'
        }
        
        response = session.get(url, params=params, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            decisions = data.get('value', [])
            print(f"   Found: {len(decisions)} decisions")
            
            for i, decision in enumerate(decisions):
                stemming = decision.get('Stemming', [])
                print(f"   Decision {i+1}: {len(stemming)} votes - {decision.get('BesluitTekst', 'No text')[:50]}...")
        else:
            print(f"   Error: {response.text[:500]}")
            
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_besluit_api()