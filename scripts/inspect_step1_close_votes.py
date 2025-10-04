import json
import pandas as pd
from pathlib import Path

FILE = Path("c:/motiematcher/step1_close_votes_filtered.json")


def main() -> None:
    with FILE.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    records = payload.get("data", [])
    df = pd.DataFrame(records)
    print(f"Total records: {len(df)}")
    print(f"Unique Besluit_Id: {df['Besluit_Id'].nunique()}")
    print(f"Unique Matched_Zaak_Id: {df['Matched_Zaak_Id'].nunique(dropna=True)}")
    print(df[['Matched_Zaak_Id', 'Matched_Zaak_Onderwerp']].drop_duplicates().head(20))


if __name__ == "__main__":
    main()
