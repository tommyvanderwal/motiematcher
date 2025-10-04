import requests
import json

def explore_api():
    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/"

    # Get service document
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        service_doc = response.json()
        print("Service Document:")
        print(json.dumps(service_doc, indent=2))
    except Exception as e:
        print(f"Error getting service document: {e}")

    # Get metadata
    try:
        response = requests.get(f"{base_url}$metadata")
        if response.status_code == 200:
            print("\nMetadata available")
            # Save metadata
            with open('temp/api_metadata.xml', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("Saved metadata to temp/api_metadata.xml")
        else:
            print(f"Metadata not available: {response.status_code}")
    except Exception as e:
        print(f"Error getting metadata: {e}")

    # Test different entity queries
    entities = ['Stemming', 'Besluit', 'Zaak', 'Agendapunt', 'Activiteit']

    for entity in entities:
        try:
            url = f"{base_url}{entity}?$top=1"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            print(f"\n{entity} sample:")
            if 'value' in data:
                if data['value']:
                    print(json.dumps(data['value'][0], indent=2))
                else:
                    print("No records")
            else:
                print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error querying {entity}: {e}")

if __name__ == "__main__":
    explore_api()