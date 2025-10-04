from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Iterable, List, Dict, Any, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "bronmateriaal-onbewerkt" / "current" / "zaak_current"
OUTPUT_DIR = BASE_DIR / "bronmateriaal-onbewerkt" / "current" / "motion_index"
OUTPUT_FILE = OUTPUT_DIR / "motions_list.json"
SUMMARY_FILE = OUTPUT_DIR / "motions_summary.json"
DEFAULT_START_DATE = date(2023, 12, 6)  # Start of the 2023-2027 parliamentary term


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    return None


def _coerce_iso(value: Any) -> str | None:
    text = _clean_text(value)
    if not text:
        return None
    try:
        # datetime.fromisoformat can parse offsets like +02:00 directly.
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    return dt.isoformat()


def _parse_start_date() -> date:
    override = None
    for arg in sys.argv[1:]:
        if arg.startswith("--start-date="):
            override = arg.split("=", 1)[1]
            break
    if not override:
        return DEFAULT_START_DATE
    try:
        return datetime.fromisoformat(override).date()
    except ValueError as exc:
        raise SystemExit(f"Invalid --start-date value '{override}': {exc}")


def load_json_records(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "value" in payload and isinstance(payload["value"], list):
        return payload["value"]
    raise ValueError(f"Unexpected JSON structure in {path}")


def _build_record(raw: Dict[str, Any], sources: Iterable[str]) -> Dict[str, Any]:
    """Return enriched motion dictionary keeping all original fields."""

    normalized: Dict[str, Any] = {
        "zaak_id": (raw.get("Id") or "").strip(),
        "nummer": (raw.get("Nummer") or "").strip() or None,
        "titel": _clean_text(raw.get("Titel")),
        "onderwerp": _clean_text(raw.get("Onderwerp")),
        "status": _clean_text(raw.get("Status")),
        "vergaderjaar": _clean_text(raw.get("Vergaderjaar")),
        "volgnummer": _safe_int(raw.get("Volgnummer")),
        "organisatie": _clean_text(raw.get("Organisatie")),
        "gestart_op": _coerce_iso(raw.get("GestartOp")),
        "gewijzigd_op": _coerce_iso(raw.get("GewijzigdOp")),
        "afgedaan": _safe_bool(raw.get("Afgedaan")),
    }

    record: Dict[str, Any] = dict(raw)
    record.update({
        "bronbestanden": sorted(set(sources)),
        "zaak_id": normalized["zaak_id"],
        "nummer": normalized["nummer"] if normalized["nummer"] is not None else record.get("Nummer"),
        "normalised": normalized,
    })

    # Preserve normalized ISO timestamps even if original fields remain.
    if normalized["gestart_op"]:
        record.setdefault("GestartOp_norm", normalized["gestart_op"])
    if normalized["gewijzigd_op"]:
        record.setdefault("GewijzigdOp_norm", normalized["gewijzigd_op"])

    return record


def collect_motions(start_date: date) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not INPUT_DIR.exists():
        raise SystemExit(f"Input directory not found: {INPUT_DIR}")

    raw_by_id: Dict[str, Dict[str, Any]] = {}
    sources_by_id: Dict[str, set[str]] = defaultdict(set)
    processed_files: List[str] = []

    for json_path in sorted(INPUT_DIR.glob("*.json")):
        processed_files.append(json_path.name)
        try:
            records = load_json_records(json_path)
        except Exception as error:
            raise SystemExit(f"Failed to parse {json_path}: {error}") from error

        for raw in records:
            if not isinstance(raw, dict):
                continue
            soort = _clean_text(raw.get("Soort"))
            if soort is None or "motie" not in soort.lower():
                continue

            gestart_op_iso = _coerce_iso(raw.get("GestartOp"))
            gestart_op_date = None
            if gestart_op_iso:
                try:
                    gestart_op_date = datetime.fromisoformat(gestart_op_iso).date()
                except ValueError:
                    gestart_op_date = None
            if gestart_op_date and gestart_op_date < start_date:
                continue

            motion_id = (raw.get("Id") or "").strip()
            if not motion_id:
                continue
            raw_by_id[motion_id] = raw
            sources_by_id[motion_id].add(json_path.name)

    motions: List[Dict[str, Any]] = []
    nummers_counter: Counter[str] = Counter()
    vergaderjaar_counter: Counter[str] = Counter()
    earliest: datetime | None = None
    latest: datetime | None = None

    for motion_id, raw in raw_by_id.items():
        sources = sources_by_id.get(motion_id, {"unknown"})
        motion = _build_record(raw, sources)
        motions.append(motion)

        nummer = motion.get("nummer")
        if nummer:
            nummers_counter[str(nummer)] += 1
        vergaderjaar = motion.get("normalised", {}).get("vergaderjaar") or motion.get("Vergaderjaar")
        if vergaderjaar:
            vergaderjaar_counter[str(vergaderjaar)] += 1
        gestart_op = motion.get("normalised", {}).get("gestart_op") or motion.get("GestartOp_norm")
        if gestart_op:
            try:
                dt = datetime.fromisoformat(gestart_op)
                earliest = dt if earliest is None or dt < earliest else earliest
                latest = dt if latest is None or dt > latest else latest
            except ValueError:
                continue

    motions.sort(key=lambda m: (
        (m.get("normalised", {}).get("gestart_op") or m.get("GestartOp_norm") or ""),
        str(m.get("nummer") or m.get("Nummer") or ""),
        m.get("zaak_id") or m.get("Id"),
    ))

    duplicate_nummers = sorted([nummer for nummer, count in nummers_counter.items() if count > 1])

    summary: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "start_date_filter": start_date.isoformat(),
        "source_files": processed_files,
        "total_motions": len(motions),
        "unique_motion_ids": len(raw_by_id),
        "unique_motion_numbers": len(nummers_counter),
        "duplicate_motion_numbers": duplicate_nummers,
        "counts_per_vergaderjaar": dict(sorted(vergaderjaar_counter.items())),
        "date_range": {
            "earliest": earliest.isoformat() if earliest else None,
            "latest": latest.isoformat() if latest else None,
        },
    }

    return motions, summary


def write_outputs(motions: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    with OUTPUT_FILE.open("w", encoding="utf-8") as handle:
        json.dump(motions, handle, ensure_ascii=False, indent=2)

    with SUMMARY_FILE.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)


def main() -> None:
    start_date = _parse_start_date()
    motions, summary = collect_motions(start_date)
    write_outputs(motions, summary)
    print(f"✅ Generated {len(motions)} motions spanning {summary['date_range']}")
    if summary["duplicate_motion_numbers"]:
        print(f"⚠️ Found duplicate motion numbers: {summary['duplicate_motion_numbers']}")
    print(f"📄 List saved to: {OUTPUT_FILE.relative_to(BASE_DIR)}")
    print(f"📝 Summary saved to: {SUMMARY_FILE.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
