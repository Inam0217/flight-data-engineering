import mysql.connector
import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path(
    "data/processed/flights_analytics.csv"
)

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Kashar",
    "database": "flight_analytics",
}

BATCH_SIZE = 5000


# ============================================================
# MYSQL CONNECTION
# ============================================================

def get_connection():

    return mysql.connector.connect(
        **DB_CONFIG
    )


# ============================================================
# CLEANING HELPERS
# ============================================================

def clean_value(value):

    if pd.isna(value):
        return None

    return value


def clean_numeric(value):

    if pd.isna(value):
        return None

    return float(value)


def clean_integer(value):

    if pd.isna(value):
        return None

    return int(value)


def clean_datetime(value):

    if pd.isna(value):
        return None

    timestamp = pd.Timestamp(value)

    return timestamp.strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ============================================================
# LOAD DIMENSION LOOKUPS
# ============================================================

def load_dimension_lookups(connection):

    cursor = connection.cursor()

    print("\nLoading dimension lookups...")

    # --------------------------------------------------------
    # AIRPORT
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            airport_id,
            airport_code
        FROM dim_airport
    """)

    airport_lookup = {
        str(code)
        .strip()
        .upper(): airport_id
        for airport_id, code
        in cursor.fetchall()
    }

    print(
        f"Airport lookup entries: "
        f"{len(airport_lookup):,}"
    )

    # --------------------------------------------------------
    # CARRIER
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            carrier_id,
            carrier_code
        FROM dim_carrier
    """)

    carrier_lookup = {
        str(code)
        .strip()
        .upper(): carrier_id
        for carrier_id, code
        in cursor.fetchall()
    }

    print(
        f"Carrier lookup entries: "
        f"{len(carrier_lookup):,}"
    )

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            date_id,
            full_date
        FROM dim_date
    """)

    date_lookup = {
        pd.Timestamp(full_date).date(): date_id
        for date_id, full_date
        in cursor.fetchall()
    }

    print(
        f"Date lookup entries: "
        f"{len(date_lookup):,}"
    )

    cursor.close()

    return (
        airport_lookup,
        carrier_lookup,
        date_lookup,
    )


# ============================================================
# DIMENSION MAPPING VALIDATION
# ============================================================

def validate_dimension_mappings(
    flights,
    airport_lookup,
    carrier_lookup,
    date_lookup,
):

    print("\n" + "-" * 80)
    print("DIMENSION MAPPING VALIDATION")
    print("-" * 80)

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    flight_dates = (
        pd.to_datetime(
            flights["FL_DATE"]
        )
        .dt.date
    )

    missing_dates = sum(
        value not in date_lookup
        for value in flight_dates
    )

    print(
        f"Missing date mappings: "
        f"{missing_dates:,}"
    )

    # --------------------------------------------------------
    # CARRIER
    # --------------------------------------------------------

    carriers = (
        flights["MKT_UNIQUE_CARRIER"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    missing_carriers = sum(
        value not in carrier_lookup
        for value in carriers
    )

    print(
        f"Missing carrier mappings: "
        f"{missing_carriers:,}"
    )

    # --------------------------------------------------------
    # ORIGIN
    # --------------------------------------------------------

    origins = (
        flights["ORIGIN"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    missing_origins = sum(
        value not in airport_lookup
        for value in origins
    )

    print(
        f"Missing origin mappings: "
        f"{missing_origins:,}"
    )

    # --------------------------------------------------------
    # DESTINATION
    # --------------------------------------------------------

    destinations = (
        flights["DEST"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    missing_destinations = sum(
        value not in airport_lookup
        for value in destinations
    )

    print(
        f"Missing destination mappings: "
        f"{missing_destinations:,}"
    )

    total_missing = (
        missing_dates
        + missing_carriers
        + missing_origins
        + missing_destinations
    )

    if total_missing > 0:

        raise ValueError(
            "Dimension mapping validation failed."
        )

    print(
        "\nAll dimension mappings: PASS"
    )


# ============================================================
# BUILD FACT ROW
# ============================================================

def build_fact_row(
    row,
    airport_lookup,
    carrier_lookup,
    date_lookup,
):

    flight_date = (
        pd.Timestamp(
            row["FL_DATE"]
        )
        .date()
    )

    carrier_code = (
        str(
            row["MKT_UNIQUE_CARRIER"]
        )
        .strip()
        .upper()
    )

    origin_code = (
        str(
            row["ORIGIN"]
        )
        .strip()
        .upper()
    )

    destination_code = (
        str(
            row["DEST"]
        )
        .strip()
        .upper()
    )

    return (

        # ====================================================
        # IDENTIFIERS / DIMENSIONS
        # ====================================================

        clean_integer(
            row["flight_row_id"]
        ),

        date_lookup[
            flight_date
        ],

        carrier_lookup[
            carrier_code
        ],

        airport_lookup[
            origin_code
        ],

        airport_lookup[
            destination_code
        ],

        clean_integer(
            row["MKT_CARRIER_FL_NUM"]
        ),

        # ====================================================
        # DEPARTURE TIMES
        # ====================================================

        clean_datetime(
            row["scheduled_departure_local"]
        ),

        clean_datetime(
            row["scheduled_departure_utc"]
        ),

        clean_datetime(
            row["actual_departure_local"]
        ),

        clean_datetime(
            row["actual_departure_utc"]
        ),

        # ====================================================
        # ARRIVAL TIMES
        # ====================================================

        clean_datetime(
            row["scheduled_arrival_local"]
        ),

        clean_datetime(
            row["scheduled_arrival_utc"]
        ),

        clean_datetime(
            row["actual_arrival_local"]
        ),

        clean_datetime(
            row["actual_arrival_utc"]
        ),

        # ====================================================
        # DEPARTURE
        # ====================================================

        clean_integer(
            row["CRS_DEP_TIME"]
        ),

        clean_integer(
            row["DEP_TIME"]
        ),

        # ====================================================
        # CORRECTED ANALYTICAL DEPARTURE DELAY
        # ====================================================

        clean_numeric(
            row["departure_delay_minutes"]
        ),

        clean_numeric(
            row["DEP_DELAY_NEW"]
        ),

        # ====================================================
        # ARRIVAL
        # ====================================================

        clean_integer(
            row["CRS_ARR_TIME"]
        ),

        clean_integer(
            row["ARR_TIME"]
        ),

        # ====================================================
        # CORRECTED ANALYTICAL ARRIVAL DELAY
        # ====================================================

        clean_numeric(
            row["arrival_delay_minutes"]
        ),

        clean_numeric(
            row["ARR_DELAY_NEW"]
        ),

        # ====================================================
        # FLIGHT METRICS
        # ====================================================

        clean_numeric(
            row["CRS_ELAPSED_TIME"]
        ),

        clean_numeric(
            row["ACTUAL_ELAPSED_TIME"]
        ),

        clean_numeric(
            row["AIR_TIME"]
        ),

        clean_numeric(
            row["DISTANCE"]
        ),

        # ====================================================
        # STATUS
        # ====================================================

        clean_integer(
            row["CANCELLED"]
        ),

        clean_value(
            row["CANCELLATION_CODE"]
        ),

        clean_integer(
            row["DIVERTED"]
        ),

        # ====================================================
        # DELAY DRIVERS
        # ====================================================

        clean_numeric(
            row["CARRIER_DELAY"]
        ),

        clean_numeric(
            row["WEATHER_DELAY"]
        ),

        clean_numeric(
            row["NAS_DELAY"]
        ),

        clean_numeric(
            row["SECURITY_DELAY"]
        ),

        clean_numeric(
            row["LATE_AIRCRAFT_DELAY"]
        ),

        # ====================================================
        # ANALYTICAL CLASSIFICATION
        # ====================================================

        clean_value(
            row["delay_category"]
        ),

        clean_value(
            row["primary_delay_driver"]
        ),

        # ====================================================
        # WEATHER
        # ====================================================

        clean_datetime(
            row[
                "departure_weather_weather_timestamp_utc"
            ]
        ),

        clean_numeric(
            row[
                "departure_weather_temperature"
            ]
        ),

        clean_numeric(
            row[
                "departure_weather_humidity"
            ]
        ),

        clean_numeric(
            row[
                "departure_weather_precipitation"
            ]
        ),

        clean_numeric(
            row[
                "departure_weather_rain"
            ]
        ),

        clean_numeric(
            row[
                "departure_weather_snowfall"
            ]
        ),

        clean_numeric(
            row[
                "departure_weather_wind_speed"
            ]
        ),

        clean_numeric(
            row[
                "departure_weather_wind_direction"
            ]
        ),

        clean_numeric(
            row[
                "departure_weather_cloud_cover"
            ]
        ),

        clean_integer(
            row[
                "departure_weather_weather_code"
            ]
        ),

        clean_numeric(
            row[
                "weather_time_difference_minutes"
            ]
        ),

        clean_value(
            row["weather_severity"]
        ),
    )


# ============================================================
# INSERT STATEMENT
# ============================================================

INSERT_SQL = """

INSERT INTO fact_flight (

    flight_row_id,

    date_id,
    carrier_id,
    origin_airport_id,
    destination_airport_id,

    carrier_flight_number,

    scheduled_departure_local,
    scheduled_departure_utc,
    actual_departure_local,
    actual_departure_utc,

    scheduled_arrival_local,
    scheduled_arrival_utc,
    actual_arrival_local,
    actual_arrival_utc,

    crs_dep_time,
    dep_time,

    dep_delay,
    dep_delay_new,

    crs_arr_time,
    arr_time,

    arr_delay,
    arr_delay_new,

    crs_elapsed_time,
    actual_elapsed_time,
    air_time,
    distance,

    cancelled,
    cancellation_code,
    diverted,

    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,

    delay_category,
    primary_delay_driver,

    weather_timestamp_utc,
    weather_temperature,
    weather_humidity,
    weather_precipitation,
    weather_rain,
    weather_snowfall,
    weather_wind_speed,
    weather_wind_direction,
    weather_cloud_cover,
    weather_code,
    weather_time_difference_minutes,
    weather_severity

)

VALUES (

    %s,

    %s,
    %s,
    %s,
    %s,

    %s,

    %s,
    %s,
    %s,
    %s,

    %s,
    %s,
    %s,
    %s,

    %s,
    %s,

    %s,
    %s,

    %s,
    %s,

    %s,
    %s,

    %s,
    %s,
    %s,
    %s,

    %s,
    %s,
    %s,

    %s,
    %s,
    %s,
    %s,
    %s,

    %s,
    %s,

    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s

)

"""


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("FLIGHT ANALYTICS WAREHOUSE - FACT LOAD")
    print("=" * 80)

    # ========================================================
    # LOAD ANALYTICAL DATASET
    # ========================================================

    print(
        "\nLoading analytical flight dataset..."
    )

    flights = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Flights loaded: "
        f"{len(flights):,}"
    )

    expected_rows = len(
        flights
    )

    # ========================================================
    # REQUIRED COLUMN VALIDATION
    # ========================================================

    required_columns = [

        "flight_row_id",

        "FL_DATE",

        "MKT_UNIQUE_CARRIER",

        "MKT_CARRIER_FL_NUM",

        "ORIGIN",

        "DEST",

        # IMPORTANT:
        # These are the actual analytical
        # delay fields in our CSV.

        "departure_delay_minutes",

        "arrival_delay_minutes",

        "delay_category",

        "primary_delay_driver",

        "weather_severity",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in flights.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(
                missing_columns
            )
        )

    # ========================================================
    # DUPLICATE INPUT VALIDATION
    # ========================================================

    duplicate_ids = (
        flights[
            "flight_row_id"
        ]
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate input flight_row_id: "
        f"{duplicate_ids:,}"
    )

    if duplicate_ids > 0:

        raise ValueError(
            "Input dataset contains duplicate "
            "flight_row_id values."
        )

    print(
        "Input validation: PASS"
    )

    # ========================================================
    # CONNECT MYSQL
    # ========================================================

    print(
        "\nConnecting to MySQL..."
    )

    connection = get_connection()

    print(
        "MySQL connection: SUCCESS"
    )

    try:

        # ====================================================
        # LOAD DIMENSION LOOKUPS
        # ====================================================

        (
            airport_lookup,
            carrier_lookup,
            date_lookup,
        ) = load_dimension_lookups(
            connection
        )

        # ====================================================
        # VALIDATE DIMENSIONS
        # ====================================================

        validate_dimension_mappings(
            flights,
            airport_lookup,
            carrier_lookup,
            date_lookup,
        )

        # ====================================================
        # CHECK EXISTING FACT ROWS
        # ====================================================

        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM fact_flight"
        )

        existing_rows = (
            cursor.fetchone()[0]
        )

        cursor.close()

        print(
            "\nExisting fact_flight rows:"
        )

        print(
            f"  {existing_rows:,}"
        )

        # ====================================================
        # CONTROLLED FULL REFRESH
        # ====================================================

        if existing_rows > 0:

            print(
                "\nWARNING: fact_flight already "
                f"contains {existing_rows:,} rows."
            )

            print(
                "Clearing fact_flight for "
                "controlled reload..."
            )

            cursor = connection.cursor()

            cursor.execute(
                "DELETE FROM fact_flight"
            )

            connection.commit()

            cursor.close()

            print(
                "Existing fact_flight rows removed."
            )

        # ====================================================
        # INSERT FACT ROWS
        # ====================================================

        print(
            "\n" + "-" * 80
        )

        print(
            "LOADING FACT_FLIGHT"
        )

        print(
            "-" * 80
        )

        cursor = connection.cursor()

        batch = []

        inserted = 0

        for _, row in flights.iterrows():

            fact_row = build_fact_row(
                row,
                airport_lookup,
                carrier_lookup,
                date_lookup,
            )

            batch.append(
                fact_row
            )

            if len(batch) >= BATCH_SIZE:

                cursor.executemany(
                    INSERT_SQL,
                    batch
                )

                inserted += len(
                    batch
                )

                print(
                    f"Inserted: "
                    f"{inserted:,} / "
                    f"{expected_rows:,}"
                )

                batch = []

        # ====================================================
        # FINAL BATCH
        # ====================================================

        if batch:

            cursor.executemany(
                INSERT_SQL,
                batch
            )

            inserted += len(
                batch
            )

            print(
                f"Inserted: "
                f"{inserted:,} / "
                f"{expected_rows:,}"
            )

        # ====================================================
        # INSERT COUNT VALIDATION
        # ====================================================

        if inserted != expected_rows:

            raise RuntimeError(
                "Inserted row count does not match "
                "analytical dataset."
            )

        # ====================================================
        # COMMIT
        # ====================================================

        print(
            "\nCommitting transaction..."
        )

        connection.commit()

        print(
            "Transaction committed."
        )

        cursor.close()

        # ====================================================
        # FACT VALIDATION
        # ====================================================

        print(
            "\n" + "-" * 80
        )

        print(
            "FACT TABLE VALIDATION"
        )

        print(
            "-" * 80
        )

        cursor = connection.cursor()

        # ----------------------------------------------------
        # ROW COUNT
        # ----------------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) FROM fact_flight"
        )

        actual_rows = (
            cursor.fetchone()[0]
        )

        print(
            f"Expected rows: "
            f"{expected_rows:,}"
        )

        print(
            f"Actual rows:   "
            f"{actual_rows:,}"
        )

        if actual_rows != expected_rows:

            raise RuntimeError(
                "Fact row count validation failed."
            )

        print(
            "Row count: PASS"
        )

        # ----------------------------------------------------
        # DUPLICATES
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT flight_row_id
                FROM fact_flight
                GROUP BY flight_row_id
                HAVING COUNT(*) > 1
            ) duplicates
        """)

        duplicate_count = (
            cursor.fetchone()[0]
        )

        print(
            f"Duplicate flight_row_id: "
            f"{duplicate_count:,}"
        )

        if duplicate_count != 0:

            raise RuntimeError(
                "Duplicate flight_row_id detected."
            )

        print(
            "Duplicate check: PASS"
        )

        # ----------------------------------------------------
        # FOREIGN KEY REFERENCES
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_flight f

            LEFT JOIN dim_date d
                ON f.date_id = d.date_id

            LEFT JOIN dim_carrier c
                ON f.carrier_id = c.carrier_id

            LEFT JOIN dim_airport oa
                ON f.origin_airport_id = oa.airport_id

            LEFT JOIN dim_airport da
                ON f.destination_airport_id = da.airport_id

            WHERE d.date_id IS NULL
               OR c.carrier_id IS NULL
               OR oa.airport_id IS NULL
               OR da.airport_id IS NULL
        """)

        broken_references = (
            cursor.fetchone()[0]
        )

        print(
            f"Broken dimension references: "
            f"{broken_references:,}"
        )

        if broken_references != 0:

            raise RuntimeError(
                "Broken dimension references detected."
            )

        print(
            "Dimension references: PASS"
        )

        # ----------------------------------------------------
        # FLIGHT STATUS
        # ----------------------------------------------------

        print(
            "\nFact flight status:"
        )

        cursor.execute("""
            SELECT
                SUM(cancelled = 1),
                SUM(diverted = 1),
                SUM(
                    cancelled = 0
                    AND diverted = 0
                )
            FROM fact_flight
        """)

        cancelled, diverted, completed = (
            cursor.fetchone()
        )

        print(
            f"  Cancelled: "
            f"{cancelled:,}"
        )

        print(
            f"  Diverted:  "
            f"{diverted:,}"
        )

        print(
            f"  Completed: "
            f"{completed:,}"
        )

        # ----------------------------------------------------
        # WEATHER COVERAGE
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                COUNT(
                    weather_timestamp_utc
                ),
                COUNT(*)
            FROM fact_flight
        """)

        weather_available, total = (
            cursor.fetchone()
        )

        print(
            f"\nWeather available: "
            f"{weather_available:,} / "
            f"{total:,}"
        )

        # ----------------------------------------------------
        # DELAY CATEGORY
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_flight
            WHERE delay_category IS NULL
        """)

        missing_categories = (
            cursor.fetchone()[0]
        )

        print(
            f"Missing delay categories: "
            f"{missing_categories:,}"
        )

        if missing_categories != 0:

            raise RuntimeError(
                "Missing delay categories detected."
            )

        print(
            "Delay category: PASS"
        )

        # ----------------------------------------------------
        # PRIMARY DELAY DRIVER
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_flight
            WHERE primary_delay_driver IS NULL
        """)

        missing_drivers = (
            cursor.fetchone()[0]
        )

        print(
            f"Missing primary delay drivers: "
            f"{missing_drivers:,}"
        )

        if missing_drivers != 0:

            raise RuntimeError(
                "Missing primary delay drivers detected."
            )

        print(
            "Primary delay driver: PASS"
        )

        # ----------------------------------------------------
        # WEATHER SEVERITY
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_flight
            WHERE weather_severity IS NULL
        """)

        missing_weather_severity = (
            cursor.fetchone()[0]
        )

        print(
            f"Missing weather severity: "
            f"{missing_weather_severity:,}"
        )

        if missing_weather_severity != 0:

            raise RuntimeError(
                "Missing weather severity detected."
            )

        print(
            "Weather severity: PASS"
        )

        # ----------------------------------------------------
        # NUMERIC SANITY
        # ----------------------------------------------------

        print(
            "\nNumeric sanity:"
        )

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_flight
            WHERE distance < 0
        """)

        negative_distance = (
            cursor.fetchone()[0]
        )

        print(
            f"DISTANCE < 0: "
            f"{negative_distance:,}"
        )

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_flight
            WHERE actual_elapsed_time < 0
        """)

        negative_elapsed = (
            cursor.fetchone()[0]
        )

        print(
            f"ACTUAL_ELAPSED_TIME < 0: "
            f"{negative_elapsed:,}"
        )

        # ----------------------------------------------------
        # EXTREME DELAYS
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM fact_flight
            WHERE arr_delay IS NOT NULL
              AND ABS(arr_delay) > 500
        """)

        extreme_arr_delay = (
            cursor.fetchone()[0]
        )

        print(
            f"Extreme ARR_DELAY values: "
            f"{extreme_arr_delay:,}"
        )

        # ----------------------------------------------------
        # SAMPLE
        # ----------------------------------------------------

        print(
            "\nSample fact rows:"
        )

        cursor.execute("""
            SELECT
                flight_id,
                flight_row_id,
                date_id,
                carrier_id,
                origin_airport_id,
                destination_airport_id,
                dep_delay,
                arr_delay,
                delay_category,
                primary_delay_driver,
                weather_severity
            FROM fact_flight
            ORDER BY flight_id
            LIMIT 5
        """)

        for record in cursor.fetchall():

            print(record)

        cursor.close()

        # ====================================================
        # COMPLETE
        # ====================================================

        print(
            "\n" + "=" * 80
        )

        print(
            "FACT FLIGHT LOAD COMPLETE"
        )

        print(
            "=" * 80
        )

    except Exception:

        print(
            "\nERROR OCCURRED."
        )

        print(
            "Rolling back transaction..."
        )

        connection.rollback()

        raise

    finally:

        connection.close()

        print(
            "\nMySQL connection closed."
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()