import json
from pathlib import Path

FILE = Path("c:/motiematcher/bronmateriaal-onbewerkt/activiteit/activiteit_page_100_fullterm_20251003_002007.json")


def main() -> None:
    with FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    record = data[0]
    for key, value in record.items():
        if isinstance(value, str) and len(value) > 120:
            value = value[:120] + "..."
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
