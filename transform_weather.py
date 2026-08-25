import pandas as pd
from pathlib import Path
from zoneinfo import ZoneInfo


INPUT_FILE = Path(
    "data/processed/weather_january_2025_all_airports.csv"
)

AIRPORT_FILE = Path(
    "data/processed/airports_enriched.csv"
)

OUTPUT_FILE = Path(
    "data/processed/weather_january_2025_all_airports_utc.csv"
)


def main():

    print("=" * 80)
    print("PRODUCTION WEATHER UTC TRANSFORMATION")
    print("=" * 80)

    # =====================================================
    # LOAD WEATHER
    # =====================================================

    print("\nLoading weather data...")

    weather = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Weather rows loaded: "
        f"{len(weather):,}"
    )

    # =====================================================
    # LOAD AIRPORT TIMEZONES
    # =====================================================

    print("\nLoading airport reference...")

    airports = pd.read_csv(
        AIRPORT_FILE
    )

    airports["airport_code"] = (
        airports["airport_code"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    timezone_lookup = (
        airports[
            [
                "airport_code",
                "timezone"
            ]
        ]
        .drop_duplicates(
            "airport_code"
        )
    )

    # =====================================================
    # JOIN TIMEZONE
    # =====================================================

    print("\nJoining airport timezones...")

    weather = weather.merge(
        timezone_lookup,
        on="airport_code",
        how="left",
        validate="many_to_one"
    )

    missing_timezone = (
        weather["timezone"]
        .isna()
        .sum()
    )

    print(
        f"Missing weather timezones: "
        f"{missing_timezone:,}"
    )

    if missing_timezone > 0:

        missing_airports = (
            weather.loc[
                weather["timezone"].isna(),
                "airport_code"
            ]
            .drop_duplicates()
            .tolist()
        )

        print(
            "Airports with missing timezone:"
        )

        print(
            missing_airports
        )

        raise ValueError(
            "Weather records contain missing "
            "airport timezones."
        )

    # =====================================================
    # CONVERT LOCAL WEATHER TIME → UTC
    # =====================================================

    print(
        "\nConverting weather timestamps to UTC..."
    )

    def convert_to_utc(row):

        local_timestamp = pd.Timestamp(
            row["weather_timestamp"]
        )

        local_timestamp = (
            local_timestamp
            .tz_localize(
                ZoneInfo(row["timezone"])
            )
        )

        return local_timestamp.tz_convert(
            "UTC"
        )

    weather[
        "weather_timestamp_utc"
    ] = weather.apply(
        convert_to_utc,
        axis=1
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    print("\n" + "-" * 80)
    print("VALIDATION")
    print("-" * 80)

    print(
        f"Rows: "
        f"{len(weather):,}"
    )

    print(
        f"Airports: "
        f"{weather['airport_code'].nunique():,}"
    )

    print(
        f"Missing UTC timestamps: "
        f"{weather['weather_timestamp_utc'].isna().sum():,}"
    )

    # -----------------------------------------------------
    # Expected row count
    # -----------------------------------------------------

    expected_rows = (
        weather["airport_code"].nunique()
        * 744
    )

    print(
        f"Expected rows: "
        f"{expected_rows:,}"
    )

    if len(weather) != expected_rows:

        print(
            "WARNING: Actual row count differs "
            "from expected airport × 744."
        )

    else:

        print(
            "Row count validation: PASS"
        )

    # -----------------------------------------------------
    # Duplicate check
    # -----------------------------------------------------

    duplicate_count = (
        weather.duplicated(
            subset=[
                "airport_code",
                "weather_timestamp"
            ]
        )
        .sum()
    )

    print(
        f"Duplicate airport/timestamp rows: "
        f"{duplicate_count:,}"
    )

    if duplicate_count > 0:

        raise ValueError(
            "Duplicate weather observations found."
        )

    # -----------------------------------------------------
    # UTC range
    # -----------------------------------------------------

    print(
        f"\nFirst UTC timestamp: "
        f"{weather['weather_timestamp_utc'].min()}"
    )

    print(
        f"Last UTC timestamp: "
        f"{weather['weather_timestamp_utc'].max()}"
    )

    # -----------------------------------------------------
    # Sample
    # -----------------------------------------------------

    print(
        "\nFirst 10 converted timestamps:"
    )

    print(
        weather[
            [
                "airport_code",
                "timezone",
                "weather_timestamp",
                "weather_timestamp_utc",
                "temperature"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    # =====================================================
    # SAVE
    # =====================================================

    weather.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nSaved to: "
        f"{OUTPUT_FILE}"
    )

    print("\n" + "=" * 80)
    print(
        "PRODUCTION WEATHER UTC TRANSFORMATION COMPLETE"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()