import requests
import json

# Query for recent motions (Zaak with Soort=Motie)
url = 'https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Zaak?$filter=Soort eq \'Motie\' and GewijzigdOp gt 2024-01-01T00:00:00Z&$top=5&$orderby=GewijzigdOp desc'
response = requests.get(url)
data = response.json()

print('Found motions:')
for zaak in data['value']:
    print(f"ID: {zaak['Id']}, Nummer: {zaak['Nummer']}, Titel: {zaak['Titel'][:50]}...")