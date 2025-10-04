import json
from pathlib import Path

KEYWORD = "veltman"
BESLUIT_DIR = Path("c:/motiematcher/bronmateriaal-onbewerkt/besluit")


def main() -> None:
    hits = 0
    for file in sorted(BESLUIT_DIR.glob("*.json")):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        records = data if isinstance(data, list) else data.get("value", [])
        for record in records:
            tekst = (record.get("BesluitTekst") or "") + " " + (record.get("Opmerking") or "")
            if KEYWORD in tekst.lower():
                hits += 1
                print(f"Found keyword in {file.name}: Besluit_Id={record.get('Id')} Tekst={record.get('BesluitTekst')}")
                return
    print(f"Hits: {hits}")


if __name__ == "__main__":
    main()
