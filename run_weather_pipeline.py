from airport_repository import get_airports
from weather_api import get_weather
from weather_loader import load_weather


START_DATE = "2025-01-05"
END_DATE = "2025-01-05"


def main():
    airports = get_airports()

    print(f"Found {len(airports)} airports.")

    all_weather_rows = []

    for airport in airports:
        print(
            f"Fetching weather for "
            f"{airport['airport_code']}..."
        )

        weather_rows = get_weather(
            airport_code=airport["airport_code"],
            latitude=airport["latitude"],
            longitude=airport["longitude"],
            timezone=airport["timezone"],
            start_date=START_DATE,
            end_date=END_DATE
        )

        print(
            f"  Received {len(weather_rows)} rows."
        )

        all_weather_rows.extend(weather_rows)

    print(
        f"Total weather rows prepared: "
        f"{len(all_weather_rows)}"
    )

    load_weather(all_weather_rows)


if __name__ == "__main__":
    main()