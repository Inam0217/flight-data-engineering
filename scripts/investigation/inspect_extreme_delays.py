import mysql.connector


DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Kashar",
    "database": "flight_analytics",
}


def main():

    print("=" * 80)
    print("EXTREME ARRIVAL DELAY INVESTIGATION")
    print("=" * 80)

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)

    print("\nLoading extreme arrival delays...")

    cursor.execute("""
        SELECT
            f.flight_row_id,
            d.full_date,
            c.carrier_code,
            f.carrier_flight_number,

            oa.airport_code AS origin,
            da.airport_code AS destination,

            f.scheduled_departure_local,
            f.actual_departure_local,
            f.scheduled_arrival_local,
            f.actual_arrival_local,

            f.crs_elapsed_time,
            f.actual_elapsed_time,
            f.arr_delay,
            f.delay_category,
            f.primary_delay_driver,

            f.cancelled,
            f.diverted,

            f.weather_delay,
            f.weather_severity

        FROM fact_flight f

        JOIN dim_date d
            ON f.date_id = d.date_id

        JOIN dim_carrier c
            ON f.carrier_id = c.carrier_id

        JOIN dim_airport oa
            ON f.origin_airport_id = oa.airport_id

        JOIN dim_airport da
            ON f.destination_airport_id = da.airport_id

        WHERE f.arr_delay < -1000
           OR f.arr_delay > 1000

        ORDER BY ABS(f.arr_delay) DESC
    """)

    rows = cursor.fetchall()

    print(
        f"\nExtreme ARR_DELAY records: "
        f"{len(rows):,}"
    )

    print("\n" + "-" * 80)

    for row in rows[:30]:

        print(
            f"\nFlight row ID: {row['flight_row_id']}"
        )

        print(
            f"Date: {row['full_date']}"
        )

        print(
            f"Flight: "
            f"{row['carrier_code']} "
            f"{row['carrier_flight_number']}"
        )

        print(
            f"Route: "
            f"{row['origin']} → "
            f"{row['destination']}"
        )

        print(
            f"Scheduled departure: "
            f"{row['scheduled_departure_local']}"
        )

        print(
            f"Actual departure: "
            f"{row['actual_departure_local']}"
        )

        print(
            f"Scheduled arrival: "
            f"{row['scheduled_arrival_local']}"
        )

        print(
            f"Actual arrival: "
            f"{row['actual_arrival_local']}"
        )

        print(
            f"CRS elapsed: "
            f"{row['crs_elapsed_time']}"
        )

        print(
            f"Actual elapsed: "
            f"{row['actual_elapsed_time']}"
        )

        print(
            f"ARR_DELAY: "
            f"{row['arr_delay']}"
        )

        print(
            f"Delay category: "
            f"{row['delay_category']}"
        )

        print(
            f"Primary driver: "
            f"{row['primary_delay_driver']}"
        )

        print(
            f"Cancelled: "
            f"{row['cancelled']}"
        )

        print(
            f"Diverted: "
            f"{row['diverted']}"
        )

        print(
            f"Weather delay: "
            f"{row['weather_delay']}"
        )

        print(
            f"Weather severity: "
            f"{row['weather_severity']}"
        )

        print("-" * 80)

    # ============================================================
    # DISTRIBUTION
    # ============================================================

    print("\n" + "=" * 80)
    print("EXTREME DELAY DISTRIBUTION")
    print("=" * 80)

    cursor.execute("""
        SELECT
            CASE
                WHEN arr_delay > 1000
                    THEN 'greater_than_1000'
                WHEN arr_delay < -1000
                    THEN 'less_than_negative_1000'
            END AS category,
            COUNT(*) AS flights,
            MIN(arr_delay) AS minimum_delay,
            MAX(arr_delay) AS maximum_delay
        FROM fact_flight
        WHERE arr_delay < -1000
           OR arr_delay > 1000
        GROUP BY
            CASE
                WHEN arr_delay > 1000
                    THEN 'greater_than_1000'
                WHEN arr_delay < -1000
                    THEN 'less_than_negative_1000'
            END
    """)

    for row in cursor.fetchall():

        print(
            f"{row['category']:<30} "
            f"Flights: {row['flights']:,} | "
            f"Min: {row['minimum_delay']} | "
            f"Max: {row['maximum_delay']}"
        )

    cursor.close()
    connection.close()

    print("\n" + "=" * 80)
    print("EXTREME DELAY INVESTIGATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()