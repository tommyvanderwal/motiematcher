import json
from pathlib import Path

DOC_PATH = Path(r"c:\motiematcher\bronmateriaal-onbewerkt\document\document_page_1_fullterm_20251002_235824.json")


def main() -> None:
    with DOC_PATH.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    first = records[0]
    print(f"Keys: {list(first.keys())}")
    for key in ("Id", "DocumentNummer", "Titel", "ContentType", "Inhoud"):
        if key in first:
            value = first[key]
            if isinstance(value, str) and len(value) > 120:
                value = value[:120] + "..."
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
