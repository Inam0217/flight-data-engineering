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
    print("ARRIVAL DELAY CALCULATION INVESTIGATION")
    print("=" * 80)

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            f.flight_row_id,
            d.full_date,
            c.carrier_code,
            f.carrier_flight_number,

            oa.airport_code AS origin,
            da.airport_code AS destination,

            f.scheduled_arrival_local,
            f.actual_arrival_local,

            f.scheduled_arrival_utc,
            f.actual_arrival_utc,

            f.arr_delay,
            f.crs_elapsed_time,
            f.actual_elapsed_time,

            TIMESTAMPDIFF(
                MINUTE,
                f.scheduled_arrival_utc,
                f.actual_arrival_utc
            ) AS calculated_arr_delay

        FROM fact_flight f

        JOIN dim_date d
            ON f.date_id = d.date_id

        JOIN dim_carrier c
            ON f.carrier_id = c.carrier_id

        JOIN dim_airport oa
            ON f.origin_airport_id = oa.airport_id

        JOIN dim_airport da
            ON f.destination_airport_id = da.airport_id

        WHERE f.arr_delay > 1000

        ORDER BY f.arr_delay DESC
        LIMIT 30
    """)

    rows = cursor.fetchall()

    print(
        f"\nExtreme records inspected: {len(rows)}"
    )

    print("\n" + "-" * 80)

    for row in rows:

        print(
            f"\nFlight: "
            f"{row['carrier_code']} "
            f"{row['carrier_flight_number']}"
        )

        print(
            f"Route: "
            f"{row['origin']} -> "
            f"{row['destination']}"
        )

        print(
            f"Scheduled arrival local: "
            f"{row['scheduled_arrival_local']}"
        )

        print(
            f"Actual arrival local: "
            f"{row['actual_arrival_local']}"
        )

        print(
            f"Scheduled arrival UTC: "
            f"{row['scheduled_arrival_utc']}"
        )

        print(
            f"Actual arrival UTC: "
            f"{row['actual_arrival_utc']}"
        )

        print(
            f"Source ARR_DELAY: "
            f"{row['arr_delay']} minutes"
        )

        print(
            f"Calculated ARR_DELAY: "
            f"{row['calculated_arr_delay']} minutes"
        )

        print(
            f"Difference: "
            f"{float(row['arr_delay']) - float(row['calculated_arr_delay']):.0f} minutes"
        )

        print("-" * 80)

    cursor.close()
    connection.close()

    print("\n" + "=" * 80)
    print("ARRIVAL DELAY CALCULATION INVESTIGATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()