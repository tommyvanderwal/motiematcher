import requests
import json

def test_expansions():
    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/"

    # Test expansion on Stemming to get Besluit and further
    expansions = [
        "Stemming?$expand=Besluit($expand=Agendapunt($expand=Activiteit($expand=Zaak)))&$top=5",
        "Stemming?$expand=Besluit($expand=Zaak)&$top=5",
        "Besluit?$expand=Agendapunt($expand=Zaak)&$top=5",
        "Agendapunt?$expand=Zaak&$top=5",
        "Zaak?$expand=Besluit($expand=Stemming)&$filter=Nummer eq '2025Z13886'",
    ]

    for query in expansions:
        url = f"{base_url}{query}"
        print(f"\nTesting: {query}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if 'value' in data:
                records = data['value']
                print(f"Got {len(records)} records")
                if records:
                    print(json.dumps(records[0], indent=2, ensure_ascii=False)[:1000])
            else:
                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_expansions()