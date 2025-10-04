import json
from pathlib import Path

MOTION_LIST = Path(__file__).resolve().parents[1] / "bronmateriaal-onbewerkt" / "current" / "motion_index" / "motions_list.json"


def main() -> None:
    try:
        with MOTION_LIST.open("r", encoding="utf-8") as handle:
            motions = json.load(handle)
    except FileNotFoundError:
        print("motions_list.json not found")
        return

    print(f"Loaded {len(motions)} motion records")
    for target in (
        "d2e882c4-4cd9-42bd-918d-6439f977a9dd",
        "99ab95e2-1c66-499b-8f08-1f0063bf75c8",
    ):
        match = next((m for m in motions if m["zaak_id"] == target), None)
        if match is None:
            print(f"No record for {target}")
            continue
        nummer = match.get("nummer") or ""
        numeric_part = "".join(ch for ch in nummer if ch.isdigit())
        print("-" * 60)
        print(f"zaak_id: {match['zaak_id']}")
        print(f"nummer: {nummer}")
        print(f"numeric part: {numeric_part}")
        print(f"vergaderjaar: {match.get('vergaderjaar')}")
        print(f"volgnummer: {match.get('volgnummer')}")
        print(f"titel: {match.get('titel')}")
        print(f"onderwerp: {match.get('onderwerp')[:120] if match.get('onderwerp') else None}")

    print("-" * 60)
    sample = motions[:5]
    print("First 5 motions numeric parts vs volgnummer:")
    for motion in sample:
        nummer = motion.get("nummer") or ""
        numeric_part = "".join(ch for ch in nummer if ch.isdigit())
        print(
            f"nummer={nummer:<12} numeric_part={numeric_part:<8} volgnummer={motion.get('volgnummer')}"
        )


if __name__ == "__main__":
    main()
