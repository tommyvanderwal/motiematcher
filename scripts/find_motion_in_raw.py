import json
from pathlib import Path

SEARCH_TERM = "noodzakelijke infrastructurele systeemtaken"

RAW_DIR = Path("c:/motiematcher/bronmateriaal-onbewerkt")


def search_json(file_path: Path) -> bool:
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to read {file_path}: {exc}")
        return False

    def contains_term(obj) -> bool:
        if isinstance(obj, dict):
            return any(contains_term(v) for v in obj.values())
        if isinstance(obj, list):
            return any(contains_term(v) for v in obj)
        if isinstance(obj, str):
            return SEARCH_TERM in obj.lower()
        return False

    return contains_term(data)


def main() -> None:
    print(f"Searching for term: {SEARCH_TERM}")
    matches = []
    for path in RAW_DIR.rglob("*.json"):
        if search_json(path):
            matches.append(str(path))
            print(f"Match: {path}")
    print(f"Total matches: {len(matches)}")


if __name__ == "__main__":
    main()
