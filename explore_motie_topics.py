import json
from pathlib import Path

# Bekijk interessante moties met veel verschillende onderwerpen
zaak_files = list(Path('bronmateriaal-onbewerkt/zaak').glob('*.json'))
onderwerpen = {}

for file in zaak_files:
    data = json.load(open(file, encoding='utf-8'))
    for motie in data:
        onderwerp = motie.get('Titel', 'Onbekend')
        if onderwerp not in onderwerpen:
            onderwerpen[onderwerp] = []
        onderwerpen[onderwerp].append({
            'nummer': motie.get('Nummer'),
            'tekst': motie.get('Onderwerp', 'Geen tekst')[:100] + '...'
        })

print("📝 MOTIE ONDERWERPEN ANALYSE:")
print("=" * 40)

# Toon onderwerpen met meerdere moties
for onderwerp, moties in onderwerpen.items():
    if len(moties) > 1:
        print(f"\n🏷️ {onderwerp}")
        print(f"   📊 {len(moties)} moties")
        for i, motie in enumerate(moties[:3]):  # Max 3 voorbeelden
            print(f"   {i+1}. #{motie['nummer']}: {motie['tekst']}")

print(f"\n📊 TOTAAL: {len(onderwerpen)} verschillende onderwerpen")
print(f"📋 Onderwerpen met meerdere moties: {sum(1 for moties in onderwerpen.values() if len(moties) > 1)}")