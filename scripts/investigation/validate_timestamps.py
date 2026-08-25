import pandas as pd
from pathlib import Path

FILE_PATH = Path("data/raw/flights_january_2025.xlsx")


def hhmm_to_timestamp(flight_date, hhmm):
    """
    Convert BTS HHMM value to a timestamp.

    Example:
        656  -> 06:56
        5    -> 00:05
        2400 -> next day 00:00
        NaN  -> NaT
    """

    if pd.isna(hhmm):
        return pd.NaT

    hhmm = int(hhmm)

    if hhmm == 2400:
        return (
            pd.Timestamp(flight_date).normalize()
            + pd.Timedelta(days=1)
        )

    hours = hhmm // 100
    minutes = hhmm % 100

    # Basic validation
    if hours > 23 or minutes > 59:
        return pd.NaT

    return (
        pd.Timestamp(flight_date).normalize()
        + pd.Timedelta(hours=hours, minutes=minutes)
    )


def main():

    df = pd.read_excel(FILE_PATH)

    # Only completed flights where we have enough information
    test = df[
        (df["CANCELLED"] == 0)
        & (df["DEP_TIME"].notna())
        & (df["ARR_TIME"].notna())
        & (df["ACTUAL_ELAPSED_TIME"].notna())
    ].copy()

    # Include interesting midnight cases first
    midnight = test[
        (test["DEP_TIME"] == 2400)
        | (test["ARR_TIME"] == 2400)
    ].head(10)

    normal = test[
        (test["DEP_TIME"] != 2400)
        & (test["ARR_TIME"] != 2400)
    ].head(10)

    sample = pd.concat([midnight, normal])

    print("=" * 100)
    print("TIMESTAMP VALIDATION")
    print("=" * 100)

    for _, row in sample.iterrows():

        actual_departure = hhmm_to_timestamp(
            row["FL_DATE"],
            row["DEP_TIME"]
        )

        calculated_arrival = (
            actual_departure
            + pd.Timedelta(
                minutes=row["ACTUAL_ELAPSED_TIME"]
            )
        )

        raw_arrival_time = (
            None
            if pd.isna(row["ARR_TIME"])
            else int(row["ARR_TIME"])
        )

        calculated_hhmm = (
            calculated_arrival.hour * 100
            + calculated_arrival.minute
        )

        # BTS may represent midnight as 2400 instead of 0000
        if raw_arrival_time == 2400:
            raw_arrival_normalized = 0
        else:
            raw_arrival_normalized = raw_arrival_time

        match = calculated_hhmm == raw_arrival_normalized

        print()
        print(
            f"{row['MKT_UNIQUE_CARRIER']} "
            f"{row['MKT_CARRIER_FL_NUM']} | "
            f"{row['ORIGIN']} -> {row['DEST']}"
        )

        print(f"Flight date:       {row['FL_DATE'].date()}")
        print(f"Raw DEP_TIME:      {row['DEP_TIME']}")
        print(f"Raw ARR_TIME:      {row['ARR_TIME']}")
        print(
            f"Elapsed minutes:   "
            f"{row['ACTUAL_ELAPSED_TIME']}"
        )

        print(f"Departure TS:      {actual_departure}")
        print(f"Calculated ARR TS: {calculated_arrival}")

        print(f"Calculated HHMM:   {calculated_hhmm:04d}")
        print(f"Arrival match:     {match}")

    print()
    print("=" * 100)
    print("VALIDATION COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()