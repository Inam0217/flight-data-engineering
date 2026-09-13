# ✈️ Flight Data Engineering

An end-to-end **Data Engineering portfolio project** that extracts flight data from a REST API, cleans and transforms it with **Python**, and loads structured data into **MySQL** for SQL-based analysis.

## 🎯 Project Goal

The project demonstrates a practical flight-data ETL workflow:

- Extract flight data from a REST API
- Clean and transform raw records
- Validate and structure the dataset
- Load processed data into MySQL
- Analyze flight data using SQL

## 🏗️ Architecture

```text
REST API
   │
   ▼
EXTRACT
   │
   ▼
TRANSFORM
   │
   ├── Clean data
   ├── Handle missing values
   ├── Standardize fields
   └── Prepare structured records
   │
   ▼
LOAD
   │
   ▼
MySQL
   │
   ▼
SQL ANALYTICS
```

## 🔄 ETL Pipeline

### 1. Extract

Flight data is retrieved from a REST API using Python.

### 2. Transform

The transformation stage uses **Pandas** and **NumPy** to clean and prepare the dataset for storage and analysis.

Key activities include:

- Data cleaning
- Type conversion
- Handling missing values
- Column selection and standardization
- Dataset preparation

### 3. Load

The processed flight data is loaded into **MySQL** for persistent storage and analysis.

### 4. Analyze

SQL queries are used to explore the processed flight dataset and derive useful flight-related insights.

## 🛠️ Technology Stack

- **Python**
- **Pandas**
- **NumPy**
- **MySQL**
- **SQL**
- **REST API**
- **Git / GitHub**
- **PowerShell**

## 📁 Project Structure

```text
flight-data-engineering/
│
├── screenshots/
├── scripts/
│   └── investigation/
├── sql/
├── extract_*.py
├── transform_*.py
├── load_*.py
├── validate_*.py
├── test_*.py
├── .gitignore
└── README.md
```

## 🧪 Data Quality

The project includes validation and investigation steps to improve the reliability of the processed flight dataset.

The workflow focuses on:

- Missing-value handling
- Data-type consistency
- Duplicate checks
- Numeric sanity checks
- Validation before analysis

## 📊 SQL Analytics

The processed flight data can be analyzed using SQL for metrics such as:

- Flight volume
- Flight status
- Airline-level statistics
- Airport-level statistics
- Delay-related analysis

Example:

```sql
SELECT
    airline_code,
    COUNT(*) AS total_flights
FROM flights
GROUP BY airline_code
ORDER BY total_flights DESC;
```

## ▶️ Running the Project

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure the required API and MySQL settings in a local `.env` file.

Run the pipeline stages in order:

```text
Extract
  ↓
Transform
  ↓
Load
  ↓
Validate
  ↓
SQL Analytics
```

## 🚧 Future Improvements

- Add automated pipeline scheduling
- Add more comprehensive automated tests
- Build a simple flight analytics dashboard

## 👨‍💻 Project Focus

This project demonstrates practical experience with:

**REST API → Python ETL → Pandas / NumPy → MySQL → SQL Analytics**

Built as part of my journey toward a **Data Engineer** role.
