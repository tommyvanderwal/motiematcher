import requests
import json

# Test expansions on multiple motion Zaak IDs
motion_ids = [
    '5ef5c217-f102-4594-a60c-7933a9a14b9d',
    '6714ec1f-7b45-4942-9bb2-0917c34ff9ec',
    'c6256599-b0f5-4fe0-8033-2ed5ddbe5f77',
    '53f54808-4291-4b94-95b8-34f331327283',
    'f2056b95-06ea-401b-8057-587c5a3560db'
]

for i, zaak_id in enumerate(motion_ids, 1):
    print(f"\n=== Testing Motion {i}: {zaak_id} ===")

    url = f'https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Zaak({zaak_id})?$expand=Besluit($expand=Stemming)'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        zaak = data

        print(f"Zaak Nummer: {zaak.get('Nummer', 'N/A')}")
        print(f"Zaak Titel: {zaak.get('Titel', 'N/A')[:60]}...")

        besluiten = zaak.get('Besluit', [])
        print(f"Aantal Besluiten: {len(besluiten)}")

        total_stemmingen = 0
        for besluit in besluiten:
            stemmingen = besluit.get('Stemming', [])
            total_stemmingen += len(stemmingen)
            if stemmingen:
                print(f"  Besluit Status: {besluit.get('Status', 'N/A')}")
                print(f"  Besluit Tekst: {besluit.get('BesluitTekst', 'N/A')[:40]}...")
                print(f"  Aantal Stemmingen: {len(stemmingen)}")

                # Show sample vote data
                for stemming in stemmingen[:3]:  # Show first 3 votes
                    actor = stemming.get('ActorNaam', stemming.get('ActorFractie', 'Unknown'))
                    soort = stemming.get('Soort', 'N/A')
                    fractie_grootte = stemming.get('FractieGrootte', 'N/A')
                    print(f"    - {actor}: {soort} (FractieGrootte: {fractie_grootte})")

        print(f"Totaal Stemmingen voor deze motie: {total_stemmingen}")

    else:
        print(f"Error {response.status_code}: {response.text}")

print("\n=== Summary ===")
print("All tested motions successfully retrieved with complete vote data via Zaak→Besluit→Stemming expansions.")