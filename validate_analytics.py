import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/flights_analytics.csv"
)


def main():

    print("=" * 80)
    print("FLIGHT ANALYTICAL LAYER VALIDATION")
    print("=" * 80)

    # =========================================================
    # LOAD
    # =========================================================

    print("\nLoading analytical dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows loaded: {len(df):,}")

    # =========================================================
    # BASIC COUNTS
    # =========================================================

    print("\n" + "-" * 80)
    print("BASIC COUNTS")
    print("-" * 80)

    print(f"Rows:             {len(df):,}")
    print(f"Columns:          {len(df.columns):,}")
    print(f"Unique flights:   {df['flight_row_id'].nunique():,}")

    # =========================================================
    # ROW COUNT
    # =========================================================

    print("\n" + "-" * 80)
    print("ROW COUNT VALIDATION")
    print("-" * 80)

    expected_rows = 599_013
    actual_rows = len(df)

    print(f"Expected rows: {expected_rows:,}")
    print(f"Actual rows:   {actual_rows:,}")

    if actual_rows == expected_rows:
        print("Row count: PASS")
    else:
        print("Row count: FAIL")

    # =========================================================
    # DUPLICATES
    # =========================================================

    print("\n" + "-" * 80)
    print("DUPLICATE CHECK")
    print("-" * 80)

    duplicate_ids = df["flight_row_id"].duplicated().sum()

    print(
        f"Duplicate flight_row_id: "
        f"{duplicate_ids:,}"
    )

    print(
        "Duplicate check: "
        + ("PASS" if duplicate_ids == 0 else "FAIL")
    )

    # =========================================================
    # REQUIRED ANALYTICAL COLUMNS
    # =========================================================

    print("\n" + "-" * 80)
    print("REQUIRED COLUMN CHECK")
    print("-" * 80)

    required_columns = [
        "flight_row_id",
        "delay_category",
        "weather_severity",
        "primary_delay_driver",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print("Missing columns:")
        for column in missing_columns:
            print(f"  {column}")

        print("Required columns: FAIL")
    else:
        print("All analytical columns present.")
        print("Required columns: PASS")

    # =========================================================
    # FLIGHT STATUS CONSISTENCY
    # =========================================================

    print("\n" + "-" * 80)
    print("FLIGHT STATUS VALIDATION")
    print("-" * 80)

    cancelled = df["CANCELLED"].fillna(0) == 1
    diverted = df["DIVERTED"].fillna(0) == 1

    completed = (
        ~cancelled
        & ~diverted
        & df["actual_departure_utc"].notna()
        & df["actual_arrival_utc"].notna()
    )

    print(f"Cancelled: {cancelled.sum():,}")
    print(f"Diverted:  {diverted.sum():,}")
    print(f"Completed: {completed.sum():,}")

    invalid_cancelled_completed = (
        cancelled
        & df["actual_arrival_utc"].notna()
    ).sum()

    print(
        "Cancelled flights with actual arrival: "
        f"{invalid_cancelled_completed:,}"
    )

    if invalid_cancelled_completed == 0:
        print("Cancelled consistency: PASS")
    else:
        print("Cancelled consistency: INFO")

    # =========================================================
    # DELAY CATEGORY VALIDATION
    # =========================================================

    print("\n" + "-" * 80)
    print("DELAY CATEGORY VALIDATION")
    print("-" * 80)

    print(
        df["delay_category"]
        .value_counts(dropna=False)
        .to_string()
    )

    missing_delay_category = (
        df["delay_category"].isna().sum()
    )

    print(
        f"\nMissing delay categories: "
        f"{missing_delay_category:,}"
    )

    if missing_delay_category == 0:
        print("Delay category: PASS")
    else:
        print("Delay category: FAIL")

    # =========================================================
    # WEATHER VALIDATION
    # =========================================================

    print("\n" + "-" * 80)
    print("WEATHER VALIDATION")
    print("-" * 80)

    weather_available = (
        df["departure_weather_weather_timestamp"]
        .notna()
    )

    weather_within_30 = (
        df["weather_time_difference_minutes"]
        .notna()
        &
        (
            df["weather_time_difference_minutes"]
            <= 30
        )
    )

    print(
        f"Weather available: "
        f"{weather_available.sum():,}"
    )

    print(
        f"Weather within 30 min: "
        f"{weather_within_30.sum():,}"
    )

    expected_weather = 580_752

    if weather_available.sum() == expected_weather:
        print("Weather count: PASS")
    else:
        print("Weather count: INFO")

    # =========================================================
    # WEATHER SEVERITY
    # =========================================================

    print("\n" + "-" * 80)
    print("WEATHER SEVERITY")
    print("-" * 80)

    print(
        df["weather_severity"]
        .value_counts(dropna=False)
        .to_string()
    )

    missing_weather_severity = (
        df["weather_severity"].isna().sum()
    )

    print(
        f"\nMissing weather severity: "
        f"{missing_weather_severity:,}"
    )

    # =========================================================
    # PRIMARY DELAY DRIVER
    # =========================================================

    print("\n" + "-" * 80)
    print("PRIMARY DELAY DRIVER")
    print("-" * 80)

    print(
        df["primary_delay_driver"]
        .value_counts(dropna=False)
        .to_string()
    )

    missing_driver = (
        df["primary_delay_driver"].isna().sum()
    )

    print(
        f"\nMissing primary delay driver: "
        f"{missing_driver:,}"
    )

    # =========================================================
    # NUMERIC SANITY
    # =========================================================

    print("\n" + "-" * 80)
    print("NUMERIC SANITY CHECK")
    print("-" * 80)

    numeric_checks = {
        "DISTANCE < 0": (
            df["DISTANCE"].fillna(0) < 0
        ).sum(),

        "ACTUAL_ELAPSED_TIME < 0": (
            df["ACTUAL_ELAPSED_TIME"].fillna(0) < 0
        ).sum(),

        "ARR_DELAY impossible extreme": (
            df["ARR_DELAY"].notna()
            & (df["ARR_DELAY"] < -1440)
        ).sum(),
    }

    for name, count in numeric_checks.items():
        print(f"{name}: {count:,}")

    if all(value == 0 for value in numeric_checks.values()):
        print("Numeric sanity: PASS")
    else:
        print("Numeric sanity: INFO")

    # =========================================================
    # FINAL STATUS
    # =========================================================

    print("\n" + "=" * 80)
    print("FINAL VALIDATION STATUS")
    print("=" * 80)

    checks = {
        "row_count": actual_rows == expected_rows,
        "unique_flights": duplicate_ids == 0,
        "required_columns": len(missing_columns) == 0,
        "delay_category": missing_delay_category == 0,
        "weather_severity": missing_weather_severity == 0,
        "primary_delay_driver": missing_driver == 0,
        "numeric_sanity": all(
            value == 0
            for value in numeric_checks.values()
        ),
    }

    for name, passed in checks.items():
        print(
            f"{name:<25}"
            f"{'PASS' if passed else 'FAIL'}"
        )

    print("\n" + "=" * 80)

    if all(checks.values()):
        print("ALL ANALYTICAL VALIDATION CHECKS PASSED")
    else:
        print("ANALYTICAL VALIDATION REQUIRES INVESTIGATION")

    print("=" * 80)


if __name__ == "__main__":
    main()