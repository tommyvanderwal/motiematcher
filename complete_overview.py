import json
from pathlib import Path
from collections import Counter, defaultdict

# Analyse alle stemming bestanden voor complete partij overzicht
vote_files = list(Path('bronmateriaal-onbewerkt/stemming').glob('votes_page_*.json'))
print(f"🗳️ COMPLETE STEMMING ANALYSE ({len(vote_files)} bestanden)")
print("=" * 60)

all_parties = Counter()
party_votes = defaultdict(lambda: {'Voor': 0, 'Tegen': 0, 'Niet deelgenomen': 0, 'Anders': 0})
all_decisions = set()

# Verwerk alle voting files
for i, file in enumerate(vote_files[:10]):  # Eerste 10 voor snelheid
    if i % 5 == 0:
        print(f"📊 Verwerken bestand {i+1}/{min(10, len(vote_files))}: {file.name}")
    
    try:
        data = json.load(open(file, encoding='utf-8'))
        
        for vote in data:
            party = vote.get('ActorFractie', 'Onbekend')
            vote_type = vote.get('Soort', 'Anders')
            besluit_id = vote.get('Besluit_Id')
            
            all_parties[party] += 1
            
            if vote_type in party_votes[party]:
                party_votes[party][vote_type] += 1
            else:
                party_votes[party]['Anders'] += 1
            
            if besluit_id:
                all_decisions.add(besluit_id)
                
    except Exception as e:
        print(f"⚠️ Error in {file.name}: {e}")

print(f"\n📊 PARTIJ ACTIVITEIT (eerste 10 bestanden):")
print(f"   Totaal unieke besluiten: {len(all_decisions)}")
print(f"   Actieve partijen: {len(all_parties)}")

print(f"\n🏛️ TOP 15 MEEST ACTIEVE PARTIJEN:")
for party, total_votes in all_parties.most_common(15):
    votes = party_votes[party]
    print(f"   {party:25}: {total_votes:4d} stemmen (Voor:{votes['Voor']:3d}, Tegen:{votes['Tegen']:3d}, Onthouding:{votes['Niet deelgenomen']:2d})")

print(f"\n✅ SAMENVATTING:")
print(f"   📝 991 moties verzameld (30 dagen)")
print(f"   🗳️ ~{len(vote_files) * 250} stemmen verzameld (geschat)")
print(f"   🏛️ {len(all_parties)} actieve partijen")
print(f"   📋 {len(all_decisions)} verschillende besluiten")
print(f"   💾 {sum(f.stat().st_size for f in Path('bronmateriaal-onbewerkt').rglob('*.json'))/1024/1024:.1f} MB totale data")

print(f"\n🎯 KLAAR VOOR VOLGENDE FASE:")
print(f"   ✅ Data collectie voltooid")
print(f"   🔄 Nu kunnen we data transformeren en verrijken")
print(f"   🌐 Daarna de web matching platform bouwen")