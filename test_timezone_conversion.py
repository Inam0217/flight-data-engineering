import pandas as pd
from zoneinfo import ZoneInfo


def convert_local_time_to_utc(
    flight_date,
    hhmm,
    timezone
):
    """
    Convert a BTS local airport time (HHMM)
    into a UTC timestamp.
    """

    if pd.isna(hhmm):
        return pd.NaT

    hhmm = int(hhmm)

    # BTS uses 2400 to represent midnight
    # at the end of the flight date.
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

    tests = [
        {
            "airport": "JFK",
            "date": "2025-01-01",
            "time": 656,
            "timezone": "America/New_York",
        },
        {
            "airport": "LAX",
            "date": "2025-01-01",
            "time": 543,
            "timezone": "America/Los_Angeles",
        },
        {
            "airport": "MIA",
            "date": "2025-01-01",
            "time": 2307,
            "timezone": "America/New_York",
        },
        {
            "airport": "MCO",
            "date": "2025-01-01",
            "time": 2400,
            "timezone": "America/New_York",
        },
    ]

    print("=" * 70)
    print("LOCAL TIME → UTC TEST")
    print("=" * 70)

    for test in tests:

        result = convert_local_time_to_utc(
            test["date"],
            test["time"],
            test["timezone"]
        )

        print(
            f"\n{test['airport']} "
            f"| local={test['time']} "
            f"| timezone={test['timezone']}"
        )

        print(
            f"UTC: {result}"
        )


if __name__ == "__main__":
    main()