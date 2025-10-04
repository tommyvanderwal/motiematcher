import pandas as pd
from pathlib import Path

BASE = Path("c:/motiematcher")
FILE = BASE / "final_linked_data.json"


def main() -> None:
    df = pd.read_json(FILE)
    print("Columns:")
    for col in df.columns:
        print(f" - {col}")
    unique_zaak = df['Matched_Zaak_Id'].nunique(dropna=True)
    print(f"Unique Matched_Zaak_Id: {unique_zaak}")
    summary = (
        df.groupby('Matched_Zaak_Id')
        .agg({
            'Matched_Zaak_Onderwerp': 'first',
            'Besluit_Id': 'nunique',
            'BesluitTekst': 'first',
        })
        .reset_index()
    )
    print(summary.head(20))


if __name__ == "__main__":
    main()
