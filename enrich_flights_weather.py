import pandas as pd
from pathlib import Path


FLIGHT_FILE = Path(
    "data/processed/flights_transformed.csv"
)

WEATHER_FILE = Path(
    "data/processed/weather_january_2025_all_airports_utc.csv"
)

OUTPUT_FILE = Path(
    "data/processed/flights_weather.csv"
)


MAX_WEATHER_DISTANCE_MINUTES = 60


def main():

    print("=" * 80)
    print("PRODUCTION FLIGHT → WEATHER ENRICHMENT")
    print("=" * 80)

    # =====================================================
    # LOAD FLIGHTS
    # =====================================================

    print("\nLoading flights...")

    flights = pd.read_csv(
        FLIGHT_FILE,
        parse_dates=[
            "actual_departure_utc",
            "actual_arrival_utc"
        ]
    )

    print(
        f"Flights loaded: {len(flights):,}"
    )

    # =====================================================
    # LOAD WEATHER
    # =====================================================

    print("\nLoading weather...")

    weather = pd.read_csv(
        WEATHER_FILE,
        parse_dates=[
            "weather_timestamp_utc"
        ]
    )

    print(
        f"Weather rows loaded: {len(weather):,}"
    )

    # =====================================================
    # NORMALIZE KEYS
    # =====================================================

    flights["ORIGIN"] = (
        flights["ORIGIN"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    weather["airport_code"] = (
        weather["airport_code"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # =====================================================
    # WEATHER AIRPORTS
    # =====================================================

    weather_airports = set(
        weather["airport_code"].unique()
    )

    print(
        f"\nWeather airports: "
        f"{len(weather_airports):,}"
    )

    # =====================================================
    # PRESERVE ORIGINAL FLIGHTS
    # =====================================================

    flights["flight_row_id"] = (
        range(len(flights))
    )

    # =====================================================
    # WEATHER COLUMNS
    # =====================================================

    weather_columns = [
        "weather_timestamp",
        "temperature",
        "humidity",
        "precipitation",
        "rain",
        "snowfall",
        "wind_speed",
        "wind_direction",
        "visibility",
        "cloud_cover",
        "weather_code",
        "timezone",
        "weather_timestamp_utc"
    ]

    # =====================================================
    # INITIALIZE WEATHER COLUMNS
    # =====================================================

    for column in weather_columns:

        flights[
            f"departure_weather_{column}"
        ] = pd.NA

    flights[
        "weather_time_difference_minutes"
    ] = pd.NA

    # =====================================================
    # DETERMINE VALID FLIGHTS
    # =====================================================

    valid_mask = (
        flights["actual_departure_utc"].notna()
        &
        flights["ORIGIN"].isin(
            weather_airports
        )
    )

    valid_flights = flights[
        valid_mask
    ].copy()

    print(
        f"\nFlights with valid departure "
        f"and weather airport: "
        f"{len(valid_flights):,}"
    )

    print(
        f"Flights not eligible for weather match: "
        f"{len(flights) - len(valid_flights):,}"
    )

    # =====================================================
    # AIRPORT-BY-AIRPORT MATCHING
    # =====================================================

    print(
        "\nMatching flights to nearest "
        "weather observation..."
    )

    enriched_parts = []

    for airport_code in sorted(
        weather_airports
    ):

        airport_flights = valid_flights[
            valid_flights["ORIGIN"]
            == airport_code
        ].copy()

        if airport_flights.empty:
            continue

        airport_weather = weather[
            weather["airport_code"]
            == airport_code
        ].copy()

        # -------------------------------------------------
        # SORT FOR MERGE_ASOF
        # -------------------------------------------------

        airport_flights = (
            airport_flights
            .sort_values(
                "actual_departure_utc"
            )
            .reset_index(drop=True)
        )

        airport_weather = (
            airport_weather
            .sort_values(
                "weather_timestamp_utc"
            )
            .reset_index(drop=True)
        )

        # -------------------------------------------------
        # MATCH NEAREST WEATHER
        # -------------------------------------------------

        matched = pd.merge_asof(
            airport_flights,
            airport_weather[
                [
                    "weather_timestamp",
                    "temperature",
                    "humidity",
                    "precipitation",
                    "rain",
                    "snowfall",
                    "wind_speed",
                    "wind_direction",
                    "visibility",
                    "cloud_cover",
                    "weather_code",
                    "timezone",
                    "weather_timestamp_utc"
                ]
            ],
            left_on="actual_departure_utc",
            right_on="weather_timestamp_utc",
            direction="nearest",
            tolerance=pd.Timedelta(
                minutes=MAX_WEATHER_DISTANCE_MINUTES
            )
        )

        # -------------------------------------------------
        # CALCULATE TIME DIFFERENCE
        # -------------------------------------------------

        matched[
            "weather_time_difference_minutes"
        ] = (
            (
                matched[
                    "weather_timestamp_utc"
                ]
                -
                matched[
                    "actual_departure_utc"
                ]
            )
            .abs()
            .dt.total_seconds()
            / 60
        )

        enriched_parts.append(
            matched
        )

        print(
            f"  {airport_code}: "
            f"{len(airport_flights):,} flights"
        )

    # =====================================================
    # COMBINE MATCHED FLIGHTS
    # =====================================================

    if enriched_parts:

        matched_flights = pd.concat(
            enriched_parts,
            ignore_index=True
        )

    else:

        matched_flights = pd.DataFrame()

    # =====================================================
    # BUILD FINAL DATASET
    # =====================================================

    if not matched_flights.empty:

        # Remove empty initialized weather columns
        for column in weather_columns:

            original_column = (
                f"departure_weather_{column}"
            )

            if original_column in matched_flights:

                matched_flights[
                    original_column
                ] = matched_flights[
                    column
                ]

                matched_flights = (
                    matched_flights
                    .drop(
                        columns=[column]
                    )
                )

        final = matched_flights

        # Flights that were not eligible
        # will be added back below.

        unmatched = flights[
            ~flights["flight_row_id"]
            .isin(
                matched_flights[
                    "flight_row_id"
                ]
            )
        ].copy()

        final = pd.concat(
            [
                final,
                unmatched
            ],
            ignore_index=True
        )

    else:

        final = flights.copy()

    # =====================================================
    # RESTORE ORIGINAL ORDER
    # =====================================================

    final = (
        final
        .sort_values(
            "flight_row_id"
        )
        .reset_index(drop=True)
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    print("\n" + "-" * 80)
    print("ENRICHMENT VALIDATION")
    print("-" * 80)

    print(
        f"Original flights: "
        f"{len(flights):,}"
    )

    print(
        f"Final flights: "
        f"{len(final):,}"
    )

    if len(final) != len(flights):

        raise ValueError(
            "Flight row count changed during "
            "weather enrichment."
        )

    # -----------------------------------------------------
    # WEATHER MATCH COUNT
    # -----------------------------------------------------

    matched_count = (
        final[
            "departure_weather_temperature"
        ]
        .notna()
        .sum()
    )

    unmatched_count = (
        len(final)
        - matched_count
    )

    print(
        f"Weather matched: "
        f"{matched_count:,}"
    )

    print(
        f"Weather unmatched: "
        f"{unmatched_count:,}"
    )

    # -----------------------------------------------------
    # MATCH RATE
    # -----------------------------------------------------

    flights_with_departure = (
        final[
            "actual_departure_utc"
        ]
        .notna()
        .sum()
    )

    if flights_with_departure > 0:

        match_rate = (
            matched_count
            /
            flights_with_departure
            *
            100
        )

        print(
            f"Weather match rate among "
            f"flights with actual departure: "
            f"{match_rate:.2f}%"
        )

    # -----------------------------------------------------
    # TIME DIFFERENCE
    # -----------------------------------------------------

    differences = (
        pd.to_numeric(
            final[
                "weather_time_difference_minutes"
            ],
            errors="coerce"
        )
        .dropna()
    )

    if not differences.empty:

        print(
            f"\nAverage weather time difference: "
            f"{differences.mean():.2f} minutes"
        )

        print(
            f"Maximum weather time difference: "
            f"{differences.max():.2f} minutes"
        )

        print(
            f"Matches within 15 minutes: "
            f"{(differences <= 15).sum():,}"
        )

        print(
            f"Matches within 30 minutes: "
            f"{(differences <= 30).sum():,}"
        )

        print(
            f"Matches within 60 minutes: "
            f"{(differences <= 60).sum():,}"
        )

    # =====================================================
    # DUPLICATE FLIGHT CHECK
    # =====================================================

    duplicate_rows = (
        final["flight_row_id"]
        .duplicated()
        .sum()
    )

    print(
        f"\nDuplicate flight rows: "
        f"{duplicate_rows:,}"
    )

    if duplicate_rows > 0:

        raise ValueError(
            "Duplicate flights detected "
            "after enrichment."
        )

    # =====================================================
    # SAMPLE
    # =====================================================

    print("\n" + "-" * 80)
    print("SAMPLE ENRICHED FLIGHTS")
    print("-" * 80)

    sample_columns = [
        "MKT_UNIQUE_CARRIER",
        "MKT_CARRIER_FL_NUM",
        "ORIGIN",
        "DEST",
        "actual_departure_utc",
        "departure_weather_weather_timestamp_utc",
        "weather_time_difference_minutes",
        "departure_weather_temperature",
        "departure_weather_humidity",
        "departure_weather_precipitation",
        "departure_weather_rain",
        "departure_weather_wind_speed",
        "departure_weather_cloud_cover",
        "departure_weather_weather_code"
    ]

    print(
        final[
            sample_columns
        ]
        .head(10)
        .to_string(index=False)
    )

    # =====================================================
    # SAVE
    # =====================================================

    final.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nSaved to: "
        f"{OUTPUT_FILE}"
    )

    print("\n" + "=" * 80)
    print(
        "PRODUCTION FLIGHT → WEATHER "
        "ENRICHMENT COMPLETE"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()