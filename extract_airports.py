import pandas as pd
from pathlib import Path


FILE_PATH = Path("data/raw/flights_january_2025.xlsx")
OUTPUT_PATH = Path("data/processed/airport_codes.csv")


def main():
    df = pd.read_excel(
        FILE_PATH,
        usecols=["ORIGIN", "DEST"]
    )

    # Combine origin and destination airports
    airport_codes = pd.concat(
        [
            df["ORIGIN"],
            df["DEST"]
        ]
    ).dropna().drop_duplicates().sort_values()

    airport_df = pd.DataFrame({
        "airport_code": airport_codes
    })

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    airport_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("=" * 60)
    print("AIRPORT EXTRACTION")
    print("=" * 60)

    print(f"Unique airports: {len(airport_df):,}")
    print(f"Saved to: {OUTPUT_PATH}")

    print("\nFirst 20 airports:")
    print(airport_df.head(20).to_string(index=False))


if __name__ == "__main__":
    main()