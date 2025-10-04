# 🏛️ **MOTIEMATCHER - ARCHITECTUUR & LESSEN OVERZICHT**

*Laatste update: 4 oktober 2025*

## 📋 **PROJECT OVERZICHT**

**Motiematcher** is een schaalbare website die Nederlandse politieke moties matcht met partij stemgedrag. Het platform helpt burgers om te zien hoe politieke partijen stemmen op verschillende onderwerpen, gebaseerd op parlementaire stemhistorie.

### 🎯 **Huidige Status**
- ✅ **Ruwe data consolidatie**: Volledige API dumps samengebracht onder `bronmateriaal-onbewerkt/` met `current/` snapshots voor moties, besluiten en stemmingen van de huidige Kamertermijn
- ✅ **Document download pad**: Volledige motieteksten bereikbaar via `DocumentPublicatie(<id>)/Resource` (XML payload bevestigd op 4 okt 2025)
- ✅ **Linkstrategie**: HTML-entity fixes en fallback zoeklinks blijven werken voor alle motievarianten
- 🚧 **Processed dataset**: ETL om ≥5 echte moties (tekst + stemmingen) te leveren is in uitvoering
- 📋 **Web Platform**: FastAPI prototype draait lokaal; wacht op nieuwe dataset voor productie wiring

---

## 🏗️ **ARCHITECTUUR OVERZICHT**

### **Fase 1: Data Collection & Enrichment** ✅ VOLTOOID

#### **Data Bronnen**
- **API**: `https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/`
- **Entities**: Zaak, Stemming, Besluit, Document, Activiteit, Agendapunt
- **Periode**: 30 dagen (September-Oktober 2025) - **gereed voor uitbreiding**
- **Document Resource**: `DocumentPublicatie(<id>)/Resource` retourneert de volledige XML van de motietekst (vergt losse follow-up call naast `$expand`)

#### **Data Volumes**
- **51,016 totaal records** (22.9 MB) in 30-daagse snapshot (baseline)
- **1,985 moties** (98.5% tekst coverage) in snapshot; full-term telling loopt
- **18,872 stemmingen** (9,435 gekoppeld aan besluiten) in snapshot
- **575 werkende Stemming-Besluit koppelingen** via snapshot scripts
- **75 wetten + 68 amendementen** in snapshot

#### **Opslag Structuur**
```
motiematcher/
├── bronmateriaal-onbewerkt/     # Raw API responses
│   ├── zaak/                    # Moties, wetten, amendementen
│   ├── stemming/               # Stemrecords per partij/persoon
│   ├── besluit/                # Besluit resultaten
│   ├── document/               # Volledige teksten
│   ├── agendapunt/            # Agenda items
│   └── activiteit/            # Parlementaire activiteiten
├── data-collection/           # ETL scripts
├── data-processing/          # Transformatie logica
└── ARCHITECTURE_AND_LESSONS.md  # Deze documentatie
```

### **Fase 2: Web Platform** 📋 GEPLAND

#### **Technologie Stack**
- **Backend**: FastAPI (Python) - hoge performance voor dynamische content
- **Frontend**: Vanilla HTML/CSS/JS - eenvoudige, snelle implementatie
- **Deployment**: AWS (EC2 + ELB) - schaalbaar voor 10+ servers
- **Static Assets**: S3 - media files, images, statische content

#### **Core Functionaliteit**
- **Motie Selectie**: Gebruikers kiezen positie op moties
- **Party Matching**: Match met historische stempatronen
- **Resultaten Sharing**: Shareable links naar resultaten
- **Real-time Data**: Directe links naar actuele parlementaire data

---

## 🎓 **MEEST RELEVANTE LESSEN GELEERD**

### **1. 🔧 API & Data Structuur**

#### **OData v4.0 Patterns**
```python
# Correcte API calls
base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/"
entities = ["Zaak", "Stemming", "Besluit", "Document", "Activiteit"]

# Pagination (250 records limit)
url = f"{base_url}/Stemming?$skip={skip}&$orderby=GewijzigdOp desc"
```

#### **Nieuwe Filter Syntax (okt 2025)**
```python
# Let op: de API accepteert geen guid-literals meer in filters
bad = "Id eq guid'93c64c34-fc1e-4de5-b812-66f5226cacde'"  # → 400 Bad Request
good = "Id eq 93c64c34-fc1e-4de5-b812-66f5226cacde"         # → 200 OK

params = {
	'$filter': good,
	'$expand': 'Agendapunt($expand=Document),Zaak($expand=Document,ZaakActor),Stemming'
}
resp = requests.get(f"{base_url}/Besluit", params=params, timeout=30)
```
*Bron: test uitgevoerd op 4 oktober 2025 (zie `temp/test_fetch_decision.py`).*

#### **Data Format Consistentie**
- **Directe JSON arrays** (geen OData wrapper)
- **UTF-8 encoding** essentieel voor Nederlandse karakters
- **Timestamped files** voor audit trail
- **Modulaire opslag** voor selectieve herverzameling

### **2. 📊 Data Koppeling Complexiteit**

#### **Directe Koppelingen** ✅
- **Stemming → Besluit**: 575 werkende koppelingen
- **Zaak → Document**: Embedded documenten voor volledige teksten
- **Persoon → Fractie**: Complete partij informatie
- **Document → Publicatie Resource**: `HuidigeDocumentVersie.DocumentPublicatie` + `DocumentPublicatie(<id>)/Resource` levert downloadbare XML

#### **Indirecte Koppelingen** ⚠️
- **Motie → Stemming**: Geen directe Zaak_Id in Besluit
- **Workarounds**: Tekst-matching, datum-correlatie, document-nummer matching
- **Les**: Niet alle relaties zijn direct beschikbaar - hybride aanpak nodig

### **3. 🔗 Link Generatie Strategie**

#### **Officiële Links** ✅
```python
# Directe links met stemuitslagen (voor oudere moties)
direct_link = f"https://www.tweedekamer.nl/kamerstukken/moties/detail?id={motie}&did={document}"

# Altijd werkende search links
search_link = f"https://www.tweedekamer.nl/zoeken?qry={motie}"
```

#### **HTML Entities Fix** 🚨 KRITIEK
```python
# VOOR (werkt NIET - 404 error):
"https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z17787&amp;did=2025D41513"

# NA (werkt WEL):
"https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z17787&did=2025D41513"
```

### **4. 🐛 Debugging & Error Handling**

#### **Veelvoorkomende Errors**
- **Tuple unpacking**: Altijd consistente return values
- **Unicode errors**: Expliciete UTF-8 encoding
- **API timeouts**: Retry logic met exponential backoff
- **HTML entities**: `&amp;` → `&` conversie

#### **Testing Strategy**
- **Mini-scripts** voor snelle iteratie (niet interactive Python)
- **Modulaire functies** voor herbruikbaarheid
- **Progress logging** voor lange runs
- **Sample testing** voor grote datasets

### **5. 📈 Performance & Schaalbaarheid**

#### **API Limits & Optimalisatie**
- **250 records per call** (hard limit)
- **Geen rate limiting** ervaren
- **0.5s sleep** tussen requests (courtesy)
- **Batch processing** voor grote volumes

#### **Data Processing**
- **JSON parsing**: Uitstekende performance
- **Memory efficient**: 22.9 MB past makkelijk
- **Pandas overkill**: Voor huidige volumes niet nodig
- **File-based opslag**: Snelle toegang, versioning mogelijk

### **6. 🏛️ Parlementaire Data Insights**

#### **Stemgedrag Patterns**
- **PVV**: Meest actief (193 stemmen)
- **GroenLinks-PvdA**: Meest eensgezind (Voor: 118/182)
- **VVD**: Meest kritisch (Tegen: 114/180)
- **15 actieve partijen** in huidige parlement

#### **Data Compleetheid**
- **98.5% motie teksten** beschikbaar
- **100% effectieve coverage** (embedded documenten)
- **Complete partij informatie** per stemming
- **Historische stemgeschiedenis** beschikbaar

### **7. 🔄 Development Workflow**

#### **Best Practices**
- **Modulaire scripts** voor verschillende fases
- **Timestamped output** voor reproduceerbaarheid
- **Error handling** in alle API calls
- **Documentation** tijdens development

#### **Version Control**
- **Git commits** na elke majeure stap
- **Betekenisvolle commit messages**
- **Separate branches** voor experimenten
- **Clean repository** zonder temporaries

### **8. 🎯 Product Strategy**

#### **Minimum Viable Product**
- **Motie browser** met teksten en links
- **Party position display** voor beschikbare data
- **Result sharing** via URLs
- **Data verification** naar officiële bronnen

#### **Scaling Strategy**
- **Larger dataset** (Dec 2023 - nu) voor betere matching
- **Hybrid matching** voor motie-stemming koppelingen
- **Progressive enhancement** van features

---

## 🚀 **VOLGENDE STAPPEN**

### **Immediate Actions**
1. **� Pilot Dataset**: Bouw ETL die ≥5 echte moties oplevert met volledige tekst, stemming per partij en metadata
2. **🧾 XML Parsing**: Zet `DocumentPublicatie` XML om naar schone tekst + HTML snippets voor weergave
3. **� Local Cache**: Sla opgehaalde resources herbruikbaar op (scheid `bronmateriaal-` en `verwerkt/` datasets)
4. **� Full Term Refresh**: Plan complete Dec 2023-heden collectie zodra pipeline staat

### **Web Platform Development**
1. **⚡ FastAPI Backend**: Sluit endpoints aan op nieuwe dataset zodra pilot klaar is
2. **🎨 Simple Frontend**: Ververs UI met echte motiecontent en downloadlinks
3. **☁️ AWS Deployment**: Voorbereiden maar pas deployen na dataset validatie
4. **📱 User Experience**: Integreer statusindicatoren voor teksten/stemmingen

### **Data Enhancement**
1. **🔍 Advanced Matching**: Combineer Zaak/Besluit routes + tekst matching voor breder bereik
2. **📚 Full Texts**: Schakel `DocumentPublicatie` resource harvesting in voor bulk moties
3. **🔗 Link Validation**: Automatiseer checks (HTML entity fix + resource availability)
4. **📊 Analytics**: Plan usage tracking na release

---

## 🏆 **SUCCES FACTOREN**

### **Wat Goed Gewerkt Heeft**
- ✅ **Modulaire architectuur** - eenvoudig uitbreidbaar
- ✅ **JSON-first approach** - snelle development, goede performance
- ✅ **Comprehensive testing** - kwaliteit gegarandeerd
- ✅ **Documentation tijdens development** - kennis behouden
- ✅ **Hybrid data strategy** - directe + indirecte koppelingen

### **Risk Mitigation**
- ⚠️ **Indirect matching** voor motie-stemming relaties
- ⚠️ **Link timing** - oudere moties hebben betere directe links
- ⚠️ **Data volume growth** - schaalbare opslag strategie
- ⚠️ **API changes** - monitoring en fallback mechanisms

---

## 📚 **BELANGRIJKSTE REFERENTIES**

- **API Documentation**: `https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/`
- **Data Quality Assessment**: `DATA_QUALITY_ASSESSMENT.md`
- **Technical Lessons**: `LESSONS_LEARNED.md`
- **Current Dataset**: `bronmateriaal-onbewerkt/` (51,016 records)

---

*Dit document vertegenwoordigt de complete stand van zaken van het motiematcher project tot 2 oktober 2025. De architectuur is bewezen, de data kwaliteit is gevalideerd, en het project is klaar voor de volgende fase: volledige termijn collectie en web platform development.*