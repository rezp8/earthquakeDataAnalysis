import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from columns_map import RENAME_MAP as rename_map

df = pd.read_csv("japan_clean_dataset.csv")

# Apply mapping only for existing columns
df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

# Create necessary columns if they do not exist (to prevent errors in to_sql)
needed = ["source","time","month","category","latitude","longitude","depth","magnitude","region","dist_to_Tokyo"]
for c in needed:
    if c not in df.columns:
        df[c] = None

# Types: time and numerics
df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce").dt.tz_convert(None)
for c in ["latitude","longitude","depth","magnitude","dist_to_Tokyo"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df["month"] = df["month"]

# Drop rows with missing key values
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

# Insert data
df.to_sql(
    name = "earthquakes",
    con = engine,
    if_exists = "append",
    index = False,
    chunksize = 1000
)

print("Data successfully loaded into MySQL table.")