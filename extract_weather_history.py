import pandas as pd
from pathlib import Path
from weather_api import get_weather
import time


# =========================================================
# CONFIGURATION
# =========================================================

AIRPORT_FILE = Path(
    "data/processed/airports_enriched.csv"
)

OUTPUT_FILE = Path(
    "data/processed/weather_january_2025_all_airports.csv"
)

START_DATE = "2025-01-01"
END_DATE = "2025-01-31"

REQUEST_DELAY_SECONDS = 0.2

WEATHER_COLUMNS = [
    "airport_code",
    "weather_timestamp",
    "temperature",
    "humidity",
    "precipitation",
    "rain",
    "snowfall",
    "wind_speed",
    "wind_direction",
    "visibility",
    "cloud_cover",
    "weather_code"
]


# =========================================================
# LOAD AIRPORTS
# =========================================================

def load_airports():

    airports = pd.read_csv(
        AIRPORT_FILE
    )

    airports["airport_code"] = (
        airports["airport_code"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Remove invalid rows
    airports = airports[
        airports["airport_code"].notna()
    ].copy()

    # Ensure one row per airport
    airports = airports.drop_duplicates(
        subset=["airport_code"]
    )

    return airports


# =========================================================
# LOAD EXISTING RESULTS
# =========================================================

def load_existing_weather():

    if not OUTPUT_FILE.exists():

        return pd.DataFrame(
            columns=WEATHER_COLUMNS
        )

    print(
        f"\nExisting output found:"
        f" {OUTPUT_FILE}"
    )

    existing = pd.read_csv(
        OUTPUT_FILE
    )

    existing["airport_code"] = (
        existing["airport_code"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return existing


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 80)
    print("PRODUCTION HISTORICAL WEATHER EXTRACTION")
    print("=" * 80)

    # -----------------------------------------------------
    # LOAD AIRPORTS
    # -----------------------------------------------------

    airports = load_airports()

    print(
        f"\nAirports available: "
        f"{len(airports):,}"
    )

    # -----------------------------------------------------
    # LOAD EXISTING DATA
    # -----------------------------------------------------

    existing_weather = (
        load_existing_weather()
    )

    completed_airports = set(
        existing_weather[
            "airport_code"
        ].unique()
    )

    print(
        f"Already completed airports: "
        f"{len(completed_airports):,}"
    )

    # -----------------------------------------------------
    # DETERMINE WORK REMAINING
    # -----------------------------------------------------

    remaining = airports[
        ~airports["airport_code"].isin(
            completed_airports
        )
    ].copy()

    print(
        f"Airports remaining: "
        f"{len(remaining):,}"
    )

    if remaining.empty:

        print(
            "\nAll airports already extracted."
        )

        return

    # -----------------------------------------------------
    # EXTRACTION
    # -----------------------------------------------------

    successful_airports = 0
    failed_airports = []

    new_weather_rows = []

    total_airports = len(remaining)

    for position, (_, airport) in enumerate(
        remaining.iterrows(),
        start=1
    ):

        airport_code = (
            airport["airport_code"]
        )

        print("\n" + "-" * 80)

        print(
            f"[{position}/{total_airports}] "
            f"Extracting {airport_code}"
        )

        print(
            f"Coordinates: "
            f"{airport['latitude']}, "
            f"{airport['longitude']}"
        )

        print(
            f"Timezone: "
            f"{airport['timezone']}"
        )

        try:

            rows = get_weather(
                airport_code=airport_code,
                latitude=airport["latitude"],
                longitude=airport["longitude"],
                timezone=airport["timezone"],
                start_date=START_DATE,
                end_date=END_DATE
            )

            print(
                f"Rows extracted: "
                f"{len(rows):,}"
            )

            new_weather_rows.extend(
                rows
            )

            successful_airports += 1

        except Exception as error:

            print(
                f"ERROR: {error}"
            )

            failed_airports.append(
                {
                    "airport_code": airport_code,
                    "error": str(error)
                }
            )

        # -------------------------------------------------
        # Small delay between API requests
        # -------------------------------------------------

        time.sleep(
            REQUEST_DELAY_SECONDS
        )

        # -------------------------------------------------
        # Checkpoint every 10 airports
        # -------------------------------------------------

        if position % 10 == 0:

            checkpoint = pd.DataFrame(
                new_weather_rows,
                columns=WEATHER_COLUMNS
            )

            combined = pd.concat(
                [
                    existing_weather,
                    checkpoint
                ],
                ignore_index=True
            )

            combined = combined.drop_duplicates(
                subset=[
                    "airport_code",
                    "weather_timestamp"
                ]
            )

            OUTPUT_FILE.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            combined.to_csv(
                OUTPUT_FILE,
                index=False
            )

            print(
                f"\nCHECKPOINT SAVED"
            )

            print(
                f"Weather rows saved: "
                f"{len(combined):,}"
            )

    # -----------------------------------------------------
    # FINAL SAVE
    # -----------------------------------------------------

    new_weather = pd.DataFrame(
        new_weather_rows,
        columns=WEATHER_COLUMNS
    )

    combined = pd.concat(
        [
            existing_weather,
            new_weather
        ],
        ignore_index=True
    )

    combined = combined.drop_duplicates(
        subset=[
            "airport_code",
            "weather_timestamp"
        ]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # =====================================================
    # FINAL REPORT
    # =====================================================

    print("\n")
    print("=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)

    print(
        f"Total airports: "
        f"{len(airports):,}"
    )

    print(
        f"Successful this run: "
        f"{successful_airports:,}"
    )

    print(
        f"Failed this run: "
        f"{len(failed_airports):,}"
    )

    print(
        f"Total airports with data: "
        f"{combined['airport_code'].nunique():,}"
    )

    print(
        f"Total weather rows: "
        f"{len(combined):,}"
    )

    if not combined.empty:

        print(
            f"First timestamp: "
            f"{combined['weather_timestamp'].min()}"
        )

        print(
            f"Last timestamp: "
            f"{combined['weather_timestamp'].max()}"
        )

    # -----------------------------------------------------
    # Failed airports
    # -----------------------------------------------------

    if failed_airports:

        print("\n" + "-" * 80)
        print("FAILED AIRPORTS")
        print("-" * 80)

        for failure in failed_airports:

            print(
                f"{failure['airport_code']}: "
                f"{failure['error']}"
            )

        failed_file = Path(
            "data/processed/"
            "weather_failed_airports.csv"
        )

        pd.DataFrame(
            failed_airports
        ).to_csv(
            failed_file,
            index=False
        )

        print(
            f"\nFailure report saved to: "
            f"{failed_file}"
        )

    print(
        f"\nWeather data saved to:"
        f" {OUTPUT_FILE}"
    )

    print("\n" + "=" * 80)
    print(
        "PRODUCTION WEATHER EXTRACTION COMPLETE"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()