import requests
import time


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)

MAX_RETRIES = 3

RETRY_DELAYS = [
    2,
    5,
    10
]

REQUEST_TIMEOUT = 30


# =========================================================
# WEATHER API
# =========================================================

def get_weather(
    airport_code,
    latitude,
    longitude,
    timezone,
    start_date,
    end_date
):

    params = {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "start_date": start_date,
        "end_date": end_date,
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
            "weather_code"
        ],
        "timezone": timezone
    }

    # =====================================================
    # RETRY LOOP
    # =====================================================

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            print(
                f"    API request attempt "
                f"{attempt}/{MAX_RETRIES}"
            )

            response = requests.get(
                API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()

            data = response.json()

            # -------------------------------------------------
            # Validate API response
            # -------------------------------------------------

            if "hourly" not in data:

                raise ValueError(
                    "API response does not contain "
                    "'hourly' data."
                )

            hourly = data["hourly"]

            weather_rows = []

            for i in range(
                len(hourly["time"])
            ):

                row = {
                    "airport_code": airport_code,
                    "weather_timestamp": (
                        hourly["time"][i]
                    ),
                    "temperature": (
                        hourly["temperature_2m"][i]
                    ),
                    "humidity": (
                        hourly[
                            "relative_humidity_2m"
                        ][i]
                    ),
                    "precipitation": (
                        hourly["precipitation"][i]
                    ),
                    "rain": (
                        hourly["rain"][i]
                    ),
                    "snowfall": (
                        hourly["snowfall"][i]
                    ),
                    "wind_speed": (
                        hourly["wind_speed_10m"][i]
                    ),
                    "wind_direction": (
                        hourly[
                            "wind_direction_10m"
                        ][i]
                    ),
                    "visibility": (
                        hourly["visibility"][i]
                    ),
                    "cloud_cover": (
                        hourly["cloud_cover"][i]
                    ),
                    "weather_code": (
                        hourly["weather_code"][i]
                    )
                }

                weather_rows.append(
                    row
                )

            # -------------------------------------------------
            # Validate row count
            # -------------------------------------------------

            if len(weather_rows) == 0:

                raise ValueError(
                    f"No weather rows returned "
                    f"for {airport_code}."
                )

            return weather_rows

        # =====================================================
        # REQUEST FAILURE
        # =====================================================

        except requests.RequestException as error:

            last_error = error

            print(
                f"    Request failed: {error}"
            )

            if attempt < MAX_RETRIES:

                delay = RETRY_DELAYS[
                    attempt - 1
                ]

                print(
                    f"    Retrying in "
                    f"{delay} seconds..."
                )

                time.sleep(delay)

        # =====================================================
        # DATA / VALIDATION FAILURE
        # =====================================================

        except Exception as error:

            last_error = error

            print(
                f"    API/data error: {error}"
            )

            if attempt < MAX_RETRIES:

                delay = RETRY_DELAYS[
                    attempt - 1
                ]

                print(
                    f"    Retrying in "
                    f"{delay} seconds..."
                )

                time.sleep(delay)

    # =====================================================
    # ALL RETRIES FAILED
    # =====================================================

    raise RuntimeError(
        f"Weather extraction failed for "
        f"{airport_code} after "
        f"{MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
    )