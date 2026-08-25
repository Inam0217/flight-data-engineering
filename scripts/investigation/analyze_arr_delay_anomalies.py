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
    print("ARRIVAL DELAY ANOMALY ANALYSIS")
    print("=" * 80)

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(
                ABS(
                    arr_delay -
                    TIMESTAMPDIFF(
                        MINUTE,
                        scheduled_arrival_utc,
                        actual_arrival_utc
                    )
                ) = 0
            ) AS exact_match,

            SUM(
                ABS(
                    arr_delay -
                    TIMESTAMPDIFF(
                        MINUTE,
                        scheduled_arrival_utc,
                        actual_arrival_utc
                    )
                ) = 1440
            ) AS off_by_1_day,

            SUM(
                ABS(
                    arr_delay -
                    TIMESTAMPDIFF(
                        MINUTE,
                        scheduled_arrival_utc,
                        actual_arrival_utc
                    )
                ) = 2880
            ) AS off_by_2_days,

            SUM(
                ABS(
                    arr_delay -
                    TIMESTAMPDIFF(
                        MINUTE,
                        scheduled_arrival_utc,
                        actual_arrival_utc
                    )
                ) > 60
            ) AS difference_over_60

        FROM fact_flight
        WHERE
            cancelled = 0
            AND actual_arrival_utc IS NOT NULL
            AND scheduled_arrival_utc IS NOT NULL
            AND arr_delay IS NOT NULL
    """)

    row = cursor.fetchone()

    print("\n" + "-" * 80)
    print("ARRIVAL DELAY COMPARISON")
    print("-" * 80)

    print(f"Total completed flights checked: {row[0]:,}")
    print(f"Exact source/calculated match:   {row[1]:,}")
    print(f"Off by exactly 1 day:            {row[2]:,}")
    print(f"Off by exactly 2 days:            {row[3]:,}")
    print(f"Difference greater than 60 min: {row[4]:,}")

    cursor.execute("""
        SELECT
            MIN(arr_delay),
            MAX(arr_delay),
            MIN(
                TIMESTAMPDIFF(
                    MINUTE,
                    scheduled_arrival_utc,
                    actual_arrival_utc
                )
            ),
            MAX(
                TIMESTAMPDIFF(
                    MINUTE,
                    scheduled_arrival_utc,
                    actual_arrival_utc
                )
            )
        FROM fact_flight
        WHERE
            cancelled = 0
            AND actual_arrival_utc IS NOT NULL
            AND scheduled_arrival_utc IS NOT NULL
    """)

    row = cursor.fetchone()

    print("\n" + "-" * 80)
    print("DELAY RANGE")
    print("-" * 80)

    print(f"Source ARR_DELAY minimum:       {row[0]}")
    print(f"Source ARR_DELAY maximum:       {row[1]}")
    print(f"Calculated delay minimum:       {row[2]}")
    print(f"Calculated delay maximum:       {row[3]}")

    cursor.close()
    connection.close()

    print("\n" + "=" * 80)
    print("ARRIVAL DELAY ANOMALY ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()