import pandas as pd
from pathlib import Path


WEATHER_FILE = Path(
    "data/processed/weather_january_2025_all_airports_utc.csv"
)

AIRPORT_FILE = Path(
    "data/processed/airports_enriched.csv"
)


def main():

    print("=" * 80)
    print("PRODUCTION WEATHER DATA VALIDATION")
    print("=" * 80)

    # =====================================================
    # LOAD
    # =====================================================

    print("\nLoading weather dataset...")

    weather = pd.read_csv(
        WEATHER_FILE,
        parse_dates=[
            "weather_timestamp",
            "weather_timestamp_utc"
        ]
    )

    print(
        f"Rows loaded: {len(weather):,}"
    )

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

    weather["airport_code"] = (
        weather["airport_code"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # =====================================================
    # BASIC COUNTS
    # =====================================================

    print("\n" + "-" * 80)
    print("BASIC COUNTS")
    print("-" * 80)

    airport_count = (
        weather["airport_code"]
        .nunique()
    )

    expected_airports = (
        airports["airport_code"]
        .nunique()
    )

    expected_rows = (
        expected_airports * 744
    )

    print(
        f"Weather airports:   {airport_count:,}"
    )

    print(
        f"Reference airports:  {expected_airports:,}"
    )

    print(
        f"Expected rows:       {expected_rows:,}"
    )

    print(
        f"Actual rows:         {len(weather):,}"
    )

    # =====================================================
    # AIRPORT COVERAGE
    # =====================================================

    print("\n" + "-" * 80)
    print("AIRPORT COVERAGE")
    print("-" * 80)

    weather_airports = set(
        weather["airport_code"]
    )

    reference_airports = set(
        airports["airport_code"]
    )

    missing_airports = (
        reference_airports
        - weather_airports
    )

    unexpected_airports = (
        weather_airports
        - reference_airports
    )

    print(
        f"Missing airports:    {len(missing_airports):,}"
    )

    print(
        f"Unexpected airports: {len(unexpected_airports):,}"
    )

    if missing_airports:

        print(
            "\nMissing airport codes:"
        )

        print(
            sorted(missing_airports)
        )

    if unexpected_airports:

        print(
            "\nUnexpected airport codes:"
        )

        print(
            sorted(unexpected_airports)
        )

    # =====================================================
    # ROWS PER AIRPORT
    # =====================================================

    print("\n" + "-" * 80)
    print("ROWS PER AIRPORT")
    print("-" * 80)

    rows_per_airport = (
        weather
        .groupby("airport_code")
        .size()
    )

    print(
        f"Minimum rows: {rows_per_airport.min():,}"
    )

    print(
        f"Maximum rows: {rows_per_airport.max():,}"
    )

    incomplete_airports = (
        rows_per_airport[
            rows_per_airport != 744
        ]
    )

    print(
        f"Airports with != 744 rows: "
        f"{len(incomplete_airports):,}"
    )

    if not incomplete_airports.empty:

        print(
            incomplete_airports
        )

    # =====================================================
    # DUPLICATES
    # =====================================================

    print("\n" + "-" * 80)
    print("DUPLICATE CHECK")
    print("-" * 80)

    duplicates = (
        weather
        .duplicated(
            subset=[
                "airport_code",
                "weather_timestamp"
            ]
        )
        .sum()
    )

    print(
        f"Duplicate airport/timestamp rows: "
        f"{duplicates:,}"
    )

    # =====================================================
    # MISSING VALUES
    # =====================================================

    print("\n" + "-" * 80)
    print("MISSING VALUES")
    print("-" * 80)

    critical_columns = [
        "airport_code",
        "weather_timestamp",
        "weather_timestamp_utc",
        "temperature",
        "humidity",
        "precipitation",
        "wind_speed",
        "cloud_cover",
        "weather_code"
    ]

    for column in critical_columns:

        missing = (
            weather[column]
            .isna()
            .sum()
        )

        print(
            f"{column:<30} {missing:,}"
        )

    # =====================================================
    # TIME RANGE
    # =====================================================

    print("\n" + "-" * 80)
    print("LOCAL TIME RANGE")
    print("-" * 80)

    print(
        f"Minimum local timestamp: "
        f"{weather['weather_timestamp'].min()}"
    )

    print(
        f"Maximum local timestamp: "
        f"{weather['weather_timestamp'].max()}"
    )

    # =====================================================
    # UTC TIME RANGE
    # =====================================================

    print("\n" + "-" * 80)
    print("UTC TIME RANGE")
    print("-" * 80)

    print(
        f"Minimum UTC timestamp: "
        f"{weather['weather_timestamp_utc'].min()}"
    )

    print(
        f"Maximum UTC timestamp: "
        f"{weather['weather_timestamp_utc'].max()}"
    )

    # =====================================================
    # TIMEZONE COVERAGE
    # =====================================================

    print("\n" + "-" * 80)
    print("TIMEZONE COVERAGE")
    print("-" * 80)

    timezone_counts = (
        weather["timezone"]
        .isna()
        .sum()
    )

    print(
        f"Missing timezone values: "
        f"{timezone_counts:,}"
    )

    print(
        f"Unique timezones: "
        f"{weather['timezone'].nunique():,}"
    )

    # =====================================================
    # UTC CONVERSION SANITY CHECK
    # =====================================================

    print("\n" + "-" * 80)
    print("UTC CONVERSION SANITY CHECK")
    print("-" * 80)

    weather["utc_offset_minutes"] = (
        (
            weather["weather_timestamp_utc"]
            - weather["weather_timestamp"]
            .dt.tz_localize("UTC")
        )
        .dt.total_seconds()
        / 60
    )

    print(
        "Note: UTC offset sanity is checked "
        "using timezone-aware reconstruction below."
    )

    # Reconstruct local timestamp using timezone
    # and compare against stored UTC.

    def check_conversion(row):

        try:

            local = pd.Timestamp(
                row["weather_timestamp"]
            )

            local = local.tz_localize(
                row["timezone"]
            )

            calculated = (
                local.tz_convert("UTC")
            )

            stored = pd.Timestamp(
                row["weather_timestamp_utc"]
            )

            return (
                calculated == stored
            )

        except Exception:

            return False

    conversion_valid = weather.apply(
        check_conversion,
        axis=1
    )

    invalid_conversions = (
        (~conversion_valid)
        .sum()
    )

    print(
        f"Invalid UTC conversions: "
        f"{invalid_conversions:,}"
    )

    # =====================================================
    # SAMPLE
    # =====================================================

    print("\n" + "-" * 80)
    print("SAMPLE")
    print("-" * 80)

    print(
        weather[
            [
                "airport_code",
                "timezone",
                "weather_timestamp",
                "weather_timestamp_utc",
                "temperature",
                "humidity",
                "precipitation",
                "wind_speed",
                "weather_code"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    # =====================================================
    # FINAL STATUS
    # =====================================================

    checks = {

        "airport_count":
            airport_count == expected_airports,

        "row_count":
            len(weather) == expected_rows,

        "missing_airports":
            len(missing_airports) == 0,

        "unexpected_airports":
            len(unexpected_airports) == 0,

        "rows_per_airport":
            len(incomplete_airports) == 0,

        "duplicates":
            duplicates == 0,

        "missing_timezones":
            timezone_counts == 0,

        "invalid_conversions":
            invalid_conversions == 0
    }

    print("\n" + "=" * 80)
    print("FINAL VALIDATION STATUS")
    print("=" * 80)

    all_passed = True

    for name, passed in checks.items():

        status = "PASS" if passed else "FAIL"

        print(
            f"{name:<25} {status}"
        )

        if not passed:
            all_passed = False

    print("\n" + "=" * 80)

    if all_passed:

        print(
            "ALL WEATHER VALIDATION CHECKS PASSED"
        )

    else:

        print(
            "WEATHER VALIDATION FAILED"
        )

    print("=" * 80)


if __name__ == "__main__":
    main()