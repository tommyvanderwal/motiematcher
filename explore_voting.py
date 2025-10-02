"""
Simple voting explorer - Just see what's in the Stemming table
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def explore_voting_table():
    """Simple exploration of the Stemming table"""
    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'MotieMatcher-Explorer/1.0',
        'Accept': 'application/json'
    })
    
    print("=== Exploring Stemming (Voting) Table ===\n")
    
    # 1. First try: Just get ANY records from Stemming
    print("1. Getting first 10 records from Stemming table:")
    try:
        url = f"{base_url}/Stemming"
        params = {'$top': 10}
        
        response = session.get(url, params=params, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('value', [])
            print(f"   Found: {len(records)} records")
            
            if records:
                print("   Sample record structure:")
                sample = records[0]
                for key, value in sample.items():
                    print(f"     {key}: {value}")
            else:
                print("   No records found")
        else:
            print(f"   Error response: {response.text}")
            
    except Exception as e:
        print(f"   Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. Try to get metadata about the table
    print("2. Getting metadata about Stemming table:")
    try:
        url = f"{base_url}/$metadata"
        response = session.get(url, timeout=30)
        
        if response.status_code == 200:
            metadata = response.text
            # Look for Stemming entity in metadata
            if "Stemming" in metadata:
                print("   ✅ Stemming entity found in metadata")
                
                # Extract lines containing Stemming
                lines = metadata.split('\n')
                stemming_lines = [line.strip() for line in lines if 'Stemming' in line]
                
                print("   Stemming-related metadata lines:")
                for line in stemming_lines[:10]:  # Show first 10 matches
                    print(f"     {line}")
            else:
                print("   ❌ No Stemming entity in metadata")
        else:
            print(f"   Error getting metadata: {response.status_code}")
            
    except Exception as e:
        print(f"   Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. Try alternative spelling or similar tables
    print("3. Checking for alternative voting-related tables:")
    
    alternative_names = [
        'Stemmingen',
        'Vote', 
        'Voting',
        'Decision',
        'Beslissing'
    ]
    
    for name in alternative_names:
        try:
            url = f"{base_url}/{name}"
            params = {'$top': 1}
            
            response = session.get(url, params=params, timeout=10)
            print(f"   {name}: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('value', [])
                print(f"     ✅ Found table with {len(records)} records")
        except:
            print(f"   {name}: ❌ Failed")
    
    print("\n" + "="*50 + "\n")
    
    # 4. List all available entities
    print("4. Discovering all available entities:")
    try:
        url = base_url
        response = session.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'value' in data:
                entities = [item.get('name', 'Unknown') for item in data.get('value', [])]
                print(f"   Found {len(entities)} entities:")
                for entity in sorted(entities):
                    print(f"     - {entity}")
            else:
                print("   No entities list found in response")
                print(f"   Response keys: {list(data.keys())}")
        else:
            print(f"   Error listing entities: {response.status_code}")
            
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    explore_voting_table()