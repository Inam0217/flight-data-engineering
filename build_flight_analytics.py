import pandas as pd
import numpy as np
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/flights_weather.csv"
)

OUTPUT_FILE = Path(
    "data/processed/flights_analytics.csv"
)


def main():

    print("=" * 80)
    print("FLIGHT ANALYTICAL LAYER")
    print("=" * 80)

    # =====================================================
    # LOAD DATA
    # =====================================================

    print("\nLoading enriched flight dataset...")

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Flights loaded: "
        f"{len(df):,}"
    )

    # =====================================================
    # NUMERIC CONVERSION
    # =====================================================

    numeric_columns = [
        "DEP_DELAY",
        "DEP_DELAY_NEW",
        "ARR_DELAY",
        "ARR_DELAY_NEW",
        "CANCELLED",
        "DIVERTED",
        "CRS_ELAPSED_TIME",
        "ACTUAL_ELAPSED_TIME",
        "AIR_TIME",
        "DISTANCE",
        "CARRIER_DELAY",
        "WEATHER_DELAY",
        "NAS_DELAY",
        "SECURITY_DELAY",
        "LATE_AIRCRAFT_DELAY",
        "departure_weather_temperature",
        "departure_weather_humidity",
        "departure_weather_precipitation",
        "departure_weather_rain",
        "departure_weather_snowfall",
        "departure_weather_wind_speed",
        "departure_weather_wind_direction",
        "departure_weather_cloud_cover",
        "departure_weather_weather_code",
        "weather_time_difference_minutes",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # =====================================================
    # DELAY METRICS
    # =====================================================

    print("\nBuilding delay metrics...")

    df["departure_delay_minutes"] = (
        df["DEP_DELAY"]
        .fillna(0)
    )

    df["arrival_delay_minutes"] = (
        df["ARR_DELAY"]
        .fillna(0)
    )

    # =====================================================
    # CANCELLED / DIVERTED FLAGS
    # =====================================================

    df["is_cancelled"] = (
        df["CANCELLED"]
        .fillna(0)
        .astype(int)
    )

    df["is_diverted"] = (
        df["DIVERTED"]
        .fillna(0)
        .astype(int)
    )

    # =====================================================
    # COMPLETED FLIGHT FLAG
    # =====================================================

    df["is_completed"] = (
        (
            df["is_cancelled"] == 0
        )
        &
        (
            df["is_diverted"] == 0
        )
        &
        (
            df["actual_departure_utc"].notna()
        )
        &
        (
            df["actual_arrival_utc"].notna()
        )
    ).astype(int)

    # =====================================================
    # DEPARTURE STATUS
    # =====================================================

    def departure_status(delay):

        if pd.isna(delay):
            return "unknown"

        if delay <= -15:
            return "early"

        if delay < 15:
            return "on_time"

        if delay < 60:
            return "delayed"

        return "severely_delayed"

    df["departure_status"] = (
        df["DEP_DELAY"]
        .apply(departure_status)
    )

    # =====================================================
    # ARRIVAL STATUS
    # =====================================================

    def arrival_status(delay):

        if pd.isna(delay):
            return "unknown"

        if delay <= -15:
            return "early"

        if delay < 15:
            return "on_time"

        if delay < 60:
            return "delayed"

        return "severely_delayed"

    df["arrival_status"] = (
        df["ARR_DELAY"]
        .apply(arrival_status)
    )

    # =====================================================
    # DELAY CATEGORY
    # =====================================================

    def delay_category(delay):

        if pd.isna(delay):
            return "unknown"

        if delay <= 0:
            return "no_delay"

        if delay <= 15:
            return "minor_delay"

        if delay <= 60:
            return "moderate_delay"

        if delay <= 180:
            return "major_delay"

        return "severe_delay"

    df["delay_category"] = (
        df["ARR_DELAY"]
        .apply(delay_category)
    )

    # =====================================================
    # WEATHER AVAILABILITY
    # =====================================================

    df["weather_available"] = (
        df["departure_weather_weather_timestamp_utc"]
        .notna()
    ).astype(int)

    # =====================================================
    # WEATHER FEATURES
    # =====================================================

    df["has_precipitation"] = (
        df["departure_weather_precipitation"]
        .fillna(0)
        > 0
    ).astype(int)

    df["has_rain"] = (
        df["departure_weather_rain"]
        .fillna(0)
        > 0
    ).astype(int)

    df["has_snow"] = (
        df["departure_weather_snowfall"]
        .fillna(0)
        > 0
    ).astype(int)

    # Wind speed from Open-Meteo is km/h.
    # 40 km/h is used as a practical high-wind
    # analytical threshold.

    df["high_wind"] = (
        df["departure_weather_wind_speed"]
        .fillna(0)
        >= 40
    ).astype(int)

    # =====================================================
    # POOR WEATHER FLAG
    # =====================================================

    df["poor_weather"] = (
        (
            df["has_precipitation"] == 1
        )
        |
        (
            df["has_snow"] == 1
        )
        |
        (
            df["high_wind"] == 1
        )
    ).astype(int)

    # =====================================================
    # WEATHER MATCH QUALITY
    # =====================================================

    df["weather_match_within_30min"] = (
        df["weather_time_difference_minutes"]
        .notna()
        &
        (
            df["weather_time_difference_minutes"]
            <= 30
        )
    ).astype(int)

    # =====================================================
    # WEATHER SEVERITY
    # =====================================================

    def weather_severity(row):

        if row["weather_available"] == 0:
            return "unavailable"

        if row["has_snow"] == 1:
            return "snow"

        if row["has_precipitation"] == 1:
            return "precipitation"

        if row["high_wind"] == 1:
            return "high_wind"

        return "normal"

    df["weather_severity"] = (
        df.apply(
            weather_severity,
            axis=1
        )
    )

    # =====================================================
    # CALENDAR FEATURES
    # =====================================================

    flight_date = pd.to_datetime(
        df["FL_DATE"],
        errors="coerce"
    )

    df["flight_year"] = (
        flight_date.dt.year
    )

    df["flight_month"] = (
        flight_date.dt.month
    )

    df["flight_day"] = (
        flight_date.dt.day
    )

    df["flight_day_of_week"] = (
        flight_date.dt.dayofweek
    )

    df["is_weekend"] = (
        df["flight_day_of_week"]
        >= 5
    ).astype(int)

    # =====================================================
    # DELAY DRIVER
    # =====================================================

    def delay_driver(row):

        if row["is_cancelled"] == 1:
            return "cancelled"

        if row["is_diverted"] == 1:
            return "diverted"

        if pd.isna(row["ARR_DELAY"]):
            return "unknown"

        if row["ARR_DELAY"] <= 0:
            return "no_delay"

        drivers = {
            "carrier": row["CARRIER_DELAY"],
            "weather": row["WEATHER_DELAY"],
            "nas": row["NAS_DELAY"],
            "security": row["SECURITY_DELAY"],
            "late_aircraft": row["LATE_AIRCRAFT_DELAY"],
        }

        valid_drivers = {
            key: value
            for key, value in drivers.items()
            if pd.notna(value)
            and value > 0
        }

        if not valid_drivers:
            return "unspecified"

        return max(
            valid_drivers,
            key=valid_drivers.get
        )

    df["primary_delay_driver"] = (
        df.apply(
            delay_driver,
            axis=1
        )
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    print("\n" + "-" * 80)
    print("ANALYTICAL VALIDATION")
    print("-" * 80)

    print(
        f"Rows: "
        f"{len(df):,}"
    )

    print(
        f"Completed flights: "
        f"{df['is_completed'].sum():,}"
    )

    print(
        f"Cancelled flights: "
        f"{df['is_cancelled'].sum():,}"
    )

    print(
        f"Diverted flights: "
        f"{df['is_diverted'].sum():,}"
    )

    print(
        f"Weather available: "
        f"{df['weather_available'].sum():,}"
    )

    print(
        f"Weather within 30 min: "
        f"{df['weather_match_within_30min'].sum():,}"
    )

    print(
        f"Flights with precipitation: "
        f"{df['has_precipitation'].sum():,}"
    )

    print(
        f"Flights with snow: "
        f"{df['has_snow'].sum():,}"
    )

    print(
        f"Flights with high wind: "
        f"{df['high_wind'].sum():,}"
    )

    # =====================================================
    # DELAY DISTRIBUTION
    # =====================================================

    print("\n" + "-" * 80)
    print("ARRIVAL DELAY CATEGORIES")
    print("-" * 80)

    print(
        df["delay_category"]
        .value_counts()
        .to_string()
    )

    # =====================================================
    # WEATHER DISTRIBUTION
    # =====================================================

    print("\n" + "-" * 80)
    print("WEATHER SEVERITY")
    print("-" * 80)

    print(
        df["weather_severity"]
        .value_counts()
        .to_string()
    )

    # =====================================================
    # PRIMARY DELAY DRIVER
    # =====================================================

    print("\n" + "-" * 80)
    print("PRIMARY DELAY DRIVER")
    print("-" * 80)

    print(
        df["primary_delay_driver"]
        .value_counts()
        .to_string()
    )

    # =====================================================
    # DUPLICATE CHECK
    # =====================================================

    print("\n" + "-" * 80)
    print("DUPLICATE CHECK")
    print("-" * 80)

    duplicate_count = (
        df["flight_row_id"]
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate flight_row_id: "
        f"{duplicate_count:,}"
    )

    if duplicate_count > 0:

        raise ValueError(
            "Duplicate flight_row_id values detected."
        )

    # =====================================================
    # SAVE
    # =====================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nSaved to: "
        f"{OUTPUT_FILE}"
    )

    print("\n" + "=" * 80)
    print("FLIGHT ANALYTICAL LAYER COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()