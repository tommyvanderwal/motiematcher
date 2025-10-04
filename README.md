# motiematcher

Motiematcher is een experimenteel platform dat Nederlandse politieke moties koppelt aan partijstemgedrag. Het doel is een "partij wijzer" te bouwen die laat zien hoe partijen stemmen op actuele onderwerpen.

## Huidige status (4 okt 2025)
- ✅ Ruwe Tweede Kamer data verzameld en opgeslagen onder `bronmateriaal-onbewerkt/`
- ✅ Document download route bevestigd via `DocumentPublicatie(<id>)/Resource`
- 🚧 Verwerkte dataset (≥5 echte moties met tekst + stemmen) wordt momenteel ontwikkeld
- 🚧 FastAPI frontend (`app/main_simple.py`) wacht op de nieuwe dataset

## Structuur
```
c:\motiematcher
├── bronmateriaal-onbewerkt/    # Raw API dumps (zaak, besluit, stemming, document, ...)
├── data-processing/            # Transform scripts (uit te breiden met pilot ETL)
├── app/                        # FastAPI backend + templates
├── static/                     # Frontend assets
└── docs (.md)                  # Architectuur, data kwaliteit en handover notities
```

## Volgende stappen
1. Bouw een pilot ETL die minimaal 5 moties verrijkt met volledige tekst en stemming per partij.
2. Pars de XML van `DocumentPublicatie(...)/Resource` naar leesbare tekst of HTML-snippets.
3. Koppel de FastAPI endpoints aan de nieuwe dataset en voer `run_web_test.py` uit.

Zie `SESSION_HANDOVER_SUMMARY.md` voor de volledige day-to-day voortgang en concrete actielijst.
