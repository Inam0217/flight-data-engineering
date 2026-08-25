import pandas as pd
from pathlib import Path


FILE_PATH = Path("data/raw/flights_january_2025.xlsx")


def main():
    df = pd.read_excel(FILE_PATH)

    departure_2400 = df[df["DEP_TIME"] == 2400]

    arrival_2400 = df[df["ARR_TIME"] == 2400]

    print("=" * 70)
    print("ACTUAL DEPARTURE = 2400")
    print("=" * 70)

    print(
        departure_2400[
            [
                "FL_DATE",
                "MKT_UNIQUE_CARRIER",
                "MKT_CARRIER_FL_NUM",
                "ORIGIN",
                "DEST",
                "CRS_DEP_TIME",
                "DEP_TIME",
                "CRS_ARR_TIME",
                "ARR_TIME",
                "CANCELLED",
                "DIVERTED"
            ]
        ].to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("ACTUAL ARRIVAL = 2400")
    print("=" * 70)

    print(
        arrival_2400[
            [
                "FL_DATE",
                "MKT_UNIQUE_CARRIER",
                "MKT_CARRIER_FL_NUM",
                "ORIGIN",
                "DEST",
                "CRS_DEP_TIME",
                "DEP_TIME",
                "CRS_ARR_TIME",
                "ARR_TIME",
                "CANCELLED",
                "DIVERTED"
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()