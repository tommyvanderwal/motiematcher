import json
from pathlib import Path

# Load first stemming file
file = list(Path('bronmateriaal-onbewerkt/stemming').glob('*.json'))[0]
data = json.load(open(file))

print(f"🗳️ File: {file.name}")
print(f"📊 Total votes: {len(data)}")

if data:
    vote = data[0]
    print(f"\n🔍 Vote keys: {list(vote.keys())}")
    print(f"\n📋 First vote example:")
    print(f"   Besluit_Id: {vote.get('Besluit_Id')}")
    print(f"   FractieNaam: {vote.get('FractieNaam')}")
    print(f"   Soort: {vote.get('Soort')}")
    print(f"   GewijzigdOp: {vote.get('GewijzigdOp')}")
    
    # Count parties and vote types
    parties = {}
    for v in data[:100]:  # First 100 for speed
        party = v.get('FractieNaam')
        vote_type = v.get('Soort')
        if party:
            if party not in parties:
                parties[party] = {'Voor': 0, 'Tegen': 0, 'Onthouding': 0}
            if vote_type in parties[party]:
                parties[party][vote_type] += 1

    print(f"\n🏛️ Parties in first 100 votes:")
    for party, votes in parties.items():
        print(f"   {party:20}: Voor={votes['Voor']:2d}, Tegen={votes['Tegen']:2d}, Onthouding={votes['Onthouding']:2d}")