#!/usr/bin/env python3
"""
Step 1: Full-term Data Filtering & Enrichment

Filters parliamentary data for the current legislative term (Dec 2023 - today),
restricts to votable items (Moties/Wetten/Amendementen), and enriches
each zaak with complete voting data derived from besluit/agendapunt/zaak
expansions.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DATA_ROOT = Path("bronmateriaal-onbewerkt")
ZAAK_DIR = DATA_ROOT / "zaak"
ENRICHED_STEMMING_DIR = DATA_ROOT / "stemming_enriched"
OUTPUT_FILE = Path("step1_fullterm_filtered_enriched_data.json")
MIN_START_DATE = datetime(2023, 12, 1, tzinfo=timezone.utc).date()
VOTABLE_TYPES = {"Motie", "Wet", "Amendement"}


def _load_json_records(directory: Path, description: str) -> List[Dict[str, Any]]:
    """Load flattened records from all JSON files in a directory."""

    records: List[Dict[str, Any]] = []
    if not directory.exists():
        print(f"⚠️  Directory {directory} missing for {description}.")
        return records

    files = sorted(directory.glob("*.json"))
    print(f"Loading {len(files)} {description} files from {directory}...")

    for path in files:
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:  # pragma: no cover - diagnostics
            print(f"  ⚠️  Skipping {path.name}: {exc}")
            continue

        if isinstance(payload, list):
            records.extend(payload)
        elif isinstance(payload, dict):
            value = payload.get("value")
            if isinstance(value, list):
                records.extend(value)
            else:
                print(f"  ⚠️  Unexpected payload structure in {path.name}")
        else:
            print(f"  ⚠️  Unknown payload type for {path.name}")

    print(f"Loaded {len(records)} {description} records.")
    return records


def load_fullterm_zaak_data() -> List[Dict[str, Any]]:
    return _load_json_records(ZAAK_DIR, "zaak")


def load_enriched_stemming_data() -> List[Dict[str, Any]]:
    return _load_json_records(ENRICHED_STEMMING_DIR, "enriched stemming")


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def filter_votable_zaken(zaken: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    filtered = [zaak for zaak in zaken if zaak.get("Soort") in VOTABLE_TYPES]
    print(f"Filtered {len(filtered)} votable zaken from {len(zaken)} total zaken")
    return filtered


def filter_recent_zaken(zaken: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    for zaak in zaken:
        started = _parse_date(zaak.get("GestartOp"))
        if started is None or started >= MIN_START_DATE:
            filtered.append(zaak)
    print(f"Filtered {len(filtered)} zaken dated on/after {MIN_START_DATE}")
    return filtered


def _initial_vote_entry(besluit: Dict[str, Any]) -> Dict[str, Any]:
    agendapunt = besluit.get("Agendapunt") or {}
    return {
        "besluit": {
            "Id": besluit.get("Id"),
            "BesluitTekst": besluit.get("BesluitTekst"),
            "BesluitSoort": besluit.get("BesluitSoort"),
            "StemmingsSoort": besluit.get("StemmingsSoort"),
            "Status": besluit.get("Status"),
            "Agendapunt_Id": besluit.get("Agendapunt_Id"),
            "GewijzigdOp": besluit.get("GewijzigdOp"),
            "ApiGewijzigdOp": besluit.get("ApiGewijzigdOp"),
        },
        "agendapunt": {
            "Id": agendapunt.get("Id"),
            "Nummer": agendapunt.get("Nummer"),
            "Onderwerp": agendapunt.get("Onderwerp"),
            "Status": agendapunt.get("Status"),
            "GewijzigdOp": agendapunt.get("GewijzigdOp"),
        },
        "zaken": set(),
        "votes": [],
        "totals": defaultdict(int),
    }


def _normalise_vote(record: Dict[str, Any]) -> Dict[str, Any]:
    fractie = record.get("Fractie") or {}
    persoon = record.get("Persoon") or {}
    return {
        "stemming_id": record.get("Id"),
        "vote": record.get("Soort"),
        "fractie_grootte": record.get("FractieGrootte"),
        "actor_naam": record.get("ActorNaam"),
        "actor_fractie": record.get("ActorFractie"),
        "fractie_id": record.get("Fractie_Id"),
        "persoon_id": record.get("Persoon_Id"),
        "fractie_details": {
            "Id": fractie.get("Id"),
            "Afkorting": fractie.get("Afkorting"),
            "NaamNL": fractie.get("NaamNL"),
        },
        "persoon_details": {
            "Id": persoon.get("Id"),
            "Roepnaam": persoon.get("Roepnaam"),
            "Achternaam": persoon.get("Achternaam"),
        },
    }


def build_vote_index(
    stemmingen: Iterable[Dict[str, Any]]
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, List[str]]]:
    index: Dict[str, Dict[str, Any]] = {}
    zaak_to_besluit: Dict[str, List[str]] = defaultdict(list)

    for record in stemmingen:
        besluit = record.get("Besluit") or {}
        besluit_id = besluit.get("Id") or record.get("Besluit_Id")
        if not besluit_id:
            continue

        entry = index.setdefault(besluit_id, _initial_vote_entry(besluit))

        vote_info = _normalise_vote(record)
        entry["votes"].append(vote_info)
        vote_type = vote_info["vote"] or "Onbekend"
        entry["totals"][vote_type] += vote_info.get("fractie_grootte") or 0

        agendapunt = besluit.get("Agendapunt") or {}
        zaken = agendapunt.get("Zaak") or []
        for zaak in zaken:
            zaak_id = zaak.get("Id")
            if not zaak_id:
                continue
            entry["zaken"].add(zaak_id)
            if zaak_id not in zaak_to_besluit[zaak_id]:
                zaak_to_besluit[zaak_id].append(besluit_id)

    # Freeze the sets and totals into JSON-friendly structures
    for besluit_id, entry in index.items():
        entry["zaken"] = list(entry["zaken"])
        entry["totals"] = dict(entry["totals"])

    return index, zaak_to_besluit


def enrich_zaken_with_voting(
    zaken: List[Dict[str, Any]],
    stemmingen: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    vote_index, zaak_to_besluit = build_vote_index(stemmingen)
    enriched: List[Dict[str, Any]] = []

    for zaak in zaken:
        zaak_id = zaak.get("Id")
        besluit_ids = zaak_to_besluit.get(zaak_id, []) if zaak_id else []
        voting_records: List[Dict[str, Any]] = []

        for besluit_id in besluit_ids:
            entry = vote_index.get(besluit_id)
            if not entry:
                continue
            totals = entry.get("totals", {})
            voting_records.append(
                {
                    "besluit_id": besluit_id,
                    "besluit": entry.get("besluit"),
                    "agendapunt": entry.get("agendapunt"),
                    "vote_totals": totals,
                    "votes": entry.get("votes", []),
                }
            )

        enriched_zaak = zaak.copy()
        enriched_zaak["voting_records"] = voting_records
        enriched_zaak["has_voting_data"] = bool(voting_records)
        enriched.append(enriched_zaak)

    return enriched

def extract_full_text(zaak: Dict[str, Any]) -> str:
    """Extract full text content from zaak"""
    # Try different text fields
    text_sources = [
        zaak.get('Onderwerp', ''),
        zaak.get('Titel', ''),
    ]

    # If zaak has Documenten, try to get text from there
    documenten = zaak.get('Documenten', [])  # May be absent in raw dumps
    if documenten and isinstance(documenten, list):
        for doc in documenten:
            if isinstance(doc, dict) and 'Inhoud' in doc:
                inhoud = doc.get('Inhoud', '')
                if inhoud:
                    text_sources.append(inhoud)

    # Combine all text sources
    full_text = " ".join(str(text) for text in text_sources if text)
    return full_text.strip()


def analyze_vote_margins(enriched_zaken: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for zaak in enriched_zaken:
        totals_voor = 0
        totals_tegen = 0
        for vote_block in zaak.get("voting_records", []):
            totals_voor += vote_block.get("vote_totals", {}).get("Voor", 0)
            totals_tegen += vote_block.get("vote_totals", {}).get("Tegen", 0)

        if totals_voor or totals_tegen:
            margin = abs(totals_voor - totals_tegen)
            zaak["vote_margin"] = margin
            zaak["close_vote"] = margin <= 20
            zaak["vote_totals_overall"] = {
                "Voor": totals_voor,
                "Tegen": totals_tegen,
            }
        else:
            zaak["vote_margin"] = None
            zaak["close_vote"] = False

    return enriched_zaken


def create_filtered_output(enriched_zaken: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create the filtered and enriched output"""
    output = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_zaken': len(enriched_zaken),
            'date_range': f"{MIN_START_DATE.isoformat()} - {datetime.now().date().isoformat()}",
            'votable_types_only': True,
            'types_allowed': ['Motie', 'Wet', 'Amendement'],
            'enrichment_level': 'besluit_agendapunt_links',
            'next_step': 'complete_voting_enrichment'
        },
        'zaken': []
    }

    for zaak in enriched_zaken:
        enriched_item = {
            'id': zaak.get('Id'),
            'nummer': zaak.get('Nummer'),
            'type': zaak.get('Soort'),
            'titel': zaak.get('Titel'),
            'onderwerp': zaak.get('Onderwerp'),
            'date': zaak.get('GestartOp'),
            'status': zaak.get('Status'),
            'vergaderjaar': zaak.get('Vergaderjaar'),
            'full_text': extract_full_text(zaak),
            'has_voting_data': zaak.get('has_voting_data', False),
            'voting_records': zaak.get('voting_records', []),
            'close_vote': zaak.get('close_vote', False),
            'vote_margin': zaak.get('vote_margin'),
            'vote_totals_overall': zaak.get('vote_totals_overall'),
            'raw_zaak': zaak  # Keep full raw data for reference
        }

        output['zaken'].append(enriched_item)

    return output

def main() -> None:
    print("=== STEP 1: Full-term Data Filtering & Enrichment ===")

    print("Loading zaak dataset...")
    zaken = load_fullterm_zaak_data()

    print("Loading enriched stemming dataset...")
    stemmingen = load_enriched_stemming_data()

    print(f"Loaded {len(zaken)} zaken and {len(stemmingen)} enriched stemmingen")

    print("\nFiltering for votable zaak types...")
    votable_zaken = filter_votable_zaken(zaken)

    print("Filtering for current term (>= Dec 2023)...")
    recent_zaken = filter_recent_zaken(votable_zaken)

    print("\nLinking zaken with voting data...")
    enriched_zaken = enrich_zaken_with_voting(recent_zaken, stemmingen)

    print("Analyzing vote margins...")
    analyzed_zaken = analyze_vote_margins(enriched_zaken)

    print("\nCreating filtered output payload...")
    output = create_filtered_output(analyzed_zaken)
    print(f"Output contains {len(output['zaken'])} zaken")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open('w', encoding='utf-8') as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)

    print(f"\n✅ Step 1 Complete! Results saved to {OUTPUT_FILE}")

    type_counts: Dict[str, int] = defaultdict(int)
    for zaak in output['zaken']:
        type_counts[zaak['type']] += 1

    print("\n📊 SUMMARY:")
    print(f"Total zaken processed: {len(output['zaken'])}")
    print(f"Date range: {output['metadata']['date_range']}")
    print(f"Types: {dict(type_counts)}")
    print("Ready for Step 2: AI Impact Assessment")

if __name__ == '__main__':
    main()