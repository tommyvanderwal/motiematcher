# October 2025 Motion Vote Audit

_Audit generated on 2025-10-04 using the refreshed `stemming_enriched` cache and the latest motion index._

## Coverage snapshot

- Target dates: 2025-10-02 and 2025-10-03
- Motions found in `motions_list.json`: **145**
- Motions with vote records in `stemming_enriched`: **140**
- Motions still without associated vote records: **5**

A machine-readable report with the same numbers is stored at `temp/october_vote_audit.json`.

## Motions missing vote data

| Motion number | Title | Notes |
| --- | --- | --- |
| 2025Z18476 | Terrorismebestrijding | Only `Ingediend` besluiten available; no `Stemmen` entries yet. |
| 2025Z18528 | Arbeidsmarktbeleid | Only `Ingediend` besluiten available; no `Stemmen` entries yet. |
| 2025Z18556 | Racisme en Discriminatie | Only `Ingediend` besluiten available; no `Stemmen` entries yet. |
| 2025Z18581 | Vreemdelingenbeleid | Only `Ingediend` besluiten available; no `Stemmen` entries yet. |
| 2025Z18626 | Begroting Financiën/Nationale Schuld 2026 | Only `Ingediend` besluiten available; no `Stemmen` entries yet. |

For each entry above, querying the Tweede Kamer OData API (`Besluit?$filter=Agendapunt_Id eq <id>&$expand=Agendapunt($expand=Zaak)`) currently returns only records with `BesluitSoort = "Ingediend"`. No `Stemming` rows (and thus no breakdown by fractie) are published at this time, so the enrichment pipeline cannot attach vote totals yet.

## Next checks

- Re-run the audit once the Tweede Kamer API begins returning `Stemmen` besluiten for the five outstanding motions.
- After new vote data appears, regenerate the enriched dataset again so the first 1,000 motions (and subsequent batches) pick up the full breakdown.
