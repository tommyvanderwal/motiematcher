"""Inspect vote pages to understand linking fields for motions."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Dict, Any

SAMPLE_FILES = [
    "bronmateriaal-onbewerkt/stemming_enriched/stemming_page_1012_enriched_20251003T141414Z.json",
    "bronmateriaal-onbewerkt/stemming_enriched/stemming_page_1013_enriched_20251003T141414Z.json",
    "bronmateriaal-onbewerkt/stemming_enriched/stemming_page_1014_enriched_20251003T141415Z.json",
]

BASE_DIR = Path(__file__).resolve().parent.parent


def iter_records(files: Iterable[str]) -> Iterable[Dict[str, Any]]:
    for rel_path in files:
        path = BASE_DIR / rel_path
        if not path.exists():
            print(f"⚠️ Missing file: {path}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"⚠️ Failed to parse {path.name}: {exc}")
            continue
        records = payload.get("value") if isinstance(payload, dict) else None
        if not records:
            continue
        for record in records:
            if isinstance(record, dict):
                yield record


def main() -> None:
    besluit_motie_counts: Counter[str] = Counter()
    motie_lookup = defaultdict(set)
    agg_counts = Counter()
    agendapunt_map: Dict[str, Dict[str, Any]] = {}

    target_match_counter = Counter()
    target_mismatch_counter = Counter()

    for record in iter_records(SAMPLE_FILES):
        besluit = record.get("Besluit") or {}
        besluit_id = (besluit.get("Id") or record.get("Besluit_Id"))
        agendapunt = besluit.get("Agendapunt") or {}
        zaak_entries = agendapunt.get("Zaak") or []
        moties = [z for z in zaak_entries if (z.get("Soort") or "").lower() == "motie"]
        agendapunt_id = agendapunt.get("Id")
        volgorde = besluit.get("AgendapuntZaakBesluitVolgorde")

        target_zaak_id = None
        if isinstance(volgorde, int) and 1 <= volgorde <= len(zaak_entries):
            target = zaak_entries[volgorde - 1]
            target_zaak_id = target.get("Id")
            if target and (target.get("Soort") or "").lower() == "motie":
                target_match_counter[target_zaak_id] += 1
            else:
                label = (target.get("Soort") if target else "missing")
                target_mismatch_counter[label] += 1

        agg_counts[len(zaak_entries)] += 1
        if isinstance(besluit_id, str):
            besluit_motie_counts[besluit_id] = len(moties)
        if isinstance(target_zaak_id, str) and isinstance(besluit_id, str):
            motie_lookup[target_zaak_id].add(besluit_id)
        if isinstance(agendapunt_id, str):
            info = agendapunt_map.setdefault(
                agendapunt_id,
                {
                    "nummer": agendapunt.get("Nummer"),
                    "onderwerp": agendapunt.get("Onderwerp"),
                    "zaken": [],
                    "volgorde_counts": Counter(),
                },
            )
            if not info["zaken"]:
                info["zaken"] = [
                    {
                        "id": z.get("Id"),
                        "soort": z.get("Soort"),
                        "nummer": z.get("Nummer"),
                        "volgnummer": z.get("Volgnummer"),
                    }
                    for z in zaak_entries
                ]
            if isinstance(volgorde, int):
                info["volgorde_counts"][volgorde] += 1

    print("Zaak entries per besluit (sample):")
    for count, total in agg_counts.most_common(5):
        print(f"  {count}: {total}")

    print("\nMotions per besluit (sample):")
    for besluit_id, motie_count in besluit_motie_counts.most_common(5):
        print(f"  {besluit_id}: {motie_count}")

    multi_link = [motie_id for motie_id, besluiten in motie_lookup.items() if len(besluiten) > 1]
    print(f"\nUnique motions observed: {len(motie_lookup)}")
    print(f"Motions linked to >1 besluit: {len(multi_link)}")
    if multi_link[:5]:
        print("  Example moties with multiple besluiten:")
        for motie_id in multi_link[:5]:
            print(f"    {motie_id}: {sorted(motie_lookup[motie_id])}")

    print("\nTarget mapping results (using AgendapuntZaakBesluitVolgorde):")
    print(f"  Motie matches: {sum(target_match_counter.values())}")
    print(f"  Non-motie targets: {dict(target_mismatch_counter)}")

    print("\nAgendapunt mapping overview:")
    for agendapunt_id, info in list(agendapunt_map.items())[:3]:
        print(f"  Agendapunt {info['nummer']} ({agendapunt_id})")
        print(f"    Onderwerp: {info['onderwerp']}")
        print(f"    Zaak entries: {len(info['zaken'])}")
        print(f"    Besluit volgorde counts: {dict(info['volgorde_counts'])}")
        for idx, zaak in enumerate(info["zaken"], start=1):
            print(
                f"      #{idx}: soort={zaak['soort']} nummer={zaak['nummer']} volgnummer={zaak['volgnummer']} id={zaak['id']}"
            )



if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - diagnostics helper
        print(f"Error during analysis: {exc}")
        raise
