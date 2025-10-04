import json
from pathlib import Path

FILE = Path("c:/motiematcher/step1_recent_filtered_enriched_data.json")


def main() -> None:
    with FILE.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    zaken = payload.get("zaken", [])
    total = len(zaken)
    with_votes = [z for z in zaken if z.get("has_voting_data")]
    print(f"Total zaken: {total}")
    print(f"Met stemdata: {len(with_votes)}")
    if with_votes:
        sample = with_votes[0]
        print("Voorbeeld met stemdata:")
        print(json.dumps(sample, indent=2, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()
