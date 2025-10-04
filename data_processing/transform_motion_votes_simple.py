#!/usr/bin/env python3
"""Simple pandas-based transformation of motion votes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE_DIR / "bronmateriaal-onbewerkt" / "current" / "motion_index" / "motions_enriched.json"
DEFAULT_OUTPUT_DIR = BASE_DIR / "bronmateriaal-onbewerkt" / "current" / "motion_votes"
DEFAULT_VOTES_JSONL = DEFAULT_OUTPUT_DIR / "motion_votes_flat.jsonl"
DEFAULT_VOTES_CSV = DEFAULT_OUTPUT_DIR / "motion_votes_flat.csv"
DEFAULT_SUMMARY_JSON = DEFAULT_OUTPUT_DIR / "motion_votes_summary.json"


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Flatten motions_enriched vote data with pandas")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to motions_enriched.json")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Target directory for transformed files")
    parser.add_argument("--max-motions", type=int, default=None, help="Limit number of motions for testing")
    parser.add_argument("--skip-csv", action="store_true", help="Only emit JSONL + summary (skip CSV output)")
    parser.add_argument("--skip-jsonl", action="store_true", help="Only emit CSV + summary (skip JSONL output)")
    return parser.parse_args(argv)


def load_records(path: Path, limit: Optional[int]) -> List[Dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"motions_enriched.json not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list):
        raise SystemExit("Unexpected structure for motions_enriched.json; expected a list")
    if limit is not None:
        return records[:limit]
    return records


def flatten_votes(records: Iterable[Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for record in records:
        base = {
            "motion_id": record.get("motion_id"),
            "motion_number": record.get("motion_number"),
            "motion_title": record.get("motion_title"),
            "motion_date": (record.get("motion") or {}).get("GestartOp"),
            "final_status": record.get("final_status"),
            "issues": record.get("issues") or [],
        }
        for vote in record.get("vote_breakdown") or []:
            row = base.copy()
            row.update(
                {
                    "stemming_id": vote.get("stemming_id"),
                    "vote": vote.get("vote"),
                    "fractie_id": vote.get("fractie", {}).get("Id") or vote.get("fractie_id"),
                    "fractie_afkorting": vote.get("fractie", {}).get("Afkorting"),
                    "fractie_naam": vote.get("fractie", {}).get("NaamNL"),
                    "fractie_grootte": vote.get("fractie_grootte"),
                    "actor_fractie": vote.get("actor_fractie"),
                    "actor_naam": vote.get("actor_naam"),
                    "vergissing": vote.get("vergissing"),
                    "persoon_id": vote.get("persoon", {}).get("Id") or vote.get("persoon_id"),
                    "persoon_naam": " ".join(
                        part
                        for part in (
                            vote.get("persoon", {}).get("Roepnaam"),
                            vote.get("persoon", {}).get("Tussenvoegsel"),
                            vote.get("persoon", {}).get("Achternaam"),
                        )
                        if part
                    ).strip()
                    or None,
                }
            )
            row["vote_weight"] = row.get("fractie_grootte") if row.get("fractie_grootte") is not None else 0
            row["issues_joined"] = ";".join(row["issues"])
            rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df = df.drop_duplicates(subset=["stemming_id"], keep="last")
    df["vote_weight"] = df["vote_weight"].fillna(0).astype(int)
    df["fractie_grootte"] = df["fractie_grootte"].fillna(0).astype(int)
    return df


def build_summary(df: pd.DataFrame) -> List[Dict[str, Any]]:
    if df.empty:
        return []

    group_cols = ["motion_id", "motion_number", "motion_title", "motion_date", "final_status", "issues_joined"]
    summary_rows: List[Dict[str, Any]] = []

    grouped = df.groupby(group_cols, dropna=False)
    for keys, sub_df in grouped:
        key_dict = dict(zip(group_cols, keys))
        vote_totals = sub_df.groupby("vote", dropna=False)["vote_weight"].sum().to_dict()
        unique_votes = int(sub_df["stemming_id"].nunique())
        raw_lines = int(len(sub_df))
        summary_rows.append(
            {
                **key_dict,
                "vote_totals": vote_totals,
                "vote_count": unique_votes,
                "raw_vote_lines": raw_lines,
            }
        )
    return summary_rows


def write_outputs(df: pd.DataFrame, summary: List[Dict[str, Any]], output_dir: Path, skip_csv: bool, skip_jsonl: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_target = output_dir / DEFAULT_VOTES_JSONL.name
    csv_target = output_dir / DEFAULT_VOTES_CSV.name
    summary_target = output_dir / DEFAULT_SUMMARY_JSON.name

    if not skip_csv:
        df.to_csv(csv_target, index=False, encoding="utf-8")
    if not skip_jsonl:
        with jsonl_target.open("w", encoding="utf-8") as handle:
            for record in df.to_dict(orient="records"):
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    with summary_target.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    records = load_records(args.input, args.max_motions)
    df = flatten_votes(records)
    summary = build_summary(df)
    write_outputs(df, summary, args.output_dir, args.skip_csv, args.skip_jsonl)
    print(f"Loaded {len(records)} motions")
    print(f"Vote rows after dedupe: {len(df)}")
    if summary:
        print(f"Summary rows: {len(summary)}")


if __name__ == "__main__":
    main()
