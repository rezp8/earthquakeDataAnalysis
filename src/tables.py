import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

DDL = """
CREATE TABLE IF NOT EXISTS earthquakes (
  id INT NOT NULL AUTO_INCREMENT,
  source VARCHAR(20) NOT NULL,
  `time` DATETIME NOT NULL,
  month VARCHAR(20) NULL,
  category VARCHAR(20) NULL,
  latitude DOUBLE NOT NULL,
  longitude DOUBLE NOT NULL,
  depth DOUBLE NULL,
  magnitude DOUBLE NULL,
  region VARCHAR(100) NULL,
  dist_to_Tokyo DOUBLE NULL,
  PRIMARY KEY (id),
  -- prevent obvious duplicates (you can adjust as needed)
  UNIQUE KEY uq_src_time_lat_lon (source, `time`, latitude, longitude),
  KEY ix_time (`time`),
  KEY ix_region (region),
  KEY ix_magnitude (magnitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

def main():
    p = argparse.ArgumentParser(description="Create MySQL DB and 'earthquakes' table (no ORM).")
    p.add_argument("--db", required=True, help="Database name")
    p.add_argument("--user", required=True, help="MySQL user")
    p.add_argument("--password", required=True, help="MySQL password")
    p.add_argument("--host", default="127.0.0.1", help="MySQL host (use 127.0.0.1 to avoid socket issues)")
    p.add_argument("--port", type=int, default=3306, help="MySQL port")
    p.add_argument("--charset", default="utf8mb4", help="DB charset")
    p.add_argument("--collation", default="utf8mb4_0900_ai_ci", help="DB collation")
    args = p.parse_args()

    # connect to server (without database) and ensure DB exists
    server_url = URL.create(
        drivername="mysql+pymysql",
        username=args.user,
        password=args.password,
        host=args.host,
        port=args.port,
        query={"charset": "utf8mb4"},
    )
    server_engine = create_engine(server_url, future=True)

    create_db_sql = text(f"CREATE DATABASE IF NOT EXISTS `{args.db}` DEFAULT CHARACTER SET {args.charset} DEFAULT COLLATE {args.collation};")

    try:
        with server_engine.begin() as conn:
            conn.execute(create_db_sql)
            print(f"Database ensured: {args.db}")
    except Exception as e:
        print("Could not create/ensure database. Check credentials, host/port, and that MySQL is running.")
        print("Tip: brew services start mysql  (on macOS with Homebrew)")
        print("Error:", e)
        return

    # connect to the target database and run DDL
    db_url = URL.create(
        drivername="mysql+pymysql",
        username=args.user,
        password=args.password,
        host=args.host,
        port=args.port,
        database=args.db,
        query={"charset": "utf8mb4"},
    )
    db_engine = create_engine(db_url, future=True)

    try:
        with db_engine.begin() as conn:
            conn.execute(text(DDL))
            print("Table ensured: earthquakes")
            print("Indexes and UNIQUE constraint created if missing.")
    except Exception as e:
        print("Could not create table 'earthquakes'.")
        print("Error:", e)
        return

    print("Done.")

if __name__ == "__main__":
    main()