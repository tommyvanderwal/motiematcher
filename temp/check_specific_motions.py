import requests
import json

# Check specific motions from website vs our data (API only)

def check_specific_motions():
    motion_urls = [
        ('2025Z18621', 'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z18621&did=2025D43264'),
        ('2025Z18608', 'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z18608&did=2025D43239')
    ]

    # Load our data
    with open('bronnateriaal-onbewerkt/zaak_current/zaak_voted_motions_20251003_200218.json', 'r', encoding='utf-8') as f:
        zaak_data = json.load(f)

    print("=== Checking Specific Motions: Website vs API Data ===\n")

    for motion_nummer, url in motion_urls:
        print(f"🔍 Checking Motion: {motion_nummer}")
        print(f"   URL: {url}")

        # Find motion in our data
        motion_in_data = None
        for zaak in zaak_data:
            if zaak.get('Nummer') == motion_nummer:
                motion_in_data = zaak
                break

        if not motion_in_data:
            print(f"   ❌ Motion {motion_nummer} NOT found in our dataset")
            continue

        print(f"   ✅ Motion found in dataset")
        print(f"   Title: {motion_in_data.get('Titel', 'No title')[:80]}...")

        # Get decisions for this motion via API expansion
        zaak_id = motion_in_data['Id']
        api_url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Zaak({zaak_id})?$expand=Besluit($expand=Stemming)"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                api_data = response.json()

                besluiten = api_data.get('Besluit', [])
                print(f"   API Decisions: {len(besluiten)}")

                for besluit in besluiten:
                    stemmingen = besluit.get('Stemming', [])
                    if stemmingen:
                        print(f"   ✅ Has votes: {len(stemmingen)} parties")
                        print(f"   Decision: {besluit.get('BesluitSoort', 'Unknown')}")

                        # Show vote breakdown
                        voor_count = sum(1 for s in stemmingen if s.get('Soort') == 'Voor')
                        tegen_count = sum(1 for s in stemmingen if s.get('Soort') == 'Tegen')
                        print(f"   Result: {voor_count} Voor, {tegen_count} Tegen")

                        # Show sample party votes
                        print("   Sample votes:")
                        for stem in stemmingen[:5]:
                            partij = stem.get('ActorFractie', 'Unknown')
                            standpunt = stem.get('Soort', 'Unknown')
                            print(f"     {partij}: {standpunt}")
                        break  # Show only first decision with votes
                    else:
                        print(f"   ⚠️  Decision without votes: {besluit.get('BesluitSoort', 'Unknown')}")
            else:
                print(f"   ❌ API error: {response.status_code}")

        except Exception as e:
            print(f"   ❌ API request failed: {e}")

        print("-" * 60)

if __name__ == "__main__":
    check_specific_motions()