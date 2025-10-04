import json
from io import TextIOWrapper
from pathlib import Path
from zipfile import ZipFile


def _load_latest_snapshot() -> list[dict]:
    json_path = Path(r"c:\motiematcher\bronmateriaal-onbewerkt\current\zaak_current\zaak_current_parliament_20251003_174519.json")
    zip_path = json_path.with_suffix(".zip")

    if json_path.exists():
        with json_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    if zip_path.exists():
        with ZipFile(zip_path) as archive:
            inner_name = archive.namelist()[0]
            with archive.open(inner_name, "r") as raw:
                with TextIOWrapper(raw, encoding="utf-8") as handle:
                    return json.load(handle)

    raise FileNotFoundError(f"Geen snapshot gevonden op {json_path} of {zip_path}")


def main() -> None:
    data = _load_latest_snapshot()
    record = data[0]
    print(sorted(record.keys()))
    doc_field = record.get("Documenten") or record.get("Document")
    if doc_field is None:
        print("No document field present")
    else:
        print(f"Document field type: {type(doc_field)}")
        if isinstance(doc_field, list) and doc_field:
            print(doc_field[0].keys())


if __name__ == "__main__":
    main()
