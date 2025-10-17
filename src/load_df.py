import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# Read CSV file
df = pd.read_csv("JAPAN_API_cleaned.csv")

# normalize to DB schema (mapping)
rename_map = {
    # time
    "Datetime": "time",
    "date_time_UTC": "time",
    "DateTime_UTC": "time",
    "time_utc": "time",
    "time": "time",
    # month
    "Month": "month",
    # latitude
    "Latitude": "latitude",
    "latitude_deg": "latitude",
    "lat": "latitude",
    # longitude
    "Longitude": "longitude",
    "longitude_deg": "longitude",
    "lon": "longitude",
    # depth
    "Depth": "depth",
    "depth_km": "depth",
    "Depth_km": "depth",
    # magnitude
    "Magnitude": "magnitude",
    "magnitude_value": "magnitude",
    "mag": "magnitude",
    # region
    "Region": "region",
    "region": "region",
    "Place": "place",
    "place": "place",
    # distance to Tokyo
    "dist_to_Tokyo_km": "dist_to_Tokyo",
    "Dist_to_Tokyo_km": "dist_to_Tokyo",
    # source
    "Data_source": "source",
    "data_source": "source",
    # category
    "Category": "category"
}

# اعمال نگاشت فقط برای ستون‌های موجود
df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

# ستون‌های ضروری را اگر نبودند، بساز (برای جلوگیری از خطا در to_sql)
needed = ["source","time","month","category","latitude","longitude","depth","magnitude","region","dist_to_Tokyo"]
for c in needed:
    if c not in df.columns:
        df[c] = None

# نوع‌ها: زمان و عددی‌ها
df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce").dt.tz_convert(None)
for c in ["latitude","longitude","depth","magnitude","dist_to_Tokyo"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# keep the month values exactly as they appear in CSV
df["month"] = df["month"]

# حذف سطرهای ناقص کلیدی
df = df.dropna(subset=["time","latitude","longitude"])

df = df[["source","time","month","category","latitude","longitude","depth","magnitude","region","dist_to_Tokyo"]]

# Create a database connection (safe for special characters in password)
url = URL.create(
    drivername = "mysql+pymysql",
    username = "root",
    password = "@rezp6374",  # handles '@' safely
    host = "127.0.0.1",
    port = 3306,
    database = "earthquakeDB",
    query = {"charset": "utf8mb4"},
)
engine = create_engine(url)

# Insert data into SQL table
df.to_sql(
    name = "earthquakes",
    con = engine,
    if_exists = "append",
    index = False,
    chunksize = 1000
)

print("Data successfully loaded into MySQL table.")