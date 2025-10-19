# Earthquake-data-analysis-in-Japan
# 🌏 Earthquake Data Analysis - Japan

Comprehensive analysis of earthquake data in **Japan** using **Python**, **Pandas**, **NumPy**, **SQL**, and **Matplotlib**.  
This project was developed as the **final project** of the Quera Python Bootcamp, focusing on real-world data processing and analytics.

---

## 📘 Project Overview

Japan is one of the most earthquake-prone countries in the world.  
This project aims to collect, clean, analyze, and visualize earthquake data from multiple trusted sources to gain insights into recent seismic activities.

### Main Data Sources
- [USGS (United States Geological Survey)](https://earthquake.usgs.gov/)
- [GEOFON (GFZ Helmholtz Centre for Geosciences)](https://geofon.gfz.de/)
- [EMSC (European-Mediterranean Seismological Centre)](https://www.emsc.eu/)

### Objectives
- Collect real earthquake data from the past month in Japan  
- Perform statistical and spatial analyses  
- Store data efficiently in an SQL database  
- Visualize findings through clear and insightful plots  
- Compare different data sources in terms of accuracy and coverage

---

## 🧠 Project Workflow

### 1️⃣ Data Collection
Data is collected using:
- **USGS API**
- **Web scraping** from GEOFON and EMSC using `requests`, `BeautifulSoup`, and `Selenium`
- **Prepared datasets** for validation and testing

Generated CSV files:

---

### 2️⃣ Data Cleaning & Preprocessing (Pandas)
Performed tasks:
- Handle missing (`NaN`) values
- Convert data types to `float` and `datetime`
- Create additional columns:
  - `Month` – month of occurrence  
  - `Category` – earthquake strength classification (Weak, Moderate, Strong)  
  - `region` – extracted from the `place` column
- Group and aggregate data by month and region
- Compute averages, min/max values, and distributions

---

### 3️⃣ Numerical & Statistical Analysis (NumPy)
Using **NumPy** for:
- Statistical calculations (`mean`, `std`, `percentile`)
- Computing **Euclidean distances** from earthquake epicenters to Tokyo
- Estimating risk indices based on magnitude and depth

---

### 4️⃣ SQL Database Integration
Data is stored in an SQL table named `earthquakes`:

| Column | Description |
|--------|--------------|
| id | Primary key (auto-increment) |
| time | Datetime of event |
| latitude / longitude | Geographic coordinates |
| depth | Earthquake depth |
| magnitude | Magnitude of earthquake |
| region | Extracted region name |
| source | Data source (USGS / GEOFON / EMSC) |

Example connection and insertion:
```python
from sqlalchemy import create_engine
engine = create_engine("mysql+pymysql://user:password@host:port/database")
df.to_sql("earthquakes", con=engine, if_exists="append", index=False)
-- Count earthquakes by region and month
SELECT region, EXTRACT(MONTH FROM time) AS month, COUNT(*)
FROM earthquakes
GROUP BY region, month;

-- Average magnitude by data source
SELECT source, AVG(magnitude)
FROM earthquakes
GROUP BY source;
pip install -r requirements.txt
pandas
numpy
matplotlib
sqlalchemy
pymysql
requests
beautifulsoup4
selenium
earthquakeDataAnalysis/
│
├── data/
│   ├── JAPAN_USGS.csv
│   ├── JAPAN_GEOFON.csv
│   ├── JAPAN_EMSC.csv
│   └── JAPAN_DATASET.csv
│
├── src/
│   ├── data_collection.py
│   ├── data_cleaning.py
│   ├── analysis.py
│   ├── visualization.py
│   └── database.py
│
├── tests/
│   └── test_validation.py
│
├── requirements.txt
├── README.md
└── main.py
