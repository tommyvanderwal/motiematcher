import json
from pathlib import Path

FILE = Path("c:/motiematcher/bronmateriaal-onbewerkt/stemming_complete/stemming_page_1_complete_20251003_084727.json")


def main() -> None:
    with FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Records: {len(data)}")
    sample = data[0]
    for key in sample.keys():
        print(f"{key}: {sample[key]}")


if __name__ == "__main__":
    main()
