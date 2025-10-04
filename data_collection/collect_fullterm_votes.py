"""Utility to collect full-term vote data with full besluit/agendapunt/zaak linkage."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence

import requests

DEFAULT_BASE_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Stemming"
DEFAULT_START_DATE = datetime(2023, 12, 1, tzinfo=timezone.utc)


class ApiError(RuntimeError):
    """Raised when the Tweede Kamer API responds with an error."""


def isoformat(dt: datetime) -> str:
    """Return ISO 8601 timestamp with timezone offset acceptable for the API."""

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def parse_datetime(value: str) -> datetime:
    """Parse an OData datetime string into an aware datetime."""

    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)


def build_initial_params(start_date: datetime) -> Dict[str, Any]:
    """Construct the OData query parameters for the first request."""

    start_iso = isoformat(start_date)
    return {
        "$filter": (
            f"Besluit/GewijzigdOp ge {start_iso} and Besluit/Verwijderd eq false "
            "and Verwijderd eq false"
        ),
        "$orderby": "Besluit/GewijzigdOp asc",
        "$top": 100,
        "$expand": "Besluit($expand=Agendapunt($expand=Zaak)),Fractie,Persoon",
    }


def store_page(output_dir: Path, page_number: int, payload_bytes: bytes) -> Path:
    """Persist the raw API payload and return the file path."""

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    file_path = output_dir / f"stemming_page_{page_number:04d}_enriched_{timestamp}.json"
    with file_path.open("wb") as fh:
        fh.write(payload_bytes)
    return file_path


def collect(
    base_url: str = DEFAULT_BASE_URL,
    start_date: datetime = DEFAULT_START_DATE,
    output_dir: Path = Path("bronmateriaal-onbewerkt/stemming_enriched"),
    pause_s: float = 0.2,
    max_pages: Optional[int] = None,
) -> Iterable[Path]:
    """Collect vote data and store enriched pages on disk."""

    base_params = build_initial_params(start_date)
    base_filter = base_params.pop("$filter")
    top = int(base_params.get("$top", 100) or 100)

    stored_files: list[Path] = []
    cursor_filter: Optional[str] = None
    cursor_dt: Optional[datetime] = None
    page_number = 0

    while True:
        params = base_params.copy()
        filter_clauses: Sequence[str] = [base_filter]
        if cursor_filter:
            filter_clauses = [base_filter, cursor_filter]
        params["$filter"] = " and ".join(filter_clauses)

        response = requests.get(base_url, params=params, timeout=60)
        if response.status_code != 200:
            raise ApiError(
                f"API request failed with status {response.status_code}: {response.text[:500]}"
            )

        raw_payload = response.content
        payload = response.json()
        records = payload.get("value")
        if not isinstance(records, list) or not records:
            break

        page_number += 1
        file_path = store_page(output_dir, page_number, raw_payload)
        stored_files.append(file_path)

        last_record = records[-1]
        besluit = last_record.get("Besluit") or {}
        last_ts = besluit.get("GewijzigdOp") or besluit.get("ApiGewijzigdOp")
        last_id = besluit.get("Id")

        if not last_ts or not last_id:
            break

        try:
            last_dt = parse_datetime(last_ts)
        except ValueError:
            break

        if cursor_dt is None or last_dt > cursor_dt:
            cursor_dt = last_dt

        cursor_dt = cursor_dt + timedelta(milliseconds=1)
        cursor_filter = f"Besluit/GewijzigdOp gt {isoformat(cursor_dt)}"

        if max_pages and page_number >= max_pages:
            break

        if len(records) < top:
            break

        time.sleep(pause_s)

    return stored_files


def summarize(payload_iter: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Produce a compact summary of the collected payloads for quick inspection."""

    total_records = 0
    besluit_ids = set()
    zaak_ids = set()

    for payload in payload_iter:
        records = payload.get("value", [])
        total_records += len(records)
        for record in records:
            besluit = record.get("Besluit") or {}
            besluit_id = besluit.get("Id")
            if besluit_id:
                besluit_ids.add(besluit_id)
            agendapunt = besluit.get("Agendapunt") or {}
            zaken = agendapunt.get("Zaak") or []
            for zaak in zaken:
                zaak_id = zaak.get("Id")
                if zaak_id:
                    zaak_ids.add(zaak_id)

    return {
        "total_records": total_records,
        "unique_besluiten": len(besluit_ids),
        "unique_zaken": len(zaak_ids),
    }


def main() -> None:
    """Command-line entry-point."""

    parser = argparse.ArgumentParser(description="Collect enriched vote data")
    parser.add_argument("--max-pages", type=int, default=None, help="Limit number of pages to fetch")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("bronmateriaal-onbewerkt/stemming_enriched"),
        help="Directory to store enriched vote pages",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Filter besluit.GewijzigdOp >= YYYY-MM-DD (defaults to 2023-12-01)",
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=0.2,
        help="Pause between API requests in seconds (default: 0.2)",
    )
    args = parser.parse_args()

    start_date = DEFAULT_START_DATE
    if args.start_date:
        try:
            parsed = datetime.fromisoformat(args.start_date)
        except ValueError as exc:  # pragma: no cover - CLI validation
            raise SystemExit(f"Invalid --start-date value: {exc}")
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)
        start_date = parsed

    print("Collecting full-term vote data with besluit/agendapunt/zaak expansion...")
    stored_files = list(
        collect(
            start_date=start_date,
            output_dir=args.output_dir,
            pause_s=args.pause,
            max_pages=args.max_pages,
        )
    )
    print(f"Stored {len(stored_files)} enriched pages in {args.output_dir}.")

    payloads = []
    for file_path in stored_files[:3]:
        with file_path.open("r", encoding="utf-8") as fh:
            payloads.append(json.load(fh))

    if payloads:
        summary = summarize(payloads)
        print("Sample summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()