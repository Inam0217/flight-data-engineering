import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

CODES_FILE = Path("data/processed/airport_codes.csv")
REFERENCE_FILE = Path("data/reference/airports.dat")
OUTPUT_FILE = Path("data/processed/airports_enriched.csv")


# ---------------------------------------------------------
# OPENFLIGHTS DATASET COLUMNS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# VERIFIED FALLBACK AIRPORT DATA
# ---------------------------------------------------------

FALLBACK_AIRPORTS = {
    "BIH": {
        "airport_name": "Eastern Sierra Regional Airport",
        "latitude": 37.3731,
        "longitude": -118.3640,
        "timezone": "America/Los_Angeles",
    },

    "EAR": {
        "airport_name": "Kearney Regional Airport",
        "latitude": 40.7270,
        "longitude": -99.0068,
        "timezone": "America/Chicago",
    },

    "XWA": {
        "airport_name": "Williston Basin International Airport",
        "latitude": 48.2598,
        "longitude": -103.7506,
        "timezone": "America/Chicago",
    },
}


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("AIRPORT ENRICHMENT")
    print("=" * 60)

    # -----------------------------------------------------
    # 1. Load our BTS airport codes
    # -----------------------------------------------------

    airport_codes = pd.read_csv(CODES_FILE)

    print(
        f"\nBTS airports: "
        f"{len(airport_codes):,}"
    )

    # -----------------------------------------------------
    # 2. Load OpenFlights reference dataset
    # -----------------------------------------------------

    reference = pd.read_csv(
        REFERENCE_FILE,
        header=None,
        names=COLUMNS,
        na_values="\\N"
    )

    print(
        f"Reference airports: "
        f"{len(reference):,}"
    )

    # -----------------------------------------------------
    # 3. Keep only required fields
    # -----------------------------------------------------

    reference = reference[
        [
            "iata_code",
            "airport_name",
            "latitude",
            "longitude",
            "tz_database_time_zone",
        ]
    ].copy()

    # -----------------------------------------------------
    # 4. Remove records without IATA code
    # -----------------------------------------------------

    reference = reference[
        reference["iata_code"].notna()
        & (reference["iata_code"] != "")
    ].copy()

    # -----------------------------------------------------
    # 5. Keep only airports from our BTS dataset
    # -----------------------------------------------------

    reference = reference[
        reference["iata_code"].isin(
            airport_codes["airport_code"]
        )
    ].copy()

    print(
        f"Reference records after filtering: "
        f"{len(reference):,}"
    )

    print(
        f"Unique reference IATA codes: "
        f"{reference['iata_code'].nunique():,}"
    )

    # -----------------------------------------------------
    # 6. Rename columns
    # -----------------------------------------------------

    reference = reference.rename(
        columns={
            "iata_code": "airport_code",
            "tz_database_time_zone": "timezone",
        }
    )

    # -----------------------------------------------------
    # 7. Validate uniqueness
    # -----------------------------------------------------

    duplicate_codes = (
        reference["airport_code"]
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate airport codes after filtering: "
        f"{duplicate_codes:,}"
    )

    if duplicate_codes > 0:

        print("\nDuplicate airport records:")

        print(
            reference[
                reference["airport_code"].duplicated(
                    keep=False
                )
            ]
            .sort_values("airport_code")
            .to_string(index=False)
        )

        raise ValueError(
            "Duplicate airport codes found "
            "in reference data."
        )

    # -----------------------------------------------------
    # 8. Join BTS airports with reference data
    # -----------------------------------------------------

    enriched = airport_codes.merge(
        reference,
        on="airport_code",
        how="left",
        validate="one_to_one"
    )

    # -----------------------------------------------------
    # 9. Apply verified fallback data
    # -----------------------------------------------------

    print("\nApplying verified fallback data...")

    for airport_code, values in FALLBACK_AIRPORTS.items():

        mask = (
            enriched["airport_code"]
            == airport_code
        )

        for column, value in values.items():

            enriched.loc[
                mask,
                column
            ] = value

        print(
            f"  {airport_code} → fallback applied"
        )

    # -----------------------------------------------------
    # 10. Matching results
    # -----------------------------------------------------

    print("\n" + "-" * 60)
    print("MATCHING RESULTS")
    print("-" * 60)

    matched = enriched["airport_name"].notna().sum()
    unmatched = enriched["airport_name"].isna().sum()

    print(
        f"Matched airports:   {matched:,}"
    )

    print(
        f"Unmatched airports: {unmatched:,}"
    )

    if unmatched > 0:

        print("\nUnmatched airport codes:")

        print(
            enriched.loc[
                enriched["airport_name"].isna(),
                "airport_code"
            ]
            .to_string(index=False)
        )

    # -----------------------------------------------------
    # 11. Missing metadata
    # -----------------------------------------------------

    print("\n" + "-" * 60)
    print("MISSING VALUES")
    print("-" * 60)

    metadata_columns = [
        "airport_name",
        "latitude",
        "longitude",
        "timezone",
    ]

    for column in metadata_columns:

        missing = enriched[column].isna().sum()

        print(
            f"{column}: {missing:,}"
        )

    # -----------------------------------------------------
    # 12. Coordinate validation
    # -----------------------------------------------------

    invalid_latitude = (
        (enriched["latitude"] < -90)
        | (enriched["latitude"] > 90)
    ).sum()

    invalid_longitude = (
        (enriched["longitude"] < -180)
        | (enriched["longitude"] > 180)
    ).sum()

    print("\n" + "-" * 60)
    print("COORDINATE VALIDATION")
    print("-" * 60)

    print(
        f"Invalid latitude:  {invalid_latitude:,}"
    )

    print(
        f"Invalid longitude: {invalid_longitude:,}"
    )

    # -----------------------------------------------------
    # 13. Save enriched data
    # -----------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    enriched.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "-" * 60)

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    # -----------------------------------------------------
    # 14. Show sample
    # -----------------------------------------------------

    print("\nFirst 10 enriched airports:")

    print(
        enriched.head(10).to_string(
            index=False
        )
    )

    # -----------------------------------------------------
    # 15. Final summary
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("ENRICHMENT COMPLETE")
    print("=" * 60)


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    main()