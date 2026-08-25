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

    mismatches = completed[
        completed["duration_difference_minutes"]
        .abs()
        >= 0.01
    ].copy()

    print("=" * 80)
    print("FLIGHT DURATION MISMATCH INVESTIGATION")
    print("=" * 80)

    print(
        f"\nTotal completed flights: "
        f"{len(completed):,}"
    )

    print(
        f"Mismatched flights: "
        f"{len(mismatches):,}"
    )

    print("\nDifference distribution:")

    print(
        mismatches[
            "duration_difference_minutes"
        ]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nLargest mismatches:")

    columns = [
        "FL_DATE",
        "MKT_UNIQUE_CARRIER",
        "MKT_CARRIER_FL_NUM",
        "ORIGIN",
        "DEST",
        "DEP_TIME",
        "ARR_TIME",
        "ACTUAL_ELAPSED_TIME",
        "actual_departure_local",
        "actual_arrival_local",
        "actual_departure_utc",
        "actual_arrival_utc",
        "duration_difference_minutes",
    ]

    print(
        mismatches[
            columns
        ]
        .sort_values(
            "duration_difference_minutes",
            key=lambda x: x.abs(),
            ascending=False
        )
        .head(50)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()