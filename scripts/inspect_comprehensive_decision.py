import json
from pathlib import Path

FILE = Path("c:/motiematcher/bronmateriaal-onbewerkt/comprehensive_motion_56e10506_20251002_192415.json")

def main() -> None:
    with FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    decision = data.get("decision", {})
    print(json.dumps(decision, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
