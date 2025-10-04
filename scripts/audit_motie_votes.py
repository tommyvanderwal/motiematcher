"""Audit Step 1 output to ensure each motie has voting data or a clear rationale."""

import json
from collections import Counter, defaultdict
from pathlib import Path

DATA_FILE = Path("step1_fullterm_filtered_enriched_data.json")


def load_data():
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["zaken"]


def summarize_missing_votes(zaken):
    moties = [zaak for zaak in zaken if zaak.get("type") == "Motie"]
    total_moties = len(moties)
    with_votes = sum(1 for zaak in moties if zaak.get("has_voting_data"))

    missing = [zaak for zaak in moties if not zaak.get("has_voting_data")]
    missing_count = len(missing)

    status_counter = Counter()
    behandelstatus_counter = Counter()
    afgedaan_counter = Counter()

    samples_by_status = defaultdict(list)

    for zaak in missing:
        raw = zaak.get("raw_zaak") or {}
        status = raw.get("Status") or "<onbekend>"
        behandelstatus = raw.get("HuidigeBehandelstatus") or "<onbekend>"
        afgedaan = raw.get("Afgedaan")

        status_counter[status] += 1
        behandelstatus_counter[behandelstatus] += 1
        afgedaan_counter[str(afgedaan)] += 1

        if len(samples_by_status[status]) < 5:
            samples_by_status[status].append(
                {
                    "Id": zaak.get("id"),
                    "Nummer": zaak.get("nummer"),
                    "Titel": zaak.get("titel"),
                    "Status": status,
                    "HuidigeBehandelstatus": behandelstatus,
                    "Afgedaan": afgedaan,
                    "GestartOp": zaak.get("date"),
                }
            )

    return {
        "total_moties": total_moties,
        "moties_with_votes": with_votes,
        "moties_without_votes": missing_count,
        "status_counter": status_counter,
        "behandelstatus_counter": behandelstatus_counter,
        "afgedaan_counter": afgedaan_counter,
        "samples_by_status": samples_by_status,
    }


def main():
    print("Loading Step 1 output...")
    zaken = load_data()
    summary = summarize_missing_votes(zaken)

    print("\n=== Motie Vote Coverage ===")
    print(f"Total moties: {summary['total_moties']}")
    print(f"Moties with votes: {summary['moties_with_votes']}")
    print(f"Moties without votes: {summary['moties_without_votes']}")

    print("\nMissing vote counts by raw Status:")
    for status, count in summary["status_counter"].most_common():
        print(f"  {status}: {count}")

    print("\nMissing vote counts by HuidigeBehandelstatus:")
    for status, count in summary["behandelstatus_counter"].most_common():
        print(f"  {status}: {count}")

    print("\nAfgedaan flag distribution for missing votes:")
    for value, count in summary["afgedaan_counter"].most_common():
        print(f"  Afgedaan={value}: {count}")

    print("\nSample records per Status (up to 5 each):")
    for status, samples in summary["samples_by_status"].items():
        print(f"\nStatus: {status}")
        for sample in samples:
            nummer = sample["Nummer"] or sample["Id"]
            print(
                f"  - {nummer}: {sample['Titel']} | "
                f"HuidigeBehandelstatus={sample['HuidigeBehandelstatus']} | "
                f"Afgedaan={sample['Afgedaan']} | GestartOp={sample['GestartOp']}"
            )
if __name__ == "__main__":
    main()