"""
Main runner: ensure table, load CSVs from src/df (or given paths), and export DB to CSV.

Usage:
  python src/main.py
  python src/main.py --run-queries
  python src/main.py --dir src/df --pattern "*.csv" --recursive
  python src/main.py file1.csv folderA/
  python src/main.py --export-path outputs/dump.csv
"""
import argparse
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from engine import get_engine
from tables import DDL as MYSQL_DDL
import re
from columns_map import RENAME_MAP as rename_map

REQUIRED = ["source","time","month","category","latitude","longitude","depth","magnitude","region","dist_to_Tokyo"]


def ensure_table(engine, table="earthquakes"):
    with engine.begin() as conn:
        conn.execute(text(MYSQL_DDL))
    print(f"[init] ensured table `{table}`")

def discover(paths, base: Path, pattern: str, recursive: bool):
    files = []
    for p in paths:
        p = Path(p).expanduser()
        if p.is_file() and p.suffix.lower()==".csv":
            files.append(p)
        elif p.is_dir():
            pat = "**/"+pattern if recursive else pattern
            files += sorted(p.glob(pat))
    if not paths:
        pat = "**/"+pattern if recursive else pattern
        files = sorted(base.glob(pat))
    seen, out = set(), []
    for f in files:
        r = f.resolve()
        if f.suffix.lower()==".csv" and f.exists() and r not in seen:
            out.append(f); seen.add(r)
    return out

def build_df(csv_path: Path):
    df = pd.read_csv(csv_path)
    df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
    for c in REQUIRED:
        if c not in df.columns:
            df[c] = None
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce").dt.tz_convert(None)
    if "dist_to_Tokyo" in df.columns:
        df["dist_to_Tokyo"] = (
            df["dist_to_Tokyo"].astype(str)
            .str.replace(r"[^0-9.\-]","", regex=True)
            .replace({"": None})
        )
    for c in ["latitude","longitude","depth","magnitude","dist_to_Tokyo"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if df["month"].isna().all():
        try:
            df["month"] = df["time"].dt.month_name()
        except Exception:
            pass
    df = df[REQUIRED].dropna(subset=["time","latitude","longitude"])
    df = df.drop_duplicates(subset=["source","time","latitude","longitude"])
    return df

def export_all(engine, table: str, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with engine.begin() as conn:
        out = pd.read_sql(f"SELECT * FROM {table}", conn)
    out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[export] {len(out):,} rows -> {out_path}")




def parse_named_queries(sql_text: str):
    """
    Parse queries of the form:
      -- name: my_query
      SELECT ...;
    Returns list of (name, sql).
    """
    blocks = re.split(r'(?m)^\s*--\s*name:\s*', sql_text)[1:]  # split and drop preamble
    named = []
    for blk in blocks:
        # first line until newline = name
        first_newline = blk.find('\n')
        name = blk[:first_newline].strip()
        sql = blk[first_newline+1:].strip()
        # trim trailing ; if present
        if sql.endswith(';'):
            sql = sql[:-1].strip()
        if name and sql:
            named.append((name, sql))
    return named

def run_queries_and_export(engine, sql_path: str, out_dir: str):
    """
    Run each named SELECT in sql_path and export to {out_dir}/{name}.csv
    """
    sql_file = Path(sql_path)
    if not sql_file.exists():
        print(f"[queries] File not found: {sql_file}. Skipping.")
        return

    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)

    text = sql_file.read_text(encoding="utf-8")
    queries = parse_named_queries(text)
    print(f"[queries] Found {len(queries)} named SELECT query(ies) in {sql_file}.")

    if not queries:
        print(f"[queries] No named queries found in {sql_path}. Use lines like:  -- name: my_query")
        return

    with engine.begin() as conn:
        for i, (name, sql) in enumerate(queries, 1):
            # فقط SELECT ها را خروجی بگیریم (ایمن‌تر)
            if not sql.strip().lower().startswith("select"):
                print(f"[queries] Skipped non-SELECT: {name}")
                continue
            try:
                df = pd.read_sql(sql, conn)
                out_file = p / f"{name}.csv"
                df.to_csv(out_file, index=False, encoding="utf-8-sig")
                print(f"[queries] ({i}/{len(queries)}) wrote {out_file}  rows={len(df)}")
            except Exception as e:
                print(f"[queries] ({i}/{len(queries)}) FAILED {name}: {e}")




def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="*", help="CSV files/dirs (optional). If none, scans --dir.")
    ap.add_argument("--dir", default="src/df")
    ap.add_argument("--pattern", default="*.csv")
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--table", default="earthquakes")
    ap.add_argument("--export-path", default="outputs/earthquakes_export.csv")

    ap.add_argument("--queries", default="src/queries.sql",
                    help="Path to .sql file with named queries (default: src/queries.sql)")
    ap.add_argument("--queries-out", default="outputs/queries",
                    help="Directory to save per-query CSVs (default: outputs/queries)")
    ap.add_argument("--run-queries", action="store_true",
                    help="Run queries from --queries and export each to CSV")

    args = ap.parse_args()

    eng = get_engine()
    ensure_table(eng, args.table)

    files = discover(args.inputs, Path(args.dir), args.pattern, args.recursive)
    if files:
        print(f"[load] Found {len(files)} CSV(s).")
        total = 0
        for i, f in enumerate(files, 1):
            try:
                df = build_df(f)
                with eng.begin() as conn:
                    df.to_sql(args.table, conn, if_exists="append", index=False, chunksize=1000)
                total += len(df)
                print(f"[{i}/{len(files)}] +{len(df)} from {f}")
            except Exception as e:
                print(f"[{i}/{len(files)}] FAILED {f}: {e}")
        print(f"[load] Total inserted: {total}")
    else:
        print("[load] No CSVs found in scan.")
    

    print(f"[queries] Running named queries from {args.queries} -> {args.queries_out}")
    if args.run_queries:
        run_queries_and_export(eng, args.queries, args.queries_out)

    export_all(eng, args.table, Path(args.export_path))
    print("✅ Done.")

if __name__ == "__main__":
    main()