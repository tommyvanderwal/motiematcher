"""
Test different OData filter syntaxes
"""

import requests
from datetime import datetime, timedelta

def test_odata_filters():
    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'MotieMatcher-FilterTest/1.0',
        'Accept': 'application/json'
    })
    
    print("=== Testing OData Filter Syntaxes ===\n")
    
    # Test 1: No filter (recent data)
    print("1. Recent Stemming data (no filter, top 10):")
    try:
        url = f"{base_url}/Stemming"
        params = {
            '$top': 10,
            '$orderby': 'GewijzigdOp desc'
        }
        
        response = session.get(url, params=params, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            votes = data.get('value', [])
            print(f"   Found: {len(votes)} votes")
            
            if votes:
                print("   Most recent vote dates:")
                for i, vote in enumerate(votes[:5]):
                    date = vote.get('GewijzigdOp', 'Unknown')
                    party = vote.get('ActorFractie', 'Unknown')
                    print(f"     {i+1}. {date} - {party}")
        else:
            print(f"   Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Different filter syntaxes
    cutoff_date = datetime.now() - timedelta(days=3)  # Try 3 days
    
    filter_variations = [
        cutoff_date.strftime("%Y-%m-%dT00:00:00Z"),
        cutoff_date.strftime("%Y-%m-%d"),
        cutoff_date.strftime("'%Y-%m-%dT00:00:00Z'"),
        cutoff_date.strftime("datetime'%Y-%m-%dT00:00:00Z'"),
    ]
    
    for i, date_format in enumerate(filter_variations):
        print(f"{i+2}. Testing filter with format: {date_format}")
        try:
            url = f"{base_url}/Stemming"
            params = {
                '$filter': f"GewijzigdOp ge {date_format}",
                '$top': 5,
                '$orderby': 'GewijzigdOp desc'
            }
            
            response = session.get(url, params=params, timeout=20)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                votes = data.get('value', [])
                print(f"   Found: {len(votes)} votes")
            else:
                print(f"   Error snippet: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Try recent without date filter
    print(f"{len(filter_variations)+2}. Get recent without date filter:")
    try:
        url = f"{base_url}/Stemming"
        params = {
            '$top': 100,
            '$orderby': 'GewijzigdOp desc',
            '$expand': 'Besluit'
        }
        
        response = session.get(url, params=params, timeout=40)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            votes = data.get('value', [])
            print(f"   Found: {len(votes)} total votes")
            
            # Filter in code instead
            recent_votes = []
            cutoff = datetime.now() - timedelta(days=10)
            
            for vote in votes:
                vote_date_str = vote.get('GewijzigdOp', '')
                if vote_date_str:
                    try:
                        vote_date = datetime.fromisoformat(vote_date_str.replace('Z', '+00:00'))
                        if vote_date.replace(tzinfo=None) >= cutoff:
                            recent_votes.append(vote)
                    except:
                        pass
            
            print(f"   Recent votes (last 10 days): {len(recent_votes)}")
            
            if recent_votes:
                print("   Sample recent votes:")
                for i, vote in enumerate(recent_votes[:3]):
                    date = vote.get('GewijzigdOp', 'Unknown')[:10]
                    party = vote.get('ActorFractie', 'Unknown')
                    besluit = vote.get('Besluit', {}).get('BesluitTekst', 'No decision text')[:50]
                    print(f"     {i+1}. {date} - {party} - {besluit}...")
        else:
            print(f"   Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_odata_filters()