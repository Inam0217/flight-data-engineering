from weather_api import get_weather


rows = get_weather(
    airport_code="JED",
    latitude=21.679600,
    longitude=39.156500,
    timezone="Asia/Riyadh",
    start_date="2025-01-05",
    end_date="2025-01-05"
)

print("Number of rows:", len(rows))

for row in rows[:3]:
    print(row)