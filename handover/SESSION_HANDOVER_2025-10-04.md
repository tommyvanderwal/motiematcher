# Motiematcher Project Status – Session Handover
**Date:** October 4, 2025  
**Context:** Doorstart naar echte moties + volledige stemdata voor de huidige Kamertermijn

---

## Snapshot (4 okt 2025)
- ✅ **Ruwe dataset op orde**: Alle entiteiten staan onder `bronmateriaal-onbewerkt/` met `current/` snapshots voor zaak, besluit en stemming (Dec 2023 → heden)
- ✅ **Document download route bevestigd**: `DocumentPublicatie(<id>)/Resource` levert de volledige XML-motietekst; getest met besluit `93c64c34-fc1e-4de5-b812-66f5226cacde`
- ✅ **Filter regressie opgelost**: Gebruik `$filter=Id eq <guid>` (zonder `guid'…'`) om 400-fouten te vermijden
- 🚧 **Processed dataset ontbreekt**: Nog geen verwerkte set met ≥5 echte moties (tekst + stemmingen + links)
- 🚧 **FastAPI UI wacht op data**: `app/main_simple.py` draait lokaal, maar toont nog demo-data (`final_linked_data.json`)

---

## Belangrijkste Resultaten van Vandaag
1. **Data housekeeping** – Directories opgeschoond en genormaliseerd (`bronmateriaal-onbewerkt/current/...`).
2. **API-onderzoek** – Werkende `$expand` keten vastgesteld: `Besluit → Zaak.Document → HuidigeDocumentVersie.DocumentPublicatie`.
3. **Resource download** – XML payload (5.2 KB) opgehaald en gelogd via `DocumentPublicatie(<id>)/Resource`; snippet in `temp/test_fetch_decision.py`.
4. **Documentatie** – Alle kern-MD bestanden bijgewerkt (architectuur, data kwaliteit, linking, lessons, voting data).

---

## Kritieke Issues & Risks
| Thema | Status | Opmerking |
|-------|--------|-----------|
| Verwerkte dataset | 🔴 Blokkerend | Geen `processed/` JSON met echte moties → UI blijft demo |
| XML parsing | 🟠 In planning | Resource geeft XML zonder HTML; parsing/cleanup nodig |
| API wijzigingen | 🟠 Gecontroleerd | 400-fouten bij oude guid-filter syntax; scripts moeten geüpdatet blijven |
| Link validatie | 🟢 Opgelost | HTML entity fix (`&amp;` → `&`) werkt, fallback zoeklinks blijven actief |

---

## Prioriteiten voor Volgende Sessie
1. **Pilot ETL** – Bouw een script (bijv. `data-processing/create_processed_dataset.py`) dat:
   - Minimaal 5 moties selecteert (recente besluiten met volledige stemming)
   - Via de bevestigde route de XML tekst downloadt en omzet naar clean HTML/tekst
   - Stemuitslagen (partijniveau) + metadata (datum, besluitstatus, officiële links) bundelt in `data/processed/moties_pilot.json`
2. **Caching-strategie** – Leg de opgehaalde XML-bestanden vast in `data/processed/resources/` zodat herhaalde runs geen extra API calls nodig hebben.
3. **FastAPI aansluiten** – Pas `app/main_simple.py` aan om het nieuwe bestand te serveren; maak een togglestand voor “pilot dataset vs. volledige productie”.
4. **Validatie** – Controleer handmatig of de motieteksten overeenkomen met de officiële Tweede Kamer pagina en of alle stemmingen compleet zijn.

---

## Relevante Bestanden & Scripts
- `temp/test_fetch_decision.py` – Proof-of-concept voor Besluit → DocumentPublicatie → Resource flow
- `ARCHITECTURE_AND_LESSONS.md` – Bijgewerkte architectuur & next steps (4 okt)
- `DATA_QUALITY_ASSESSMENT.md` – Nieuwe workflow, risico’s en XML download stappen
- `DATA_STRUCTURE_AND_LINKING.md` – Volledig overzicht van entiteiten, koppelingen en filterwijziging
- `CURRENT_PARLIAMENT_VOTING_DATA.md` – Snapshot van huidige dataset + nieuwe bevindingen
- `LESSONS_LEARNED.md` – Samenvatting van alle technische inzichten (inclusief resource call)

---

## Data Locaties (okt 2025)
```
bronmateriaal-onbewerkt/
├── current/
│   ├── zaak_current/zaak_voted_motions_20251003_200218.json
│   ├── besluit_current/besluit_voted_motions_20251003_200218.json
│   └── stemming_current/stemming_voted_motions_20251003_200218.json
├── document/...
├── stemming_complete/...
└── comprehensive_motion_*.json (oude samengestelde dumps)
```

**Nog te creëren:** `data/processed/` (pilot outputs + gecachte XML’s)

---

## Quick Reference – Werkende Besluit Query
```python
BASE_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
params = {
   '$filter': f"Id eq {besluit_id}",
   '$expand': 'Agendapunt($expand=Document),Zaak($expand=Document($expand=HuidigeDocumentVersie($expand=DocumentPublicatie))),Stemming'
}
resp = requests.get(f"{BASE_URL}/Besluit", params=params, timeout=30)
publication_id = resp.json()['value'][0]['Zaak'][0]['Document'][0]['HuidigeDocumentVersie']['DocumentPublicatie'][0]['Id']
xml = requests.get(f"{BASE_URL}/DocumentPublicatie({publication_id})/Resource", timeout=30).text
```

---

## Handige Checklijst voor Morgen
- [ ] Script skeleton maken voor pilot ETL (met try/except + logging)
- [ ] `xmltodict` of vergelijkbare parser gebruiken om tekst uit XML te halen
- [ ] Output-schema definiëren (titel, volledige tekst, stemmen per partij, links, metadata)
- [ ] Nieuwe JSON in `data/processed/` leggen en versie-tag toevoegen
- [ ] FastAPI routes updaten + smoke-test (`run_web_test.py`)
- [ ] Documenteer resultaten & openstaande vragen

---

**Slotopmerking:** Alles staat klaar om echte moties te gaan serveren. Zolang we de pilot dataset neerzetten en het Resource-pad automatiseren, kan de webapp los van de oude demo-data. Veel succes morgen! 💪
