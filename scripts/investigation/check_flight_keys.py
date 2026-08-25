import pandas as pd
from pathlib import Path


FILE_PATH = Path("data/raw/flights_january_2025.xlsx")


def main():
    df = pd.read_excel(FILE_PATH)

    key_columns = [
        "FL_DATE",
        "MKT_UNIQUE_CARRIER",
        "MKT_CARRIER_FL_NUM",
        "ORIGIN",
        "DEST"
    ]

    duplicate_keys = df.duplicated(
        subset=key_columns,
        keep=False
    )

    print("Total flights:", len(df))
    print("Duplicate business keys:", duplicate_keys.sum())

    if duplicate_keys.sum() > 0:
        print("\nExample duplicate keys:")
        print(
            df.loc[
                duplicate_keys,
                key_columns
            ].sort_values(key_columns).head(20)
        )
    else:
        print("No duplicate business keys found.")


if __name__ == "__main__":
    main()