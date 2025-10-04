import requests
from pprint import pprint

BASE_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"

def fetch(decision_id: str):
    resp = requests.get(
        f"{BASE_URL}/Besluit",
        params={
            '$filter': f"Id eq {decision_id}",
            '$expand': 'Agendapunt($expand=Document),Zaak($expand=Document($expand=HuidigeDocumentVersie($expand=DocumentPublicatie,DocumentPublicatieMetadata)),ZaakActor),Stemming',
        },
        timeout=30,
    )
    print(resp.url)
    resp.raise_for_status()
    data = resp.json()
    items = data.get('value', [])
    print('count', len(items))
    if items:
        pprint(list(items[0].keys()))
        return items[0]
    return None

if __name__ == '__main__':
    decision_id = "93c64c34-fc1e-4de5-b812-66f5226cacde"
    try:
        data = fetch(decision_id)
        if data:
            print('Keys available:', list(data.keys()))
            agendapunt = data.get('Agendapunt')
            if agendapunt:
                print('Agendapunt keys:', list(agendapunt.keys()))
                docs = agendapunt.get('Document')
                if isinstance(docs, list):
                    print('Agendapunt documents:', len(docs))
            zaak = data.get('Zaak')
            if isinstance(zaak, list):
                print('Zaak count:', len(zaak))
                if zaak:
                    print('Zaak[0] keys:', list(zaak[0].keys()))
                    docs = zaak[0].get('Document')
                    if isinstance(docs, list):
                        print('Zaak documents:', len(docs))
                        if docs:
                            print('First document keys:', list(docs[0].keys()))
                            huidige = docs[0].get('HuidigeDocumentVersie')
                            if huidige:
                                print('HuidigeDocumentVersie keys:', list(huidige.keys()))
                                pub = huidige.get('DocumentPublicatie')
                                if isinstance(pub, list):
                                    print('DocumentPublicaties:', len(pub))
                                    if pub:
                                        print('First publication keys:', list(pub[0].keys()))
                                        pub_id = pub[0].get('Id')
                                        print('First publication URL:', pub[0].get('Url'))
                                        if pub_id:
                                            resource_url = f"{BASE_URL}/DocumentPublicatie({pub_id})/Resource"
                                            try:
                                                resource_resp = requests.get(resource_url, timeout=30)
                                                print('Resource status:', resource_resp.status_code)
                                                print('Resource headers:', dict(resource_resp.headers))
                                                if resource_resp.ok:
                                                    snippet = resource_resp.text[:400]
                                                    print('Resource snippet:', snippet[:400].replace('\n', ' ')[:400])
                                            except Exception as resource_exc:
                                                print('Resource fetch failed:', resource_exc)
                                pub_meta = huidige.get('DocumentPublicatieMetadata')
                                if isinstance(pub_meta, list):
                                    print('DocumentPublicatieMetadata:', len(pub_meta))
                                    if pub_meta:
                                        print('First metadata keys:', list(pub_meta[0].keys()))
                                        print('First metadata URL:', pub_meta[0].get('Url'))
            stemmingen = data.get('Stemming')
            if isinstance(stemmingen, list):
                print('Stemmingen count:', len(stemmingen))
        else:
            print('No data returned')
    except Exception as exc:
        print('Error:', exc)
