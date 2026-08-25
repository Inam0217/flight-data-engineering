import os

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


def get_mysql_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


def load_weather(weather_rows):
    connection = get_mysql_connection()
    cursor = connection.cursor()

    sql = """
    INSERT INTO weather (
        airport_code,
        weather_timestamp,
        temperature,
        humidity,
        precipitation,
        rain,
        snowfall,
        wind_speed,
        wind_direction,
        visibility,
        cloud_cover,
        weather_code
    )
    VALUES (
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE
        temperature = VALUES(temperature),
        humidity = VALUES(humidity),
        precipitation = VALUES(precipitation),
        rain = VALUES(rain),
        snowfall = VALUES(snowfall),
        wind_speed = VALUES(wind_speed),
        wind_direction = VALUES(wind_direction),
        visibility = VALUES(visibility),
        cloud_cover = VALUES(cloud_cover),
        weather_code = VALUES(weather_code)
"""

    values = [
        (
            row["airport_code"],
            row["weather_timestamp"],
            row["temperature"],
            row["humidity"],
            row["precipitation"],
            row["rain"],
            row["snowfall"],
            row["wind_speed"],
            row["wind_direction"],
            row["visibility"],
            row["cloud_cover"],
            row["weather_code"]
        )
        for row in weather_rows
    ]

    cursor.executemany(sql, values)

    connection.commit()

    print(f"Processed {len(values)} weather rows.")

    cursor.close()
    connection.close()