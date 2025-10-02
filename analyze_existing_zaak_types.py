import json
from pathlib import Path
from collections import Counter

def analyze_existing_zaak_data():
    """Analyseer al verzamelde Zaak data voor andere types dan Motie"""
    
    print("🔍 ANALYSE VERZAMELDE ZAAK DATA")
    print("=" * 45)
    
    zaak_files = list(Path('bronmateriaal-onbewerkt/zaak').glob('*.json'))
    
    all_soorten = Counter()
    examples_per_soort = {}
    
    print(f"📊 Verwerken {len(zaak_files)} Zaak bestanden...")
    
    for file in zaak_files:
        try:
            data = json.load(open(file, encoding='utf-8'))
            
            for zaak in data:
                soort = zaak.get('Soort', 'Onbekend')
                all_soorten[soort] += 1
                
                # Bewaar voorbeelden
                if soort not in examples_per_soort:
                    examples_per_soort[soort] = []
                
                if len(examples_per_soort[soort]) < 3:  # Max 3 voorbeelden per type
                    examples_per_soort[soort].append({
                        'nummer': zaak.get('Nummer'),
                        'titel': zaak.get('Titel'),
                        'onderwerp': zaak.get('Onderwerp', '')[:100] + '...' if zaak.get('Onderwerp') else 'Geen onderwerp'
                    })
                    
        except Exception as e:
            print(f"   ❌ Error in {file.name}: {e}")
    
    print(f"\n📋 GEVONDEN ZAAK TYPES ({len(all_soorten)}):")
    
    for soort, count in all_soorten.most_common():
        print(f"   {soort:30}: {count:4d} items")
        
        # Toon voorbeelden
        if soort in examples_per_soort:
            for i, example in enumerate(examples_per_soort[soort][:2]):
                titel = example['titel'] or 'Geen titel'
                print(f"      {i+1}. #{example['nummer']}: {titel[:60]}...")
    
    # Zoek specifiek naar wetten en amendementen
    print(f"\n🔍 SPECIFIEK ZOEKEN:")
    
    wet_related = [soort for soort in all_soorten.keys() if any(word in soort.lower() for word in ['wet', 'law'])]
    amendement_related = [soort for soort in all_soorten.keys() if any(word in soort.lower() for word in ['amendement', 'wijzig'])]
    
    print(f"   📝 Wet-gerelateerd ({len(wet_related)}): {wet_related}")
    print(f"   📝 Amendement-gerelateerd ({len(amendement_related)}): {amendement_related}")
    
    # Kijk naar totalen
    motie_count = all_soorten.get('Motie', 0)
    other_count = sum(count for soort, count in all_soorten.items() if soort != 'Motie')
    
    print(f"\n📊 TOTAAL OVERZICHT:")
    print(f"   🎯 Moties: {motie_count}")
    print(f"   📋 Andere types: {other_count}")
    print(f"   📊 Totaal Zaak items: {sum(all_soorten.values())}")
    
    return all_soorten, wet_related, amendement_related

def check_existing_data_completeness():
    """Check of we alle beschikbare data types hebben"""
    
    print(f"\n✅ DATA VOLLEDIGHEID CHECK")
    print("=" * 35)
    
    directories = ['zaak', 'stemming', 'besluit', 'agendapunt', 'document', 'activiteit']
    
    for dirname in directories:
        dirpath = Path('bronmateriaal-onbewerkt') / dirname
        if dirpath.exists():
            files = list(dirpath.glob('*.json'))
            total_size = sum(f.stat().st_size for f in files)
            print(f"   {dirname:12}: {len(files):3d} files, {total_size/1024/1024:.1f} MB")
        else:
            print(f"   {dirname:12}: ❌ Niet verzameld")
    
    print(f"\n🎯 AANBEVELINGEN:")
    print(f"   ✅ Moties: Volledig verzameld (991 items)")
    print(f"   ✅ Stemmingen: Volledig verzameld (~9500 stemmen)")
    print(f"   ⚠️ Wetten: Mogelijk in Zaak data, maar niet gefilterd")
    print(f"   ⚠️ Amendementen: Mogelijk in Zaak data, maar niet gefilterd")
    print(f"   ❌ Stemverklaringen: Nog niet onderzocht")
    print(f"   ❌ Document teksten: Mogelijk aanvullende content")

if __name__ == "__main__":
    soorten, wetten, amendementen = analyze_existing_zaak_data()
    check_existing_data_completeness()
    
    print(f"\n🔄 VOLGENDE STAPPEN:")
    print(f"   1. Collect Zaak items met andere Soort dan 'Motie'")
    print(f"   2. Specifiek zoeken naar wetten en amendementen")
    print(f"   3. Onderzoek Document entities voor volledige teksten")
    print(f"   4. Zoek naar stemverklaringen in andere entities")