import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("c:/motiematcher/final_filtered_data.json")
TARGET_KEYWORD = "philadelphia"


def load_data() -> list[dict]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")
    with DATA_FILE.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected list of records in final_filtered_data.json")
    return data


def normalize_datetime(value: str | None) -> str | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    return value


def summarize_records(records: list[dict]) -> None:
    print(f"Total records: {len(records)}")
    by_subject: dict[str, list[dict]] = defaultdict(list)
    for item in records:
        subject = (item.get("Matched_Zaak_Onderwerp") or item.get("Zaak_Onderwerp") or "").strip()
        by_subject[subject].append(item)

    duplicates = {subj: rows for subj, rows in by_subject.items() if len(rows) > 1}
    if not duplicates:
        print("No duplicate subjects found.")
        return

    print(f"Found {len(duplicates)} subjects with duplicates.")
    for subject, rows in sorted(duplicates.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        keyword_flag = TARGET_KEYWORD in subject.lower()
        print("-" * 80)
        print(f"Subject: {subject}")
        print(f"Count: {len(rows)}{'  <-- keyword match' if keyword_flag else ''}")
        zaak_ids = {row.get('Matched_Zaak_Id') or row.get('Zaak_Id') for row in rows}
        print(f"Zaak IDs: {', '.join(sorted(filter(None, zaak_ids))) or 'n/a'}")
        besluit_ids = {row.get('Besluit_Id') for row in rows if row.get('Besluit_Id')}
        print(f"Besluit IDs: {', '.join(sorted(besluit_ids)) or 'n/a'}")

        dates = []
        for row in rows:
            for key in ("GewijzigdOp_stemming", "GewijzigdOp", "ApiGewijzigdOp"):
                if key in row and row[key]:
                    dates.append(normalize_datetime(row[key]))
        unique_dates = sorted({d for d in dates if d})
        if unique_dates:
            print("Dates observed:")
            for d in unique_dates:
                print(f"  - {d}")
        else:
            print("Dates observed: n/a")

        vote_summary: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for row in rows:
            party = row.get("ActorFractie", "Onbekend")
            vote = row.get("Soort_stemming", "?")
            vote_summary[party.strip()][vote] += 1
        print("Sample votes (counts per party & vote type):")
        for party, votes in list(vote_summary.items())[:5]:
            vote_details = ", ".join(f"{vt}:{cnt}" for vt, cnt in votes.items())
            print(f"  - {party}: {vote_details}")

        if keyword_flag:
            print("Detailed records for keyword match:")
            for idx, row in enumerate(rows, start=1):
                print(f"  Record {idx}:")
                for key in (
                    "Besluit_Id",
                    "Zaak_Id",
                    "Matched_Zaak_Id",
                    "Besluit_Soort",
                    "Totaal_Voor",
                    "Totaal_Tegen",
                    "GewijzigdOp",
                    "GewijzigdOp_stemming",
                    "ApiGewijzigdOp",
                ):
                    if key in row:
                        print(f"    {key}: {row[key]}")


def main() -> None:
    records = load_data()
    summarize_records(records)


if __name__ == "__main__":
    main()
