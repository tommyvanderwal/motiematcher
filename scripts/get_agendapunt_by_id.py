import json
from pathlib import Path

TARGET_ID = "a697a3a1-bcd0-447f-82f9-08076a44d566"
AGENDAPUNT_DIR = Path("c:/motiematcher/bronmateriaal-onbewerkt/agendapunt")


def main() -> None:
    for file in sorted(AGENDAPUNT_DIR.glob("*.json")):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        records = data if isinstance(data, list) else data.get("value", [])
        for record in records:
            if record.get("Id") == TARGET_ID:
                print(f"Found in {file.name}")
                print(json.dumps(record, indent=2, ensure_ascii=False))
                return
    print("Not found")


if __name__ == "__main__":
    main()
