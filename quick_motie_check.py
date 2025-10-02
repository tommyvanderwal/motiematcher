import json
from pathlib import Path

# Load first motie file
file = list(Path('bronmateriaal-onbewerkt/zaak').glob('*.json'))[0]
data = json.load(open(file))

print(f"📝 File: {file.name}")
print(f"📊 Total moties: {len(data)}")
print(f"\n🔍 First 5 moties:")

for i, motie in enumerate(data[:5]):
    titel = motie.get('Titel', 'Geen titel')
    onderwerp = motie.get('Onderwerp', 'Geen onderwerp')
    nummer = motie.get('Nummer', 'N/A')
    
    print(f"{i+1}. #{nummer}")
    print(f"   Titel: {titel}")
    print(f"   Onderwerp: {onderwerp[:100]}...")
    print()