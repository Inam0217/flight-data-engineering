import pandas as pd
from pathlib import Path


FILE = Path(
    "data/processed/flights_transformed.csv"
)


def main():

    df = pd.read_csv(
        FILE,
        parse_dates=[
            "actual_departure_utc",
            "actual_arrival_utc"
        ]
    )

    completed = df[
        (df["CANCELLED"] == 0)
        & df["actual_departure_utc"].notna()
        & df["actual_arrival_utc"].notna()
        & df["ACTUAL_ELAPSED_TIME"].notna()
    ].copy()

    completed["calculated_duration_minutes"] = (
        (
            completed["actual_arrival_utc"]
            - completed["actual_departure_utc"]
        )
        .dt.total_seconds()
        / 60
    )

    completed["duration_difference_minutes"] = (
        completed["calculated_duration_minutes"]
        - completed["ACTUAL_ELAPSED_TIME"]
    )

    # Only the exact 24-hour errors
    mismatches = completed[
        completed["duration_difference_minutes"]
        .abs()
        == 1440
    ].copy()

    print("=" * 90)
    print("24-HOUR TIMESTAMP MISMATCHES")
    print("=" * 90)

    print(
        f"\nNumber of 24-hour mismatches: "
        f"{len(mismatches):,}"
    )

    columns = [
        "FL_DATE",
        "MKT_UNIQUE_CARRIER",
        "MKT_CARRIER_FL_NUM",
        "ORIGIN",
        "DEST",
        "DEP_TIME",
        "ARR_TIME",
        "ACTUAL_ELAPSED_TIME",
        "origin_timezone",
        "destination_timezone",
        "actual_departure_local",
        "actual_arrival_local",
        "actual_departure_utc",
        "actual_arrival_utc",
        "duration_difference_minutes",
    ]

    print("\nRecords:\n")

    print(
        mismatches[
            columns
        ]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()