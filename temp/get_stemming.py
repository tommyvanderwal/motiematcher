import requests
import json

def get_stemming_for_besluit():
    besluit_id = "afcb9d90-db5a-4aff-b150-17e9339114d7"
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Stemming?$filter=Besluit_Id eq {besluit_id}&$expand=Besluit"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        print(f"Found {len(data.get('value', []))} Stemming records")
        if 'value' in data and data['value']:
            print(json.dumps(data['value'], indent=2, ensure_ascii=False)[:3000])
        else:
            print("No records found")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_stemming_for_besluit()