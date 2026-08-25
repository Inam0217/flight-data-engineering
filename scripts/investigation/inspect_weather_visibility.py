import pandas as pd
from pathlib import Path


WEATHER_FILE = Path(
    "data/processed/weather_january_2025_all_airports_utc.csv"
)

ENRICHED_FILE = Path(
    "data/processed/flights_weather.csv"
)


def main():

    print("=" * 80)
    print("WEATHER VISIBILITY INVESTIGATION")
    print("=" * 80)

    # =====================================================
    # LOAD PRODUCTION WEATHER
    # =====================================================

    print("\nLoading production weather dataset...")

    weather = pd.read_csv(
        WEATHER_FILE
    )

    print(
        f"Weather rows loaded: "
        f"{len(weather):,}"
    )

    print("\nWeather columns:")
    print(
        weather.columns.tolist()
    )

    # =====================================================
    # VISIBILITY COLUMN
    # =====================================================

    print("\n" + "-" * 80)
    print("VISIBILITY COLUMN")
    print("-" * 80)

    if "visibility" not in weather.columns:

        print(
            "ERROR: visibility column does not exist "
            "in the production weather dataset."
        )

        return

    print(
        f"Visibility dtype: "
        f"{weather['visibility'].dtype}"
    )

    print(
        f"Missing visibility: "
        f"{weather['visibility'].isna().sum():,}"
    )

    print(
        f"Non-missing visibility: "
        f"{weather['visibility'].notna().sum():,}"
    )

    # =====================================================
    # UNIQUE VALUES
    # =====================================================

    print("\n" + "-" * 80)
    print("VISIBILITY VALUES")
    print("-" * 80)

    print(
        weather["visibility"]
        .value_counts(dropna=False)
        .head(20)
        .to_string()
    )

    # =====================================================
    # SAMPLE RAW WEATHER ROWS
    # =====================================================

    print("\n" + "-" * 80)
    print("SAMPLE WEATHER ROWS")
    print("-" * 80)

    columns = [
        "airport_code",
        "weather_timestamp",
        "visibility",
        "temperature",
        "humidity",
        "precipitation",
        "wind_speed",
        "cloud_cover",
        "weather_code",
    ]

    existing_columns = [
        col for col in columns
        if col in weather.columns
    ]

    print(
        weather[
            existing_columns
        ]
        .head(20)
        .to_string(index=False)
    )

    # =====================================================
    # CHECK OTHER WEATHER FIELDS
    # =====================================================

    print("\n" + "-" * 80)
    print("MISSINGNESS COMPARISON")
    print("-" * 80)

    weather_fields = [
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
    ]

    for column in weather_fields:

        if column in weather.columns:

            missing = weather[column].isna().sum()

            percentage = (
                missing / len(weather) * 100
            )

            print(
                f"{column:<25}"
                f"missing: {missing:>8,} "
                f"({percentage:>6.2f}%)"
            )

    # =====================================================
    # CHECK ENRICHED FLIGHTS
    # =====================================================

    print("\n" + "-" * 80)
    print("ENRICHED FLIGHT VISIBILITY")
    print("-" * 80)

    if ENRICHED_FILE.exists():

        enriched = pd.read_csv(
            ENRICHED_FILE
        )

        print(
            f"Enriched flight rows: "
            f"{len(enriched):,}"
        )

        visibility_columns = [
            column
            for column in enriched.columns
            if "visibility" in column.lower()
        ]

        print(
            f"Visibility columns: "
            f"{visibility_columns}"
        )

        for column in visibility_columns:

            missing = (
                enriched[column]
                .isna()
                .sum()
            )

            percentage = (
                missing / len(enriched) * 100
            )

            print(
                f"{column:<50}"
                f"missing: {missing:>8,} "
                f"({percentage:>6.2f}%)"
            )

    else:

        print(
            f"Enriched file not found: "
            f"{ENRICHED_FILE}"
        )

    # =====================================================
    # FINAL ASSESSMENT
    # =====================================================

    print("\n" + "=" * 80)
    print("VISIBILITY INVESTIGATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()