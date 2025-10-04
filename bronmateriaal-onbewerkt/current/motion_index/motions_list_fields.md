# motions_list.json – veldbeschrijving

`motions_list.json` bevat per motie één record dat nu:

- **alle oorspronkelijke velden uit de OData 2.0-`Zaak` respons** bewaart (zoals `Kabinetsappreciatie`, `Grondslagvoorhang`, etc.);
- extra sleutelvelden toevoegt om koppelen eenvoudiger te maken; en
- genormaliseerde varianten van veelgebruikte velden aanbiedt met voorspelbare types/formaten.

Onderstaande tabel beschrijft de toegevoegde/afgeleide velden. Alle overige properties komen ongewijzigd uit de bron-`Zaak` en behouden hun oorspronkelijke betekenis.

| Veld | Type | Herkomst | Betekenis | Voorbeeld |
| --- | --- | --- | --- | --- |
| `bronbestanden` | array van strings | samengesteld in script | Elke bestandsnaam in `bronmateriaal-onbewerkt/current/zaak_current/` waarin deze motie is aangetroffen. Handig voor traceerbaarheid en herverzameling. | `['zaak_current_parliament_20251003_174519.json']` |
| `zaak_id` | string (GUID) | afgeleid uit `Id` | Primaire sleutel die in alle datasets gelijk is aan `Zaak.Id`. Wordt ook 1-op-1 gebruikt om te koppelen aan besluiten, documenten en stemmingen. | `d2e882c4-4cd9-42bd-918d-6439f977a9dd` |
| `nummer` | string | afgeleid uit `Nummer` | Kamerstuknummer met whitespace verwijderd. Houdt één consistente weergave aan, ook als het bronveld leeg of null is (dan ontbreekt het). | `2023Z20042` |
| `normalised` | object | samengesteld in script | Verzamelt de meest gebruikte kernvelden in opgeschoonde vorm (getrimde tekst, integers, ISO-datumstrings). Zie tabel hieronder voor de subvelden. | `{ "zaak_id": ..., "vergaderjaar": ... }` |
| `GestartOp_norm` | string (ISO 8601) | afgeleid uit `GestartOp` | Genormaliseerde timestamp met expliciete offset; blijft aanwezig naast het ongewijzigde bronveld. Alleen aanwezig als de parser het veld succesvol kan omzetten. | `2023-12-12T00:00:00+01:00` |
| `GewijzigdOp_norm` | string (ISO 8601) | afgeleid uit `GewijzigdOp` | Zie `GestartOp_norm`, maar voor de wijzigingsdatum. | `2024-02-19T10:59:02.367000+01:00` |

### Subvelden binnen `normalised`

| Subveld | Type | Oorspronkelijk veld | Uitleg |
| --- | --- | --- | --- |
| `zaak_id` | string (GUID) | `Id` | Zelfde betekenis als het top-level `zaak_id`; meegegeven voor gemak. |
| `nummer` | string | `Nummer` | Gestandaardiseerde versie van het Kamerstuknummer. |
| `titel` | string of null | `Titel` | Bijgesneden titeltekst (lege strings → null). |
| `onderwerp` | string of null | `Onderwerp` | Bijgesneden onderwerp/omschrijving. |
| `status` | string of null | `Status` | Huidige status zoals gemeld door de Tweede Kamer (`Vrijgegeven`, `Ingediend`, …). |
| `vergaderjaar` | string of null | `Vergaderjaar` | Parlementair jaar in notatie `YYYY-YYYY`. |
| `volgnummer` | integer of null | `Volgnummer` | Intern volgnummer binnen het vergaderjaar; vormt samen met `vergaderjaar` de officiële dossierverwijzing “Vergaderjaar YYYY-YYYY, nr. NNNN”. |
| `organisatie` | string of null | `Organisatie` | Behandelende organisatie (bij moties vrijwel altijd `Tweede Kamer`). |
| `gestart_op` | string of null (ISO 8601) | `GestartOp` | Genormaliseerde startdatum van de motie. |
| `gewijzigd_op` | string of null (ISO 8601) | `GewijzigdOp` | Genormaliseerde laatste wijzigingsmoment. |
| `afgedaan` | boolean of null | `Afgedaan` | Indicator of de motie is afgehandeld. |

## Verdere opmerkingen

- Omdat het volledige `Zaak`-record behouden blijft, zijn ook velden als `Grondslagvoorhang`, `Kabinetsappreciatie`, `HuidigeBehandelstatus`, `GrootProject`, etc. beschikbaar voor downstream-analyses.
- De combinatie `vergaderjaar` + `volgnummer` blijft dé officiële verwijzing binnen het parlementair jaar. Voor publicaties op overheid.nl is daarnaast `nummer` het meest herkenbare kenmerk (`2023Z20042`).
- `bronbestanden` kan meerdere items bevatten wanneer dezelfde motie in meerdere snapshots voorkomt; hiermee kun je snel terug naar de ruwe bronbestanden.
- Null-waarden uit de bron blijven behouden. Alleen de genormaliseerde velden (zoals `normalised.gestart_op`) proberen het bronveld om te zetten; lukt dat niet, dan ontbreekt het normale veld maar blijft het originele ongewijzigd aanwezig.
