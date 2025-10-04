#!/usr/bin/env python3
"""Build an enriched motion dataset with full text and voting details."""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_DIR = Path(__file__).resolve().parent.parent
MOTION_INDEX_FILE = BASE_DIR / "bronmateriaal-onbewerkt" / "current" / "motion_index" / "motions_list.json"
STEMMING_DIR = BASE_DIR / "bronmateriaal-onbewerkt" / "stemming_enriched"
OUTPUT_DIR = BASE_DIR / "bronmateriaal-onbewerkt" / "current" / "motion_index"
OUTPUT_FILE = OUTPUT_DIR / "motions_enriched.json"
SUMMARY_FILE = OUTPUT_DIR / "motions_enriched_summary.json"
CACHE_ROOT = BASE_DIR / "bronmateriaal-onbewerkt" / "cache"
ZAAK_CACHE_DIR = CACHE_ROOT / "zaak_documents"
PUBLICATION_CACHE_DIR = CACHE_ROOT / "document_publications"
PUBLICATION_TEXT_CACHE_DIR = CACHE_ROOT / "document_texts"

BASE_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
REQUEST_TIMEOUT = 45
API_SLEEP_SECONDS = 0.02  # 50 requests per second

def parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        cleaned = value.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def isoformat_or_none(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.isoformat()


def load_motions() -> List[Dict[str, Any]]:
    if not MOTION_INDEX_FILE.exists():
        raise SystemExit(f"Motion index not found: {MOTION_INDEX_FILE}")
    with MOTION_INDEX_FILE.open("r", encoding="utf-8") as handle:
        motions = json.load(handle)
    if not isinstance(motions, list):
        raise SystemExit("Unexpected structure for motions_list.json")
    return motions


def iter_enriched_stemmingen(directory: Path) -> Iterable[Dict[str, Any]]:
    if not directory.exists():
        raise SystemExit(f"Enriched stemming directory missing: {directory}")
    for json_path in sorted(directory.glob("*.json")):
        try:
            with json_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:  # pragma: no cover - diagnostics
            print(f"⚠️  Unable to read {json_path.name}: {exc}")
            continue
        records: Iterable[Dict[str, Any]]
        if isinstance(payload, dict):
            records = payload.get("value") or []
        elif isinstance(payload, list):
            records = payload
        else:
            records = []
        for record in records:
            if isinstance(record, dict):
                yield record


def _initial_decision_entry(besluit: Dict[str, Any]) -> Dict[str, Any]:
    agendapunt = besluit.get("Agendapunt") or {}
    decision = {
        "besluit_id": besluit.get("Id"),
        "besluit": {
            "Id": besluit.get("Id"),
            "Agendapunt_Id": besluit.get("Agendapunt_Id"),
            "StemmingsSoort": besluit.get("StemmingsSoort"),
            "BesluitSoort": besluit.get("BesluitSoort"),
            "BesluitTekst": besluit.get("BesluitTekst"),
            "Status": besluit.get("Status"),
            "AgendapuntZaakBesluitVolgorde": besluit.get("AgendapuntZaakBesluitVolgorde"),
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
        "votes": [],
        "vote_totals": defaultdict(int),
        "votes_by_id": {},
        "votes_without_id": [],
        "duplicate_vote_ids": set(),
        "linked_zaak_ids": set(),
        "agendapunt_zaken": [],
        "linking_notes": set(),
        "raw_vote_count": 0,
        "last_changed": parse_iso_datetime(besluit.get("ApiGewijzigdOp") or besluit.get("GewijzigdOp")),
    }
    return decision


def _normalise_vote(record: Dict[str, Any]) -> Dict[str, Any]:
    fractie = record.get("Fractie") or {}
    persoon = record.get("Persoon") or {}
    return {
        "stemming_id": record.get("Id"),
        "vote": record.get("Soort"),
        "fractie_grootte": record.get("FractieGrootte"),
        "actor_naam": record.get("ActorNaam"),
        "actor_fractie": record.get("ActorFractie"),
        "vergissing": record.get("Vergissing"),
        "fractie_id": record.get("Fractie_Id"),
        "persoon_id": record.get("Persoon_Id"),
        "fractie": {
            "Id": fractie.get("Id"),
            "Afkorting": fractie.get("Afkorting"),
            "NaamNL": fractie.get("NaamNL"),
        },
        "persoon": {
            "Id": persoon.get("Id"),
            "Roepnaam": persoon.get("Roepnaam"),
            "Achternaam": persoon.get("Achternaam"),
            "Tussenvoegsel": persoon.get("Tussenvoegsel"),
        },
    }


def build_motion_vote_lookup(directory: Path) -> Dict[str, List[Dict[str, Any]]]:
    decisions_by_id: Dict[str, Dict[str, Any]] = {}

    for record in iter_enriched_stemmingen(directory):
        besluit = record.get("Besluit") or {}
        besluit_id = besluit.get("Id") or record.get("Besluit_Id")
        if not besluit_id:
            continue

        entry = decisions_by_id.setdefault(besluit_id, _initial_decision_entry(besluit))
        vote_info = _normalise_vote(record)
        vote_changed = parse_iso_datetime(record.get("ApiGewijzigdOp") or record.get("GewijzigdOp"))
        vote_id = vote_info.get("stemming_id")
        entry["raw_vote_count"] += 1

        if vote_changed and (entry["last_changed"] is None or vote_changed > entry["last_changed"]):
            entry["last_changed"] = vote_changed

        if vote_id:
            existing = entry["votes_by_id"].get(vote_id)
            if existing:
                entry["duplicate_vote_ids"].add(vote_id)
                existing_changed = existing.get("_changed")
                if existing_changed and vote_changed and vote_changed <= existing_changed:
                    continue
            vote_info["_changed"] = vote_changed
            entry["votes_by_id"][vote_id] = vote_info
        else:
            entry["votes_without_id"].append(vote_info)

        agendapunt = besluit.get("Agendapunt") or {}
        zaak_entries = agendapunt.get("Zaak") or []

        if not entry["agendapunt_zaken"]:
            entry["agendapunt_zaken"] = [
                {
                    "id": zaak.get("Id"),
                    "soort": zaak.get("Soort"),
                    "nummer": zaak.get("Nummer"),
                    "volgnummer": zaak.get("Volgnummer"),
                }
                for zaak in zaak_entries
            ]

        motie_candidates = [
            zaak for zaak in zaak_entries if (zaak.get("Soort") or "").lower() == "motie"
        ]
        volgorde = besluit.get("AgendapuntZaakBesluitVolgorde")
        target_zaak = None

        if isinstance(volgorde, int) and 1 <= volgorde <= len(zaak_entries):
            target_zaak = zaak_entries[volgorde - 1]
        else:
            if isinstance(volgorde, int):
                entry["linking_notes"].add("volgorde_out_of_range")
            elif volgorde is None:
                entry["linking_notes"].add("volgorde_missing")
            else:
                entry["linking_notes"].add("volgorde_invalid_type")
            if len(motie_candidates) == 1:
                target_zaak = motie_candidates[0]
                entry["linking_notes"].add("fallback_single_motie")
            elif len(motie_candidates) > 1:
                entry["linking_notes"].add("ambiguous_motie_candidates")
            elif zaak_entries:
                entry["linking_notes"].add("no_motie_candidates")

        if target_zaak:
            target_id = target_zaak.get("Id")
            target_soort = (target_zaak.get("Soort") or "").lower()
            if target_soort == "motie" and target_id:
                entry["linked_zaak_ids"].add(target_id)
            elif target_id:
                entry["linking_notes"].add(f"target_not_motie:{target_soort or 'onbekend'}")

    decisions_by_zaak: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for entry in decisions_by_id.values():
        unique_votes: List[Dict[str, Any]] = []
        vote_totals: Dict[str, int] = defaultdict(int)

        for vote in entry["votes_by_id"].values():
            vote_clean = dict(vote)
            vote_clean.pop("_changed", None)
            unique_votes.append(vote_clean)
            vote_type = vote_clean.get("vote") or "Onbekend"
            weight = vote_clean.get("fractie_grootte") or 0
            vote_totals[vote_type] += weight

        for vote in entry["votes_without_id"]:
            vote_clean = dict(vote)
            unique_votes.append(vote_clean)
            vote_type = vote_clean.get("vote") or "Onbekend"
            weight = vote_clean.get("fractie_grootte") or 0
            vote_totals[vote_type] += weight

        entry["votes"] = unique_votes
        entry["vote_totals"] = vote_totals

        final_entry = {
            "besluit_id": entry["besluit_id"],
            "besluit": entry["besluit"],
            "agendapunt": entry["agendapunt"],
            "vote_totals": dict(entry["vote_totals"]),
            "votes": [dict(vote) for vote in entry["votes"]],
            "zaak_ids": sorted(entry["linked_zaak_ids"]),
            "agendapunt_zaken": [dict(zaak) for zaak in entry["agendapunt_zaken"]],
            "motie_candidate_ids": sorted(
                {
                    zaak.get("id")
                    for zaak in entry["agendapunt_zaken"]
                    if (zaak.get("soort") or "").lower() == "motie" and zaak.get("id")
                }
            ),
            "linking_notes": sorted(entry["linking_notes"]),
            "vote_count": len(unique_votes),
            "raw_vote_count": entry["raw_vote_count"],
            "duplicates_removed": entry["raw_vote_count"] - len(unique_votes),
            "last_changed": isoformat_or_none(entry["last_changed"]),
        }
        for zaak_id in final_entry["zaak_ids"]:
            decisions_by_zaak[zaak_id].append(final_entry)

    for records in decisions_by_zaak.values():
        records.sort(key=lambda item: item.get("last_changed") or "", reverse=True)

    return decisions_by_zaak


class MotionTextFetcher:
    def __init__(
        self,
        base_url: str,
        cache_root: Path,
        refresh: bool = False,
        rate_sleep: float = API_SLEEP_SECONDS,
        max_api_calls: Optional[int] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.refresh = refresh
        self.rate_sleep = rate_sleep
        self.max_api_calls = max_api_calls
        self.api_calls_made = 0

        self.zaak_cache_dir = cache_root / "zaak_documents"
        self.publication_cache_dir = cache_root / "document_publications"
        self.publication_text_cache_dir = cache_root / "document_texts"
        self.zaak_cache_dir.mkdir(parents=True, exist_ok=True)
        self.publication_cache_dir.mkdir(parents=True, exist_ok=True)
        self.publication_text_cache_dir.mkdir(parents=True, exist_ok=True)

        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=0.4,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "MotieMatcher-Enrichment/1.0",
            "Accept": "application/json",
        })
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _can_call_api(self) -> bool:
        if self.max_api_calls is None:
            return True
        return self.api_calls_made < self.max_api_calls

    def _register_call(self) -> None:
        self.api_calls_made += 1

    def _zaak_cache_path(self, zaak_id: str) -> Path:
        return self.zaak_cache_dir / f"{zaak_id}.json"

    def _publication_text_path(self, publication_id: str) -> Path:
        return self.publication_text_cache_dir / f"{publication_id}.json"

    def _find_publication_binary(self, publication_id: str) -> Optional[Path]:
        matches = list(self.publication_cache_dir.glob(f"{publication_id}.*"))
        if matches:
            return matches[0]
        return None

    def _guess_extension(self, content_type: Optional[str]) -> str:
        if not content_type:
            return ".bin"
        value = content_type.lower()
        if "xml" in value:
            return ".xml"
        if "json" in value:
            return ".json"
        if "pdf" in value:
            return ".pdf"
        if "word" in value or "msword" in value:
            return ".docx"
        if "html" in value:
            return ".html"
        return ".bin"

    def _sleep(self) -> None:
        if self.rate_sleep:
            time.sleep(self.rate_sleep)

    def _load_zaak_payload(self, zaak_id: str, issues: List[str]) -> Optional[Dict[str, Any]]:
        cache_path = self._zaak_cache_path(zaak_id)
        if cache_path.exists() and not self.refresh:
            try:
                with cache_path.open("r", encoding="utf-8") as handle:
                    return json.load(handle)
            except json.JSONDecodeError:
                issues.append("cached_zaak_corrupt")
                cache_path.unlink(missing_ok=True)

        if not self._can_call_api():
            issues.append("api_limit_reached_zaak")
            return None

        params = {
            "$expand": "Document($expand=HuidigeDocumentVersie($expand=DocumentPublicatie,DocumentPublicatieMetadata))",
            "$filter": f"Id eq {zaak_id}",
            "$top": 1,
        }
        url = f"{self.base_url}/Zaak"
        try:
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            self._register_call()
            if response.status_code == 404:
                issues.append("zaak_not_found")
                return None
            response.raise_for_status()
            payload = response.json()
            records = payload.get("value") if isinstance(payload, dict) else None
            if not records:
                issues.append("zaak_not_found")
                return None
            record = records[0]
            with cache_path.open("w", encoding="utf-8") as handle:
                json.dump(record, handle, ensure_ascii=False, indent=2)
            return record
        except requests.RequestException as exc:
            issues.append(f"zaak_fetch_error:{exc.__class__.__name__}")
            return None
        finally:
            self._sleep()

    def _ensure_publication_binary(self, publication: Dict[str, Any], issues: List[str]) -> Tuple[Optional[Path], bool]:
        publication_id = publication.get("Id")
        if not publication_id:
            issues.append("publication_missing_id")
            return None, False

        cached_path = self._find_publication_binary(publication_id)
        if cached_path and not self.refresh:
            return cached_path, True

        if not self._can_call_api():
            issues.append("api_limit_reached_publication")
            return None, False

        url = f"{self.base_url}/DocumentPublicatie({publication_id})/Resource"
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 404:
                issues.append("publication_resource_not_found")
                return None, False
            response.raise_for_status()
            content_type = response.headers.get("Content-Type") or publication.get("ContentType")
            ext = self._guess_extension(content_type)
            target_path = self.publication_cache_dir / f"{publication_id}{ext}"
            target_path.write_bytes(response.content)
            self._register_call()
            self._sleep()
            return target_path, False
        except requests.RequestException as exc:
            issues.append(f"publication_fetch_error:{exc.__class__.__name__}")
            return None, False

    def _extract_text_from_publication(self, publication: Dict[str, Any], binary_path: Path, issues: List[str]) -> Optional[str]:
        content_type = (publication.get("ContentType") or "").lower()
        if binary_path.suffix.lower() == ".xml" or "xml" in content_type:
            try:
                text = binary_path.read_text(encoding="utf-8", errors="replace")
            except UnicodeDecodeError:
                issues.append("publication_decode_error")
                return None
            parsed = extract_plain_text_from_xml(text)
            if not parsed:
                issues.append("publication_text_empty")
            return parsed
        if "text" in content_type:
            try:
                return binary_path.read_text(encoding="utf-8", errors="replace")
            except UnicodeDecodeError:
                issues.append("publication_decode_error")
                return None
        issues.append("publication_unsupported_type")
        return None

    def _prioritise_documents(
        self,
        documents: List[Dict[str, Any]],
        motion_number: Optional[str],
        motion_title: Optional[str],
    ) -> List[Dict[str, Any]]:
        def score(document: Dict[str, Any]) -> Tuple[int, int]:
            value = 0
            soort = (document.get("Soort") or "").lower()
            if "motie" in soort:
                value += 100
            doc_nummer = document.get("DocumentNummer") or ""
            if motion_number and motion_number in doc_nummer:
                value += 40
            onderwerp = document.get("Onderwerp") or ""
            titel = document.get("Titel") or ""
            norm_title = (motion_title or "").lower()
            if norm_title and norm_title in (titel or "").lower():
                value += 15
            if norm_title and norm_title in (onderwerp or "").lower():
                value += 25
            version = (document.get("HuidigeDocumentVersie") or {})
            publications = version.get("DocumentPublicatie") or []
            if any("xml" in (pub.get("ContentType") or "").lower() for pub in publications):
                value += 120
            length = document.get("ContentLength") or 0
            return value, length

        return sorted(documents, key=score, reverse=True)

    def _iter_candidate_publications(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        version = document.get("HuidigeDocumentVersie") or {}
        publications = version.get("DocumentPublicatie") or []

        def pub_score(pub: Dict[str, Any]) -> Tuple[int, int]:
            ctype = (pub.get("ContentType") or "").lower()
            score = 0
            if "xml" in ctype:
                score += 100
            elif "text" in ctype:
                score += 80
            elif "html" in ctype:
                score += 60
            elif "pdf" in ctype:
                score += 20
            length = pub.get("ContentLength") or 0
            return score, length

        return sorted(publications, key=pub_score, reverse=True)

    def fetch_motion_text(self, motion: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        motion_id_raw = motion.get("zaak_id") or motion.get("Id")
        motion_id = str(motion_id_raw) if motion_id_raw else None
        if not motion_id:
            return {
                "content": None,
                "content_char_count": 0,
                "source": None,
                "issues": ["missing_zaak_id"],
            }

        motion_number = motion.get("nummer") or motion.get("Nummer")
        motion_title = None
        normalised = motion.get("normalised") or {}
        if isinstance(normalised, dict):
            motion_title = normalised.get("titel") or normalised.get("onderwerp")
        motion_title = motion_title or motion.get("Titel") or motion.get("Onderwerp")

        zaak_payload = self._load_zaak_payload(motion_id, issues)
        if not zaak_payload:
            return {
                "content": None,
                "content_char_count": 0,
                "source": None,
                "issues": issues or ["zaak_payload_missing"],
            }

        documents = zaak_payload.get("Document") or []
        if not documents:
            issues.append("zaak_has_no_documents")
            return {
                "content": None,
                "content_char_count": 0,
                "source": None,
                "issues": issues,
            }

        documents_sorted = self._prioritise_documents(documents, motion_number, motion_title)
        for document in documents_sorted:
            publications = self._iter_candidate_publications(document)
            if not publications:
                issues.append("document_missing_publications")
                continue

            for publication in publications:
                publication_id = publication.get("Id")
                text_cache_path = self._publication_text_path(publication_id) if publication_id else None
                if text_cache_path and text_cache_path.exists() and not self.refresh:
                    try:
                        with text_cache_path.open("r", encoding="utf-8") as handle:
                            cached = json.load(handle)
                        cached.setdefault("issues", [])
                        cached["issues"] = list(set(issues + cached.get("issues", [])))
                        cached.setdefault("source", {})
                        cached["source"]["cached"] = True
                        return cached
                    except json.JSONDecodeError:
                        text_cache_path.unlink(missing_ok=True)

                binary_path, was_cached = self._ensure_publication_binary(publication, issues)
                if not binary_path:
                    continue

                content = self._extract_text_from_publication(publication, binary_path, issues)
                if content:
                    result = {
                        "content": content,
                        "content_char_count": len(content),
                        "source": {
                            "document_id": document.get("Id"),
                            "document_nummer": document.get("DocumentNummer"),
                            "document_soort": document.get("Soort"),
                            "publication_id": publication.get("Id"),
                            "publication_content_type": publication.get("ContentType"),
                            "publication_length": publication.get("ContentLength"),
                            "cached": was_cached,
                            "binary_path": str(binary_path.relative_to(BASE_DIR)),
                        },
                        "issues": issues,
                    }
                    if text_cache_path:
                        with text_cache_path.open("w", encoding="utf-8") as handle:
                            json.dump(result, handle, ensure_ascii=False, indent=2)
                    return result

            issues.append("document_no_parseable_publication")

        if not issues:
            issues.append("no_document_text_retrieved")
        return {
            "content": None,
            "content_char_count": 0,
            "source": None,
            "issues": issues,
        }


def extract_plain_text_from_xml(xml_text: str) -> Optional[str]:
    try:
        from xml.etree import ElementTree as ET

        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None

    segments: List[str] = []
    for text in root.itertext():
        cleaned = re.sub(r"\s+", " ", text or "").strip()
        if cleaned:
            segments.append(cleaned)

    if not segments:
        return None

    deduped: List[str] = []
    previous: Optional[str] = None
    for segment in segments:
        if segment == previous:
            continue
        deduped.append(segment)
        previous = segment

    return "\n".join(deduped)


def determine_final_status(decision: Optional[Dict[str, Any]]) -> Optional[str]:
    if not decision:
        return None
    besluit = decision.get("besluit") or {}
    status = besluit.get("BesluitSoort") or besluit.get("BesluitTekst")
    if status:
        return status
    return besluit.get("Status")


def build_record(
    motion: Dict[str, Any],
    vote_records: List[Dict[str, Any]],
    text_info: Dict[str, Any],
) -> Dict[str, Any]:
    motion_id_raw = motion.get("zaak_id") or motion.get("Id")
    motion_id = str(motion_id_raw) if motion_id_raw else None
    motion_number = motion.get("nummer") or motion.get("Nummer")
    motion_title = None
    normalised = motion.get("normalised") or {}
    if isinstance(normalised, dict):
        motion_title = normalised.get("titel") or normalised.get("onderwerp")
    motion_title = motion_title or motion.get("Titel") or motion.get("Onderwerp")

    final_decision = vote_records[0] if vote_records else None
    vote_totals = final_decision.get("vote_totals") if final_decision else {}
    vote_breakdown = final_decision.get("votes") if final_decision else []

    combined_issues = set(text_info.get("issues", []))
    if not vote_records:
        combined_issues.add("no_vote_data")
    for record in vote_records:
        for note in record.get("linking_notes", []):
            combined_issues.add(f"vote_link:{note}")

    decision_summaries = [
        {
            "besluit_id": record.get("besluit_id"),
            "besluit_soort": (record.get("besluit") or {}).get("BesluitSoort"),
            "besluit_tekst": (record.get("besluit") or {}).get("BesluitTekst"),
            "last_changed": record.get("last_changed"),
            "vote_totals": record.get("vote_totals"),
            "vote_count": record.get("vote_count"),
            "raw_vote_count": record.get("raw_vote_count"),
            "duplicates_removed": record.get("duplicates_removed"),
            "linked_zaak_ids": record.get("zaak_ids"),
            "motie_candidate_ids": record.get("motie_candidate_ids"),
            "linking_notes": record.get("linking_notes"),
        }
        for record in vote_records
    ]

    for record in vote_records:
        duplicates_removed = record.get("duplicates_removed") or 0
        if duplicates_removed:
            combined_issues.add(f"vote_dedup:removed_{duplicates_removed}")

    combined_issues = sorted(combined_issues)

    return {
        "motion_id": motion_id,
        "motion_number": motion_number,
        "motion_title": motion_title,
        "motion": motion,
        "text": text_info,
        "final_status": determine_final_status(final_decision),
        "vote_totals": vote_totals,
        "vote_breakdown": vote_breakdown,
        "decision_summaries": decision_summaries,
        "issues": combined_issues,
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enrich motion dataset with votes and text")
    parser.add_argument("--max-motions", type=int, default=None, help="Process only the first N motions (for testing)")
    parser.add_argument("--skip-text", action="store_true", help="Skip fetching motion text")
    parser.add_argument("--refresh-text", action="store_true", help="Ignore cached text/publication files and refetch")
    parser.add_argument("--max-api-calls", type=int, default=None, help="Limit the number of remote API calls (mainly for testing)")
    return parser.parse_args(argv)


def ensure_directories() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    ZAAK_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    PUBLICATION_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    PUBLICATION_TEXT_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def run(args: argparse.Namespace) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    ensure_directories()
    motions = load_motions()
    motion_count = len(motions)
    print(f"Loaded {motion_count} motions from motion index")

    vote_lookup = build_motion_vote_lookup(STEMMING_DIR)
    print(f"Built vote index for {len(vote_lookup)} motions")

    fetcher = MotionTextFetcher(
        base_url=BASE_URL,
        cache_root=CACHE_ROOT,
        refresh=args.refresh_text,
        max_api_calls=None if args.skip_text else args.max_api_calls,
    )

    enriched_records: List[Dict[str, Any]] = []
    text_coverage = Counter()
    vote_coverage = Counter()
    issue_counter = Counter()

    limit = args.max_motions if args.max_motions is not None else motion_count

    for idx, motion in enumerate(motions):
        if idx >= limit:
            break
        motion_id_raw = motion.get("zaak_id") or motion.get("Id")
        motion_id = str(motion_id_raw) if motion_id_raw else None
        vote_records = vote_lookup.get(motion_id, []) if motion_id else []
        if vote_records:
            vote_coverage["with_vote"] += 1
        else:
            vote_coverage["without_vote"] += 1

        if args.skip_text:
            text_info = {
                "content": None,
                "content_char_count": 0,
                "source": None,
                "issues": ["text_fetch_skipped"],
            }
        else:
            text_info = fetcher.fetch_motion_text(motion)
        if text_info.get("content"):
            text_coverage["with_text"] += 1
        else:
            text_coverage["without_text"] += 1
        for issue in text_info.get("issues", []):
            issue_counter[issue] += 1
        if not vote_records:
            issue_counter["no_vote_data"] += 1

        enriched_records.append(build_record(motion, vote_records, text_info))

        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1} motions")

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "motion_count_input": motion_count,
        "motion_count_output": len(enriched_records),
        "limit_applied": limit != motion_count,
        "vote_coverage": dict(vote_coverage),
        "text_coverage": dict(text_coverage),
        "issue_counts": dict(issue_counter),
        "api_calls_used": fetcher.api_calls_made,
    }

    return enriched_records, summary


def write_outputs(records: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    with OUTPUT_FILE.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, ensure_ascii=False, indent=2)
    with SUMMARY_FILE.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
    print(f"Saved enriched dataset to {OUTPUT_FILE.relative_to(BASE_DIR)}")
    print(f"Saved summary to {SUMMARY_FILE.relative_to(BASE_DIR)}")


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    records, summary = run(args)
    write_outputs(records, summary)


if __name__ == "__main__":
    main(sys.argv[1:])
