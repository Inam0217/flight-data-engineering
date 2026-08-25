import pandas as pd
import mysql.connector
from pathlib import Path
from datetime import date, timedelta


# =========================================================
# CONFIGURATION
# =========================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Kashar",
    "database": "flight_analytics",
}

AIRPORT_FILE = Path(
    "data/processed/airports_enriched.csv"
)

FLIGHT_FILE = Path(
    "data/processed/flights_analytics.csv"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
    )


# =========================================================
# LOAD AIRPORT DIMENSION
# =========================================================

def load_airports(cursor):

    print("\n" + "-" * 80)
    print("LOADING DIM_AIRPORT")
    print("-" * 80)

    airports = pd.read_csv(AIRPORT_FILE)

    airports["airport_code"] = (
        airports["airport_code"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    airports = airports.drop_duplicates(
        subset=["airport_code"]
    )

    print(
        f"Airports in CSV: "
        f"{len(airports):,}"
    )

    sql = """
        INSERT INTO dim_airport (
            airport_code,
            airport_name,
            latitude,
            longitude,
            timezone
        )
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            airport_name = VALUES(airport_name),
            latitude = VALUES(latitude),
            longitude = VALUES(longitude),
            timezone = VALUES(timezone)
    """

    rows = []

    for _, row in airports.iterrows():

        rows.append(
            (
                row["airport_code"],
                row["airport_name"],
                None if pd.isna(row["latitude"])
                else float(row["latitude"]),
                None if pd.isna(row["longitude"])
                else float(row["longitude"]),
                row["timezone"],
            )
        )

    cursor.executemany(sql, rows)

    print(
        f"Airport records processed: "
        f"{len(rows):,}"
    )


# =========================================================
# LOAD CARRIER DIMENSION
# =========================================================

def load_carriers(cursor):

    print("\n" + "-" * 80)
    print("LOADING DIM_CARRIER")
    print("-" * 80)

    flights = pd.read_csv(
        FLIGHT_FILE,
        usecols=["MKT_UNIQUE_CARRIER"]
    )

    carriers = (
        flights["MKT_UNIQUE_CARRIER"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .drop_duplicates()
        .sort_values()
    )

    print(
        f"Unique carriers found: "
        f"{len(carriers):,}"
    )

    sql = """
        INSERT INTO dim_carrier (
            carrier_code
        )
        VALUES (%s)
        ON DUPLICATE KEY UPDATE
            carrier_code = VALUES(carrier_code)
    """

    rows = [
        (carrier,)
        for carrier in carriers
    ]

    cursor.executemany(sql, rows)

    print(
        f"Carrier records processed: "
        f"{len(rows):,}"
    )

    print("\nCarrier codes:")

    for carrier in carriers:
        print(f"  {carrier}")


# =========================================================
# LOAD DATE DIMENSION
# =========================================================

def load_dates(cursor):

    print("\n" + "-" * 80)
    print("LOADING DIM_DATE")
    print("-" * 80)

    start_date = date(2025, 1, 1)
    end_date = date(2025, 1, 31)

    rows = []

    current = start_date

    while current <= end_date:

        date_id = int(
            current.strftime("%Y%m%d")
        )

        quarter = (
            (current.month - 1) // 3
        ) + 1

        rows.append(
            (
                date_id,
                current,
                current.year,
                quarter,
                current.month,
                current.strftime("%B"),
                current.day,
                current.isoweekday(),
                current.strftime("%A"),
                current.isocalendar().week,
            )
        )

        current += timedelta(days=1)

    sql = """
        INSERT INTO dim_date (
            date_id,
            full_date,
            year,
            quarter,
            month,
            month_name,
            day,
            day_of_week,
            day_name,
            week_of_year
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            full_date = VALUES(full_date),
            year = VALUES(year),
            quarter = VALUES(quarter),
            month = VALUES(month),
            month_name = VALUES(month_name),
            day = VALUES(day),
            day_of_week = VALUES(day_of_week),
            day_name = VALUES(day_name),
            week_of_year = VALUES(week_of_year)
    """

    cursor.executemany(
        sql,
        rows
    )

    print(
        f"Date records processed: "
        f"{len(rows):,}"
    )


# =========================================================
# VALIDATE DIMENSIONS
# =========================================================

def validate_dimensions(cursor):

    print("\n" + "-" * 80)
    print("DIMENSION VALIDATION")
    print("-" * 80)

    checks = {
        "dim_airport": (
            "SELECT COUNT(*) FROM dim_airport"
        ),
        "dim_carrier": (
            "SELECT COUNT(*) FROM dim_carrier"
        ),
        "dim_date": (
            "SELECT COUNT(*) FROM dim_date"
        ),
    }

    for table, sql in checks.items():

        cursor.execute(sql)

        count = cursor.fetchone()[0]

        print(
            f"{table:<20} {count:,}"
        )

    print("\nAirport sample:")

    cursor.execute(
        """
        SELECT
            airport_id,
            airport_code,
            airport_name,
            timezone
        FROM dim_airport
        ORDER BY airport_code
        LIMIT 5
        """
    )

    for row in cursor.fetchall():
        print(row)

    print("\nCarrier dimension:")

    cursor.execute(
        """
        SELECT
            carrier_id,
            carrier_code
        FROM dim_carrier
        ORDER BY carrier_code
        """
    )

    for row in cursor.fetchall():
        print(row)

    print("\nDate dimension sample:")

    cursor.execute(
        """
        SELECT
            date_id,
            full_date,
            year,
            month,
            day,
            day_name
        FROM dim_date
        ORDER BY full_date
        LIMIT 5
        """
    )

    for row in cursor.fetchall():
        print(row)


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 80)
    print("FLIGHT ANALYTICS WAREHOUSE - DIMENSION LOAD")
    print("=" * 80)

    print("\nConnecting to MySQL...")

    connection = get_connection()

    cursor = connection.cursor()

    print("MySQL connection: SUCCESS")

    try:

        load_airports(cursor)

        load_carriers(cursor)

        load_dates(cursor)

        connection.commit()

        print("\nTransaction committed.")

        validate_dimensions(cursor)

    except Exception:

        connection.rollback()

        print(
            "\nERROR: Transaction rolled back."
        )

        raise

    finally:

        cursor.close()
        connection.close()

    print("\n" + "=" * 80)
    print("DIMENSION LOAD COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()