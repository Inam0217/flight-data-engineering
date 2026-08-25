import requests


LATITUDE = 40.63980103
LONGITUDE = -73.77890015

URL = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "start_date": "2025-01-01",
    "end_date": "2025-01-01",
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "rain",
        "snowfall",
        "wind_speed_10m",
        "wind_direction_10m",
        "visibility",
        "cloud_cover",
        "weather_code",
    ],
    "timezone": "America/New_York",
}


def main():

    print("=" * 80)
    print("OPEN-METEO VISIBILITY API TEST")
    print("=" * 80)

    print("\nRequesting JFK weather...")

    response = requests.get(
        URL,
        params=params,
        timeout=60,
    )

    print(
        f"HTTP status: {response.status_code}"
    )

    response.raise_for_status()

    data = response.json()

    print("\nReturned hourly variables:")

    for key in data.get("hourly", {}):
        print(f"  {key}")

    hourly = data["hourly"]

    print("\n" + "-" * 80)
    print("VISIBILITY RESPONSE")
    print("-" * 80)

    if "visibility" not in hourly:

        print(
            "ERROR: visibility was not returned by the API."
        )

    else:

        visibility = hourly["visibility"]

        print(
            f"Number of values: {len(visibility)}"
        )

        print(
            f"First 10 values: {visibility[:10]}"
        )

        non_null = [
            value
            for value in visibility
            if value is not None
        ]

        print(
            f"Non-null values: {len(non_null)}"
        )

        if non_null:

            print(
                f"Minimum: {min(non_null)}"
            )

            print(
                f"Maximum: {max(non_null)}"
            )

    print("\n" + "=" * 80)
    print("API TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()