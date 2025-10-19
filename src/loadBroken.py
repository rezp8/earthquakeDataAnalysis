import pandas as pd
from pathlib import Path
from columns_map import RENAME_MAP as rename_map
from engine import get_engine

REQUIRED = ["source","time","month","category","latitude","longitude","depth","magnitude","region","dist_to_Tokyo"]

def infer_source_from_name(path: Path) -> str:
    name = path.stem.lower()
    if "usgs" in name:
        return "USGS"
    if "geofon" in name:
        return "GEOFON"
    if "emsc" in name:
        return "EMSC"
    if "api" in name or "dataset" in name or "clean_dataset" in name:
        return "API"
    return "UNKNOWN"

def coalesce_dupes(frame: pd.DataFrame, colname: str) -> pd.DataFrame:
    """If duplicate columns with the same final name exist, keep first non-null across them."""
    # Collect exact-name duplicates (pandas keeps them but not addressable by unique name)
    same = [i for i, c in enumerate(frame.columns) if c == colname]
    if len(same) <= 1:
        return frame
    # build a small DF of the dupes in order and backfill left-to-right
    sub = frame.iloc[:, same]
    combined = sub.bfill(axis=1).iloc[:, 0]
    # drop all duplicates by position, then set the combined column once
    frame = frame.drop(frame.columns[same], axis=1)
    frame[colname] = combined
    return frame

def normalize_one_csv(csv_path: Path) -> pd.DataFrame:
    """Read one CSV, normalize columns/types, and return clean dataframe."""
    df = pd.read_csv(csv_path)

    # Ensure/patch source
    inferred = infer_source_from_name(csv_path)
    if "source" not in df.columns or df["source"].isna().all():
        df["source"] = inferred
    else:
        df["source"] = df["source"].fillna(inferred)

    # Rename only existing columns
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Coalesce duplicates that may have been created by rename (e.g., Datetime + time -> time)
    for _col in ["time", "latitude", "longitude", "depth", "magnitude", "region", "source", "month", "category", "dist_to_Tokyo"]:
        df = coalesce_dupes(df, _col)

    # Ensure required columns exist
    for c in REQUIRED:
        if c not in df.columns:
            df[c] = None

    # Robust datetime parsing with fallbacks
    t0 = pd.to_datetime(df["time"], utc=True, errors="coerce")
    if t0.isna().mean() > 0.5:
        t0 = pd.to_datetime(df["time"], errors="coerce")
    if t0.isna().mean() > 0.5:
        t0 = pd.to_datetime(df["time"], errors="coerce", dayfirst=True)
    df["time"] = pd.to_datetime(t0, utc=True, errors="coerce").dt.tz_convert(None)

    # Clean distance like "380.5 km" and cast numerics
    if "dist_to_Tokyo" in df.columns:
        df["dist_to_Tokyo"] = (
            df["dist_to_Tokyo"].astype(str)
            .str.replace(r"[^0-9.\-]", "", regex=True)
            .replace({"": None})
        )

    for c in ["latitude","longitude","depth","magnitude","dist_to_Tokyo"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Derive month if empty
    try:
        if df["month"].isna().all():
            df["month"] = df["time"].dt.month_name()
    except Exception:
        pass

    # Keep only required columns (ordered)
    df = df[REQUIRED]

    # Drop rows missing key fields
    before = len(df)
    df = df.dropna(subset=["time","latitude","longitude"])
    dropped = before - len(df)

    # De-duplicate
    before_dups = len(df)
    df = df.drop_duplicates(subset=["source","time","latitude","longitude"])
    removed_dups = before_dups - len(df)

    print(f"  - {csv_path.name}: {before} rows, dropped {dropped} invalid, removed {removed_dups} dups -> {len(df)} kept")
    return df

def main():
    folder = Path("src/df")
    files = sorted(p for p in folder.glob("*.csv") if p.is_file())

    if not files:
        print("⚠ No CSV files found in src/df. Place your cleaned CSVs there.")
        return

    print(f"📂 Found {len(files)} CSV file(s) in {folder}")
    frames = []
    for f in files:
        try:
            frames.append(normalize_one_csv(f))
        except Exception as e:
            print(f"  ✖ Failed on {f.name}: {e}")

    if not frames:
        print("⚠ No valid dataframes to insert.")
        return

    df_all = pd.concat(frames, ignore_index=True)
    print(f"[merge] Total rows to insert: {len(df_all)}")

    # Insert into MySQL
    engine = get_engine()
    with engine.begin() as conn:
        df_all.to_sql(
            name="earthquakes",
            con=conn,
            if_exists="append",
            index=False,
            chunksize=1000
        )

    print(f"✔ Inserted {len(df_all)} rows into MySQL table 'earthquakes'.")

if __name__ == "__main__":
    main()