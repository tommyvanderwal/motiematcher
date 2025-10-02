import requests
import json

def investigate_zaak_types():
    """Onderzoek welke Soort types er zijn in Zaak entities"""
    
    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
    
    print("🔍 ZAAK TYPES ONDERZOEK")
    print("=" * 40)
    
    # Haal een grote sample van Zaak entities op
    print("📊 Stap 1: Verzamel Zaak types uit sample")
    
    try:
        # Haal 1000 recente Zaak records op
        response = requests.get(f"{base_url}/Zaak?$top=1000&$orderby=GewijzigdOp desc")
        
        if response.status_code == 200:
            data = response.json()
            zaken = data.get('value', [])
            
            print(f"   ✅ Opgehaald: {len(zaken)} Zaak records")
            
            # Analyseer Soort types
            soorten = {}
            for zaak in zaken:
                soort = zaak.get('Soort', 'Onbekend')
                if soort not in soorten:
                    soorten[soort] = []
                soorten[soort].append({
                    'id': zaak.get('Id'),
                    'nummer': zaak.get('Nummer'),
                    'titel': zaak.get('Titel'),
                    'onderwerp': zaak.get('Onderwerp', '')[:100] + '...' if zaak.get('Onderwerp') else 'Geen onderwerp'
                })
            
            print(f"\n📋 Gevonden Zaak types ({len(soorten)}):")
            for soort, examples in soorden.items():
                print(f"   {soort:30}: {len(examples):4d} items")
                if len(examples) > 0 and examples[0]['onderwerp'] != 'Geen onderwerp...':
                    print(f"      Voorbeeld: {examples[0]['onderwerp']}")
            
            # Zoek specifiek naar wetten en amendementen
            print(f"\n🔍 Stap 2: Zoek naar Wetten en Amendementen")
            
            wet_types = [soort for soort in soorten.keys() if 'wet' in soort.lower()]
            amendement_types = [soort for soort in soorten.keys() if 'amendement' in soort.lower()]
            
            print(f"   📝 Wet-gerelateerde types: {wet_types}")
            print(f"   📝 Amendement-gerelateerde types: {amendement_types}")
            
            # Toon voorbeelden van wetten
            for wet_type in wet_types:
                if wet_type in soorten:
                    print(f"\n   🏛️ {wet_type} voorbeelden:")
                    for i, voorbeeld in enumerate(soorten[wet_type][:3]):
                        print(f"      {i+1}. {voorbeeld['titel'] or 'Geen titel'}")
                        print(f"         {voorbeeld['onderwerp']}")
            
            # Toon voorbeelden van amendementen  
            for amend_type in amendement_types:
                if amend_type in soorten:
                    print(f"\n   📝 {amend_type} voorbeelden:")
                    for i, voorbeeld in enumerate(soorten[amend_type][:3]):
                        print(f"      {i+1}. {voorbeeld['titel'] or 'Geen titel'}")
                        print(f"         {voorbeeld['onderwerp']}")
                        
            return soorten
            
        else:
            print(f"   ❌ API fout: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {}

def investigate_activiteit_for_stemverklaringen():
    """Onderzoek of Activiteit entities stemverklaringen bevatten"""
    
    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
    
    print(f"\n🗣️ ACTIVITEIT ONDERZOEK VOOR STEMVERKLARINGEN")
    print("=" * 50)
    
    try:
        # Haal Activiteit records op die mogelijk stemverklaringen zijn
        response = requests.get(f"{base_url}/Activiteit?$top=500&$orderby=GewijzigdOp desc")
        
        if response.status_code == 200:
            data = response.json()
            activiteiten = data.get('value', [])
            
            print(f"   ✅ Opgehaald: {len(activiteiten)} Activiteit records")
            
            # Analyseer Activiteit types
            activiteit_soorten = {}
            for act in activiteiten:
                soort = act.get('Soort', 'Onbekend')
                if soort not in activiteit_soorten:
                    activiteit_soorten[soort] = []
                activiteit_soorten[soort].append(act)
            
            print(f"\n📋 Activiteit types ({len(activiteit_soorten)}):")
            for soort, examples in activiteit_soorten.items():
                print(f"   {soort:40}: {len(examples):3d} items")
            
            # Zoek naar stemverklaring-gerelateerde activiteiten
            stemverklaring_types = []
            for soort in activiteit_soorten.keys():
                if any(word in soort.lower() for word in ['stem', 'verklar', 'motivat', 'toelicht']):
                    stemverklaring_types.append(soort)
            
            print(f"\n🎯 Mogelijk stemverklaring-gerelateerd: {stemverklaring_types}")
            
            # Toon voorbeelden
            for stem_type in stemverklaring_types[:3]:
                if stem_type in activiteit_soorten:
                    print(f"\n   🗣️ {stem_type}:")
                    for i, act in enumerate(activiteit_soorten[stem_type][:2]):
                        print(f"      {i+1}. {act.get('Onderwerp', 'Geen onderwerp')[:80]}...")
                        
            return activiteit_soorten
            
        else:
            print(f"   ❌ API fout: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {}

if __name__ == "__main__":
    print("🔍 COMPLETE API DATA TYPE VERKENNING")
    print("=" * 60)
    
    zaak_types = investigate_zaak_types()
    activiteit_types = investigate_activiteit_for_stemverklaringen()
    
    print(f"\n✅ SAMENVATTING:")
    print(f"   📋 Zaak types gevonden: {len(zaak_types)}")
    print(f"   🎭 Activiteit types gevonden: {len(activiteit_types)}")
    print(f"   🎯 Volgende stap: Collect wetten en amendementen via Zaak entities")