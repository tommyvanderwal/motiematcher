# Motiematcher Project Status - Session Handover Summary
**Date:** October 3, 2025  
**Context:** Overstap naar nieuwe workspace met lokale bestanden

## Project Overview
Schaalbale website die politieke moties matcht aan partijen - een partijgids gebaseerd op Nederlandse parlementaire stemgeschiedenis van de laatste 10 jaar.

### Architecture Goals
- **Part 1:** Data collectie & verrijking van alle moties, wetten & amendementen (laatste 10 jaar)
- **Part 2:** Schaalbale webplatform (10+ webservers, S3-hosted assets)
- **Core Function:** Gebruiker selecteert positie op moties → match met partij stempatronen

## Current Critical Issue - Data Quality Problems
**HOOFDPROBLEEM:** De huidige implementatie analyseert oude data (2012-2019) en niet-stemmingsdata (brieven, rapporten) die geen recente stemgeschiedenis hebben.

### Problematische Voorbeelden uit Huidige Output:
```json
{
  "id": "9ff70d63-3f8d-4a58-9ec0-da26b5b26832",
  "type": "Motie",
  "title": "Wijziging van de Wet marktordening gezondheidszorg...",
  "date": "2016-09-08T00:00:00+02:00",  // ← TE OUD!
  "voting_records": []  // ← GEEN STEMDATA!
}
```

## Required Immediate Actions (2-Step Process)

### **STAP 1: Recente Data Filtering & Enrichment**
1. **Hard Filter op Periode:** Alleen laatste 2-3 jaar (2022-2025)
2. **Hard Filter op Type:** Alleen Moties, Wetten, Amendementen (geen brieven/rapporten)
3. **Volledige Verrijking met:**
   - Volledig stemgedrag ALLE partijen per item
   - Complete inhoudelijke tekst waar over gestemd wordt
   - Voor moties: volledige tekst
   - Voor wetten/amendementen: minimum 5 regels duidelijke omschrijving
4. **Analyse Krappe Uitslagen:** Identificeer zaken waar 1 partij de uitslag had kunnen veranderen

### **STAP 2: AI Impact Assessment (alleen na 100% correcte Stap 1)**
1. **LLM Objectieve Beoordeling:** Lange termijn impact op:
   - Fundamentele democratische vrijheden
   - Vrijheid van informatie (burgers moeten alles weten om democratisch te kunnen stemmen)
   - Grote overheidsuitgaven die inflatie veroorzaken
2. **Selectie Criteria:** ECHT high impact zaken waar 1 partij verschil had kunnen maken

## Technical Foundation
- **Python 3.13.7** in virtual environment
- **Real Parliamentary Data:** 263,241 zaken, 150,208 stemmingen in `bronmateriaal-onbewerkt/`
- **Data Structure:** JSON files in zaak/ en stemming/ directories
- **Current Scripts:** `analyze_real_long_term_impact.py` (werkt maar analyseert verkeerde data)

## Data Infrastructure Status
```
C:\motiematcher\
├── bronmateriaal-onbewerkt/
│   ├── zaak/           # 263,241 parlementaire zaken (alle jaren)
│   └── stemming/       # 150,208 stemmingen
├── output/             # Gegenereerde analyses
├── analyze_*.py        # Analyse scripts
└── real_high_impact_parliamentary_items.json  # Huidige output (FOUT - te oude data)
```

## Known Technical Issues
1. **ID Linking Failure:** 0 matches tussen zaak IDs en stemming Besluit_IDs
2. **Date Range Problem:** Script analyseert alle jaren i.p.v. recente periode
3. **Type Filtering Missing:** Brieven/rapporten worden meegenomen
4. **Voting Enrichment Incomplete:** Geen volledige partij stemdata per zaak

## Completed Work (Ready for New Session)
✅ **Data Loading:** Successful loading of 263k+ zaken and 150k+ stemmingen  
✅ **Basic Analysis Framework:** Working Python scripts for impact assessment  
✅ **None-Safe Handling:** Robust handling of missing data fields  
✅ **JSON Output Generation:** Structured output format for website integration  
✅ **Mock Data Cleanup:** Removed confusing test files

## Immediate Next Steps for New Session
1. **Create new filtering script** with strict date range (2022-2025) and document type filtering
2. **Implement proper voting enrichment** to get complete party voting records per zaak
3. **Add full text extraction** for motion/law content
4. **Analyze vote margins** to identify single-party decisive votes
5. **Only then proceed to AI impact assessment** of filtered, enriched data

## Key Files to Reference
- `analyze_real_long_term_impact.py` - Current working script (needs modification)
- `real_high_impact_parliamentary_items.json` - Current output (wrong data, shows structure)
- `ARCHITECTURE_AND_LESSONS.md` - Technical architecture decisions
- `DATA_STRUCTURE_AND_LINKING.md` - Data schema and linking strategies

## Critical Success Criteria
- ✅ **Recency:** Only 2022-2025 data
- ✅ **Votable Items:** Only Moties/Wetten/Amendementen
- ✅ **Complete Voting Data:** All party positions per item
- ✅ **Full Content:** Complete text or clear 5+ line descriptions
- ✅ **Margin Analysis:** Identify single-party decisive votes
- ✅ **Democratic Impact:** Focus on freedom of information & major spending

## User's Final Feedback
"Slecht. Dit zijn oude moties en ook brieven en dergelijke. Zorg dat je opnieuw begint en nu in 2 stappen verrijkt: 1. Hard filteren op huidige periode + volledig stemgedrag + volledig tekst + krappe uitslagen. 2. LLM beoordeling democratische impact van die krappe high-impact zaken."

---
**Status:** Ready for complete restart with proper filtering and enrichment approach in new local workspace session.