# Huidige Kamer Stemming Data - Compleet Overzicht

**Verzameld op:** 3 oktober 2025 _(laatste validatie: 4 oktober 2025)_
**Periode:** December 2023 - Oktober 2025 (huidige 2e Kamer zittingsperiode)
**Methode:** Zaak-centric collectie met API expansions

## Data Volumes
- **Moties (Zaak):** 2,000 records
- **Besluiten:** 4,239 records
- **Stemmingen:** 28,083 records
- **Dekking:** 83.7% van moties heeft stemmingen (1,674/2,000)

## Partij Stemverdelingen (Top 10)
| Partij | Totaal Stemmen | Voor | Tegen | Overig |
|--------|----------------|------|-------|--------|
| PVV | 2,446 | 1,191 | 1,221 | 34 |
| VVD | 2,186 | 1,023 | 1,155 | 8 |
| GroenLinks-PvdA | 2,175 | 1,435 | 722 | 18 |
| NSC | 2,061 | 1,265 | 774 | 22 |
| D66 | 1,865 | 1,226 | 630 | 9 |
| BBB | 1,807 | 1,031 | 772 | 4 |
| CDA | 1,771 | 859 | 902 | 10 |
| SP | 1,766 | 1,295 | 469 | 2 |
| PvdD | 1,721 | 1,192 | 517 | 12 |
| ChristenUnie | 1,720 | 1,157 | 561 | 2 |

## Data Structuur
```
bronmateriaal-onbewerkt/
└── current/
    ├── zaak_current/
    │   └── zaak_voted_motions_20251003_200218.json
    ├── besluit_current/
    │   └── besluit_voted_motions_20251003_200218.json
    └── stemming_current/
        └── stemming_voted_motions_20251003_200218.json
```

## Validatie Resultaten
✅ **API Compleet:** Alle stemmingen beschikbaar via Zaak→Besluit→Stemming expansions  
✅ **Tijdperiode Correct:** December 2023 - Oktober 2025 (huidige Kamer)  
✅ **Partij Dekking:** Alle 17 fracties vertegenwoordigd  
✅ **Stem Types:** Voor/Tegen/Overig correct vastgelegd  
✅ **Recent Data:** Tot vandaag (3 oktober 2025)  

## Nieuwe bevindingen (4 oktober 2025)
- **Volledige motietekst beschikbaar:** `DocumentPublicatie(<id>)/Resource` retourneert de XML van de motie (getest op besluit 93c64c34-…)
- **Filter wijziging:** Gebruik `$filter=Id eq <guid>`; de `guid'...'` syntax levert nu 400-fouten
- **Pilot ETL pending:** Minimaal 5 moties worden nu handmatig geselecteerd voor een eerste verwerkte dataset met tekst + stemuitslag

## Gebruik
Deze data bevat alle stemmingen waarover in de huidige 2e Kamer is gestemd sinds de beëdiging. Perfect voor partij-positionering analyse en stemgedrag onderzoek.

**Opmerking:** Sommige moties (16.3%) hebben nog geen stemmingen omdat ze nog niet in stemming zijn gebracht.