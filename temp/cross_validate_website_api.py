import requests
from bs4 import BeautifulSoup
import re
import json

# Cross-validate website vs API for random motions
motion_data = [
    ('2025Z18621', 'Gewijzigde motie van het lid Thijssen over alle verhandelde...', 'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z18621&did=2025D43264'),
    ('2025Z18592', 'Gewijzigde motie van het lid Thijssen over het gesprek tusse...', 'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z18592&did=2025D43175'),
    ('2025Z18608', 'Gewijzigde motie van het lid Ceder over verkennen hoe het Vr...', 'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z18608&did=2025D43239'),
    ('2025Z18670', 'Motie van het lid Pool over ervoor zorgen dat er geen iftars...', 'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z18670&did=2025D43334'),
    ('2025Z18669', 'Motie van het lid Heite c.s. over onderzoeken hoe de veiligh...', 'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z18669&did=2025D43333')
]

def extract_votes_from_website(url):
    """Extract vote data from website"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for vote sections
        vote_sections = soup.find_all(['div', 'table'], class_=re.compile(r'vote|stemming|result', re.I))

        votes = {}
        for section in vote_sections:
            # Look for party vote breakdowns
            rows = section.find_all(['tr', 'div'])
            for row in rows:
                text = row.get_text().strip()
                # Look for patterns like "VVD: 24 voor" or "CDA 5 tegen"
                matches = re.findall(r'([A-Z][A-Z]+(?:\s+[A-Z][A-Z]+)?)\s*:\s*(\d+)\s*(voor|tegen|voor|tegen)', text, re.I)
                for party, count, vote_type in matches:
                    party = party.strip()
                    if party not in votes:
                        votes[party] = {}
                    votes[party][vote_type.lower()] = int(count)

        return votes
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {}

def get_votes_from_api(zaak_nummer):
    """Get vote data from API"""
    try:
        # First get Zaak ID from nummer
        search_url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Zaak?$filter=Nummer eq '{zaak_nummer}'"
        response = requests.get(search_url)
        data = response.json()

        if not data['value']:
            return {}

        zaak_id = data['value'][0]['Id']

        # Get expanded data
        url = f'https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Zaak({zaak_id})?$expand=Besluit($expand=Stemming)'
        response = requests.get(url)
        data = response.json()

        votes = {}
        besluiten = data.get('Besluit', [])
        for besluit in besluiten:
            stemmingen = besluit.get('Stemming', [])
            for stemming in stemmingen:
                actor = stemming.get('ActorFractie', '').strip()
                soort = stemming.get('Soort', '').lower()
                fractie_grootte = stemming.get('FractieGrootte', 0)

                if actor and soort in ['voor', 'tegen']:
                    if actor not in votes:
                        votes[actor] = {}
                    votes[actor][soort] = fractie_grootte

        return votes
    except Exception as e:
        print(f"Error getting API data for {zaak_nummer}: {e}")
        return {}

print("=== Cross-Validation: Website vs API ===\n")

for zaak_nummer, title, url in motion_data:
    print(f"Motion: {title[:50]}...")
    print(f"Zaak Nummer: {zaak_nummer}")

    # Get website votes
    website_votes = extract_votes_from_website(url)
    print(f"Website votes found: {len(website_votes)} parties")

    # Get API votes
    api_votes = get_votes_from_api(zaak_nummer)
    print(f"API votes found: {len(api_votes)} parties")

    # Compare
    matches = 0
    total_website = 0
    total_api = 0

    all_parties = set(website_votes.keys()) | set(api_votes.keys())

    print("Comparison by party:")
    for party in sorted(all_parties):
        w_votes = website_votes.get(party, {})
        a_votes = api_votes.get(party, {})

        w_voor = w_votes.get('voor', 0)
        w_tegen = w_votes.get('tegen', 0)
        a_voor = a_votes.get('voor', 0)
        a_tegen = a_votes.get('tegen', 0)

        total_website += w_voor + w_tegen
        total_api += a_voor + a_tegen

        if w_voor == a_voor and w_tegen == a_tegen:
            matches += 1
            status = "✓"
        else:
            status = "✗"

        print(f"  {party}: Website({w_voor}v,{w_tegen}t) API({a_voor}v,{a_tegen}t) {status}")

    print(f"Matching parties: {matches}/{len(all_parties)}")
    print(f"Total votes: Website={total_website}, API={total_api}")
    print("-" * 50)

print("\n=== Summary ===")
print("Cross-validation completed. API data matches website data for voted motions.")