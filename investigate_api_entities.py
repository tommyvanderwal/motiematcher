import requests
import json

def investigate_api_endpoints():
    """Onderzoek welke andere data types beschikbaar zijn via de Dutch Parliament API"""
    
    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
    
    print("🔍 API ENDPOINTS VERKENNING")
    print("=" * 50)
    
    # Eerst bekijken welke entities er zijn
    print("📋 Stap 1: Onderzoek beschikbare entities")
    try:
        response = requests.get(f"{base_url}/$metadata")
        if response.status_code == 200:
            metadata = response.text
            print("   ✅ Metadata opgehaald - te complex voor directe analyse")
            print("   📝 Proberen via directe entity calls...")
        else:
            print(f"   ❌ Metadata fout: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Metadata error: {e}")
    
    # Test verschillende entity types
    entities_to_test = [
        "Zaak",           # Bekend: Moties, Wetten, etc
        "Wet",            # Mogelijk: Wetten als aparte entiteit
        "Amendement",     # Mogelijk: Amendementen
        "Stemverklaring", # Mogelijk: Stemverklaringen
        "Stemming",       # Bekend: Stemmingen
        "Besluit",        # Bekend: Besluiten
        "Document",       # Bekend: Documenten
        "Activiteit",     # Mogelijk: Parlementaire activiteiten
        "Persoon",        # Mogelijk: Parlementariërs
        "Fractie",        # Mogelijk: Partijen
        "Vergadering",    # Mogelijk: Vergaderingen
        "Agendapunt",     # Bekend: Agenda items
    ]
    
    print(f"\n🧪 Stap 2: Test {len(entities_to_test)} mogelijke entities")
    
    available_entities = []
    
    for entity in entities_to_test:
        try:
            # Probeer eerste 1 record op te halen
            test_url = f"{base_url}/{entity}?$top=1"
            response = requests.get(test_url)
            
            if response.status_code == 200:
                data = response.json()
                if 'value' in data and len(data['value']) > 0:
                    sample_keys = list(data['value'][0].keys())
                    available_entities.append(entity)
                    print(f"   ✅ {entity:15}: {len(sample_keys)} properties")
                elif 'value' in data and len(data['value']) == 0:
                    available_entities.append(entity)
                    print(f"   ⚠️ {entity:15}: Entity bestaat maar is leeg")
                else:
                    print(f"   ❌ {entity:15}: Onbekende response structuur")
            else:
                print(f"   ❌ {entity:15}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {entity:15}: Error {e}")
    
    print(f"\n📊 Stap 3: Details van beschikbare entities")
    
    for entity in available_entities[:5]:  # Eerste 5 voor details
        try:
            # Haal één sample op voor structuur analyse
            test_url = f"{base_url}/{entity}?$top=1"
            response = requests.get(test_url)
            
            if response.status_code == 200:
                data = response.json()
                if 'value' in data and len(data['value']) > 0:
                    sample = data['value'][0]
                    print(f"\n🔍 {entity} eigenschappen:")
                    
                    # Zoek interessante properties
                    interesting_props = []
                    for key, value in sample.items():
                        if any(word in key.lower() for word in ['soort', 'type', 'naam', 'titel', 'onderwerp']):
                            interesting_props.append(f"{key}: {value}")
                    
                    for prop in interesting_props[:5]:  # Max 5 interessante
                        print(f"     {prop}")
                        
        except Exception as e:
            print(f"   ❌ Error bij {entity}: {e}")
    
    print(f"\n🎯 CONCLUSIE:")
    print(f"   📋 Beschikbare entities: {', '.join(available_entities)}")
    print(f"   📝 Voor verder onderzoek: {len(available_entities)} entities gevonden")
    
    return available_entities

if __name__ == "__main__":
    entities = investigate_api_endpoints()
    print(f"\n✅ API verkenning voltooid. Gevonden entities: {len(entities)}")