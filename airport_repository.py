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


def get_airports():
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            airport_code,
            latitude,
            longitude,
            timezone
        FROM airports
    """

    cursor.execute(query)

    airports = cursor.fetchall()

    cursor.close()
    connection.close()

    return airports