import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Kashar",
    "database": "flight_analytics",
}

connection = mysql.connector.connect(**DB_CONFIG)
cursor = connection.cursor()

cursor.execute("""
    SELECT
        COUNT(*) AS total,
        SUM(
            ABS(
                dep_delay -
                TIMESTAMPDIFF(
                    MINUTE,
                    scheduled_departure_utc,
                    actual_departure_utc
                )
            ) = 0
        ) AS exact_match,
        SUM(
            ABS(
                dep_delay -
                TIMESTAMPDIFF(
                    MINUTE,
                    scheduled_departure_utc,
                    actual_departure_utc
                )
            ) = 1440
        ) AS off_by_1_day,
        SUM(
            ABS(
                dep_delay -
                TIMESTAMPDIFF(
                    MINUTE,
                    scheduled_departure_utc,
                    actual_departure_utc
                )
            ) = 2880
        ) AS off_by_2_days,
        SUM(
            ABS(
                dep_delay -
                TIMESTAMPDIFF(
                    MINUTE,
                    scheduled_departure_utc,
                    actual_departure_utc
                )
            ) > 60
        ) AS difference_over_60
    FROM fact_flight
    WHERE
        cancelled = 0
        AND actual_departure_utc IS NOT NULL
        AND scheduled_departure_utc IS NOT NULL
        AND dep_delay IS NOT NULL
""")

row = cursor.fetchone()

print("=" * 80)
print("DEPARTURE DELAY ANOMALY ANALYSIS")
print("=" * 80)

print(f"\nTotal completed flights checked: {row[0]:,}")
print(f"Exact source/calculated match:   {row[1]:,}")
print(f"Off by exactly 1 day:            {row[2]:,}")
print(f"Off by exactly 2 days:           {row[3]:,}")
print(f"Difference greater than 60 min:  {row[4]:,}")

cursor.close()
connection.close()