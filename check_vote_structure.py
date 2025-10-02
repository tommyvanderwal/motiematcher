import json
from pathlib import Path

# Find votes_page files (the new paginated ones)
vote_files = list(Path('bronmateriaal-onbewerkt/stemming').glob('votes_page_*.json'))
print(f"🗳️ Found {len(vote_files)} vote page files")

if vote_files:
    # Load first page
    file = vote_files[0]
    data = json.load(open(file))
    
    print(f"\n📝 File: {file.name}")
    print(f"📊 Data type: {type(data)}")
    
    if isinstance(data, dict):
        print(f"📋 Keys: {list(data.keys())}")
        if 'value' in data:
            votes = data['value']
            print(f"📊 Votes in this page: {len(votes)}")
            
            if votes:
                vote = votes[0]
                print(f"\n🔍 First vote:")
                print(f"   Party: {vote.get('FractieNaam')}")
                print(f"   Vote: {vote.get('Soort')}")
                print(f"   Besluit_Id: {vote.get('Besluit_Id')}")
    
    elif isinstance(data, list):
        print(f"📊 Direct list with {len(data)} votes")
        if data:
            vote = data[0]
            print(f"\n🔍 First vote:")
            print(f"   Party: {vote.get('FractieNaam')}")
            print(f"   Vote: {vote.get('Soort')}")
            print(f"   Besluit_Id: {vote.get('Besluit_Id')}")
else:
    print("❌ No vote page files found")