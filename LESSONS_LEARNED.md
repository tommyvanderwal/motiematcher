# Lessons Learned - Dutch Parliament Data Collection

## 📚 IMPORTANT API DISCOVERIES & PATTERNS

### 🌐 API Structure & Endpoints
- **Base URL**: `https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/`
- **Available Entities**: Zaak, Stemming, Besluit, Document, Activiteit, Persoon, Fractie, Vergadering, Agendapunt
- **Non-existent Entities**: Wet, Amendement, Stemverklaring (as separate entities)
- **Data Format**: OData v4 with JSON responses
- **Filter wijziging (okt 2025)**: `$filter=Id eq <guid>` werkt, maar `$filter=Id eq guid'…'` geeft 400-fouten

### 🔍 Data Structure Patterns

#### Zaak Entities (Parliamentary Cases)
```python
# Structure: Direct list (not OData wrapper)
data = json.load(file)  # List of 250 zaak objects
sample_zaak = {
    'Id': 'uuid',
    'Nummer': '2025Z18657', 
    'Soort': 'Motie',  # Filter key for different types
    'Titel': 'Racisme en Discriminatie',
    'Onderwerp': 'Motie van het lid Ergin over...',
    'GewijzigdOp': '2025-09-30T...'
}
```

#### Stemming Entities (Voting Records)  
#### DocumentVersie & DocumentPublicatie (Full Text Access)
```python
# Expand vanuit Besluit → Zaak → Document → HuidigeDocumentVersie
params = {
    '$filter': f"Id eq {besluit_id}",
    '$expand': 'Zaak($expand=Document($expand=HuidigeDocumentVersie($expand=DocumentPublicatie)))'
}

# XML downloaden via Resource endpoint
publication_id = document['HuidigeDocumentVersie']['DocumentPublicatie'][0]['Id']
resp = requests.get(f"{BASE_URL}/DocumentPublicatie({publication_id})/Resource", timeout=30)
xml_text = resp.text  # Complete motietekst
```
- **Content-Type**: `application/xml`
- **Gebruik**: Parse naar HTML of plain-text voor motiematcher
- **Caching**: Sla response op in `verwerkt/` dataset om herhaalde downloads te vermijden
```python
# Structure: Direct list (not OData wrapper)
data = json.load(file)  # List of 250 voting objects
sample_vote = {
    'Id': 'uuid',
    'Besluit_Id': 'uuid',
    'ActorFractie': 'PVV',  # Party name
    'Soort': 'Voor',  # Vote type: Voor/Tegen/Niet deelgenomen
    'GewijzigdOp': '2025-09-30T...'
}
```

### 📊 Pagination Patterns

#### API Limits & Pagination
- **Record Limit**: 250 records per API call (hard limit)
- **Pagination Parameter**: `$skip=N` where N = page * 250
- **Date Filtering**: Use `$filter=GewijzigdOp ge '2025-09-02T00:00:00Z'`
- **Ordering**: `$orderby=GewijzigdOp desc` for most recent first

#### Successful Pagination Implementation
```python
skip = 0
page = 1
while True:
    url = f"{base_url}/Stemming?$skip={skip}&$orderby=GewijzigdOp desc"
    # Process response
    if len(votes) < 250:  # End of data indicator
        break
    skip += 250
    page += 1
```

### 🎯 Key Filter Discoveries

#### Zaak Entity Filtering
- **Moties**: `Soort eq 'Motie'` ✅ (991 collected in 30 days)
- **Wetten**: Need to collect all Zaak without Soort filter, then analyze
- **Amendementen**: Likely in Zaak with different Soort value

#### Date Filtering Strategy
- **Client-side filtering works better** than API $filter for complex date ranges
- **30-day collection**: Use GewijzigdOp field for recent activity
- **API date format**: ISO 8601 with Z timezone (`2025-09-02T00:00:00Z`)

### 💾 Data Storage Best Practices

#### File Organization
```
bronmateriaal-onbewerkt/
├── zaak/           # Motion texts and parliamentary cases
├── stemming/       # Voting records with party positions  
├── besluit/        # Decision outcomes
├── document/       # Document content and texts
├── agendapunt/     # Agenda items
└── activiteit/     # Parliamentary activities
```

#### File Naming Convention
- **Format**: `{entity_type}_page_{N}_{timespan}_{timestamp}.json`
- **Example**: `moties_page_1_30days_20251002_193201.json`
- **Benefits**: Timestamped, paginated, clearly identified

### 🚨 Critical Error Patterns

#### Tuple Unpacking Errors
```python
# Problem: Inconsistent return values
def get_data():
    if condition:
        return data, extra  # Sometimes 2 values
    else:
        return data         # Sometimes 1 value

# Solution: Always return consistent tuple
def get_data():
    # Process data...
    return data, extra_dict  # Always return 2 values
```

#### Encoding Issues
```python
# Problem: Default encoding fails on Dutch characters
data = json.load(open(file))  # UnicodeDecodeError

# Solution: Explicit UTF-8 encoding
data = json.load(open(file, encoding='utf-8'))  # Works
```

#### Besluit Filter Errors (400 Bad Request)
```python
# Problem: Nieuwere API-versie accepteert geen guid-literal meer
requests.get(f"{BASE_URL}/Besluit", params={'$filter': "Id eq guid'…'"})
# → 400 Bad Request

# Solution: Gebruik raw GUID zonder literal wrapper
requests.get(f"{BASE_URL}/Besluit", params={'$filter': f"Id eq {besluit_id}"})
```

### 🏛️ Parliamentary Data Insights

#### Party Activity (Top 5 Most Active)
1. **PVV**: 193 votes (Voor:117, Tegen:75)
2. **GroenLinks-PvdA**: 182 votes (Voor:118, Tegen:64) 
3. **VVD**: 180 votes (Voor:66, Tegen:114)
4. **NSC**: 176 votes (Voor:132, Tegen:43)
5. **BBB**: 165 votes (Voor:92, Tegen:73)

#### Data Volume (30 days)
- **991 Moties** collected across 4 paginated files (3.7 MB)
- **~9,500 Votes** collected across 38 paginated files (17.1 MB)
- **158 Unique Decisions** with voting records
- **15 Active Political Parties** in parliament

### 🔧 Development Workflow Lessons

#### Python Command Line Patterns
```bash
# Effective for quick data exploration
py -c "import json; data = json.load(open('file.json', encoding='utf-8')); print(len(data))"

# Better for complex analysis: create mini-scripts
py quick_analysis.py
```

#### Avoid Interactive Python Session
- ❌ `py` interactive session blocks until exit - no intermediate feedback
- ✅ Mini-scripts with `py script.py` provide immediate results and reusable code

#### Resource Download Discipline
- ✅ Gebruik dedicated scripts (bv. `temp/test_fetch_decision.py`) om `DocumentPublicatie(...)/Resource` responses vast te leggen en in `verwerkt/` op te slaan
- ✅ Voeg snippet logging toe zodat XML parsing reproduceerbaar blijft

### 📈 Performance & Scalability

#### API Rate Limits
- **No obvious rate limiting** encountered during testing
- **Sleep 0.5s** between requests as courtesy (prevents overwhelming server)
- **Batch processing** works well for large collections

#### Data Processing Speed
- **JSON parsing**: Very fast even for large files (1MB+ files load instantly)
- **Pandas consideration**: Current JSON processing fast enough, pandas may be overkill for current volume
- **Memory usage**: 22.9 MB total data easily fits in memory

### 🎯 Missing Data Types Investigation

#### What We Have ✅
- **Moties (Motions)**: Complete with texts, titles, subjects
- **Stemmingen (Votes)**: Complete with party positions and decision IDs
- **Basic Metadata**: Dates, IDs, party info, vote counts

#### What We Need ⚠️
- **Wetten (Laws)**: In Zaak entities but not filtered yet
- **Amendementen (Amendments)**: In Zaak entities but not filtered yet
- **Stemverklaringen (Vote Explanations)**: May be in Activiteit or Document entities
- **Full Document Texts**: Document entities not collected yet

#### API Limitations Discovered
- **No dedicated Wet entity** - laws are Zaak items with different Soort
- **No dedicated Amendement entity** - amendments are Zaak items  
- **No dedicated Stemverklaring entity** - explanations may be in Activiteit
- **Metadata endpoint** complex - direct entity testing more reliable

### 🔄 Next Phase Strategy

#### Data Collection Priority
1. **Collect all Zaak types** (not just Motie) to get laws and amendments
2. **Collect Document entities** for full text content
3. **Collect Activiteit entities** for potential vote explanations
4. **Collect Besluit entities** for decision context

#### Processing Approach
- **Keep current JSON approach** - fast and flexible
- **Consider pandas** only if complex cross-dataset queries needed
- **Maintain modular structure** for selective refresh capability

### 🏆 Success Factors
- **Modular file structure** enables selective re-collection
- **Timestamped files** provide audit trail and version control
- **Pagination handling** scales to large datasets
- **UTF-8 encoding** handles Dutch characters correctly
- **Mini-script approach** enables rapid iteration and testing

---

*Generated: 2025-10-04*  
*Dataset: 30-day Dutch Parliament baseline (991 moties, ~9500 votes, 22.9 MB) + DocumentPublicatie resource workflow*