import pandas as pd
from pathlib import Path
from zoneinfo import ZoneInfo


# =========================================================
# FILE PATHS
# =========================================================

FLIGHT_FILE = Path(
    "data/raw/flights_january_2025.xlsx"
)

AIRPORT_FILE = Path(
    "data/processed/airports_enriched.csv"
)

OUTPUT_FILE = Path(
    "data/processed/flights_transformed.csv"
)


# =========================================================
# HHMM → LOCAL TIMESTAMP
# =========================================================

def hhmm_to_local_timestamp(
    flight_date,
    hhmm,
    timezone
):
    """
    Convert a BTS HHMM value into a timezone-aware
    local timestamp.

    2400 means midnight at the END of flight date.
    """

    if pd.isna(hhmm):
        return pd.NaT

    hhmm = int(hhmm)

    if hhmm == 2400:

        local_date = (
            pd.Timestamp(flight_date)
            + pd.Timedelta(days=1)
        ).date()

        hours = 0
        minutes = 0

    else:

        hours = hhmm // 100
        minutes = hhmm % 100

        if hours > 23 or minutes > 59:
            raise ValueError(
                f"Invalid HHMM value: {hhmm}"
            )

        local_date = pd.Timestamp(
            flight_date
        ).date()

    timestamp = pd.Timestamp(
        year=local_date.year,
        month=local_date.month,
        day=local_date.day,
        hour=hours,
        minute=minutes
    )

    return timestamp.tz_localize(
        ZoneInfo(timezone)
    )


# =========================================================
# SCHEDULED TIMESTAMPS
# =========================================================

def build_scheduled_timestamps(row):

    departure_local = hhmm_to_local_timestamp(
        row["FL_DATE"],
        row["CRS_DEP_TIME"],
        row["origin_timezone"]
    )

    arrival_local = hhmm_to_local_timestamp(
        row["FL_DATE"],
        row["CRS_ARR_TIME"],
        row["destination_timezone"]
    )

    # Scheduled flights normally cross midnight when
    # destination local time is earlier than origin time.
    #
    # IMPORTANT:
    # Compare LOCAL clock values, not UTC values.

    if (
        pd.notna(departure_local)
        and pd.notna(arrival_local)
        and arrival_local.replace(
            tzinfo=None
        ) < departure_local.replace(
            tzinfo=None
        )
    ):
        arrival_local = (
            arrival_local
            + pd.Timedelta(days=1)
        )

    departure_utc = (
        departure_local.tz_convert("UTC")
        if pd.notna(departure_local)
        else pd.NaT
    )

    arrival_utc = (
        arrival_local.tz_convert("UTC")
        if pd.notna(arrival_local)
        else pd.NaT
    )

    return (
        departure_local,
        arrival_local,
        departure_utc,
        arrival_utc
    )


# =========================================================
# ACTUAL TIMESTAMPS
# =========================================================

def build_actual_timestamps(row):

    departure_local = hhmm_to_local_timestamp(
        row["FL_DATE"],
        row["DEP_TIME"],
        row["origin_timezone"]
    )

    arrival_base_local = hhmm_to_local_timestamp(
        row["FL_DATE"],
        row["ARR_TIME"],
        row["destination_timezone"]
    )

    if (
        pd.isna(departure_local)
        or pd.isna(arrival_base_local)
    ):
        departure_utc = (
            departure_local.tz_convert("UTC")
            if pd.notna(departure_local)
            else pd.NaT
        )

        return (
            departure_local,
            arrival_base_local,
            departure_utc,
            pd.NaT
        )

    departure_utc = (
        departure_local.tz_convert("UTC")
    )

    elapsed = row["ACTUAL_ELAPSED_TIME"]

    # =====================================================
    # COMPLETED FLIGHT WITH KNOWN ELAPSED TIME
    # =====================================================

    if pd.notna(elapsed):

        elapsed = float(elapsed)

        expected_arrival_utc = (
            departure_utc
            + pd.Timedelta(
                minutes=elapsed
            )
        )

        candidates = []

        # Test destination local date from
        # one day before through two days after FL_DATE.
        for day_offset in [-1, 0, 1, 2]:

            candidate_local = (
                arrival_base_local
                + pd.Timedelta(
                    days=day_offset
                )
            )

            candidate_utc = (
                candidate_local.tz_convert("UTC")
            )

            difference = abs(
                (
                    candidate_utc
                    - expected_arrival_utc
                ).total_seconds()
            )

            candidates.append(
                (
                    difference,
                    candidate_local,
                    candidate_utc
                )
            )

        # Select the candidate closest to the
        # BTS elapsed time.

        (
            _,
            arrival_local,
            arrival_utc
        ) = min(
            candidates,
            key=lambda x: x[0]
        )

    # =====================================================
    # NO ELAPSED TIME
    # =====================================================

    else:

        arrival_local = arrival_base_local

        # Local-clock overnight fallback only.
        if (
            arrival_local.replace(tzinfo=None)
            < departure_local.replace(tzinfo=None)
        ):
            arrival_local = (
                arrival_local
                + pd.Timedelta(days=1)
            )

        arrival_utc = (
            arrival_local.tz_convert("UTC")
        )

    return (
        departure_local,
        arrival_local,
        departure_utc,
        arrival_utc
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 80)
    print("FLIGHT DATA TRANSFORMATION")
    print("=" * 80)

    # =====================================================
    # 1. LOAD FLIGHTS
    # =====================================================

    print("\nLoading flight data...")

    df = pd.read_excel(
        FLIGHT_FILE
    )

    print(
        f"Flights loaded: {len(df):,}"
    )

    # =====================================================
    # 2. LOAD AIRPORT REFERENCE
    # =====================================================

    print("\nLoading airport reference...")

    airports = pd.read_csv(
        AIRPORT_FILE
    )

    print(
        f"Airports loaded: {len(airports):,}"
    )

    # =====================================================
    # 3. AIRPORT TIMEZONE LOOKUP
    # =====================================================

    airport_timezones = (
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
    # 4. ORIGIN TIMEZONE
    # =====================================================

    print("\nJoining origin timezones...")

    df = df.merge(
        airport_timezones.rename(
            columns={
                "airport_code": "ORIGIN",
                "timezone": "origin_timezone"
            }
        ),
        on="ORIGIN",
        how="left",
        validate="many_to_one"
    )

    # =====================================================
    # 5. DESTINATION TIMEZONE
    # =====================================================

    print("Joining destination timezones...")

    df = df.merge(
        airport_timezones.rename(
            columns={
                "airport_code": "DEST",
                "timezone": "destination_timezone"
            }
        ),
        on="DEST",
        how="left",
        validate="many_to_one"
    )

    # =====================================================
    # 6. TIMEZONE VALIDATION
    # =====================================================

    missing_origin = (
        df["origin_timezone"]
        .isna()
        .sum()
    )

    missing_destination = (
        df["destination_timezone"]
        .isna()
        .sum()
    )

    print("\n" + "-" * 80)
    print("TIMEZONE COVERAGE")
    print("-" * 80)

    print(
        f"Missing origin timezone:      "
        f"{missing_origin:,}"
    )

    print(
        f"Missing destination timezone: "
        f"{missing_destination:,}"
    )

    if (
        missing_origin > 0
        or missing_destination > 0
    ):
        raise ValueError(
            "Missing airport timezone detected."
        )

    # =====================================================
    # 7. SCHEDULED TIMESTAMPS
    # =====================================================

    print(
        "\nBuilding scheduled timestamps..."
    )

    scheduled_results = df.apply(
        build_scheduled_timestamps,
        axis=1,
        result_type="expand"
    )

    scheduled_results.columns = [
        "scheduled_departure_local",
        "scheduled_arrival_local",
        "scheduled_departure_utc",
        "scheduled_arrival_utc"
    ]

    df = pd.concat(
        [
            df,
            scheduled_results
        ],
        axis=1
    )

    # =====================================================
    # 8. ACTUAL TIMESTAMPS
    # =====================================================

    print(
        "Building actual timestamps..."
    )

    actual_results = df.apply(
        build_actual_timestamps,
        axis=1,
        result_type="expand"
    )

    actual_results.columns = [
        "actual_departure_local",
        "actual_arrival_local",
        "actual_departure_utc",
        "actual_arrival_utc"
    ]

    df = pd.concat(
        [
            df,
            actual_results
        ],
        axis=1
    )

    # =====================================================
    # 9. DURATION VALIDATION
    # =====================================================

    print(
        "\nValidating actual flight durations..."
    )

    completed = df[
        (df["CANCELLED"] == 0)
        & df["actual_departure_utc"].notna()
        & df["actual_arrival_utc"].notna()
        & df["ACTUAL_ELAPSED_TIME"].notna()
    ].copy()

    completed[
        "calculated_duration_minutes"
    ] = (
        (
            completed["actual_arrival_utc"]
            - completed["actual_departure_utc"]
        )
        .dt.total_seconds()
        / 60
    )

    completed[
        "duration_difference_minutes"
    ] = (
        completed[
            "calculated_duration_minutes"
        ]
        - completed["ACTUAL_ELAPSED_TIME"]
    )

    # =====================================================
    # 10. VALIDATION STATISTICS
    # =====================================================

    print("\n" + "-" * 80)
    print("DURATION VALIDATION")
    print("-" * 80)

    print(
        f"Completed flights checked: "
        f"{len(completed):,}"
    )

    max_difference = (
        completed[
            "duration_difference_minutes"
        ]
        .abs()
        .max()
    )

    mean_difference = (
        completed[
            "duration_difference_minutes"
        ]
        .abs()
        .mean()
    )

    exact_matches = (
        completed[
            "duration_difference_minutes"
        ]
        .abs()
        < 0.01
    ).sum()

    print(
        f"Maximum absolute difference: "
        f"{max_difference:.1f} minutes"
    )

    print(
        f"Mean absolute difference: "
        f"{mean_difference:.2f} minutes"
    )

    print(
        f"Exact matches: "
        f"{exact_matches:,}"
    )

    print(
        f"Exact match percentage: "
        f"{exact_matches / len(completed) * 100:.2f}%"
    )

    # =====================================================
    # 11. IMPOSSIBLE TIMELINES
    # =====================================================

    impossible = completed[
        completed["actual_arrival_utc"]
        < completed["actual_departure_utc"]
    ]

    print(
        f"\nImpossible arrival < departure: "
        f"{len(impossible):,}"
    )

    # =====================================================
    # 12. LARGE MISMATCHES
    # =====================================================

    large_mismatches = completed[
        completed[
            "duration_difference_minutes"
        ]
        .abs()
        > 1
    ]

    print(
        f"Duration mismatches > 1 minute: "
        f"{len(large_mismatches):,}"
    )

    # =====================================================
    # 13. SAVE
    # =====================================================

    print(
        "\nSaving transformed dataset..."
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    # =====================================================
    # 14. SAMPLE
    # =====================================================

    print("\n" + "-" * 80)
    print("SAMPLE TRANSFORMED FLIGHTS")
    print("-" * 80)

    print(
        df[
            [
                "MKT_UNIQUE_CARRIER",
                "MKT_CARRIER_FL_NUM",
                "ORIGIN",
                "DEST",
                "actual_departure_local",
                "actual_departure_utc",
                "actual_arrival_local",
                "actual_arrival_utc"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    # =====================================================
    # FINAL
    # =====================================================

    print("\n" + "=" * 80)
    print("FLIGHT TRANSFORMATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()