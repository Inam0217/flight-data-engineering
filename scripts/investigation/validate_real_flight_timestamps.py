import pandas as pd
from pathlib import Path
from zoneinfo import ZoneInfo


FLIGHT_FILE = Path(
    "data/raw/flights_january_2025.xlsx"
)

AIRPORT_FILE = Path(
    "data/processed/airports_enriched.csv"
)


def convert_local_time_to_utc(
    flight_date,
    hhmm,
    timezone
):
    """
    Convert BTS local airport time (HHMM)
    into UTC.
    """

    if pd.isna(hhmm):
        return pd.NaT

    hhmm = int(hhmm)

    if hhmm == 2400:

        local_date = (
            pd.Timestamp(flight_date)
            + pd.Timedelta(days=1)
        ).date()

        local_time = "00:00"

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

        local_time = (
            f"{hours:02d}:{minutes:02d}"
        )

    local_timestamp = pd.Timestamp(
        f"{local_date} {local_time}"
    )

    localized = local_timestamp.tz_localize(
        ZoneInfo(timezone)
    )

    return localized.tz_convert("UTC")


def main():

    # -----------------------------------------------------
    # Load flight data
    # -----------------------------------------------------

    df = pd.read_excel(
        FLIGHT_FILE,
        nrows=1000
    )

    # -----------------------------------------------------
    # Load airport metadata
    # -----------------------------------------------------

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
        .drop_duplicates(
            "airport_code"
        )
    )

    # -----------------------------------------------------
    # Add origin timezone
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Add destination timezone
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Validate timezone coverage
    # -----------------------------------------------------

    print("=" * 70)
    print("REAL FLIGHT TIMESTAMP VALIDATION")
    print("=" * 70)

    print(
        "\nMissing origin timezones:",
        df["origin_timezone"].isna().sum()
    )

    print(
        "Missing destination timezones:",
        df["destination_timezone"].isna().sum()
    )

    # -----------------------------------------------------
    # Convert sample flights
    # -----------------------------------------------------

    sample = df[
        (df["CANCELLED"] == 0)
        & df["DEP_TIME"].notna()
        & df["ARR_TIME"].notna()
    ].head(10)

    print("\n" + "=" * 70)
    print("SAMPLE FLIGHTS")
    print("=" * 70)

    for _, row in sample.iterrows():

        departure_utc = convert_local_time_to_utc(
            row["FL_DATE"],
            row["DEP_TIME"],
            row["origin_timezone"]
        )

        arrival_utc = convert_local_time_to_utc(
            row["FL_DATE"],
            row["ARR_TIME"],
            row["destination_timezone"]
        )

        print()
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
            f"Local departure: "
            f"{row['DEP_TIME']}"
            f" ({row['origin_timezone']})"
        )

        print(
            f"UTC departure:   "
            f"{departure_utc}"
        )

        print(
            f"Local arrival:   "
            f"{row['ARR_TIME']}"
            f" ({row['destination_timezone']})"
        )

        print(
            f"UTC arrival:     "
            f"{arrival_utc}"
        )

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()