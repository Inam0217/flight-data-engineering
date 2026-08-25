import pandas as pd
from pathlib import Path
from zoneinfo import ZoneInfo


FLIGHT_FILE = Path(
    "data/raw/flights_january_2025.xlsx"
)

AIRPORT_FILE = Path(
    "data/processed/airports_enriched.csv"
)


def hhmm_to_local_timestamp(
    flight_date,
    hhmm,
    timezone
):
    """
    Convert BTS HHMM into a timezone-aware
    local timestamp.

    2400 means midnight at the END
    of the flight date.
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


def build_actual_timestamps(row):

    departure_local = hhmm_to_local_timestamp(
        row["FL_DATE"],
        row["DEP_TIME"],
        row["origin_timezone"]
    )

    arrival_local = hhmm_to_local_timestamp(
        row["FL_DATE"],
        row["ARR_TIME"],
        row["destination_timezone"]
    )

    # -------------------------------------------------
    # Overnight correction
    # -------------------------------------------------

    if (
        pd.notna(departure_local)
        and pd.notna(arrival_local)
        and arrival_local < departure_local
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


def main():

    print("=" * 80)
    print("OVERNIGHT FLIGHT TIMESTAMP VALIDATION")
    print("=" * 80)

    # -------------------------------------------------
    # Load flights
    # -------------------------------------------------

    df = pd.read_excel(
        FLIGHT_FILE,
        nrows=5000
    )

    # -------------------------------------------------
    # Load airport timezones
    # -------------------------------------------------

    airports = pd.read_csv(
        AIRPORT_FILE
    )

    airport_timezones = (
        airports[
            [
                "airport_code",
                "timezone"
            ]
        ]
        .drop_duplicates("airport_code")
    )

    # -------------------------------------------------
    # Origin timezone
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Destination timezone
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Only completed flights with required fields
    # -------------------------------------------------

    test = df[
        (df["CANCELLED"] == 0)
        & (df["DEP_TIME"].notna())
        & (df["ARR_TIME"].notna())
        & (df["ACTUAL_ELAPSED_TIME"].notna())
    ].copy()

    # -------------------------------------------------
    # Find flights where raw arrival clock
    # is earlier than raw departure clock.
    # These are our overnight candidates.
    # -------------------------------------------------

    test["overnight_candidate"] = (
        test["ARR_TIME"]
        < test["DEP_TIME"]
    )

    overnight = test[
        test["overnight_candidate"]
    ].head(10)

    print(
        f"\nOvernight candidates in first "
        f"{len(test):,} rows: "
        f"{test['overnight_candidate'].sum():,}"
    )

    print(
        "\nShowing first 10 overnight candidates:"
    )

    # -------------------------------------------------
    # Validate selected flights
    # -------------------------------------------------

    for _, row in overnight.iterrows():

        (
            departure_local,
            arrival_local,
            departure_utc,
            arrival_utc
        ) = build_actual_timestamps(row)

        calculated_duration = (
            arrival_utc - departure_utc
        ).total_seconds() / 60

        reported_duration = (
            row["ACTUAL_ELAPSED_TIME"]
        )

        difference = (
            calculated_duration
            - reported_duration
        )

        print("\n" + "-" * 80)

        print(
            f"{row['MKT_UNIQUE_CARRIER']} "
            f"{int(row['MKT_CARRIER_FL_NUM'])} | "
            f"{row['ORIGIN']} → {row['DEST']}"
        )

        print(
            f"Flight date: "
            f"{row['FL_DATE'].date()}"
        )

        print(
            f"Raw departure: "
            f"{int(row['DEP_TIME']):04d}"
        )

        print(
            f"Raw arrival:   "
            f"{int(row['ARR_TIME']):04d}"
        )

        print(
            f"Departure local: "
            f"{departure_local}"
        )

        print(
            f"Arrival local:   "
            f"{arrival_local}"
        )

        print(
            f"Departure UTC: "
            f"{departure_utc}"
        )

        print(
            f"Arrival UTC:   "
            f"{arrival_utc}"
        )

        print(
            f"Calculated duration: "
            f"{calculated_duration:.1f} minutes"
        )

        print(
            f"BTS elapsed time:    "
            f"{reported_duration:.1f} minutes"
        )

        print(
            f"Difference:           "
            f"{difference:.1f} minutes"
        )

    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()