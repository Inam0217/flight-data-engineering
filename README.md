# ✈️ Flight Delay & Weather Analytics

An end-to-end **Data Engineering portfolio project** that transforms flight data, enriches it with historical weather information, builds a MySQL analytical warehouse, and performs SQL-based flight performance analysis.

## 🎯 Project Goal

The project analyzes:

- Flight delays
- Airline performance
- Airport performance
- Route performance
- Cancellations
- Weather impact on flight delays

## 🏗️ Architecture

```text
Raw Flight Data
      │
      ▼
Python ETL
      │
      ├──────────────► Airport Data
      │
      └──────────────► Weather API
                            │
                            ▼
                   Flight + Weather
                      Enrichment
                            │
                            ▼
                   Analytical Layer
                            │
                            ▼
                    MySQL Warehouse
                            │
                            ▼
                     SQL Analytics
```

## 🔄 Pipeline

1. Extract flight and airport data
2. Clean and transform flight records
3. Enrich flights with airport/timezone information
4. Collect historical weather data through an API
5. Match weather observations with flight departure times
6. Build the analytical flight dataset
7. Load the data into a MySQL dimensional warehouse
8. Validate the warehouse
9. Run SQL analytics

## 🗄️ Data Warehouse

The MySQL warehouse uses a simple dimensional model:

```text
dim_airport
dim_carrier
dim_date
     │
     ▼
fact_flight
```

The fact table contains flight timing, delays, cancellation/diversion information, delay drivers, and weather attributes.

## 📊 Project Results

| Metric | Result |
|---|---:|
| Flight records | **599,013** |
| Airports | **352** |
| Carriers | **10** |
| Weather available | **580,752** |
| Duplicate flight IDs | **0** |
| Broken dimension references | **0** |

Approximately **97% of flights have weather data available**.

## 🔎 SQL Analytics

### 1. Airline Performance

Analyzes flight volume, cancellation rate, and average delays.

![Airline Performance](screenshots/1.%20Airline%20Performance.png)

### 2. Airport Performance

Analyzes completed departures and departure-delay performance.

![Airport Performance](screenshots/2.%20Airport%20Performance.png)

### 3. Weather Impact

Compares flight delays across different weather severity categories.

![Weather Impact](screenshots/3.%20Weather%20Impact.png)

### 4. Route Performance

Analyzes completed flights and average delays by origin-destination route.

![Route Performance](screenshots/4.%20Route%20Performance.png)

## 🛠️ Technology Stack

- Python
- Pandas
- NumPy
- MySQL
- SQL
- REST API
- Git / GitHub
- PowerShell

## 📁 Project Structure

```text
flight-data-engineering/
│
├── screenshots/
├── scripts/
│   └── investigation/
├── sql/
│   └── flight_analytics_warehouse.sql
│
├── extract_*.py
├── transform_*.py
├── enrich_*.py
├── build_flight_analytics.py
├── load_warehouse.py
├── load_fact_flights.py
├── validate_*.py
├── test_*.py
├── weather_api.py
├── weather_loader.py
│
├── .gitignore
└── README.md
```

## ▶️ Running the Project

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scriptsctivate
```

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

Configure the required API/database settings in a local `.env` file.

The `.env`, virtual environment, caches, and generated datasets are excluded from Git.

Run the pipeline stages in order:

```text
Extract
  ↓
Transform
  ↓
Enrich
  ↓
Build Analytical Layer
  ↓
Load MySQL Warehouse
  ↓
Validate
  ↓
SQL Analytics
```

## 🧪 Data Quality

The project includes validation for:

- Row counts
- Duplicate flight IDs
- Dimension mappings
- Foreign-key references
- Flight status
- Weather coverage
- Delay categories
- Weather severity
- Numeric sanity

Unusual source delay values were investigated and retained rather than silently removed.

## 🚧 Limitations & Future Work

This is a learning/portfolio project rather than a production airline platform.

Possible future improvements:

- Apache Airflow orchestration
- Automated scheduling
- BI dashboard
- Cloud warehouse deployment
- Incremental loading
- More comprehensive automated tests
- Improved API retry and monitoring

## 👨‍💻 Project Focus

This project demonstrates practical experience with:

**ETL → API Integration → Data Quality → Data Warehouse → SQL Analytics**

Built as part of my journey toward a **Junior Data Engineer** role.
