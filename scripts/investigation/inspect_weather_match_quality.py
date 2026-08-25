import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/flights_weather.csv"
)


def main():

    print("=" * 80)
    print("WEATHER MATCH QUALITY INVESTIGATION")
    print("=" * 80)

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    print("\nLoading enriched flight dataset...")

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Flights loaded: {len(df):,}"
    )

    # ==========================================================
    # BASIC MATCH COUNTS
    # ==========================================================

    weather_timestamp = (
        "departure_weather_weather_timestamp_utc"
    )

    time_difference = (
        "weather_time_difference_minutes"
    )

    weather_temperature = (
        "departure_weather_temperature"
    )

    matched = df[
        df[weather_timestamp].notna()
    ].copy()

    unmatched = df[
        df[weather_timestamp].isna()
    ].copy()

    print("\n" + "-" * 80)
    print("MATCH COUNTS")
    print("-" * 80)

    print(
        f"Total flights:                 {len(df):,}"
    )

    print(
        f"Weather matched:               {len(matched):,}"
    )

    print(
        f"Weather unmatched:             {len(unmatched):,}"
    )

    print(
        f"Overall match rate:            "
        f"{len(matched) / len(df) * 100:.2f}%"
    )

    # ==========================================================
    # UNMATCHED INVESTIGATION
    # ==========================================================

    print("\n" + "-" * 80)
    print("UNMATCHED FLIGHTS")
    print("-" * 80)

    if len(unmatched) > 0:

        print(
            "\nUnmatched by origin airport:"
        )

        print(
            unmatched["ORIGIN"]
            .value_counts()
            .head(20)
            .to_string()
        )

        print(
            "\nUnmatched by carrier:"
        )

        print(
            unmatched["MKT_UNIQUE_CARRIER"]
            .value_counts()
            .to_string()
        )

        # Check whether departure UTC is missing
        if "actual_departure_utc" in df.columns:

            missing_departure_utc = (
                unmatched["actual_departure_utc"]
                .isna()
                .sum()
            )

            print(
                f"\nUnmatched with missing "
                f"actual_departure_utc: "
                f"{missing_departure_utc:,}"
            )

    # ==========================================================
    # TIME DIFFERENCE ANALYSIS
    # ==========================================================

    print("\n" + "-" * 80)
    print("WEATHER TIME DIFFERENCE")
    print("-" * 80)

    if len(matched) > 0:

        diff = matched[
            time_difference
        ].dropna()

        print(
            f"Minimum difference:   "
            f"{diff.min():.2f} minutes"
        )

        print(
            f"Maximum difference:   "
            f"{diff.max():.2f} minutes"
        )

        print(
            f"Mean difference:      "
            f"{diff.mean():.2f} minutes"
        )

        print(
            f"Median difference:    "
            f"{diff.median():.2f} minutes"
        )

        print(
            f"95th percentile:      "
            f"{diff.quantile(0.95):.2f} minutes"
        )

        print(
            f"99th percentile:      "
            f"{diff.quantile(0.99):.2f} minutes"
        )

    # ==========================================================
    # MATCH QUALITY BUCKETS
    # ==========================================================

    print("\n" + "-" * 80)
    print("MATCH QUALITY BUCKETS")
    print("-" * 80)

    if len(matched) > 0:

        within_5 = (
            diff <= 5
        ).sum()

        within_10 = (
            diff <= 10
        ).sum()

        within_15 = (
            diff <= 15
        ).sum()

        within_30 = (
            diff <= 30
        ).sum()

        within_45 = (
            diff <= 45
        ).sum()

        within_60 = (
            diff <= 60
        ).sum()

        total = len(diff)

        buckets = [
            ("≤ 5 minutes", within_5),
            ("≤ 10 minutes", within_10),
            ("≤ 15 minutes", within_15),
            ("≤ 30 minutes", within_30),
            ("≤ 45 minutes", within_45),
            ("≤ 60 minutes", within_60),
        ]

        for label, count in buckets:

            print(
                f"{label:<15} "
                f"{count:>10,} "
                f"({count / total * 100:>6.2f}%)"
            )

    # ==========================================================
    # EXACT HOUR MATCHES
    # ==========================================================

    print("\n" + "-" * 80)
    print("EXACT / NEAR HOURLY MATCHES")
    print("-" * 80)

    if len(matched) > 0:

        for minutes in [0, 1, 2, 3, 5]:

            count = (
                diff <= minutes
            ).sum()

            print(
                f"Within {minutes:>2} minutes: "
                f"{count:,}"
            )

    # ==========================================================
    # WORST MATCHES
    # ==========================================================

    print("\n" + "-" * 80)
    print("WORST WEATHER MATCHES")
    print("-" * 80)

    if len(matched) > 0:

        columns = [
            "FL_DATE",
            "MKT_UNIQUE_CARRIER",
            "MKT_CARRIER_FL_NUM",
            "ORIGIN",
            "DEST",
            "actual_departure_utc",
            weather_timestamp,
            time_difference,
            weather_temperature,
        ]

        columns = [
            col
            for col in columns
            if col in matched.columns
        ]

        worst = (
            matched
            .sort_values(
                time_difference,
                ascending=False
            )
            .head(20)
        )

        print(
            worst[
                columns
            ]
            .to_string(index=False)
        )

    # ==========================================================
    # WEATHER COVERAGE BY AIRPORT
    # ==========================================================

    print("\n" + "-" * 80)
    print("WEATHER MATCH RATE BY AIRPORT")
    print("-" * 80)

    airport_summary = (
        df.groupby("ORIGIN")
        .agg(
            flights=("ORIGIN", "size"),
            matched=(
                weather_timestamp,
                lambda x: x.notna().sum()
            )
        )
    )

    airport_summary[
        "match_rate_pct"
    ] = (
        airport_summary["matched"]
        / airport_summary["flights"]
        * 100
    )

    airport_summary = (
        airport_summary
        .sort_values(
            "match_rate_pct"
        )
    )

    print(
        "\nLowest airport match rates:"
    )

    print(
        airport_summary
        .head(20)
        .to_string()
    )

    # ==========================================================
    # WEATHER VALUE COMPLETENESS
    # ==========================================================

    print("\n" + "-" * 80)
    print("MATCHED WEATHER FIELD COMPLETENESS")
    print("-" * 80)

    if len(matched) > 0:

        weather_columns = [
            col
            for col in matched.columns
            if col.startswith(
                "departure_weather_"
            )
        ]

        for col in weather_columns:

            missing = (
                matched[col]
                .isna()
                .sum()
            )

            print(
                f"{col:<50} "
                f"missing: {missing:,}"
            )

    # ==========================================================
    # FINAL ASSESSMENT
    # ==========================================================

    print("\n" + "=" * 80)
    print("FINAL ASSESSMENT")
    print("=" * 80)

    if len(unmatched) == 0:

        print(
            "PASS: Every flight has a weather match."
        )

    else:

        print(
            f"INFO: {len(unmatched):,} flights "
            f"do not have weather enrichment."
        )

        print(
            "These should be investigated before "
            "building the analytical layer."
        )

    if len(matched) > 0:

        max_diff = diff.max()

        if max_diff <= 60:

            print(
                "PASS: All weather matches are "
                "within the 60-minute tolerance."
            )

        else:

            print(
                "WARNING: Some weather matches "
                "exceed the 60-minute tolerance."
            )

    print("\n" + "=" * 80)
    print("WEATHER MATCH QUALITY INVESTIGATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()