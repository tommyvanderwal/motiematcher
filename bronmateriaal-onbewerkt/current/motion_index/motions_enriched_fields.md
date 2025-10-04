# motions_enriched.json – veldbeschrijving

`motions_enriched.json` combineert de oorspronkelijke motielijst met stemmingdetails en de volledige motietekst. Elk record heeft de volgende velden:

- **motion_id**: `str` – GUID van de motie/zaak.
- **motion_number**: `str | null` – Officieel kamerstuknummer.
- **motion_title**: `str | null` – Titel of onderwerp van de motie (geprefereerde normalisatie indien beschikbaar).
- **motion**: `object` – Het volledige originele motie-record uit `motions_list.json` (alle bronvelden blijven intact).
- **text**: `object`
  - **content**: `str | null` – Volledige tekst van de motie (plain text). `null` wanneer de tekst niet beschikbaar is.
  - **content_char_count**: `int` – Aantal karakters in `content` (0 bij missende tekst).
  - **source**: `object | null` – Metadata over de bronpublicatie:
    - **document_id**: `str` – Document GUID.
    - **document_nummer**: `str | null` – Documentnummer (bijv. "2023D48274").
    - **document_soort**: `str | null` – Documenttype; XML-publicaties met `Soort` bevat vaak "Motie".
    - **publication_id**: `str` – GUID van de gekozen `DocumentPublicatie`.
    - **publication_content_type**: `str | null` – MIME-type van de publicatie (doelwit: `application/xml` of `text/*`).
    - **publication_length**: `int | null` – Grootte in bytes.
    - **cached**: `bool` – `true` indien de binaire download uit de cache kwam.
    - **binary_path**: `str` – Relatief pad naar het gecachte bestand in `bronmateriaal-onbewerkt/cache/document_publications/`.
  - **issues**: `list[str]` – Labels voor eventuele problemen tijdens het ophalen of parsen (bijvoorbeeld `publication_decode_error`, `document_no_parseable_publication`).
- **final_status**: `str | null` – Beschikbaar besluitresultaat (bijv. "Stemmen - aangenomen"). Afgeleid van het meest recente besluitrecord.
- **vote_totals**: `dict[str, int]` – Gestapelde stemtotalen per stemtype (`Voor`, `Tegen`, `Onthouden`, etc.) gebruikmakend van fractiegrootte (zetelgewogen).
- **vote_breakdown**: `list[object]` – Eén item per stemming, inclusief fractie- en persoonsmetadata (zoals `fractie_grootte`, `actor_naam`, `persoon`-gegevens).
- **decision_summaries**: `list[object]` – Samenvatting per gekoppeld besluit:
  - **besluit_id**: `str`
  - **besluit_soort** / **besluit_tekst**: Kerninformatie over het besluit.
  - **last_changed**: `str | null` – ISO8601 timestamp van laatste wijziging in stemming/besluitdata.
  - **vote_totals**: `dict[str, int]`
  - **vote_count**: `int` – Aantal individueel geregistreerde stemmingrecords.
- **issues**: `list[str]` – Gecombineerde lijst van tekst- en stemproblemen. Bijvoorbeeld `no_vote_data` (geen stemming gevonden) of tekstgerelateerde labels.

## Summarybestand

`motions_enriched_summary.json` bevat globale statistieken over de run:

- **generated_at** – UTC-timestamp van de run.
- **motion_count_input** – Aantal moties in de bronlijst.
- **motion_count_output** – Aantal moties in de output (geïnvloed door `--max-motions`).
- **limit_applied** – `true` als `--max-motions` een subset produceerde.
- **vote_coverage** – Tellingen voor moties met/zonder stemdata.
- **text_coverage** – Tellingen voor moties met/zonder tekst.
- **issue_counts** – Frequentie van alle aangetroffen issues.
- **api_calls_used** – Aantal uitgevoerde API-aanroepen richting de Tweede Kamer OData-service in deze run (inclusief cache-refreshes).

## Databronnen en caching

De verrijking gebruikt drie hoofdbronnen:

1. `motions_list.json` (basisregistratie van moties/zaakgegevens).
2. JSON-dumps in `bronmateriaal-onbewerkt/stemming_enriched/` (bevat uitgebreide stemming- en besluitinformatie).
3. Live OData-aanroepen naar `/Zaak` en `DocumentPublicatie/Resource` voor motiedocumenten.

Om herhaald downloaden te beperken worden responses lokaal gecached onder `bronmateriaal-onbewerkt/cache/`:

- `zaak_documents/` – Gecachete `Zaak`-payloads (één record per bestand).
- `document_publications/` – Binaire downloads van `DocumentPublicatie` resources (bijv. XML-bestanden).
- `document_texts/` – Geparste teksten als JSON met metadata.

Gebruik `--refresh-text` om caches voor een run te negeren, en `--max-api-calls` om het aantal live verzoeken te beschermen tijdens tests. De CLI ondersteunt daarnaast `--max-motions` om een subset te verwerken en `--skip-text` voor snellere iteraties wanneer alleen stemgegevens nodig zijn.

## Bekende issues

- Wanneer geen stemgegevens worden gevonden komt `no_vote_data` zowel in `issues` als in `issue_counts` terecht.
- Indien geen parseerbare publicatie wordt aangetroffen, blijft `text.content` leeg en worden de relevante tekst issues opgenomen voor latere analyse.
- Het script logt iedere 50 moties voortgang in de console; grotere runs kunnen tientallen minuten duren afhankelijk van cachehits en netwerkrespons.
