import pandas as pd
from pathlib import Path


CODES_FILE = Path("data/processed/airport_codes.csv")
REFERENCE_FILE = Path("data/reference/airports.dat")


COLUMNS = [
    "airport_id",
    "airport_name",
    "city",
    "country",
    "iata_code",
    "icao_code",
    "latitude",
    "longitude",
    "altitude",
    "timezone",
    "dst",
    "tz_database_time_zone",
    "type",
    "source",
]


def main():

    airport_codes = pd.read_csv(CODES_FILE)

    reference = pd.read_csv(
        REFERENCE_FILE,
        header=None,
        names=COLUMNS,
        na_values="\\N"
    )

    # Only records with an IATA code
    reference = reference[
        reference["iata_code"].notna()
        & (reference["iata_code"] != "")
    ].copy()

    duplicate_codes = (
        reference["iata_code"]
        .value_counts()
    )

    duplicate_codes = duplicate_codes[
        duplicate_codes > 1
    ]

    print("=" * 70)
    print("REFERENCE DATA DUPLICATE CHECK")
    print("=" * 70)

    print(
        f"\nDuplicate IATA codes in reference: "
        f"{len(duplicate_codes)}"
    )

    print("\nDuplicate IATA codes:")
    print(duplicate_codes.to_string())

    # Which duplicates affect OUR 352 airports?
    our_codes = set(
        airport_codes["airport_code"]
    )

    affected = duplicate_codes[
        duplicate_codes.index.isin(our_codes)
    ]

    print("\n" + "=" * 70)
    print("DUPLICATES AFFECTING OUR BTS AIRPORTS")
    print("=" * 70)

    print(
        f"\nAffected airport codes: "
        f"{len(affected)}"
    )

    if len(affected) > 0:

        print("\nAffected codes:")
        print(affected.to_string())

        print("\nDetailed records:")

        affected_records = reference[
            reference["iata_code"].isin(
                affected.index
            )
        ]

        print(
            affected_records[
                [
                    "iata_code",
                    "airport_name",
                    "city",
                    "country",
                    "icao_code",
                    "latitude",
                    "longitude",
                    "tz_database_time_zone",
                ]
            ].to_string(index=False)
        )

    else:
        print(
            "None of our 352 BTS airports "
            "are affected."
        )


if __name__ == "__main__":
    main()