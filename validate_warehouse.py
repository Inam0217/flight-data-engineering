import mysql.connector


DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Kashar",
    "database": "flight_analytics",
}


EXPECTED_FACT_ROWS = 599_013
EXPECTED_AIRPORTS = 352
EXPECTED_CARRIERS = 10
EXPECTED_DATES = 31


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def check_count(cursor, table, expected):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    actual = cursor.fetchone()[0]

    status = "PASS" if actual == expected else "FAIL"

    print(
        f"{table:<25} "
        f"Expected: {expected:>10,} | "
        f"Actual: {actual:>10,} | "
        f"{status}"
    )

    return actual == expected


def main():

    print("=" * 80)
    print("FLIGHT ANALYTICS WAREHOUSE VALIDATION")
    print("=" * 80)

    print("\nConnecting to MySQL...")

    connection = get_connection()

    print("MySQL connection: SUCCESS")

    cursor = connection.cursor()

    all_passed = True

    # ============================================================
    # DIMENSION COUNTS
    # ============================================================

    print("\n" + "-" * 80)
    print("DIMENSION COUNTS")
    print("-" * 80)

    all_passed &= check_count(
        cursor,
        "dim_airport",
        EXPECTED_AIRPORTS
    )

    all_passed &= check_count(
        cursor,
        "dim_carrier",
        EXPECTED_CARRIERS
    )

    all_passed &= check_count(
        cursor,
        "dim_date",
        EXPECTED_DATES
    )

    # ============================================================
    # FACT COUNT
    # ============================================================

    print("\n" + "-" * 80)
    print("FACT TABLE")
    print("-" * 80)

    all_passed &= check_count(
        cursor,
        "fact_flight",
        EXPECTED_FACT_ROWS
    )

    # ============================================================
    # DUPLICATE FLIGHTS
    # ============================================================

    print("\n" + "-" * 80)
    print("DUPLICATE CHECK")
    print("-" * 80)

    cursor.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT flight_row_id
            FROM fact_flight
            GROUP BY flight_row_id
            HAVING COUNT(*) > 1
        ) d
    """)

    duplicate_flights = cursor.fetchone()[0]

    print(
        f"Duplicate flight_row_id: "
        f"{duplicate_flights:,}"
    )

    if duplicate_flights != 0:
        all_passed = False
        print("Duplicate check: FAIL")
    else:
        print("Duplicate check: PASS")

    # ============================================================
    # AIRPORT FOREIGN KEYS
    # ============================================================

    print("\n" + "-" * 80)
    print("AIRPORT FOREIGN KEY VALIDATION")
    print("-" * 80)

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_flight f
        LEFT JOIN dim_airport a
            ON f.origin_airport_id = a.airport_id
        WHERE a.airport_id IS NULL
    """)

    missing_origin = cursor.fetchone()[0]

    print(
        f"Missing origin airport references: "
        f"{missing_origin:,}"
    )

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_flight f
        LEFT JOIN dim_airport a
            ON f.destination_airport_id = a.airport_id
        WHERE a.airport_id IS NULL
    """)

    missing_destination = cursor.fetchone()[0]

    print(
        f"Missing destination airport references: "
        f"{missing_destination:,}"
    )

    if missing_origin == 0 and missing_destination == 0:
        print("Airport references: PASS")
    else:
        print("Airport references: FAIL")
        all_passed = False

    # ============================================================
    # CARRIER FOREIGN KEY
    # ============================================================

    print("\n" + "-" * 80)
    print("CARRIER FOREIGN KEY VALIDATION")
    print("-" * 80)

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_flight f
        LEFT JOIN dim_carrier c
            ON f.carrier_id = c.carrier_id
        WHERE c.carrier_id IS NULL
    """)

    missing_carriers = cursor.fetchone()[0]

    print(
        f"Missing carrier references: "
        f"{missing_carriers:,}"
    )

    if missing_carriers == 0:
        print("Carrier references: PASS")
    else:
        print("Carrier references: FAIL")
        all_passed = False

    # ============================================================
    # DATE FOREIGN KEY
    # ============================================================

    print("\n" + "-" * 80)
    print("DATE FOREIGN KEY VALIDATION")
    print("-" * 80)

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_flight f
        LEFT JOIN dim_date d
            ON f.date_id = d.date_id
        WHERE d.date_id IS NULL
    """)

    missing_dates = cursor.fetchone()[0]

    print(
        f"Missing date references: "
        f"{missing_dates:,}"
    )

    if missing_dates == 0:
        print("Date references: PASS")
    else:
        print("Date references: FAIL")
        all_passed = False

    # ============================================================
    # FLIGHT STATUS
    # ============================================================

    print("\n" + "-" * 80)
    print("FLIGHT STATUS")
    print("-" * 80)

    cursor.execute("""
        SELECT
            SUM(cancelled = 1),
            SUM(diverted = 1),
            SUM(cancelled = 0 AND diverted = 0)
        FROM fact_flight
    """)

    cancelled, diverted, completed = cursor.fetchone()

    print(f"Cancelled: {cancelled:,}")
    print(f"Diverted:  {diverted:,}")
    print(f"Completed: {completed:,}")

    if (
        cancelled == 18_740
        and diverted == 1_316
        and completed == 578_957
    ):
        print("Flight status: PASS")
    else:
        print("Flight status: FAIL")
        all_passed = False

    # ============================================================
    # WEATHER COVERAGE
    # ============================================================

    print("\n" + "-" * 80)
    print("WEATHER COVERAGE")
    print("-" * 80)

    cursor.execute("""
        SELECT
            COUNT(weather_timestamp_utc),
            COUNT(*)
        FROM fact_flight
    """)

    weather_available, total_flights = cursor.fetchone()

    print(
        f"Weather available: "
        f"{weather_available:,}"
    )

    print(
        f"Weather unavailable: "
        f"{total_flights - weather_available:,}"
    )

    if weather_available == 580_752:
        print("Weather coverage: PASS")
    else:
        print("Weather coverage: FAIL")
        all_passed = False

    # ============================================================
    # DELAY CATEGORY
    # ============================================================

    print("\n" + "-" * 80)
    print("DELAY CATEGORY VALIDATION")
    print("-" * 80)

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_flight
        WHERE delay_category IS NULL
           OR delay_category = ''
    """)

    missing_delay_category = cursor.fetchone()[0]

    print(
        f"Missing delay categories: "
        f"{missing_delay_category:,}"
    )

    if missing_delay_category == 0:
        print("Delay category: PASS")
    else:
        print("Delay category: FAIL")
        all_passed = False

    # ============================================================
    # PRIMARY DELAY DRIVER
    # ============================================================

    print("\n" + "-" * 80)
    print("PRIMARY DELAY DRIVER")
    print("-" * 80)

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_flight
        WHERE primary_delay_driver IS NULL
           OR primary_delay_driver = ''
    """)

    missing_driver = cursor.fetchone()[0]

    print(
        f"Missing primary delay drivers: "
        f"{missing_driver:,}"
    )

    if missing_driver == 0:
        print("Primary delay driver: PASS")
    else:
        print("Primary delay driver: FAIL")
        all_passed = False

    # ============================================================
    # WEATHER SEVERITY
    # ============================================================

    print("\n" + "-" * 80)
    print("WEATHER SEVERITY")
    print("-" * 80)

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_flight
        WHERE weather_severity IS NULL
           OR weather_severity = ''
    """)

    missing_severity = cursor.fetchone()[0]

    print(
        f"Missing weather severity: "
        f"{missing_severity:,}"
    )

    if missing_severity == 0:
        print("Weather severity: PASS")
    else:
        print("Weather severity: FAIL")
        all_passed = False

    # ============================================================
    # NUMERIC SANITY
    # ============================================================

    print("\n" + "-" * 80)
    print("NUMERIC SANITY")
    print("-" * 80)

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_flight
        WHERE distance < 0
    """)

    negative_distance = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_flight
        WHERE actual_elapsed_time < 0
    """)

    negative_elapsed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_flight
        WHERE arr_delay < -1000
           OR arr_delay > 1000
    """)

    extreme_delays = cursor.fetchone()[0]

    print(
        f"DISTANCE < 0: "
        f"{negative_distance:,}"
    )

    print(
        f"ACTUAL_ELAPSED_TIME < 0: "
        f"{negative_elapsed:,}"
    )

    print(
        f"Extreme ARR_DELAY values: "
        f"{extreme_delays:,}"
    )

    if (
        negative_distance == 0
        and negative_elapsed == 0
        and extreme_delays == 0
    ):
        print("Numeric sanity: PASS")
    else:
        print("Numeric sanity: FAIL")
        all_passed = False

    # ============================================================
    # FINAL STATUS
    # ============================================================

    print("\n" + "=" * 80)
    print("FINAL WAREHOUSE VALIDATION STATUS")
    print("=" * 80)

    if all_passed:
        print("\nALL WAREHOUSE VALIDATION CHECKS PASSED")
        print("\nWarehouse status: READY FOR ANALYTICS")
    else:
        print("\nWAREHOUSE VALIDATION FAILED")
        print("Review the failed checks above.")

    print("\n" + "=" * 80)

    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()