import pandas as pd
from pathlib import Path


FILE_PATH = Path("data/raw/flights_january_2025.xlsx")


def main():
    df = pd.read_excel(FILE_PATH)

    time_columns = [
        "CRS_DEP_TIME",
        "DEP_TIME",
        "CRS_ARR_TIME",
        "ARR_TIME"
    ]

    for column in time_columns:
        print("\n" + "=" * 50)
        print(column)

        print("Minimum:", df[column].min())
        print("Maximum:", df[column].max())

        print("\nLargest values:")
        print(
            df[column]
            .dropna()
            .sort_values(ascending=False)
            .head(10)
            .to_list()
        )

        print("\n2400 count:")
        print((df[column] == 2400).sum())


if __name__ == "__main__":
    main()