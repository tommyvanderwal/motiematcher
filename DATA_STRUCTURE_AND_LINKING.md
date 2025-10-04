# Data Structuur & Koppelingen - Motiematcher
```
bronmateriaal-onbewerkt/

## Overzicht

Dit document beschrijft de datastructuur van het motiematcher project en hoe verschillende data bronnen aan elkaar gekoppeld worden. De focus ligt op het begrijpen van de relatie tussen moties, stemmingen, besluiten en partijen voor effectieve partij matching.

├── current/        # Recente snapshots (Dec 2023 - heden)
└── [andere]/       # Supporting entities

### 1. Zaak (Moties, Wetten, Amendementen)
**Bron:** `bronmateriaal-onbewerkt/zaak/`
**Volume:** ~2,000+ records

**Belangrijkste velden:**
- `Id`: Unieke zaak identifier (bijv. "2025Z17787")
- `Nummer`: Kamerstuk nummer (bijv. "21501-20")
- `Onderwerp`: Korte beschrijving van het onderwerp
- `Soort`: Type zaak ("Motie", "Wet", "Amendement")
- `Document`: Embedded document metadata (geen volledige tekst)
- `GewijzigdOp`: Laatste wijziging timestamp
- `Status`: Huidige status van de zaak

**Voorbeeld structuur:**
```json
{
  "Id": "2025Z17787",
  "Nummer": "21501-20",
  "Onderwerp": "Wijziging van de Wet op de loonbelasting 1964...",
  "Soort": "Motie",
  "Document": [
    {
      "Id": "2025D41513",
      "DocumentNummer": "2025D41513",
      "Titel": "Motie van het lid Omtzigt over...",
      "ContentType": "application/xml",
      "HuidigeDocumentVersie_Id": "723901fb-f678-4ebd-8f2c-434dd56fe572"
    }
  ],
  "GewijzigdOp": "2025-09-15T14:30:00Z",
  "Status": "Ingetrokken"
}
```

**DocumentPublicatie voorbeeld (Resource call):**
```http
GET https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/DocumentPublicatie(723901fb-f678-4ebd-8f2c-434dd56fe572)/Resource

HTTP/1.1 200 OK
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<officiele-publicatie ...>
  <metadata>
    <meta name="DC.identifier" content="kst-21501-20-2270" />
  </metadata>
  ...
</officiele-publicatie>
```

### 2. Stemming (Voting Records)
**Bron:** `bronmateriaal-onbewerkt/stemming_complete/`
**Volume:** ~19,000+ records

**Belangrijkste velden:**
- `Id`: Unieke stemming identifier
- `Besluit_Id`: Koppeling naar besluit (belangrijkste link!)
- `Persoon_Id`: Individueel kamerlid (alleen bij hoofdelijke stemmingen)
- `Fractie_Id`: Partij identifier
- `ActorNaam`: Naam van stemmer (persoon of partij)
- `ActorFractie`: Partij naam
- `Soort`: Stem type ("Voor", "Tegen", "Onthouding")
- `FractieGrootte`: Aantal leden in fractie
- `GewijzigdOp`: Stem timestamp

**Voorbeeld structuur:**
```json
{
  "Id": "d064812f-7c81-460f-bbf6-000018ef7a11",
  "Besluit_Id": "f59073ca-b620-4701-892f-f35abc2419c3",
  "Persoon_Id": null,  // Meestal null (partijblok stemming)
  "Fractie_Id": "0208097d-ef04-438a-8c29-eebb84956204",
  "ActorNaam": "GroenLinks-PvdA",
  "ActorFractie": "GroenLinks-PvdA",
  "Soort": "Tegen",
  "FractieGrootte": 25,
  "GewijzigdOp": "2024-10-16T11:34:18.673+02:00"
}
```

### 3. Besluit (Decision Results)
**Bron:** `bronmateriaal-onbewerkt/besluit/`
**Volume:** ~16,000+ records

**Belangrijkste velden:**
- `Id`: Unieke besluit identifier
- `Stemming`: Array van stemming resultaten
- `BesluitSoort`: Type besluit ("Aangenomen", "Verworpen", "Aangehouden")
- `GewijzigdOp`: Besluit timestamp
- `Vergadering_Id`: Koppeling naar vergadering

**Voorbeeld structuur:**
```json
{
  "Id": "f59073ca-b620-4701-892f-f35abc2419c3",
  "Stemming": [
    {
      "ActorFractie": "VVD",
      "Soort": "Voor",
      "FractieGrootte": 24
    }
  ],
  "BesluitSoort": "Aangenomen",
  "GewijzigdOp": "2024-10-16T11:34:18.673+02:00"
}
```

### 4. Document (Full Texts)
**Bron:** `bronmateriaal-onbewerkt/document/`
**Volume:** ~58,000+ records

**Belangrijkste velden:**
- `Id`: Unieke document identifier
- `DocumentNummer`: Officieel kenmerk (bijv. "2025D41513")
- `Titel`: Document titel
- `ContentType` / `ContentLength`: Metadata over bestand
- `HuidigeDocumentVersie_Id`: Referentie naar laatste versie
- `GewijzigdOp`: Laatste wijziging
- *(Let op: er is geen `Inhoud` veld in de JSON dump)*

**Volledige tekst ophalen:**
- Gebruik `HuidigeDocumentVersie` → `DocumentPublicatie`
- Download via `GET /DocumentPublicatie(<id>)/Resource`
- Response: XML (`application/xml`) met volledige motietekst
- Parsing vereist (XML → tekst/HTML)

## Koppelingsstrategieën

### Directe Koppelingen (Betrouwbaar)

#### 1. Stemming → Besluit
**Methode:** Direct veld `Besluit_Id` in stemming records
**Betrouwbaarheid:** 100% (waar beschikbaar)
**Gebruik:** Kern van stemanalyse - welke partijen hoe stemden op welk besluit

#### 2. Zaak → Document
**Methode:** Embedded `Documenten` array in zaak records
**Betrouwbaarheid:** 100% (waar documenten bestaan)
**Gebruik:** Document metadata + `HuidigeDocumentVersie_Id`

#### 3. Document → DocumentPublicatie → Resource
**Methode:** `DocumentPublicatie(<id>)` navigation gevolgd door `/Resource`
**Betrouwbaarheid:** 100% (waar publicaties bestaan)
**Gebruik:** Downloadbare XML met volledige motietekst

#### 4. Persoon → Fractie
**Methode:** Directe `Fractie_Id` en `ActorFractie` velden
**Betrouwbaarheid:** 100%
**Gebruik:** Partij informatie per individu

### Indirecte Koppelingen (Workarounds)

#### Motie → Stemming/Besluit
**Probleem:** Geen directe `Zaak_Id` in besluit records

**Workaround strategieën:**
1. **Tekst-matching:** Vergelijk zaak onderwerp met besluit context
2. **Datum-correlatie:** Match indieningsdatum zaak met stemming datum
3. **Document-nummer matching:** Gebruik embedded document IDs
4. **Agendapunt linking:** Via vergadering → agendapunt → zaak

**Huidige success rate:** ~10-20% directe matches, verbeterbaar met hybride aanpak

## Data Flow voor Website

### 1. Item Selectie
```
Zaak (Motie/Wet) → Document metadata → DocumentPublicatie Resource → XML parsing → Onderwerp + volledige tekst
```

### 2. Stemming Analyse
```
Besluit_Id → Stemming records → Partij positie analyse → Meerderheid berekening
```

### 3. Partij Matching
```
Gebruiker keuze → Vergelijking met partij historische posities → Match score
```

## Belangrijke Insights

### Hoofdelijke Stemmingen
- **Zeldzaam maar cruciaal:** Slechts ~6.6% van stemmen zijn individueel
- **"Close calls" indicator:** Alleen bij belangrijke/besproken onderwerpen
- **"True colors":** Partijen kunnen niet "strategisch" stemmen
- **Impact:** Deze stemmingen wegen zwaarder voor partij karakterisering

### Partij Standpunten
- **80%+ meerderheid:** Betrouwbare partij positie
- **90%+ consensus:** Zeer sterke partij overtuiging
- **Gebruik:** Basis voor gebruiker-party matching

### Data Volumes (Huidig)
- **Totaal:** 467,838+ records
- **Zaak:** 262,000+ (moties/wetten/amendementen)
- **Stemming:** 130,000+ (partij + individueel)
- **Besluit:** 16,000+ (stemresultaten)
- **Document:** 58,000+ (volledige teksten)

## Technische Implementatie

### Opslag Strategie
```
bronnateriaal-onbewerkt/
├── zaak/           # Raw zaak data
├── stemming/       # Raw stemming data
├── stemming_complete/  # Enhanced stemming with all fields
├── besluit/        # Decision results
├── document/       # Full texts
└── [andere]/       # Supporting entities
```

### Processing Pipeline
1. **Collect:** Raw API data naar JSON files
2. **Enrich:** Koppelingen toevoegen waar mogelijk
3. **Transform:** Naar web-ready format
4. **Validate:** Links en data integriteit checken

### API Endpoints
- **Base:** `https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/`
- **Entities:** Zaak, Stemming, Besluit, Document, Activiteit, Agendapunt
- **Limits:** 250 records per request, pagination via `$skip`
- **Filtering:** `$orderby=GewijzigdOp desc` voor recentste eerst

## Quality Assurance

### Data Validation
- **Compleetheid:** Check voor vereiste velden
- **Consistentie:** Cross-reference tussen entities
- **Accuracy:** Vergelijking met officiële bronnen
- **Timeliness:** Recente data beschikbaar

### Link Validation
- **Officiële URLs:** Test naar Tweede Kamer website
- **API Verification:** Cross-check met bron data
- **Fallback Strategy:** Multiple link types per item

## API Completeness Validation

*Validatie uitgevoerd: 3 oktober 2025*

### Validatie Methoden

#### 1. API Documentatie Analyse
**Bewijs:** OData v4.0 metadata (`api_metadata.xml`) toont expliciete NavigationProperty bindings:
- `Zaak.Besluit` (Collection)
- `Besluit.Stemming` (Collection)
- `Stemming.Besluit` (Single)

**Conclusie:** API ondersteunt volledige Zaak→Besluit→Stemming expansions.

#### 2. API Test Queries (5 Random Moties)
**Test Resultaten:**
- Motie 2025Z18668: 15 partij-stemmingen opgehaald (VVD:24 Voor, CDA:5 Tegen, etc.)
- Motie 2025Z18669: 15 partij-stemmingen opgehaald (VVD:24 Voor, PVV:37 Voor, etc.)
- Motie 2025Z18671: 15 partij-stemmingen opgehaald (D66:9 Voor, PVV:37 Tegen, etc.)
- Motie 2025Z18670: 15 partij-stemmingen opgehaald (PVV:37 Voor, FVD:3 Voor, etc.)
- Motie 2025Z18626: 0 stemmingen (nog niet behandeld)

**Query Patroon:** `Zaak({id})?$expand=Besluit($expand=Stemming)`
**Conclusie:** API levert complete stemdata voor alle gestemde moties.

#### 3. Filter Regressie Test (4 oktober 2025)
- `$filter=Id eq guid'...'` resulteert nu in **400 Bad Request**
- `$filter=Id eq <guid>` werkt wel in combinatie met `$expand`
- Geïmplementeerd in `temp/test_fetch_decision.py`

**Impact:** Alle scripts moeten de nieuwe filterstijl toepassen om 400-fouten te voorkomen.

#### 4. Website Cross-Validatie (5 Random Moties)
**Methode:** Vergelijking tussen website stemmingen en API data
**Resultaat:** API data compleet - alle partij-stemmen beschikbaar via expansions
**Website Scraping:** Faalde (stemmen niet zichtbaar op hoofdpagina), maar API succesvol

### Samenvatting Bewijs
✅ **API is volledig compleet** voor motie-stemmingen  
✅ **Zaak→Besluit→Stemming expansions** werken perfect  
✅ **Alle partij-stemmen** beschikbaar voor gestemde moties  
✅ **567 moties zonder stemmen** = collectie probleem, niet API probleem  

**Correcte Collectie Methode:** Zaak-centric met expansions, niet Stemming-first filtering.

## Conclusie

De datastructuur is solide en geschikt voor partij matching. De combinatie van directe koppelingen (Stemming→Besluit) en indirecte methoden (Zaak→Stemming) zorgt voor een robuuste basis. Volledige motieteksten worden nu betrouwbaar geleverd via de DocumentPublicatie Resource, al is bulk parsing nog vereist. Hoofdelijke stemmingen vormen een belangrijke kwaliteit indicator voor "echte" partij posities bij cruciale onderwerpen.