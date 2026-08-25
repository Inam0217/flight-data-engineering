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
    print("ARRIVAL DELAY ANOMALY INSPECTION")
    print("=" * 80)

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            flight_row_id,
            carrier_flight_number,
            dep_delay,
            arr_delay,
            scheduled_arrival_utc,
            actual_arrival_utc,

            TIMESTAMPDIFF(
                MINUTE,
                scheduled_arrival_utc,
                actual_arrival_utc
            ) AS calculated_arr_delay,

            arr_delay -
            TIMESTAMPDIFF(
                MINUTE,
                scheduled_arrival_utc,
                actual_arrival_utc
            ) AS difference

        FROM fact_flight

        WHERE
            cancelled = 0
            AND actual_arrival_utc IS NOT NULL
            AND scheduled_arrival_utc IS NOT NULL
            AND arr_delay IS NOT NULL

            AND ABS(
                arr_delay -
                TIMESTAMPDIFF(
                    MINUTE,
                    scheduled_arrival_utc,
                    actual_arrival_utc
                )
            ) > 60

        ORDER BY
            ABS(
                arr_delay -
                TIMESTAMPDIFF(
                    MINUTE,
                    scheduled_arrival_utc,
                    actual_arrival_utc
                )
            ) DESC

        LIMIT 50
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    print("\n" + "-" * 80)
    print("ANOMALOUS RECORDS")
    print("-" * 80)

    for row in rows:

        print(
            f"\nflight_row_id:          {row['flight_row_id']}"
        )

        print(
            f"carrier_flight_number:  {row['carrier_flight_number']}"
        )

        print(
            f"scheduled_arrival_utc:  {row['scheduled_arrival_utc']}"
        )

        print(
            f"actual_arrival_utc:     {row['actual_arrival_utc']}"
        )

        print(
            f"source ARR_DELAY:       {row['arr_delay']}"
        )

        print(
            f"calculated ARR_DELAY:   {row['calculated_arr_delay']}"
        )

        print(
            f"difference:             {row['difference']}"
        )

        print("-" * 40)

    cursor.close()
    connection.close()

    print("\n" + "=" * 80)
    print(f"Records displayed: {len(rows)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
    