import json
from pathlib import Path

STEMMING_DIR = Path("c:/motiematcher/bronmateriaal-onbewerkt/stemming_complete")

def main() -> None:
    actors = set()
    for file in STEMMING_DIR.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for record in data:
            actor = record.get("ActorNaam")
            if actor:
                actors.add(actor)
    for actor in sorted(actors):
        print(actor)


if __name__ == "__main__":
    main()
