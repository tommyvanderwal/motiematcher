import json
from pathlib import Path

FILE = Path("c:/motiematcher/bronmateriaal-onbewerkt/comprehensive_motion_56e10506_20251002_192415.json")


def main() -> None:
    with FILE.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    print(f"Keys: {list(payload.keys())}")
    decision = payload.get("decision", {})
    if decision:
        print(f"Decision keys: {list(decision.keys())[:20]}")
    votes = payload.get("votes", [])
    print(f"Votes: {len(votes)} entries")
    enriched = payload.get("enriched_content", {})
    print("Enriched content:")
    print(json.dumps(enriched, indent=2, ensure_ascii=False))
    agendapunt = payload.get("agendapunt")
    if agendapunt:
        print("Agendapunt keys:")
        print(list(agendapunt.keys()))
        print("Agendapunt onderwerp:", agendapunt.get('Onderwerp'))


if __name__ == "__main__":
    main()
