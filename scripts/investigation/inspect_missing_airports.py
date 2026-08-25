import pandas as pd
from pathlib import Path


FLIGHT_FILE = Path(
    "data/raw/flights_january_2025.xlsx"
)

MISSING_AIRPORTS = ["EAR", "XWA"]


def main():

    df = pd.read_excel(
        FLIGHT_FILE,
        usecols=[
            "FL_DATE",
            "MKT_UNIQUE_CARRIER",
            "MKT_CARRIER_FL_NUM",
            "ORIGIN",
            "DEST"
        ]
    )

    for airport in MISSING_AIRPORTS:

        print("=" * 70)
        print(f"AIRPORT: {airport}")
        print("=" * 70)

        origin_count = (
            df["ORIGIN"] == airport
        ).sum()

        destination_count = (
            df["DEST"] == airport
        ).sum()

        print(
            f"Origin flights:      {origin_count:,}"
        )

        print(
            f"Destination flights: {destination_count:,}"
        )

        records = df[
            (df["ORIGIN"] == airport)
            | (df["DEST"] == airport)
        ]

        print(
            f"Total occurrences:   {len(records):,}"
        )

        print("\nExample flights:")

        print(
            records.head(10).to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()