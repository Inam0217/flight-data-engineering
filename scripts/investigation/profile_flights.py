import pandas as pd
from pathlib import Path


FILE_PATH = Path("data/raw/flights_january_2025.xlsx")


def main():
    print("=" * 60)
    print("FLIGHT DATA PROFILING")
    print("=" * 60)

    print(f"\nFile: {FILE_PATH}")
    print(f"Exists: {FILE_PATH.exists()}")

    if not FILE_PATH.exists():
        print("ERROR: File not found.")
        return

    # Read Excel
    df = pd.read_excel(FILE_PATH)

    print("\n--- BASIC INFORMATION ---")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\n--- COLUMNS ---")
    for i, column in enumerate(df.columns, start=1):
        print(f"{i:02d}. {column}")

    print("\n--- DATA TYPES ---")
    print(df.dtypes)

    print("\n--- MISSING VALUES ---")
    missing = df.isnull().sum()

    for column, count in missing.items():
        if count > 0:
            percentage = count / len(df) * 100
            print(
                f"{column}: "
                f"{count:,} ({percentage:.2f}%)"
            )

    print("\n--- DUPLICATE ROWS ---")
    print(f"Duplicate rows: {df.duplicated().sum():,}")

    print("\n--- DATE RANGE ---")
    print(f"Minimum date: {df['FL_DATE'].min()}")
    print(f"Maximum date: {df['FL_DATE'].max()}")

    print("\n--- AIRLINES ---")
    print(df["MKT_UNIQUE_CARRIER"].value_counts())

    print("\n--- ORIGIN AIRPORTS ---")
    print(f"Unique origins: {df['ORIGIN'].nunique():,}")

    print("\n--- DESTINATION AIRPORTS ---")
    print(f"Unique destinations: {df['DEST'].nunique():,}")

    print("\n--- CANCELLATIONS ---")
    print(
        df["CANCELLED"].value_counts(dropna=False)
    )

    print("\n--- DIVERTED ---")
    print(
        df["DIVERTED"].value_counts(dropna=False)
    )

    print("\n--- FIRST 5 ROWS ---")
    print(df.head())

    print("\n" + "=" * 60)
    print("PROFILING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()